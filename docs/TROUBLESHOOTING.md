# Troubleshooting

First open the logs: the console when running locally, the **Logs** tab on Render, or `journalctl -u funpay-bot -f` on a VPS. Then find a message similar to yours in the table below.

Some log messages are in Russian (they come from the bot or from the FunPayAPI library); the English meaning is given in parentheses.

| What you see | Cause | What to do |
|---|---|---|
| `KeyError: 'FUNPAY_GOLDEN_KEY'` (or another variable) | The variable is not set | Fill in `.env` or the host's environment variables ([SETUP.md](SETUP.md)) |
| `UnauthorizedError` / 403 at startup | `golden_key` is wrong or expired | Copy `golden_key` from the browser again |
| `Telegram (chat …): 401 Unauthorized` | Wrong bot token | Make sure the whole token is pasted, including the part before `:` |
| `Telegram (chat …): 400 Bad Request: chat not found` | Wrong chat id | Check the id with [@userinfobot](https://t.me/userinfobot) |
| `Telegram (chat …): 403 Forbidden: bot can't initiate conversation` | The recipient hasn't pressed Start | Open the bot and press **Start** |
| `Произошла ошибка при получении событий` ("error while fetching events") on every request | FunPay rejects requests to `runner/` | See "FunPay changed the website" below |
| `Не удалось получить истории чатов [...]` ("failed to fetch chat histories"); orders arrive but messages don't | FunPay changed the chat HTML | See "FunPay changed the website" below |
| Every notification arrives twice | The bot is running in two places | Keep only one copy running |
| The bot falls asleep on Render | Nothing pings it | Check the UptimeRobot monitor ([DEPLOY.md](DEPLOY.md)) |

An occasional `Произошла ошибка при получении событий` is normal: FunPay sometimes responds unreliably. Worry only if it happens on every request.

## FunPay changed the website

The bot relies on an unofficial library that parses the site's HTML and internal requests. When FunPay changes them, the bot breaks. This has happened twice already:

- **400 error from `runner/`** with the response `Необходимая cookie отсутствует или устарела` ("a required cookie is missing or outdated"). FunPay started requiring the `golden_seal` cookie. Fixed by `_patched_method` in `bot.py`, which sends requests through a `requests.Session` with all cookies.
- **`AttributeError: 'NoneType' object has no attribute 'text'`** while parsing messages. The `message-text` class was renamed to `chat-msg-text`. Fixed by `_patched_parse_messages`.

How to track down a new breakage:

1. Run the bot locally and look at the full traceback.
2. If the error is in a server response, print `e.response.text`: FunPay usually states the reason.
3. If the error is in HTML parsing, print the message's `html` and compare its classes with what the parser looks for in `FunPayAPI/account.py`.
4. Add a patch to `bot.py` following the existing ones, and send a pull request 🙂
