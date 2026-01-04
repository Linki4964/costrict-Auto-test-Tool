# -*- coding: utf-8 -*-
import requests
import json
import os
import subprocess
from pathlib import Path

def fetch_and_save_token(base_url: str, username: str, password: str):
    """获取鉴权Token并保存到配置文件"""
    login_url = f"{base_url}/prod-api/login"
    
    try:
        resp = requests.post(login_url, json={"username": username, "password": password}, timeout=10)
        
        if resp.status_code == 200:
            result = resp.json()
            if result.get("code") == 200:
                token = result.get("token")
                print(f"[SUCCESS] 登录成功，获取Token: {token[:20]}...")
                return token
            else:
                print(f"[ERROR] 登录失败，业务错误: {result.get('msg')}")
                return None
        else:
            print(f"[ERROR] HTTP请求失败，状态码: {resp.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] 请求异常: {str(e)}")
        return None

def capture_project_structure(source_path: str):
    """分析项目结构，生成技术栈信息"""
    # 转换为绝对路径
    source_path = os.path.abspath(source_path)
    
    if not os.path.exists(source_path):
        print(f"[ERROR] 源码路径不存在: {source_path}")
        return {"error": "源码路径不存在"}
    
    print(f"[INFO] 分析源码路径: {source_path}")
    
    project_info = {
        "project_structure": {},
        "tech_stack": {
            "language": "unknown",
            "framework": "unknown"
        },
        "java_files": 0,
        "js_vue_files": 0
    }
    
    # 使用Windows的dir命令获取文件结构
    try:
        cmd = f'dir "{source_path}" /s /b'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk')
        
        if result.returncode == 0:
            files = result.stdout.split('\n')
            
            # 统计文件类型识别技术栈
            for file_path in files:
                if file_path.strip():
                    ext = os.path.splitext(file_path)[1].lower()
                    
                    if ext == '.java':
                        project_info['java_files'] += 1
                        if project_info['tech_stack']['language'] == 'unknown':
                            project_info['tech_stack']['language'] = 'Java'
                    
                    if ext in ['.vue', '.js']:
                        project_info['js_vue_files'] += 1
                        if ext == '.vue' and project_info['tech_stack']['framework'] == 'unknown':
                            project_info['tech_stack']['framework'] = 'Vue'
                    
                    if ext == '.java' and project_info['tech_stack']['framework'] == 'unknown':
                        # 检查是否存在Spring相关文件
                        if 'pom.xml' in file_path or 'Spring' in file_path:
                            project_info['tech_stack']['framework'] = 'Spring Boot'
            
            # 简化的目录结构（仅记录顶层目录）
            for root, dirs, files in os.walk(source_path):
                level = root.replace(source_path, '').count(os.sep)
                if level <= 2:  # 只记录前两层
                    project_info['project_structure'][root] = {
                        'dirs': dirs,
                        'file_count': len(files)
                    }
                if level > 2:
                    continue
            
            print(f"[SUCCESS] 项目结构分析完成")
            print(f"   - Java文件数: {project_info['java_files']}")
            print(f"   - JS/Vue文件数: {project_info['js_vue_files']}")
            print(f"   - 识别技术栈: {project_info['tech_stack']['language']} / {project_info['tech_stack']['framework']}")
            
        else:
            print(f"[ERROR] 执行dir命令失败: {result.stderr}")
            
    except Exception as e:
        print(f"[ERROR] 分析过程异常: {str(e)}")
    
    return project_info

def generate_project_config():
    """生成project_config.json配置文件"""
    print("=" * 60)
    print("[START] 开始配置自动化测试环境")
    print("=" * 60)
    
    # 读取配置文件
    config_path = "configure.json"
    if not os.path.exists(config_path):
        print(f"[ERROR] 配置文件不存在: {config_path}")
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 提取关键参数
    target_url = config['project_setup']['target_url']
    source_code_path = config['project_setup']['source_code_path']
    username = config['authentication']['username']
    password = config['authentication']['password']
    work_dir = config['workspace']['path'][0]
    
    print(f"\n[INFO] 配置信息:")
    print(f"   目标URL: {target_url}")
    print(f"   源码路径: {source_code_path}")
    print(f"   账号: {username}")
    print(f"   工作目录: {work_dir}")
    
    # 步骤1: 获取Token
    print(f"\n{'='*20} Step 1: 获取鉴权Token {'='*20}")
    auth_token = fetch_and_save_token(target_url, username, password)
    
    if not auth_token:
        print("[ERROR] 无法获取Token，配置终止")
        return None
    
    # 步骤2: 分析项目结构
    print(f"\n{'='*20} Step 2: 分析项目结构 {'='*20}")
    project_info = capture_project_structure(source_code_path)
    
    # 步骤3: 生成project_config.json
    print(f"\n{'='*20} Step 3: 生成配置文件 {'='*20}")
    
    final_config = {
        "auth": {
            "base_url": target_url,
            "username": username,
            "password": password,
            "auth_token": auth_token
        },
        "source_analysis": {
            "source_path": os.path.abspath(source_code_path),
            "tech_stack": project_info.get('tech_stack', {}),
            "java_files": project_info.get('java_files', 0),
            "js_vue_files": project_info.get('js_vue_files', 0)
        },
        "workspace": {
            "work_dir": os.path.abspath(work_dir),
            "created_time": "2026-01-04"
        }
    }
    
    output_path = "project_config.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_config, f, indent=4, ensure_ascii=False)
    
    print(f"[SUCCESS] 配置文件已生成: {output_path}")
    
    print(f"\n" + "=" * 60)
    print("[DONE] 配置完成！技术栈信息:")
    lang = final_config['source_analysis']['tech_stack'].get('language', 'unknown')
    framework = final_config['source_analysis']['tech_stack'].get('framework', 'unknown')
    print(f"   语言: {lang}")
    print(f"   框架: {framework}")
    print("=" * 60)
    
    return final_config

if __name__ == "__main__":
    generate_project_config()