import sqlite3
conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()
cursor.execute('SELECT id, nickname, avatar, bio FROM users')
print('用户数据:')
for r in cursor.fetchall():
    avatar_status = '有' if r[2] else '无'
    bio_preview = r[3][:20] if r[3] else '无'
    print(f'{r[0][:20]}... | {r[1]} | avatar: {avatar_status} | bio: {bio_preview}')
conn.close()
