import sqlite3
import sys

conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()

print('=== 数据库表 ===')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
for table in tables:
    print(table[0])

print('\n=== 用户表数据 ===')
cursor.execute('SELECT id, nickname, email, is_active FROM users')
users = cursor.fetchall()
if not users:
    print('数据库中没有用户数据！')
else:
    for user in users:
        print(f'ID: {user[0]}, 昵称: {user[1]}, 邮箱: {user[2]}, 激活: {user[3]}')

conn.close()
