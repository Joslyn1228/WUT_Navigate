import requests
import json

BASE_URL = "http://localhost:8000"

# 先登录获取token
login_data = {
    "email": "1025181275@qq.com",
    "password": "Wut@2024"
}

print("=== 测试运动API ===")

try:
    # 登录
    print("\n1. 登录...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    login_result = login_response.json()
    print(f"登录响应: {json.dumps(login_result, indent=2, ensure_ascii=False)}")
    
    if "access_token" in login_result:
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 开始运动
        print("\n2. 开始运动...")
        start_response = requests.post(
            f"{BASE_URL}/api/fitness/start?workout_type=walking&start_latitude=30.5075&start_longitude=114.3795",
            headers=headers
        )
        start_result = start_response.json()
        print(f"开始运动响应: {json.dumps(start_result, indent=2, ensure_ascii=False)}")
        
        if start_result.get("success") and start_result.get("data", {}).get("workout_id"):
            workout_id = start_result["data"]["workout_id"]
            print(f"✅ 运动开始成功，ID: {workout_id}")
            
            # 结束运动
            print("\n3. 结束运动...")
            end_response = requests.post(
                f"{BASE_URL}/api/fitness/end?workout_id={workout_id}",
                headers=headers
            )
            end_result = end_response.json()
            print(f"结束运动响应: {json.dumps(end_result, indent=2, ensure_ascii=False)}")
            
            # 获取运动统计
            print("\n4. 获取运动统计...")
            stats_response = requests.get(
                f"{BASE_URL}/api/fitness/statistics?period=week",
                headers=headers
            )
            stats_result = stats_response.json()
            print(f"运动统计响应: {json.dumps(stats_result, indent=2, ensure_ascii=False)}")
            
            # 获取运动历史
            print("\n5. 获取运动历史...")
            history_response = requests.get(
                f"{BASE_URL}/api/fitness/history",
                headers=headers
            )
            history_result = history_response.json()
            print(f"运动历史响应: {json.dumps(history_result, indent=2, ensure_ascii=False)}")
        else:
            print("❌ 运动开始失败")
            
    else:
        print("❌ 登录失败")
        
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")