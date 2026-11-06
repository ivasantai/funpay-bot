"""Шлёт в Telegram уведомления о новых сообщениях и заказах на FunPay."""
import html
import logging
import os
import time

import requests
from FunPayAPI import Account, Runner
from FunPayAPI.common import exceptions as fp_exceptions
from FunPayAPI.updater.events import EventTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("funpay-bot")


def _patched_method(self, request_method, api_method, headers, payload,
                    exclude_phpsessid=False, raise_not_200=False):
    """FunPay теперь требует cookie golden_seal, которую FunPayAPI 1.1.0 не передаёт.
    Шлём запросы через requests.Session, чтобы все выданные сайтом cookie сохранялись."""
    session = getattr(self, "_fp_session", None)
    if session is None:
        session = self._fp_session = requests.Session()
        session.cookies.set("golden_key", self.golden_key, domain="funpay.com")
    if exclude_phpsessid:
        for c in list(session.cookies):
            if c.name == "PHPSESSID":
                session.cookies.clear(c.domain, c.path, c.name)
    headers = dict(headers)
    headers.pop("cookie", None)
    headers["user-agent"] = self.user_agent or (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
    )
    link = api_method if api_method.startswith("https://funpay.com") else "https://funpay.com/" + api_method
    response = getattr(session, request_method)(
        link, headers=headers, data=payload, timeout=self.requests_timeout, proxies=self.proxy or {}
    )
    if response.status_code == 403:
        raise fp_exceptions.UnauthorizedError(response)
    if response.status_code != 200 and raise_not_200:
        raise fp_exceptions.RequestFailedError(response)
    return response


Account.method = _patched_method

_orig_parse_messages = Account._Account__parse_messages


def _patched_parse_messages(self, json_messages, *args, **kwargs):
    """FunPay переименовал класс текста сообщения: message-text -> chat-msg-text.
    Подменяем класс обратно, чтобы парсер FunPayAPI 1.1.0 его находил."""
    fixed = []
    for m in json_messages:
        m = dict(m)
        h = m.get("html", "")
        h = h.replace('class="chat-msg-text"', 'class="message-text"')
        if ('class="message-text"' not in h and "chat-img-link" not in h
                and "alert-with-icon" not in h):
            h += '<div class="message-text"></div>'  # на случай сообщений без текста
        m["html"] = h
        fixed.append(m)
    return _orig_parse_messages(self, fixed, *args, **kwargs)


Account._Account__parse_messages = _patched_parse_messages


def load_env(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def send_telegram(token: str, chat_id: str, text: str) -> None:
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        if not r.ok:
            log.error("Telegram: %s %s", r.status_code, r.text)
    except requests.RequestException as e:
        log.error("Telegram недоступен: %s", e)


def main() -> None:
    load_env()
    golden_key = os.environ["FUNPAY_GOLDEN_KEY"]
    tg_token = os.environ["TELEGRAM_BOT_TOKEN"]
    tg_chat = os.environ["TELEGRAM_CHAT_ID"]
    delay = float(os.environ.get("POLL_DELAY", "6"))

    account = Account(golden_key).get()
    log.info("Вошёл на FunPay как %s (id %s)", account.username, account.id)
    send_telegram(tg_token, tg_chat, f"✅ Бот запущен, аккаунт FunPay: <b>{html.escape(account.username)}</b>")

    runner = Runner(account)
    for event in runner.listen(requests_delay=delay):
        try:
            if event.type is EventTypes.NEW_MESSAGE:
                msg = event.message
                if msg.author_id == account.id:  # свои сообщения пропускаем
                    continue
                body = msg.text or ("🖼 изображение" if msg.image_link else "")
                text = (
                    f"💬 <b>Новое сообщение</b> от <b>{html.escape(str(msg.author))}</b>\n"
                    f"{html.escape(body)}\n"
                    f'<a href="https://funpay.com/chat/?node={msg.chat_id}">Открыть чат</a>'
                )
                send_telegram(tg_token, tg_chat, text)
            elif event.type is EventTypes.NEW_ORDER:
                o = event.order
                text = (
                    f"🛒 <b>Новый заказ #{html.escape(str(o.id))}</b>\n"
                    f"Покупатель: <b>{html.escape(o.buyer_username)}</b>\n"
                    f"Товар: {html.escape(o.description)}\n"
                    f"Сумма: {o.price}\n"
                    f'<a href="https://funpay.com/orders/{html.escape(str(o.id))}/">Открыть заказ</a>'
                )
                send_telegram(tg_token, tg_chat, text)
        except Exception:
            log.exception("Ошибка обработки события")


def start_health_server() -> None:
    """Для хостингов типа Render: если задан PORT, отвечаем 200 на любой GET,
    чтобы сервис считался живым (и его можно было «будить» пингом UptimeRobot)."""
    port = os.environ.get("PORT")
    if not port:
        return
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("ok".encode())

        do_HEAD = do_GET

        def log_message(self, *args):
            pass

    server = HTTPServer(("0.0.0.0", int(port)), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log.info("Health-сервер слушает порт %s", port)


if __name__ == "__main__":
    load_env()
    start_health_server()
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
        except Exception:
            log.exception("Бот упал, перезапуск через 30 с")
            time.sleep(30)
