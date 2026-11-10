# FunPay → Telegram: new message and order notifications

The bot watches your [FunPay](https://funpay.com) account and instantly sends to Telegram:

- 💬 **new chat messages**: who wrote, the text (or an "image" note) and a link to the chat;
- 🛒 **new orders**: order number, buyer, item, price and a link to the order.

Your own messages are not forwarded. Notifications can be sent to several Telegram chats at once.

```
💬 Новое сообщение от buyer_123
Здравствуйте, товар в наличии?
Открыть чат
```

> The notification texts are in Russian ("Новое сообщение от" = "New message from", "Открыть чат" = "Open chat"). You can change them in `bot.py`.

## How it works

FunPay has no official API, so the bot signs in the same way a browser does: with your account's `golden_key` cookie. Every few seconds (6 by default) it polls FunPay through the [FunPayAPI](https://pypi.org/project/FunPayAPI/) library. When a new message or order appears, the bot sends it to Telegram via the Bot API.

The bot is **read-only**: it doesn't write to chats or touch your lots and orders.

> ⚠️ `golden_key` gives full access to your FunPay account. Never share it and never commit your `.env` file (it is already in `.gitignore`).

## Quick start (on your own computer)

Requires Python 3.10+.

```bash
git clone https://github.com/ivasantai/funpay-bot.git
cd funpay-bot
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\pip install -r requirements.txt
```

Linux / macOS:

```bash
.venv/bin/pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill it in (see [setup](docs/SETUP.md) for where to get the values). Then run:

```bash
.venv/Scripts/python bot.py
```

On Linux / macOS: `.venv/bin/python bot.py`. If everything is fine, you'll get "✅ Бот запущен" ("Bot started") in Telegram.

## Configuration

All settings are environment variables or lines in the `.env` file:

| Variable | Required | Description |
|---|---|---|
| `FUNPAY_GOLDEN_KEY` | yes | The `golden_key` cookie from funpay.com |
| `TELEGRAM_BOT_TOKEN` | yes | Bot token from [@BotFather](https://t.me/BotFather), the whole thing including the colon |
| `TELEGRAM_CHAT_ID` | yes | Your chat id. For several recipients separate ids with commas: `123456789,987654321` |
| `POLL_DELAY` | no | FunPay polling interval in seconds, `6` by default |
| `PORT` | no | If set, the bot serves an HTTP endpoint `/` that answers `ok` (needed for Render and UptimeRobot) |

## Documentation

- [Setup: golden_key, Telegram bot, chat id](docs/SETUP.md)
- [24/7 hosting: Render + UptimeRobot (free) or your own VPS](docs/DEPLOY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Project files

| File | Purpose |
|---|---|
| `bot.py` | The bot itself |
| `requirements.txt` | Python dependencies |
| `.env.example` | Settings template |
| `render.yaml` | Blueprint for deploying to Render |
| `install.sh` | Installs the bot on a Linux server as a systemd service |

## FunPay compatibility

FunPayAPI 1.1.0 is no longer maintained, and FunPay changes its website from time to time. That's why `bot.py` contains two patches on top of the library:

1. **`golden_seal` cookie**: FunPay now requires it for requests to `runner/`. The bot sends requests through a `requests.Session` that keeps every cookie the site sets.
2. **`chat-msg-text` class**: the message text in the chat HTML used to be in `message-text`. The bot renames the class back so the library's parser can find the text.

If the bot suddenly stops sending notifications, FunPay has most likely changed something again; see [TROUBLESHOOTING](docs/TROUBLESHOOTING.md).

## Disclaimer

This is an unofficial project, not affiliated with FunPay. Use it at your own risk and in accordance with the marketplace rules.
