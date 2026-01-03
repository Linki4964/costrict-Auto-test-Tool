import json
import requests
import time
import os
from datetime import datetime
from typing import Dict, List, Any

class BoundaryValueTester:
    def __init__(self, config_path: str = "project_config.json", apis_path: str = "apis.json"):
        self.config_path = config_path
        self.apis_path = apis_path
        self.results = []
        self.session = requests.Session()
        self.base_url = ""
        self.token = ""
        self.work_dir = "."
        
        # 边界值定义
        self.boundary_values = {
            'integer': [
                -2147483648,  # INT_MIN
                -2147483647,  # INT_MIN + 1
                -1,           # 负数
                0,            # 零
                1,            # 正数
                2147483646,   # INT_MAX - 1
                2147483647,   # INT_MAX
                2147483648,   # INT_MAX + 1 (溢出)
                -2147483649,  # INT_MIN - 1 (溢出)
                999999999999999999999999999999  # 极大值
            ],
            'string': [
                "",           # 空字符串
                "A",          # 单字符
                "A" * 10,     # 短字符串
                "A" * 100,    # 中等长度
                "A" * 1000,   # 长字符串
                "A" * 10000,  # 超长字符串
                "中文测试",    # 中文字符
                "🚀🎉💯",     # Emoji字符
                "special!@#$%^&*()",  # 特殊字符
                "null",       # 字符串"null"
                "undefined",  # 字符串"undefined"
                "true",       # 字符串"true"
                "false"       # 字符串"false"
            ],
            'boolean': [
                True,
                False,
                "true",       # 字符串形式
                "false",      # 字符串形式
                1,            # 数字形式
                0,            # 数字形式
                "1",
                "0"
            ],
            'array': [
                [],           # 空数组
                [1],          # 单元素
                [1, 2, 3],    # 多元素
                list(range(100)),  # 大数组
                [None],       # 包含null
                ["", ""],     # 包含空字符串
                [1, "test", True]  # 混合类型
            ],
            'null': [
                None,
                "null",
                "",
                0,
                False
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
            'User-Agent': 'RuoYi-Boundary-Tester/1.0'
        })
    
    def detect_param_type(self, param_name: str, example_value: Any = None) -> str:
        """根据参数名和示例值推断参数类型"""
        param_lower = param_name.lower()
        
        # 基于参数名推断类型
        if any(keyword in param_lower for keyword in ['id', 'count', 'size', 'limit', 'page', 'num']):
            return 'integer'
        elif any(keyword in param_lower for keyword in ['name', 'title', 'description', 'content', 'remark']):
            return 'string'
        elif any(keyword in param_lower for keyword in ['status', 'flag', 'enable', 'disable']):
            return 'boolean'
        elif any(keyword in param_lower for keyword in ['list', 'array', 'items']):
            return 'array'
        
        # 基于示例值推断类型
        if example_value is not None:
            if isinstance(example_value, bool):
                return 'boolean'
            elif isinstance(example_value, int):
                return 'integer'
            elif isinstance(example_value, str):
                return 'string'
            elif isinstance(example_value, list):
                return 'array'
        
        return 'string'  # 默认类型
    
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
                param_type = self.detect_param_type(param_name)
                
                if param_type == 'integer':
                    query_params[param_name] = 1
                elif param_type == 'string':
                    query_params[param_name] = 'test'
                elif param_type == 'boolean':
                    query_params[param_name] = True
                else:
                    query_params[param_name] = 'test'
            
            return query_params
        
        return None
    
    def generate_boundary_payloads(self, api: Dict) -> List[Dict]:
        """生成边界值测试载荷"""
        payloads = []
        method = api.get('method', '').upper()
        base_payload = {}
        
        # 基础有效载荷
        if method in ['POST', 'PUT'] and api.get('payload'):
            base_payload = api['payload'].get('example', {}).copy()
        
        # 1. 路径参数边界值测试
        params = api.get('params', [])
        for param in params:
            param_name = param.get('name', '')
            param_type = self.detect_param_type(param_name)
            
            if param_type in self.boundary_values:
                boundary_values = self.boundary_values[param_type]
                for boundary_value in boundary_values:
                    boundary_test = {
                        'type': 'path_param',
                        'param_name': param_name,
                        'param_type': param_type,
                        'boundary_value': boundary_value,
                        'payload': base_payload.copy()
                    }
                    payloads.append(boundary_test)
        
        # 2. 请求体参数边界值测试
        if base_payload:
            for key in base_payload:
                original_value = base_payload[key]
                param_type = self.detect_param_type(key, original_value)
                
                if param_type in self.boundary_values:
                    boundary_values = self.boundary_values[param_type]
                    for boundary_value in boundary_values:
                        fuzzed_payload = base_payload.copy()
                        fuzzed_payload[key] = boundary_value
                        
                        boundary_test = {
                            'type': 'body_param',
                            'param_name': key,
                            'param_type': param_type,
                            'boundary_value': boundary_value,
                            'payload': fuzzed_payload,
                            'original_value': original_value
                        }
                        payloads.append(boundary_test)
        
        # 如果没有生成载荷，添加一个基础载荷
        if not payloads and base_payload:
            payloads.append({
                'type': 'baseline',
                'payload': base_payload,
                'param_name': None,
                'param_type': None,
                'boundary_value': None
            })
        
        return payloads[:15]  # 限制载荷数量，避免测试时间过长
    
    def test_api_boundary(self, api: Dict) -> List[Dict]:
        """对单个API进行边界值测试"""
        results = []
        
        # 生成边界值测试载荷
        boundary_payloads = self.generate_boundary_payloads(api)
        
        for i, boundary_test in enumerate(boundary_payloads):
            result = {
                'api': api,
                'test_type': 'BOUNDARY_VALUE',
                'timestamp': datetime.now().isoformat(),
                'boundary_info': {
                    'type': boundary_test['type'],
                    'param_name': boundary_test.get('param_name'),
                    'param_type': boundary_test.get('param_type'),
                    'boundary_value': boundary_test.get('boundary_value'),
                    'original_value': boundary_test.get('original_value')
                },
                'status_code': None,
                'biz_code': None,
                'biz_msg': None,
                'security_result': 'UNKNOWN',
                'error': None,
                'risk_level': 'SAFE',
                'validation_result': None
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
                        # 如果有边界值测试的路径参数，使用边界值
                        if (boundary_test['type'] == 'path_param' and 
                            boundary_test['param_name'] == param_name):
                            boundary_value = boundary_test['boundary_value']
                        else:
                            # 使用默认值
                            if 'Id' in param_name:
                                boundary_value = '1'
                            elif 'Name' in param_name:
                                boundary_value = 'admin'
                            else:
                                boundary_value = 'test'
                        
                        fuzzed_path = fuzzed_path.replace(f"{{{param_name}}}", str(boundary_value))
                
                full_url = f"{self.base_url}{fuzzed_path}"
                
                # 准备请求数据
                request_data = boundary_test['payload']
                
                print(f"[BOUNDARY][{i+1}/{len(boundary_payloads)}] {method} {fuzzed_path}")
                
                # 发送边界值测试请求
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
                    # 服务器错误，可能存在边界值处理问题
                    result['security_result'] = 'HIGH_RISK'
                    result['risk_level'] = 'HIGH_RISK'
                    result['error'] = '服务器内部错误 (500) - 边界值处理异常'
                    
                    # 尝试提取错误信息
                    try:
                        error_data = response.json()
                        result['validation_result'] = str(error_data)[:300]
                    except:
                        result['validation_result'] = response.text[:300]
                        
                elif response.status_code == 200:
                    try:
                        response_data = response.json()
                        result['response_data'] = response_data
                        result['biz_code'] = response_data.get('code')
                        result['biz_msg'] = response_data.get('msg', '')
                        
                        # 检查业务逻辑是否正确处理边界值
                        if result['biz_code'] == 200:
                            result['security_result'] = 'SAFE'
                            result['risk_level'] = 'SAFE'
                            result['validation_result'] = '边界值处理正常'
                        else:
                            # 业务逻辑拒绝，检查是否合理
                            error_msg = result['biz_msg'].lower()
                            if any(keyword in error_msg for keyword in ['invalid', 'error', 'fail', 'exception']):
                                result['security_result'] = 'SAFE'
                                result['risk_level'] = 'SAFE'
                                result['validation_result'] = '合理的边界值验证'
                            else:
                                result['security_result'] = 'MEDIUM_RISK'
                                result['risk_level'] = 'MEDIUM_RISK'
                                result['validation_result'] = '边界值处理异常'
                                
                    except json.JSONDecodeError:
                        result['security_result'] = 'MEDIUM_RISK'
                        result['risk_level'] = 'MEDIUM_RISK'
                        result['validation_result'] = '非JSON响应'
                else:
                    # 其他状态码
                    result['security_result'] = 'SAFE'
                    result['risk_level'] = 'SAFE'
                    result['validation_result'] = f'请求被拒绝: HTTP {response.status_code}'
                    
            except requests.exceptions.RequestException as e:
                result['security_result'] = 'ERROR'
                result['error'] = f'请求异常: {str(e)}'
            except Exception as e:
                result['security_result'] = 'ERROR'
                result['error'] = f'边界值测试异常: {str(e)}'
            
            results.append(result)
            
            # 避免请求过快
            time.sleep(0.05)
        
        return results
    
    def run_boundary_tests(self) -> bool:
        """运行边界值测试"""
        print("[INFO] 开始执行边界值测试...")
        
        # 加载配置和API
        if not self.load_config():
            return False
        
        apis = self.load_apis()
        if not apis:
            return False
        
        self.setup_session()
        
        # 执行边界值测试
        high_risk_count = 0
        medium_risk_count = 0
        safe_count = 0
        error_count = 0
        
        for i, api in enumerate(apis, 1):
            print(f"\n[{i}/{len(apis)}] ", end='')
            api_results = self.test_api_boundary(api)
            
            for result in api_results:
                self.results.append(result)
                
                if result['security_result'] == 'HIGH_RISK':
                    high_risk_count += 1
                    boundary_info = result.get('boundary_info', {})
                    print(f"[HIGH_RISK] {api['method']} {api['path']}: "
                          f"参数{boundary_info.get('param_name')}边界值{boundary_info.get('boundary_value')}导致服务器错误")
                elif result['security_result'] == 'MEDIUM_RISK':
                    medium_risk_count += 1
                    print(f"[MEDIUM_RISK] {api['method']} {api['path']}: 边界值处理异常")
                elif result['security_result'] == 'SAFE':
                    safe_count += 1
                    print(f"[SAFE] {api['method']} {api['path']}: 边界值处理正常")
                else:
                    error_count += 1
                    print(f"[ERROR] {api['method']} {api['path']}: {result.get('error', 'Unknown')}")
        
        # 生成测试报告
        self.generate_report(high_risk_count, medium_risk_count, safe_count, error_count)
        
        # 保存结果
        return self.save_results()
    
    def generate_report(self, high_risk: int, medium_risk: int, safe: int, error: int):
        """生成测试报告"""
        total = high_risk + medium_risk + safe + error
        
        print(f"\n{'='*60}")
        print("边界值测试报告")
        print(f"{'='*60}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总测试数: {total}")
        print(f"高危漏洞: {high_risk}")
        print(f"中风险: {medium_risk}")
        print(f"安全: {safe}")
        print(f"错误: {error}")
        
        if high_risk > 0:
            print(f"\n[!] 发现 {high_risk} 个边界值处理高危漏洞！")
            high_risk_results = [r for r in self.results if r.get('security_result') == 'HIGH_RISK']
            for result in high_risk_results[:3]:  # 只显示前3个
                api = result['api']
                boundary_info = result.get('boundary_info', {})
                print(f"  - {api['method']} {api['path']}: "
                      f"参数{boundary_info.get('param_name')}边界值{boundary_info.get('boundary_value')}")
        print(f"{'='*60}")
    
    def save_results(self) -> bool:
        """保存测试结果"""
        try:
            output_file = os.path.join(self.work_dir, "results_boundary.json")
            
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
    print("[WARNING] 仅限授权测试！开始边界值测试...")
    print("=" * 60)
    
    tester = BoundaryValueTester()
    success = tester.run_boundary_tests()
    
    if success:
        print("\n[SUCCESS] 边界值测试完成！")
        return True
    else:
        print("\n[ERROR] 边界值测试失败！")
        return False

if __name__ == "__main__":
    main()