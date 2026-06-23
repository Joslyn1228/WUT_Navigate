import sqlite3

conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()

print("=== workouts 表结构 ===")
cursor.execute("PRAGMA table_info(workouts)")
columns = cursor.fetchall()
for col in columns:
    print(col)

print("\n=== workouts 表中的数据 ===")
cursor.execute("SELECT * FROM workouts LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
