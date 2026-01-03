import os
import json
import requests
import subprocess
from pathlib import Path

class ProjectConfigurator:
    def __init__(self, source_path, base_url, work_dir, username, password):
        self.source_path = source_path
        self.base_url = base_url
        self.work_dir = work_dir
        self.username = username
        self.password = password
        self.config_file = os.path.join(work_dir, "project_config.json")
        
    def fetch_and_save_token(self):
        """获取鉴权Token并保存到配置文件"""
        try:
            login_url = f"http://{self.base_url}/prod-api/login"
            payload = {"username": self.username, "password": self.password}
            
            resp = requests.post(login_url, json=payload, timeout=10)
            
            if resp.status_code == 200:
                response_data = resp.json()
                if response_data.get("code") == 200:
                    token = response_data.get("token")
                    if token:
                        config = {
                            "auth_token": token,
                            "base_url": self.base_url,
                            "username": self.username,
                            "source_path": self.source_path,
                            "work_dir": self.work_dir
                        }
                        
                        os.makedirs(self.work_dir, exist_ok=True)
                        with open(self.config_file, "w", encoding='utf-8') as f:
                            json.dump(config, f, indent=4, ensure_ascii=False)
                        print(f"[SUCCESS] Token获取成功，已保存到 {self.config_file}")
                        return True
                    else:
                        print("[ERROR] Token获取失败：响应中未找到token字段")
                        return False
                else:
                    print(f"[ERROR] 登录失败：{response_data.get('msg', '未知错误')}")
                    return False
            else:
                print(f"[ERROR] 网络请求失败：HTTP {resp.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Token获取异常：{str(e)}")
            return False
    
    def capture_project_structure(self):
        """分析项目结构，识别技术栈"""
        try:
            if not os.path.exists(self.source_path):
                print(f"[ERROR] 源码路径不存在：{self.source_path}")
                return False
                
            # 生成项目结构文件
            structure_file = os.path.join(self.work_dir, "project_structure.txt")
            
            # 使用Windows的dir命令获取目录结构
            cmd = f'dir "{self.source_path}" /s /b'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='gbk')
            
            if result.returncode == 0:
                with open(structure_file, "w", encoding='utf-8') as f:
                    f.write(result.stdout)
                
                # 技术栈识别
                tech_stack = self._identify_tech_stack()
                tech_file = os.path.join(self.work_dir, "tech_stack_analysis.json")
                
                with open(tech_file, "w", encoding='utf-8') as f:
                    json.dump(tech_stack, f, indent=4, ensure_ascii=False)
                
                print(f"[SUCCESS] 项目结构分析完成，技术栈：{tech_stack.get('primary_tech', '未知')}")
                return True
            else:
                print(f"[ERROR] 目录扫描失败：{result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 项目结构分析异常：{str(e)}")
            return False
    
    def _identify_tech_stack(self):
        """基于文件扩展名和目录结构识别技术栈"""
        tech_indicators = {
            'java': ['.java', 'pom.xml', 'build.gradle'],
            'python': ['.py', 'requirements.txt', 'setup.py'],
            'javascript': ['.js', 'package.json', 'node_modules'],
            'typescript': ['.ts', 'tsconfig.json'],
            'vue': ['.vue', 'vue.config.js'],
            'react': ['.jsx', '.tsx', 'react'],
            'spring': ['application.yml', 'application.properties', '@SpringBootApplication'],
            'mybatis': ['.xml', 'mybatis', 'mapper'],
            'mysql': ['.sql', 'mysql'],
            'redis': ['redis', 'cache']
        }
        
        detected_techs = []
        file_counts = {}
        
        # 扫描项目文件
        for root, dirs, files in os.walk(self.source_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in tech_indicators['java']:
                    detected_techs.append('java')
                    file_counts['java'] = file_counts.get('java', 0) + 1
                elif ext in tech_indicators['python']:
                    detected_techs.append('python')
                    file_counts['python'] = file_counts.get('python', 0) + 1
                elif ext in tech_indicators['javascript']:
                    detected_techs.append('javascript')
                    file_counts['javascript'] = file_counts.get('javascript', 0) + 1
                elif ext in tech_indicators['typescript']:
                    detected_techs.append('typescript')
                    file_counts['typescript'] = file_counts.get('typescript', 0) + 1
                elif ext in tech_indicators['vue']:
                    detected_techs.append('vue')
                    file_counts['vue'] = file_counts.get('vue', 0) + 1
                
                # 检查配置文件
                if file == 'pom.xml':
                    detected_techs.append('maven')
                elif file == 'package.json':
                    detected_techs.append('nodejs')
                elif 'application.yml' in file or 'application.properties' in file:
                    detected_techs.append('spring')
                elif 'mybatis' in root.lower():
                    detected_techs.append('mybatis')
        
        # 确定主要技术栈
        primary_tech = max(file_counts.items(), key=lambda x: x[1])[0] if file_counts else 'unknown'
        
        return {
            'detected_techs': list(set(detected_techs)),
            'primary_tech': primary_tech,
            'file_counts': file_counts,
            'analysis_time': '2026-01-03T14:55:39.481Z'
        }

def main():
    """主函数：执行配置与初始化"""
    # 用户提供的参数
    source_path = r"E:\project\Costric\RuoYi-Vue"
    base_url = "192.168.142.146"
    work_dir = r"e:\project\Costric\costrict-Auto-test-Tool\工作区"
    username = "admin"
    password = "admin123"
    
    print("[WARNING] 仅限授权测试！开始配置与初始化...")
    print("=" * 50)
    
    # 创建配置器实例
    configurator = ProjectConfigurator(source_path, base_url, work_dir, username, password)
    
    # 步骤1：获取Token
    print("步骤1：获取鉴权Token...")
    token_success = configurator.fetch_and_save_token()
    
    if not token_success:
        print("[ERROR] Token获取失败，终止初始化")
        return False
    
    # 步骤2：分析项目结构
    print("\n步骤2：分析项目结构...")
    structure_success = configurator.capture_project_structure()
    
    if not structure_success:
        print("[ERROR] 项目结构分析失败")
        return False
    
    print("\n[SUCCESS] 配置与初始化完成！")
    print(f"配置文件位置：{configurator.config_file}")
    return True

if __name__ == "__main__":
    main()