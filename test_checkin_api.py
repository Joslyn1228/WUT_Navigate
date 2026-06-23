import requests
import json

BASE_URL = "http://localhost:8000"

print('=== 测试打卡统计API ===\n')

with open('wut_auth.db', 'rb'):
    pass

print('请先登录获取token，然后测试API')
print('或者直接在浏览器中访问: http://localhost:8000/api/checkin/statistics')
print('\n提示：确保服务器正在运行')
