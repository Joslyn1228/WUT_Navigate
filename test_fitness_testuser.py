# -*- coding: utf-8 -*-
import sys
import requests
import json

# 设置标准输出编码
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

# 使用 TestUser 用户
test_user = "testuser@example.com"
test_password = "Test@123"

def test_api():
    print("=== 测试运动API ===")
    
    # 测试登录
    print("\n1. 测试登录接口...")
    login_data = {"email": test_user, "password": test_password}
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print("登录状态码:", login_response.status_code)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            if "access_token" in login_result:
                token = login_result["access_token"]
                user_id = login_result["user"]["id"]
                headers = {"Authorization": "Bearer " + token}
                print("登录成功，用户ID:", user_id)
                
                # 测试开始运动
                print("\n2. 测试开始运动...")
                start_response = requests.post(
                    BASE_URL + "/api/fitness/start?workout_type=walking&start_latitude=30.5075&start_longitude=114.3795",
                    headers=headers
                )
                print("开始运动状态码:", start_response.status_code)
                start_result = start_response.json()
                print("响应:", json.dumps(start_result, ensure_ascii=False))
                
                if start_result.get("success") and start_result.get("data", {}).get("workout_id"):
                    workout_id = start_result["data"]["workout_id"]
                    print("运动开始成功，ID:", workout_id)
                    
                    # 测试结束运动
                    print("\n3. 测试结束运动...")
                    end_response = requests.post(
                        BASE_URL + "/api/fitness/end?workout_id=" + str(workout_id),
                        headers=headers
                    )
                    print("结束运动状态码:", end_response.status_code)
                    end_result = end_response.json()
                    print("响应:", json.dumps(end_result, ensure_ascii=False))
                    
                    if end_result.get("success"):
                        print("运动结束成功")
                        
                        # 测试获取统计
                        print("\n4. 测试获取运动统计...")
                        stats_response = requests.get(
                            BASE_URL + "/api/fitness/statistics?period=week",
                            headers=headers
                        )
                        print("统计状态码:", stats_response.status_code)
                        stats_result = stats_response.json()
                        print("响应:", json.dumps(stats_result, ensure_ascii=False))
                        
                        # 测试获取历史
                        print("\n5. 测试获取运动历史...")
                        history_response = requests.get(
                            BASE_URL + "/api/fitness/history",
                            headers=headers
                        )
                        print("历史状态码:", history_response.status_code)
                        history_result = history_response.json()
                        print("响应:", json.dumps(history_result, ensure_ascii=False))
                else:
                    print("运动开始失败")
            else:
                print("登录失败:", login_result.get('message', '未知错误'))
        else:
            print("登录请求失败，状态码:", login_response.status_code)
            
    except Exception as e:
        print("测试异常:", str(e))

if __name__ == "__main__":
    test_api()