# -*- coding: utf-8 -*-
"""
配置与初始化脚本
功能：获取鉴权Token并分析项目结构
"""

import requests
import json
import subprocess
import os
from datetime import datetime


def fetch_and_save_token(base_url: str, username: str, password: str, work_dir: str = "."):
    """
    获取鉴权Token并保存到配置文件
    
    Args:
        base_url: 目标系统Base URL
        username: 用户名
        password: 密码
        work_dir: 工作目录
    
    Returns:
        str: 认证Token
    """
    try:
        login_url = f"{base_url}/prod-api/login"
        print(f"正在登录: {login_url}")
        
        payload = {
            "username": username,
            "password": password
        }
        
        resp = requests.post(login_url, json=payload, timeout=10)
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 200:
                token = result.get("token")
                print("Token获取成功")
                return token
            else:
                print(f"登录失败: {result.get('msg')}")
                return None
        else:
            print(f"HTTP请求失败: {resp.status_code}")
            return None
            
    except Exception as e:
        print(f"获取Token时发生错误: {str(e)}")
        return None


def capture_project_structure(source_path: str, work_dir: str = "."):
    """
    分析源码目录结构并保存到文件
    
    Args:
        source_path: 源码根路径
        work_dir: 工作目录
    
    Returns:
        str: 项目结构文件路径
    """
    try:
        output_file = os.path.join(work_dir, "project_structure.txt")
        print(f"正在分析源码结构: {source_path}")
        
        # Windows系统使用dir命令
        if os.name == 'nt':
            cmd = f'dir "{source_path}" /s /b > "{output_file}"'
        else:
            cmd = f'find "{source_path}" -type f > "{output_file}"'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"项目结构已保存到: {output_file}")
            return output_file
        else:
            print(f"分析项目结构失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"分析项目结构时发生错误: {str(e)}")
        return None


def analyze_tech_stack(structure_file: str):
    """
    根据项目结构文件识别技术栈
    
    Args:
        structure_file: 项目结构文件路径
    
    Returns:
        dict: 技术栈信息
    """
    tech_stack = {
        "backend": "Unknown",
        "language": "Unknown",
        "framework": "Unknown"
    }
    
    try:
        with open(structure_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 识别Java Spring
        if 'pom.xml' in content or 'application.java' in content.lower():
            tech_stack["backend"] = "Java"
            tech_stack["language"] = "Java"
            tech_stack["framework"] = "Spring Boot"
            
        # 识别Python
        elif 'requirements.txt' in content or 'manage.py' in content:
            tech_stack["backend"] = "Python"
            tech_stack["language"] = "Python"
            if 'flask' in content.lower():
                tech_stack["framework"] = "Flask"
            elif 'django' in content.lower():
                tech_stack["framework"] = "Django"
            elif 'fastapi' in content.lower():
                tech_stack["framework"] = "FastAPI"
                
        # 识别Node.js
        elif 'package.json' in content:
            tech_stack["backend"] = "Node.js"
            tech_stack["language"] = "JavaScript/TypeScript"
            
            # 检测框架
            if 'express' in content.lower():
                tech_stack["framework"] = "Express"
            elif 'nest' in content.lower():
                tech_stack["framework"] = "NestJS"
                
        # Go
        elif 'go.mod' in content or 'main.go' in content:
            tech_stack["backend"] = "Go"
            tech_stack["language"] = "Go"
            
    except Exception as e:
        print(f"分析技术栈时发生错误: {str(e)}")
        
    return tech_stack


def main():
    """
    主函数：执行配置与初始化流程
    """
    print("="*60)
    print("开始配置与初始化")
    print("="*60)
    
    # 默认配置
    config = {
        "source_path": r"D:\desktop\AI Coding\RuoYi-Vue",
        "base_url": "http://192.168.236.128",
        "work_dir": r"d:\desktop\AI Coding\costrict-Auto-test-Tool",
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"\n配置信息:")
    print(f"  源码路径: {config['source_path']}")
    print(f"  目标URL: {config['base_url']}")
    print(f"  工作目录: {config['work_dir']}")
    print(f"  用户名: {config['username']}")
    
    # 1. 获取Token
    print("\n[步骤 1/3] 获取鉴权Token...")
    token = fetch_and_save_token(
        config['base_url'],
        config['username'],
        config['password'],
        config['work_dir']
    )
    
    if not token:
        print("错误: 无法获取Token，初始化失败")
        return
    
    # 2. 分析项目结构
    print("\n[步骤 2/3] 分析源码结构...")
    structure_file = capture_project_structure(
        config['source_path'],
        config['work_dir']
    )
    
    if not structure_file:
        print("警告: 无法分析项目结构")
    
    # 3. 识别技术栈
    print("\n[步骤 3/3] 识别技术栈...")
    tech_stack = {}
    if structure_file:
        tech_stack = analyze_tech_stack(structure_file)
    
    print(f"\n识别到的技术栈:")
    print(f"  后端: {tech_stack.get('backend', 'Unknown')}")
    print(f"  语言: {tech_stack.get('language', 'Unknown')}")
    print(f"  框架: {tech_stack.get('framework', 'Unknown')}")
    
    # 4. 生成配置文件
    project_config = {
        "source_path": config['source_path'],
        "base_url": config['base_url'],
        "work_dir": config['work_dir'],
        "authentication": {
            "username": config['username'],
            "password": config['password'],
            "token": token,
            "login_url": f"{config['base_url']}/prod-api/login"
        },
        "tech_stack": tech_stack,
        "created_at": datetime.now().isoformat(),
        "config_file": structure_file
    }
    
    config_file = os.path.join(config['work_dir'], "project_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(project_config, f, indent=4, ensure_ascii=False)
    
    print(f"\n配置文件已生成: {config_file}")
    print("="*60)
    print("配置与初始化完成")
    print("="*60)


if __name__ == "__main__":
    main()