import sqlite3
conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()
cursor.execute('SELECT id, nickname, avatar FROM users')
for r in cursor.fetchall():
    print(f'用户: {r[1]}')
    if r[2]:
        print(f'头像URL开头: {r[2][:100]}')
conn.close()
