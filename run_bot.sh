#!/bin/sh
# При 409 Conflict бот падает; ждём 60 сек и перезапускаем, пока старый экземпляр не освободит токен.
while true; do
  python bot.py
  code=$?
  echo "Bot exited with code $code. Waiting 60s before restart..."
  sleep 60
done
