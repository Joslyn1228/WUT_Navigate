"""
武汉理工大学智能导游 - 数据持久化测试指南
"""

print("""
╔═══════════════════════════════════════════════════════════════╗
║          数据持久化测试指南                                   ║
╚═══════════════════════════════════════════════════════════════╝

【问题背景】
之前打卡记录、成就等数据使用内存存储，重启服务器后数据丢失。
现在已将所有数据迁移到 SQLite 数据库持久化存储。

【当前数据库状态】
""")

import sqlite3
conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"已创建的表: {[t[0] for t in tables if t[0] != 'sqlite_sequence']}\n")

print("【测试步骤】\n")

print("步骤 1: 查看当前用户数据")
print("-" * 60)
cursor.execute('SELECT id, nickname, email, avatar, bio FROM users LIMIT 1')
user = cursor.fetchone()
if user:
    print(f"用户ID: {user[0][:30]}...")
    print(f"昵称: {user[1]}")
    print(f"邮箱: {user[2]}")
    print(f"头像: {'已设置' if user[3] else '未设置'}")
    print(f"签名: {user[4] if user[4] else '未设置'}")
else:
    print("没有用户数据，请先注册账号")

print("\n步骤 2: 查看打卡记录")
print("-" * 60)
cursor.execute('SELECT COUNT(*) FROM checkins')
count = cursor.fetchone()[0]
print(f"打卡记录数: {count} 条")

if count > 0:
    cursor.execute('SELECT user_id, place_name, checkin_time FROM checkins LIMIT 3')
    for record in cursor.fetchall():
        print(f"  - {record[2]} | {record[1]}")
else:
    print("暂无打卡记录，请在网页端进行打卡测试")

print("\n步骤 3: 查看成就数据")
print("-" * 60)
cursor.execute('SELECT COUNT(*) FROM achievements')
ach_count = cursor.fetchone()[0]
print(f"已解锁成就数: {ach_count} 个")

if ach_count > 0:
    cursor.execute('SELECT achievement_id, unlocked_at FROM achievements LIMIT 5')
    for ach in cursor.fetchall():
        print(f"  - {ach[0]} | {ach[1]}")
else:
    print("暂无已解锁成就")

print("\n步骤 4: 查看活动计数")
print("-" * 60)
cursor.execute('SELECT COUNT(*) FROM activity_counts')
act_count = cursor.fetchone()[0]
print(f"活动计数记录数: {act_count} 条")

if act_count > 0:
    cursor.execute('SELECT activity_id, count FROM activity_counts LIMIT 5')
    for act in cursor.fetchall():
        print(f"  - {act[0]}: {act[1]} 次")

conn.close()

print("""
\n╔═══════════════════════════════════════════════════════════════╗
║                     测试验证方法                              ║
╚═══════════════════════════════════════════════════════════════╝

【测试场景1: 验证头像和签名的持久化】
1. 在网页端上传头像和设置签名
2. 检查数据库: python test_db.py
3. 重启服务器
4. 再次检查数据库和网页，确认数据仍然存在

【测试场景2: 验证打卡记录的持久化】
1. 在网页端进行打卡
2. 检查数据库中的 checkins 表
3. 重启服务器
4. 查看打卡历史，确认记录保留

【测试场景3: 验证成就的持久化】
1. 完成足够的打卡来解锁成就
2. 检查数据库中的 achievements 表
3. 重启服务器
4. 查看成就列表，确认成就保留

【测试场景4: 验证活动计数的持久化】
1. 在特定时间段（如 07:30-08:30）进行打卡
2. 检查数据库中的 activity_counts 表
3. 重启服务器
4. 再次在该时间段打卡，观察计数是否正确累加

【数据库文件位置】
d:\\桌面\\武理导航\\wut_auth.db

【查看数据库的命令】
cd "d:\\桌面\\武理导航"
.venv\\Scripts\\python.exe test_db.py

【初始化数据库的命令】
cd "d:\\桌面\\武理导航"
.venv\\Scripts\\python.exe init_database.py
""")

print("\n[SUCCESS] 测试指南生成完成！")
