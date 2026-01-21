import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_name='bot.db'):
        self.db_name = db_name
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
        cursor.execute('SELECT value FROM settings WHERE key = ?', ('referral_link',))
        if not cursor.fetchone():
            from config import DEFAULT_REFERRAL_LINK
            cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('referral_link', DEFAULT_REFERRAL_LINK))
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO users (user_id, username, last_active) VALUES (?, ?, CURRENT_TIMESTAMP)', (user_id, username))
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
