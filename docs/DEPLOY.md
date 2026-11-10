# 24/7 hosting

On your home computer the bot runs only while the computer is on. Below are two ways to keep it online all the time.

> Run the bot **in one place only**. If it runs in two places at once (for example, on your computer and on a host), every notification will arrive twice.

## Option 1. Render + UptimeRobot (free)

A free web service on [Render](https://render.com) goes to sleep after 15 minutes without incoming requests. To prevent that, the bot serves a simple HTTP endpoint, and [UptimeRobot](https://uptimerobot.com) pings it every 5 minutes.

### Steps

1. **Fork** this repository (or push the code to your own GitHub repository).
2. On render.com, sign in with GitHub and choose **New → Blueprint**.
3. Select your repository. Render will read [`render.yaml`](../render.yaml) and ask you to enter:
   - `FUNPAY_GOLDEN_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

   See [SETUP.md](SETUP.md) for where to get them.
4. Click **Apply**. The build takes a couple of minutes; after that you'll get "✅ Бот запущен" ("Bot started") in Telegram.
5. Copy the service URL, something like `https://funpay-bot-xxxx.onrender.com`. Opening it in a browser should show `ok`.
6. On uptimerobot.com, create a monitor:
   - **Monitor Type:** HTTP(s)
   - **URL:** the URL from step 5
   - **Monitoring Interval:** 5 minutes

### Updating

Render picks up every `git push` to the `main` branch automatically and rebuilds the bot.

Variables (for example, a new `golden_key` or another chat id) are changed in the service's **Environment** tab. After **Save Changes** the bot restarts by itself.

### Free plan limitations

- 750 hours per month per account. That's enough for one service to run the whole month.
- Render restarts the service now and then. The bot sends "✅ Бот запущен" again when that happens; this is normal.
- Messages that arrive exactly during a restart (a few seconds) may be missed.

## Option 2. Your own Linux server (VPS)

Any VPS with Ubuntu or Debian will do, including the free Oracle Cloud Always Free tier. This is more reliable than Render: the server doesn't sleep or restart on its own.

```bash
git clone https://github.com/ivasantai/funpay-bot.git
cd funpay-bot
cp .env.example .env
nano .env
sudo bash install.sh
```

Fill in the keys in `nano`. The [`install.sh`](../install.sh) script installs Python, creates a virtual environment, installs the dependencies and registers a `funpay-bot` systemd service. The service starts when the server boots and restarts if it crashes.

Useful commands:

```bash
journalctl -u funpay-bot -f
```

```bash
sudo systemctl restart funpay-bot
```

```bash
sudo systemctl stop funpay-bot
```

The first shows live logs, the second restarts the bot (for example, after editing `.env`), the third stops it.

Updating:

```bash
cd funpay-bot && git pull && sudo systemctl restart funpay-bot
```
