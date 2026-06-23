import sqlite3
from datetime import datetime

conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()

print('=== 数据库打卡记录检查 ===\n')

print('1. 用户表:')
cursor.execute('SELECT id, nickname FROM users')
users = cursor.fetchall()
for user in users:
    print(f'   用户ID: {user[0][:30]}...')
    print(f'   昵称: {user[1]}')

print('\n2. 打卡记录表:')
cursor.execute('SELECT id, user_id, place_name, checkin_time FROM checkins ORDER BY checkin_time DESC')
checkins = cursor.fetchall()
print(f'   总记录数: {len(checkins)}')
for checkin in checkins[:10]:
    print(f'   - ID: {checkin[0]} | 用户: {checkin[1][:20]}... | 地点: {checkin[2]} | 时间: {checkin[3]}')

print('\n3. 成就记录表:')
cursor.execute('SELECT id, user_id, achievement_id, unlocked_at FROM achievements')
achievements = cursor.fetchall()
print(f'   总记录数: {len(achievements)}')
for ach in achievements[:10]:
    print(f'   - ID: {ach[0]} | 用户: {ach[1][:20]}... | 成就: {ach[2]} | 解锁时间: {ach[3]}')

print('\n4. 活动计数表:')
cursor.execute('SELECT id, user_id, activity_id, count FROM activity_counts')
counts = cursor.fetchall()
print(f'   总记录数: {len(counts)}')
for count in counts[:10]:
    print(f'   - ID: {count[0]} | 用户: {count[1][:20]}... | 活动: {count[2]} | 计数: {count[3]}')

conn.close()
print('\n=== 检查完成 ===')
