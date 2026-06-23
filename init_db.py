from app.auth_service import Base, engine
from app.auth_service import DBUser, DBCheckin, DBAchievement, DBActivityCount

print("正在创建所有数据库表...")
Base.metadata.create_all(bind=engine)
print("✅ 数据库表创建完成！")

print("\n=== 验证数据库表 ===")
import sqlite3
conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"数据库中的表: {[t[0] for t in tables]}")
conn.close()
