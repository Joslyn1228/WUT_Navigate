import sqlite3
import jwt

# 测试数据库连接
conn = sqlite3.connect('wut_auth.db')
cursor = conn.cursor()

print('=== 数据库用户数据 ===')
cursor.execute('SELECT id, nickname, email FROM users')
users = cursor.fetchall()
for user in users:
    print(f'ID: {user[0]}, 昵称: {user[1]}, 邮箱: {user[2]}')

conn.close()

# 测试JWT Token解析
SECRET_KEY = "wuhan_university_of_technology_secret_key_2024"
ALGORITHM = "HS256"

print('\n=== 测试JWT解析 ===')
sample_token = input('请输入您的Bearer Token（可以从浏览器开发者工具获取）: ').strip()

if sample_token.startswith('Bearer '):
    sample_token = sample_token[7:]

try:
    payload = jwt.decode(sample_token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f'Token解析成功！')
    print(f'用户ID (sub): {payload.get("sub")}')
    print(f'用户昵称: {payload.get("nickname")}')
    print(f'用户邮箱: {payload.get("email")}')
    
    user_id_from_token = payload.get("sub")
    
    conn = sqlite3.connect('wut_auth.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nickname FROM users WHERE id = ?', (user_id_from_token,))
    user = cursor.fetchone()
    
    if user:
        print(f'\n✅ 用户存在！ID: {user[0]}, 昵称: {user[1]}')
    else:
        print(f'\n❌ 用户不存在！Token中的用户ID: {user_id_from_token}')
        print('可能的原因：Token已过期或用户数据在token签发后被删除')
    
    conn.close()
    
except jwt.ExpiredSignatureError:
    print('❌ Token已过期')
except jwt.InvalidTokenError as e:
    print(f'❌ Token无效: {str(e)}')
except Exception as e:
    print(f'❌ 解析失败: {str(e)}')