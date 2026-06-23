# -*- coding: utf-8 -*-
"""
数据库索引优化脚本
为运动相关表添加必要的索引，提高查询性能
"""
import sqlite3

def add_indexes():
    """为数据库表添加索引"""
    conn = sqlite3.connect('wut_auth.db')
    cursor = conn.cursor()
    
    print("=== 开始添加数据库索引 ===")
    
    try:
        # 为 workouts 表添加索引
        print("1. 为 workouts 表添加索引...")
        
        # user_id 索引 - 用于按用户查询运动记录
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_user_id ON workouts(user_id)')
        
        # start_time 索引 - 用于按时间范围查询
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_start_time ON workouts(start_time)')
        
        # end_time 索引 - 用于查询已结束的运动
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_end_time ON workouts(end_time)')
        
        # user_id + start_time 复合索引 - 用于查询用户的运动历史
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_user_start ON workouts(user_id, start_time)')
        
        # 为 checkins 表添加索引
        print("2. 为 checkins 表添加索引...")
        
        # user_id 索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_checkins_user_id ON checkins(user_id)')
        
        # checkin_time 索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_checkins_time ON checkins(checkin_time)')
        
        # 为 users 表添加索引
        print("3. 为 users 表添加索引...")
        
        # email 索引 - 用于登录查询
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        
        conn.commit()
        print("✓ 所有索引添加成功！")
        
    except Exception as e:
        print(f"✗ 添加索引失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def check_indexes():
    """检查已存在的索引"""
    conn = sqlite3.connect('wut_auth.db')
    cursor = conn.cursor()
    
    print("\n=== 检查现有索引 ===")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
    indexes = cursor.fetchall()
    
    if indexes:
        for idx in indexes:
            print(f"  ✓ {idx[0]}")
    else:
        print("  未找到任何索引")
    
    conn.close()

if __name__ == "__main__":
    add_indexes()
    check_indexes()