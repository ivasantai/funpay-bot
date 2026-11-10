# Setup

The bot needs three values. Put them in the `.env` file (when running locally) or in environment variables (on a hosting service).

## 1. `FUNPAY_GOLDEN_KEY`: access to your FunPay account

1. Open [funpay.com](https://funpay.com) in your browser and sign in.
2. Press **F12** and go to the **Application** tab (in Firefox it's called **Storage**).
3. On the left, select **Cookies → https://funpay.com**.
4. Find the `golden_key` row and copy its value: 32 letters and digits.

```
FUNPAY_GOLDEN_KEY=abcd1234...
```

> `golden_key` is effectively the password to your account. If you sign out on FunPay ("sign out on all devices" or a password change), the key stops working. Copy the new one in that case.

## 2. `TELEGRAM_BOT_TOKEN`: your own Telegram bot

1. Message [@BotFather](https://t.me/BotFather) and send `/newbot`.
2. Choose a name and a username for the bot (the username must end with `bot`).
3. BotFather will send a token like `1234567890:AAH5kXyZ-abcd...`. Paste it **in full**, including the digits before the colon.

```
TELEGRAM_BOT_TOKEN=1234567890:AAH5kXyZ-abcdEFGhijkLMNop_qrstUVwx
```

## 3. `TELEGRAM_CHAT_ID`: who receives notifications

1. Message [@userinfobot](https://t.me/userinfobot); it will reply with your numeric `Id`.
2. **Make sure** to open your new bot and press **Start**. Otherwise Telegram won't let the bot message you first, and the log will show `403 Forbidden: bot can't initiate conversation`.

```
TELEGRAM_CHAT_ID=123456789
```

### Several recipients

List the ids separated by commas, without spaces. Every recipient must also press **Start** in the bot.

```
TELEGRAM_CHAT_ID=123456789,987654321
```

You can also use a group id. It starts with `-100…`, and the bot must be added to that group.

## 4. `POLL_DELAY` (optional)

How often to poll FunPay, in seconds. `6` by default. Don't make it much lower: FunPay may not like frequent requests.

## Checking that it works

Run `python bot.py`. The console will show a line like:

```
INFO Вошёл на FunPay как <your nickname> (id ...)
```

("Signed in to FunPay as …"). And Telegram will receive "✅ Бот запущен, аккаунт FunPay: …" ("Bot started, FunPay account: …"). If not, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
