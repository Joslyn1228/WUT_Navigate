import sqlite3

conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()

print('=== 数据库中的表 ===')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f'- {table[0]}')

print('\n=== 各表记录数 ===')
for table in tables:
    table_name = table[0]
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f'{table_name}: {count} 条记录')

print('\n=== 用户表样例 ===')
cursor.execute('SELECT id, nickname, email, avatar, bio FROM users LIMIT 3')
users = cursor.fetchall()
for user in users:
    avatar_preview = user[3][:30] if user[3] else "无"
    bio_preview = user[4][:20] if user[4] else "无"
    print(f'ID: {user[0][:20]}... | 昵称: {user[1]} | 邮箱: {user[2]}')
    print(f'  头像: {avatar_preview}...')
    print(f'  签名: {bio_preview}...')

print('\n=== 打卡记录样例 ===')
cursor.execute('SELECT id, user_id, place_name, checkin_time FROM checkins LIMIT 5')
checkins = cursor.fetchall()
for checkin in checkins:
    print(f'ID: {checkin[0]} | 用户: {checkin[1][:20]}... | 地点: {checkin[2]} | 时间: {checkin[3]}')

print('\n=== 成就表样例 ===')
cursor.execute('SELECT id, user_id, achievement_id, unlocked_at FROM achievements LIMIT 5')
achievements = cursor.fetchall()
for ach in achievements:
    print(f'ID: {ach[0]} | 用户: {ach[1][:20]}... | 成就: {ach[2]} | 解锁时间: {ach[3]}')

print('\n=== 活动计数表样例 ===')
cursor.execute('SELECT id, user_id, activity_id, count FROM activity_counts LIMIT 5')
counts = cursor.fetchall()
for count in counts:
    print(f'ID: {count[0]} | 用户: {count[1][:20]}... | 活动: {count[2]} | 计数: {count[3]}')

conn.close()
