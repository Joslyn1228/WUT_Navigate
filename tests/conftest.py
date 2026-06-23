# -*- coding: utf-8 -*-
"""
测试配置文件
包含测试所需的fixtures和工具函数
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.auth_service import AuthService
from app.fitness_service import FitnessService

@pytest.fixture
def auth_service():
    """创建认证服务实例"""
    return AuthService()

@pytest.fixture
def fitness_service():
    """创建运动服务实例"""
    return FitnessService()

@pytest.fixture
def test_user_email():
    """测试用户邮箱"""
    return "1025181275@qq.com"

@pytest.fixture
def test_user_password():
    """测试用户密码"""
    return "Wut@2024"