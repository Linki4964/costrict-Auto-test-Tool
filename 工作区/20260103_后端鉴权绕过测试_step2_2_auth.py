import json
import requests
import time
import os
from datetime import datetime
from typing import Dict, List, Any

class AuthBypassTester:
    def __init__(self, config_path: str = "project_config.json", apis_path: str = "apis.json"):
        self.config_path = config_path
        self.apis_path = apis_path
        self.results = []
        self.session = requests.Session()
        self.base_url = ""
        self.valid_token = ""
        self.work_dir = "."
        
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.base_url = f"http://{config.get('base_url', '')}"
            self.valid_token = config.get('auth_token', '')
            self.work_dir = config.get('work_dir', '.')
            
            if not self.valid_token:
                print("[ERROR] 未找到有效Token，需要重新获取")
                return False
            return True
        except Exception as e:
            print(f"[ERROR] 加载配置文件失败: {str(e)}")
            return False
    
    def load_apis(self) -> List[Dict]:
        """加载API列表"""
        try:
            with open(self.apis_path, 'r', encoding='utf-8') as f:
                apis = json.load(f)
            print(f"[INFO] 成功加载 {len(apis)} 个API接口")
            return apis
        except Exception as e:
            print(f"[ERROR] 加载API列表失败: {str(e)}")
            return []
    
    def setup_session_no_auth(self):
        """设置无认证请求会话"""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'RuoYi-Auth-Tester/1.0'
        })
    
    def setup_session_invalid_auth(self):
        """设置无效认证请求会话"""
        self.session.headers.update({
            'Authorization': 'Bearer invalid_token_12345',
            'Content-Type': 'application/json',
            'User-Agent': 'RuoYi-Auth-Tester/1.0'
        })
    
    def setup_session_expired_auth(self):
        """设置过期认证请求会话"""
        # 使用一个格式正确但已过期的token
        expired_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJleHBpcmVkIiwibG9naW5fdXNlcl9rZXkiOiJleHBpcmVkIn0.invalid_signature"
        self.session.headers.update({
            'Authorization': f'Bearer {expired_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'RuoYi-Auth-Tester/1.0'
        })
    
    def generate_valid_payload(self, api: Dict) -> Any:
        """生成有效的请求载荷"""
        method = api.get('method', '').upper()
        
        if method in ['POST', 'PUT'] and api.get('payload'):
            return api['payload'].get('example', {})
        
        # 根据路径参数生成查询参数
        params = api.get('params', [])
        if params and method == 'GET':
            query_params = {}
            for param in params:
                param_name = param.get('name', '')
                if 'Id' in param_name or 'Name' in param_name:
                    query_params[param_name] = '1'
                else:
                    query_params[param_name] = 'test'
            return query_params
        
        return None
    
    def test_api_no_auth(self, api: Dict) -> Dict:
        """测试无认证访问"""
        result = {
            'api': api,
            'test_type': 'NO_AUTH',
            'timestamp': datetime.now().isoformat(),
            'status_code': None,
            'biz_code': None,
            'biz_msg': None,
            'response_data': None,
            'security_result': 'UNKNOWN',
            'error': None,
            'risk_level': 'SAFE'
        }
        
        try:
            method = api.get('method', '').upper()
            path = api.get('path', '')
            full_url = f"{self.base_url}{path}"
            
            # 替换路径参数
            params = api.get('params', [])
            for param in params:
                param_name = param.get('name', '')
                if f"{{{param_name}}}" in path:
                    if 'Id' in param_name:
                        path = path.replace(f"{{{param_name}}}", '1')
                    elif 'Name' in param_name:
                        path = path.replace(f"{{{param_name}}}", 'admin')
                    else:
                        path = path.replace(f"{{{param_name}}}", 'test')
            
            full_url = f"{self.base_url}{path}"
            payload = self.generate_valid_payload(api)
            
            print(f"[TEST][NO_AUTH] {method} {path}")
            
            # 发送无认证请求
            if method == 'GET':
                response = self.session.get(full_url, params=payload, timeout=10)
            elif method == 'POST':
                response = self.session.post(full_url, json=payload, timeout=10)
            elif method == 'PUT':
                response = self.session.put(full_url, json=payload, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(full_url, timeout=10)
            else:
                result['error'] = f"不支持的HTTP方法: {method}"
                return result
            
            result['status_code'] = response.status_code
            
            # 解析响应
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    result['response_data'] = response_data
                    result['biz_code'] = response_data.get('code')
                    result['biz_msg'] = response_data.get('msg', '')
                    
                    # 安全判定：无认证但返回200且业务成功，判定为越权漏洞
                    if result['biz_code'] == 200:
                        result['security_result'] = 'HIGH_RISK'
                        result['risk_level'] = 'HIGH_RISK'
                        result['error'] = '越权访问：无认证但业务逻辑成功'
                    else:
                        result['security_result'] = 'SAFE'
                        result['risk_level'] = 'SAFE'
                        
                except json.JSONDecodeError:
                    # 返回非JSON但状态码200，也判定为潜在风险
                    result['security_result'] = 'MEDIUM_RISK'
                    result['risk_level'] = 'MEDIUM_RISK'
                    result['error'] = '无认证访问返回非JSON响应'
            elif response.status_code in [401, 403]:
                result['security_result'] = 'SAFE'
                result['risk_level'] = 'SAFE'
                result['error'] = f'正确的认证拦截: HTTP {response.status_code}'
            else:
                result['security_result'] = 'SAFE'
                result['risk_level'] = 'SAFE'
                result['error'] = f'请求被拒绝: HTTP {response.status_code}'
                
        except requests.exceptions.RequestException as e:
            result['security_result'] = 'ERROR'
            result['error'] = f'请求异常: {str(e)}'
        except Exception as e:
            result['security_result'] = 'ERROR'
            result['error'] = f'测试异常: {str(e)}'
        
        return result
    
    def test_api_invalid_auth(self, api: Dict) -> Dict:
        """测试无效认证访问"""
        result = {
            'api': api,
            'test_type': 'INVALID_AUTH',
            'timestamp': datetime.now().isoformat(),
            'status_code': None,
            'biz_code': None,
            'biz_msg': None,
            'response_data': None,
            'security_result': 'UNKNOWN',
            'error': None,
            'risk_level': 'SAFE'
        }
        
        try:
            method = api.get('method', '').upper()
            path = api.get('path', '')
            full_url = f"{self.base_url}{path}"
            
            # 替换路径参数
            params = api.get('params', [])
            for param in params:
                param_name = param.get('name', '')
                if f"{{{param_name}}}" in path:
                    if 'Id' in param_name:
                        path = path.replace(f"{{{param_name}}}", '1')
                    elif 'Name' in param_name:
                        path = path.replace(f"{{{param_name}}}", 'admin')
                    else:
                        path = path.replace(f"{{{param_name}}}", 'test')
            
            full_url = f"{self.base_url}{path}"
            payload = self.generate_valid_payload(api)
            
            print(f"[TEST][INVALID_AUTH] {method} {path}")
            
            # 发送无效认证请求
            if method == 'GET':
                response = self.session.get(full_url, params=payload, timeout=10)
            elif method == 'POST':
                response = self.session.post(full_url, json=payload, timeout=10)
            elif method == 'PUT':
                response = self.session.put(full_url, json=payload, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(full_url, timeout=10)
            else:
                result['error'] = f"不支持的HTTP方法: {method}"
                return result
            
            result['status_code'] = response.status_code
            
            # 解析响应
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    result['response_data'] = response_data
                    result['biz_code'] = response_data.get('code')
                    result['biz_msg'] = response_data.get('msg', '')
                    
                    # 无效认证但业务成功，判定为认证绕过漏洞
                    if result['biz_code'] == 200:
                        result['security_result'] = 'HIGH_RISK'
                        result['risk_level'] = 'HIGH_RISK'
                        result['error'] = '认证绕过：无效Token但业务逻辑成功'
                    else:
                        result['security_result'] = 'SAFE'
                        result['risk_level'] = 'SAFE'
                        
                except json.JSONDecodeError:
                    result['security_result'] = 'MEDIUM_RISK'
                    result['risk_level'] = 'MEDIUM_RISK'
                    result['error'] = '无效认证访问返回非JSON响应'
            elif response.status_code in [401, 403]:
                result['security_result'] = 'SAFE'
                result['risk_level'] = 'SAFE'
                result['error'] = f'正确的认证拦截: HTTP {response.status_code}'
            else:
                result['security_result'] = 'SAFE'
                result['risk_level'] = 'SAFE'
                result['error'] = f'请求被拒绝: HTTP {response.status_code}'
                
        except requests.exceptions.RequestException as e:
            result['security_result'] = 'ERROR'
            result['error'] = f'请求异常: {str(e)}'
        except Exception as e:
            result['security_result'] = 'ERROR'
            result['error'] = f'测试异常: {str(e)}'
        
        return result
    
    def run_auth_tests(self) -> bool:
        """运行鉴权绕过测试"""
        print("[INFO] 开始执行鉴权绕过测试...")
        
        # 加载配置和API
        if not self.load_config():
            return False
        
        apis = self.load_apis()
        if not apis:
            return False
        
        # 执行无认证测试
        print("\n[INFO] 执行无认证访问测试...")
        self.setup_session_no_auth()
        
        for i, api in enumerate(apis, 1):
            print(f"\n[{i}/{len(apis)}][NO_AUTH] ", end='')
            result = self.test_api_no_auth(api)
            self.results.append(result)
            
            if result['security_result'] == 'HIGH_RISK':
                print(f"[HIGH_RISK] {api['method']} {api['path']}: 发现越权漏洞！")
            elif result['security_result'] == 'SAFE':
                print(f"[SAFE] {api['method']} {api['path']}: 认证拦截正常")
            else:
                print(f"[{result['security_result']}] {api['method']} {api['path']}: {result.get('error', 'Unknown')}")
            
            time.sleep(0.1)
        
        # 执行无效认证测试
        print("\n[INFO] 执行无效认证访问测试...")
        self.setup_session_invalid_auth()
        
        for i, api in enumerate(apis, 1):
            print(f"\n[{i}/{len(apis)}][INVALID_AUTH] ", end='')
            result = self.test_api_invalid_auth(api)
            self.results.append(result)
            
            if result['security_result'] == 'HIGH_RISK':
                print(f"[HIGH_RISK] {api['method']} {api['path']}: 发现认证绕过漏洞！")
            elif result['security_result'] == 'SAFE':
                print(f"[SAFE] {api['method']} {api['path']}: 认证验证正常")
            else:
                print(f"[{result['security_result']}] {api['method']} {api['path']}: {result.get('error', 'Unknown')}")
            
            time.sleep(0.1)
        
        # 生成测试报告
        self.generate_report()
        
        # 保存结果
        return self.save_results()
    
    def generate_report(self):
        """生成测试报告"""
        high_risk_count = sum(1 for r in self.results if r['risk_level'] == 'HIGH_RISK')
        safe_count = sum(1 for r in self.results if r['risk_level'] == 'SAFE')
        medium_risk_count = sum(1 for r in self.results if r['risk_level'] == 'MEDIUM_RISK')
        error_count = sum(1 for r in self.results if r['security_result'] == 'ERROR')
        
        print(f"\n{'='*60}")
        print("鉴权绕过测试报告")
        print(f"{'='*60}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总测试数: {len(self.results)}")
        print(f"高危漏洞: {high_risk_count}")
        print(f"安全: {safe_count}")
        print(f"中风险: {medium_risk_count}")
        print(f"错误: {error_count}")
        
        if high_risk_count > 0:
            print(f"\n[!] 发现 {high_risk_count} 个高危越权/认证绕过漏洞！")
            high_risk_apis = [r for r in self.results if r['risk_level'] == 'HIGH_RISK']
            for api_result in high_risk_apis[:5]:  # 只显示前5个
                api = api_result['api']
                print(f"  - {api_result['test_type']}: {api['method']} {api['path']}")
        print(f"{'='*60}")
    
    def save_results(self) -> bool:
        """保存测试结果"""
        try:
            output_file = os.path.join(self.work_dir, "results_auth_bypass.json")
            
            # 脱敏处理：替换Token
            results_for_save = []
            for result in self.results:
                result_copy = result.copy()
                if 'Authorization' in str(result_copy):
                    result_copy = str(result_copy).replace(self.valid_token, '<REDACTED>')
                results_for_save.append(result_copy)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_for_save, f, indent=2, ensure_ascii=False)
            
            print(f"[SUCCESS] 测试结果已保存至: {output_file}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存测试结果失败: {str(e)}")
            return False

def main():
    """主函数"""
    print("[WARNING] 仅限授权测试！开始鉴权绕过测试...")
    print("=" * 60)
    
    tester = AuthBypassTester()
    success = tester.run_auth_tests()
    
    if success:
        print("\n[SUCCESS] 鉴权绕过测试完成！")
        return True
    else:
        print("\n[ERROR] 鉴权绕过测试失败！")
        return False

if __name__ == "__main__":
    main()