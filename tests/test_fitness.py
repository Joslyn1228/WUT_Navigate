# -*- coding: utf-8 -*-
"""
运动模块测试
包含运动开始、结束、统计、历史等功能的测试用例
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import requests
import json

BASE_URL = "http://localhost:8000"

class TestFitnessAPI:
    """运动API测试类"""
    
    def test_start_workout(self):
        """测试开始运动"""
        # 使用已登录用户的Token
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGJmZTY1Zi1lZjYyLTRjMWQtOTdmMS1kODZjYzJmNDg3ODUiLCJuaWNrbmFtZSI6Ikpvc2x5biIsImVtYWlsIjoiMTAyNTE4MTI3NUBxcS5jb20iLCJleHAiOjE3ODM1MTI0NjF9.J2AyQtrZMmaQtgsGSNmHZninkal9O4j3CSVaFLV0mRw"}
        
        response = requests.post(
            f"{BASE_URL}/api/fitness/start?workout_type=walking&start_latitude=30.5075&start_longitude=114.3795",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "workout_id" in data["data"]
        print(f"✓ 开始运动成功，运动ID: {data['data']['workout_id']}")
        
        return data["data"]["workout_id"]
    
    def test_end_workout(self):
        """测试结束运动"""
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGJmZTY1Zi1lZjYyLTRjMWQtOTdmMS1kODZjYzJmNDg3ODUiLCJuaWNrbmFtZSI6Ikpvc2x5biIsImVtYWlsIjoiMTAyNTE4MTI3NUBxcS5jb20iLCJleHAiOjE3ODM1MTI0NjF9.J2AyQtrZMmaQtgsGSNmHZninkal9O4j3CSVaFLV0mRw"}
        
        # 先开始运动
        start_response = requests.post(
            f"{BASE_URL}/api/fitness/start?workout_type=walking&start_latitude=30.5075&start_longitude=114.3795",
            headers=headers
        )
        workout_id = start_response.json()["data"]["workout_id"]
        
        # 结束运动
        response = requests.post(
            f"{BASE_URL}/api/fitness/end?workout_id={workout_id}&distance=100.5&duration=60&calories=5.0",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        print(f"✓ 结束运动成功，运动ID: {workout_id}")
    
    def test_get_statistics(self):
        """测试获取运动统计"""
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGJmZTY1Zi1lZjYyLTRjMWQtOTdmMS1kODZjYzJmNDg3ODUiLCJuaWNrbmFtZSI6Ikpvc2x5biIsImVtYWlsIjoiMTAyNTE4MTI3NUBxcS5jb20iLCJleHAiOjE3ODM1MTI0NjF9.J2AyQtrZMmaQtgsGSNmHZninkal9O4j3CSVaFLV0mRw"}
        
        # 测试周统计
        response = requests.get(f"{BASE_URL}/api/fitness/statistics?period=week", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "distance" in data["data"]
        assert "calories" in data["data"]
        assert "count" in data["data"]
        print(f"✓ 获取周统计成功: 距离={data['data']['distance']}m, 卡路里={data['data']['calories']}, 次数={data['data']['count']}")
        
        # 测试累计统计
        response = requests.get(f"{BASE_URL}/api/fitness/statistics?period=all", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_distance" in data["data"]
        print(f"✓ 获取累计统计成功: 累计距离={data['data']['total_distance']}m")
    
    def test_get_history(self):
        """测试获取运动历史"""
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NGJmZTY1Zi1lZjYyLTRjMWQtOTdmMS1kODZjYzJmNDg3ODUiLCJuaWNrbmFtZSI6Ikpvc2x5biIsImVtYWlsIjoiMTAyNTE4MTI3NUBxcS5jb20iLCJleHAiOjE3ODM1MTI0NjF9.J2AyQtrZMmaQtgsGSNmHZninkal9O4j3CSVaFLV0mRw"}
        
        response = requests.get(f"{BASE_URL}/api/fitness/history", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        print(f"✓ 获取运动历史成功，共 {len(data['data'])} 条记录")

if __name__ == "__main__":
    test = TestFitnessAPI()
    print("=== 开始测试运动模块 ===")
    test.test_get_statistics()
    test.test_get_history()
    print("=== 运动模块测试完成 ===")