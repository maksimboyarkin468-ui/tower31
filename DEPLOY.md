# РРЅСЃС‚СЂСѓРєС†РёСЏ РїРѕ РґРµРїР»РѕСЋ РЅР° СЃРµСЂРІРµСЂ

## Р’Р°СЂРёР°РЅС‚ 1: Р”РµРїР»РѕР№ РЅР° VPS/СЃРµСЂРІРµСЂ (Linux)

### РЁР°РіРё:

1. **РџРѕРґРєР»СЋС‡РёС‚РµСЃСЊ Рє СЃРµСЂРІРµСЂСѓ РїРѕ SSH:**
   ```bash
   ssh user@your-server-ip
   ```

2. **РЈСЃС‚Р°РЅРѕРІРёС‚Рµ Python Рё pip (РµСЃР»Рё РЅРµ СѓСЃС‚Р°РЅРѕРІР»РµРЅС‹):**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv -y
   ```

3. **РЎРѕР·РґР°Р№С‚Рµ РґРёСЂРµРєС‚РѕСЂРёСЋ РґР»СЏ Р±РѕС‚Р°:**
   ```bash
   mkdir -p ~/tower_bot
   cd ~/tower_bot
   ```

4. **Р—Р°РіСЂСѓР·РёС‚Рµ С„Р°Р№Р»С‹ РЅР° СЃРµСЂРІРµСЂ:**
   - РСЃРїРѕР»СЊР·СѓР№С‚Рµ SCP:
     ```bash
     scp -r C:\Users\boiar\tower_bot\* user@your-server-ip:~/tower_bot/
     ```
   - РР»Рё РёСЃРїРѕР»СЊР·СѓР№С‚Рµ FTP/SFTP РєР»РёРµРЅС‚ (FileZilla, WinSCP)
   - РР»Рё СЃРєР»РѕРЅРёСЂСѓР№С‚Рµ С‡РµСЂРµР· Git

5. **РЎРѕР·РґР°Р№С‚Рµ РІРёСЂС‚СѓР°Р»СЊРЅРѕРµ РѕРєСЂСѓР¶РµРЅРёРµ:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

6. **РЈСЃС‚Р°РЅРѕРІРёС‚Рµ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё:**
   ```bash
   pip install -r requirements.txt
   ```

7. **РќР°СЃС‚СЂРѕР№С‚Рµ РІРµР±С…СѓРє (РІР°Р¶РЅРѕ!):**
   - РЈР±РµРґРёС‚РµСЃСЊ, С‡С‚Рѕ РІР°С€ СЃРµСЂРІРµСЂ РґРѕСЃС‚СѓРїРµРЅ РёР· РёРЅС‚РµСЂРЅРµС‚Р°
   - РЈСЃС‚Р°РЅРѕРІРёС‚Рµ РІРµР±С…СѓРє, РѕС‚РєСЂС‹РІ РІ Р±СЂР°СѓР·РµСЂРµ РёР»Рё С‡РµСЂРµР· curl:
     ```bash
     curl "http://localhost:5000/set_webhook?url=https://your-domain.com/webhook"
     ```
   - РР»Рё РµСЃР»Рё Сѓ РІР°СЃ РµСЃС‚СЊ РґРѕРјРµРЅ:
     ```bash
     curl "http://localhost:5000/set_webhook?url=https://yourdomain.com/webhook"
     ```

8. **Р—Р°РїСѓСЃС‚РёС‚Рµ Р±РѕС‚Р° С‡РµСЂРµР· screen РёР»Рё tmux:**
   ```bash
   screen -S tower_bot
   python bot.py
   # РќР°Р¶РјРёС‚Рµ Ctrl+A Р·Р°С‚РµРј D РґР»СЏ РѕС‚РєР»СЋС‡РµРЅРёСЏ
   ```

   РР»Рё РёСЃРїРѕР»СЊР·СѓР№С‚Рµ systemd (СЃРј. РЅРёР¶Рµ)

## Р’Р°СЂРёР°РЅС‚ 2: РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ systemd (Р°РІС‚РѕР·Р°РїСѓСЃРє)

1. **РЎРѕР·РґР°Р№С‚Рµ С„Р°Р№Р» СЃРµСЂРІРёСЃР°:**
   ```bash
   sudo nano /etc/systemd/system/tower-bot.service
   ```

2. **Р’СЃС‚Р°РІСЊС‚Рµ СЃР»РµРґСѓСЋС‰РµРµ СЃРѕРґРµСЂР¶РёРјРѕРµ:**
   ```
   [Unit]
   Description=Tower Cheat Bot
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/home/your-username/tower_bot
   Environment="PATH=/home/your-username/tower_bot/venv/bin"
   ExecStart=/home/your-username/tower_bot/venv/bin/python bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Р’РєР»СЋС‡РёС‚Рµ Рё Р·Р°РїСѓСЃС‚РёС‚Рµ СЃРµСЂРІРёСЃ:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable tower-bot
   sudo systemctl start tower-bot
   ```

4. **РџСЂРѕРІРµСЂСЊС‚Рµ СЃС‚Р°С‚СѓСЃ:**
   ```bash
   sudo systemctl status tower-bot
   ```

## Р’Р°СЂРёР°РЅС‚ 3: РСЃРїРѕР»СЊР·РѕРІР°РЅРёРµ nginx (СЂРµРєРѕРјРµРЅРґСѓРµС‚СЃСЏ)

1. **РЈСЃС‚Р°РЅРѕРІРёС‚Рµ nginx:**
   ```bash
   sudo apt install nginx -y
   ```

2. **РќР°СЃС‚СЂРѕР№С‚Рµ nginx:**
   ```bash
   sudo nano /etc/nginx/sites-available/tower-bot
   ```

3. **Р”РѕР±Р°РІСЊС‚Рµ РєРѕРЅС„РёРіСѓСЂР°С†РёСЋ:**
   ```
   server {
       listen 80;
       server_name your-domain.com;

       location /webhook {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Р’РєР»СЋС‡РёС‚Рµ РєРѕРЅС„РёРіСѓСЂР°С†РёСЋ:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/tower-bot /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Р’Р°Р¶РЅС‹Рµ РјРѕРјРµРЅС‚С‹:

1. **Р‘РµР·РѕРїР°СЃРЅРѕСЃС‚СЊ:**
   - РќРµ РїСѓР±Р»РёРєСѓР№С‚Рµ `config.py` СЃ С‚РѕРєРµРЅРѕРј РІ РїСѓР±Р»РёС‡РЅС‹С… СЂРµРїРѕР·РёС‚РѕСЂРёСЏС…
   - РСЃРїРѕР»СЊР·СѓР№С‚Рµ РїРµСЂРµРјРµРЅРЅС‹Рµ РѕРєСЂСѓР¶РµРЅРёСЏ РґР»СЏ С‡СѓРІСЃС‚РІРёС‚РµР»СЊРЅС‹С… РґР°РЅРЅС‹С…
   - РќР°СЃС‚СЂРѕР№С‚Рµ firewall (ufw)

2. **РџСЂРѕРІРµСЂРєР° СЂР°Р±РѕС‚С‹:**
   - РџСЂРѕРІРµСЂСЊС‚Рµ Р»РѕРіРё: `journalctl -u tower-bot -f`
   - РџСЂРѕРІРµСЂСЊС‚Рµ РґРѕСЃС‚СѓРїРЅРѕСЃС‚СЊ: `curl http://localhost:5000/health`

3. **РћР±РЅРѕРІР»РµРЅРёРµ РІРµР±С…СѓРєР°:**
   - РџСЂРё РёР·РјРµРЅРµРЅРёРё РґРѕРјРµРЅР° РёР»Рё РїРѕСЂС‚Р° РѕР±РЅРѕРІРёС‚Рµ РІРµР±С…СѓРє
   - РСЃРїРѕР»СЊР·СѓР№С‚Рµ РєРѕРјР°РЅРґСѓ: `/set_webhook?url=NEW_URL`

## РџСЂРѕРІРµСЂРєР° РїРѕСЃР»Рµ РґРµРїР»РѕСЏ:

1. РџСЂРѕРІРµСЂСЊС‚Рµ, С‡С‚Рѕ Р±РѕС‚ Р·Р°РїСѓС‰РµРЅ
2. РћС‚РїСЂР°РІСЊС‚Рµ `/start` Р±РѕС‚Сѓ РІ Telegram
3. РџСЂРѕРІРµСЂСЊС‚Рµ Р»РѕРіРё РЅР° РЅР°Р»РёС‡РёРµ РѕС€РёР±РѕРє
