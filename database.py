import sqlite3
import os
from datetime import datetime

# Путь к БД: задай DATABASE_PATH в Railway (например /data/bot.db) и смонтируй Volume на /data — данные сохранятся при редиплое
DB_PATH = os.getenv('DATABASE_PATH', 'bot.db')


class Database:
    def __init__(self, db_name=None):
        self.db_name = db_name or DB_PATH
        _dir = os.path.dirname(self.db_name)
        if _dir:
            os.makedirs(_dir, exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            has_access INTEGER DEFAULT 0,
            access_level INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS postbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            onewin_user_id TEXT NOT NULL,
            raw_text TEXT,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed INTEGER DEFAULT 0
        )''')
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN awaiting_1win_id_since REAL')
        except sqlite3.OperationalError:
            pass
        cursor.execute('SELECT value FROM settings WHERE key = ?', ('referral_link',))
        if not cursor.fetchone():
            from config import DEFAULT_REFERRAL_LINK
            cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('referral_link', DEFAULT_REFERRAL_LINK))
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            cursor.execute('UPDATE users SET username = ?, last_active = CURRENT_TIMESTAMP WHERE user_id = ?', (username, user_id))
        else:
            cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        conn.close()
    
    def user_has_access(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT has_access FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == 1
    
    def give_access(self, user_id, access_level=1):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO users (user_id, has_access, access_level) VALUES (?, 1, ?)', (user_id, access_level))
        else:
            cursor.execute('UPDATE users SET has_access = 1, access_level = ? WHERE user_id = ?', (access_level, user_id))
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, has_access FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        return [(row[0], row[1], row[2]) for row in users]
    
    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM users WHERE has_access = 1')
        users_with_access = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE(\"now\")')
        new_today = cursor.fetchone()[0]
        conn.close()
        return {'total_users': total_users, 'users_with_access': users_with_access, 'new_today': new_today}
    
    def get_referral_link(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', ('referral_link',))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            from config import DEFAULT_REFERRAL_LINK
            return DEFAULT_REFERRAL_LINK
    
    def update_referral_link(self, new_link):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('referral_link', new_link))
        conn.commit()
        conn.close()

    # Постбэки 1win (из группы обсуждения канала)
    def add_postback(self, onewin_user_id, raw_text=None, amount=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO postbacks (onewin_user_id, raw_text, amount) VALUES (?, ?, ?)',
            (str(onewin_user_id).strip(), raw_text, amount)
        )
        conn.commit()
        conn.close()

    def get_unprocessed_postback_for_1win_id(self, onewin_user_id):
        """Возвращает последний необработанный постбэк с таким ID 1win или None."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, onewin_user_id, raw_text, amount, created_at FROM postbacks '
            'WHERE onewin_user_id = ? AND processed = 0 ORDER BY created_at DESC LIMIT 1',
            (str(onewin_user_id).strip(),)
        )
        row = cursor.fetchone()
        conn.close()
        return (row[0], row[1], row[2], row[3], row[4]) if row else None

    def mark_postback_processed(self, postback_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE postbacks SET processed = 1 WHERE id = ?', (postback_id,))
        conn.commit()
        conn.close()

    # Ожидание ввода ID 1win после нажатия «Готово»
    def set_awaiting_1win_id(self, user_id):
        import time
        conn = self.get_connection()
        cursor = conn.cursor()
        ts = time.time()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone():
            cursor.execute('UPDATE users SET awaiting_1win_id_since = ? WHERE user_id = ?', (ts, user_id))
        else:
            cursor.execute('INSERT INTO users (user_id, awaiting_1win_id_since) VALUES (?, ?)', (user_id, ts))
        conn.commit()
        conn.close()

    def get_awaiting_1win_id_since(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT awaiting_1win_id_since FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row and row[0] else None

    def clear_awaiting_1win_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET awaiting_1win_id_since = NULL WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
