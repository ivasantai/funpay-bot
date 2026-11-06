#!/usr/bin/env bash
# Установка бота на Linux-сервер (Ubuntu/Debian) как systemd-сервиса.
# Запуск из папки бота:  sudo bash install.sh
set -euo pipefail

BOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOT_USER="${SUDO_USER:-$(whoami)}"

if [ ! -f "$BOT_DIR/.env" ]; then
  echo "Нет файла .env в $BOT_DIR — скопируй его сюда и запусти снова." >&2
  exit 1
fi

apt-get update -y
apt-get install -y python3 python3-venv

python3 -m venv "$BOT_DIR/.venv"
"$BOT_DIR/.venv/bin/pip" install --upgrade pip
"$BOT_DIR/.venv/bin/pip" install -r "$BOT_DIR/requirements.txt"
chown -R "$BOT_USER":"$BOT_USER" "$BOT_DIR"

cat > /etc/systemd/system/funpay-bot.service <<EOF
[Unit]
Description=FunPay -> Telegram notifier
After=network-online.target
Wants=network-online.target

[Service]
User=$BOT_USER
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/.venv/bin/python bot.py
Environment=PYTHONUNBUFFERED=1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now funpay-bot
sleep 3
systemctl --no-pager status funpay-bot || true
echo
echo "Готово. Логи: journalctl -u funpay-bot -f"
