# -*- coding: utf-8 -*-
import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

# 使用Token登录
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGJmZTY1Zi1lZjYyLTRjMWQtOTdmMS1kODZjYzJmNDg3ODUiLCJuaWNrbmFtZSI6Ikpvc2x5biIsImVtYWlsIjoiMTAyNTE4MTI3NUBxcS5jb20iLCJleHAiOjE3ODM1MTI0NjF9.J2AyQtrZMmaQtgsGSNmHZninkal9O4j3CSVaFLV0mRw"}

print("=== 测试运动历史API ===")

try:
    # 获取运动历史
    print("1. 获取运动历史...")
    history_response = requests.get(
        BASE_URL + "/api/fitness/history",
        headers=headers
    )
    print("状态码:", history_response.status_code)
    history_result = history_response.json()
    print("完整响应:", json.dumps(history_result, ensure_ascii=False, indent=2))
    
except Exception as e:
    print("测试异常:", str(e))