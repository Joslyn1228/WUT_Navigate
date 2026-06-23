import sqlite3
import shutil
from datetime import datetime

print('=== 检查备份数据库 ===')
conn = sqlite3.connect('wut_auth.db.backup')
cursor = conn.cursor()

print('\n=== 用户表数据 ===')
cursor.execute('SELECT id, nickname, email, is_active FROM users')
users = cursor.fetchall()
if not users:
    print('备份中也没有用户数据！')
else:
    for user in users:
        print(f'ID: {user[0]}, 昵称: {user[1]}, 邮箱: {user[2]}, 激活: {user[3]}')

print('\n=== 打卡记录数量 ===')
cursor.execute('SELECT COUNT(*) FROM checkins')
print(f'{cursor.fetchone()[0]} 条记录')

print('\n=== 运动记录数量 ===')
cursor.execute('SELECT COUNT(*) FROM workouts')
print(f'{cursor.fetchone()[0]} 条记录')

print('\n=== 社区帖子数量 ===')
cursor.execute('SELECT COUNT(*) FROM posts')
print(f'{cursor.fetchone()[0]} 条记录')

conn.close()

print(f'\n备份文件大小: {shutil.getsize("wut_auth.db.backup") / 1024:.2f} KB')
print(f'当前数据库大小: {shutil.getsize("wut_auth.db") / 1024:.2f} KB')
