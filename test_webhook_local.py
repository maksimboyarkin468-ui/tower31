#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования вебхука локально
Требуется ngrok для создания туннеля
"""

import os
import sys
import subprocess

def check_ngrok():
    """Проверяет установлен ли ngrok"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✅ ngrok установлен")
            return True
    except:
        pass
    
    print("❌ ngrok не найден!")
    print("Установите ngrok: https://ngrok.com/download")
    print("Или используйте другой туннель (Cloudflared, localtunnel и т.д.)")
    return False

def main():
    print("=" * 60)
    print("🧪 Тестирование вебхука локально")
    print("=" * 60)
    
    if not check_ngrok():
        sys.exit(1)
    
    print("\n1. Сначала запустите бота:")
    print("   python bot.py")
    print("\n2. В другом терминале запустите ngrok:")
    print("   ngrok http 5000")
    print("\n3. Скопируйте HTTPS URL из ngrok (например: https://abc123.ngrok.io)")
    print("\n4. Установите вебхук, открыв в браузере:")
    print("   http://localhost:5000/set_webhook?url=https://abc123.ngrok.io/webhook")
    print("\n5. Тестируйте бота в Telegram!")

if __name__ == '__main__':
    main()
