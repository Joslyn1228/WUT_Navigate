import sqlite3

conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()

print("正在检查并创建缺失的表...")

tables_to_create = [
    """CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR,
        place_name VARCHAR,
        checkin_time DATETIME,
        latitude FLOAT DEFAULT 0.0,
        longitude FLOAT DEFAULT 0.0,
        activity_id VARCHAR DEFAULT ''
    )""",
    """CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR,
        achievement_id VARCHAR,
        unlocked_at DATETIME
    )""",
    """CREATE TABLE IF NOT EXISTS activity_counts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR,
        activity_id VARCHAR,
        count INTEGER DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR,
        workout_type VARCHAR,
        start_time DATETIME,
        end_time DATETIME,
        total_distance FLOAT DEFAULT 0.0,
        total_duration INTEGER DEFAULT 0,
        calories_burned FLOAT DEFAULT 0.0,
        avg_speed FLOAT DEFAULT 0.0,
        created_at DATETIME
    )""",
    """CREATE TABLE IF NOT EXISTS workout_routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER,
        latitude FLOAT,
        longitude FLOAT,
        recorded_at DATETIME
    )"""
]

for i, sql in enumerate(tables_to_create):
    table_name = ['checkins', 'achievements', 'activity_counts', 'workouts', 'workout_routes'][i]
    try:
        cursor.execute(sql)
        print(f"[OK] {table_name} 表创建成功")
    except Exception as e:
        print(f"[FAIL] {table_name} 表创建失败: {e}")

conn.commit()

print("\n=== 验证数据库表 ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"数据库中的表: {[t[0] for t in tables]}")

print("\n=== 各表记录数 ===")
for table in tables:
    table_name = table[0]
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f'{table_name}: {count} 条记录')

conn.close()
print("\n[SUCCESS] 数据库初始化完成！")
