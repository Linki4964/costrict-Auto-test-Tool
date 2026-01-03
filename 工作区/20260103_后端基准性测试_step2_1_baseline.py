import json
import requests
import time
import os
from datetime import datetime
from typing import Dict, List, Any

class BaselineAPITester:
    def __init__(self, config_path: str = "project_config.json", apis_path: str = "apis.json"):
        self.config_path = config_path
        self.apis_path = apis_path
        self.results = []
        self.session = requests.Session()
        self.base_url = ""
        self.token = ""
        self.work_dir = "."
        
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
            'User-Agent': 'RuoYi-API-Tester/1.0'
        })
    
    def generate_valid_payload(self, api: Dict) -> Any:
        """生成有效的请求载荷"""
        method = api.get('method', '').upper()
        
        if method in ['POST', 'PUT'] and api.get('payload'):
            # 使用预定义的payload示例
            return api['payload'].get('example', {})
        
        # 根据路径参数生成查询参数
        params = api.get('params', [])
        if params and method == 'GET':
            query_params = {}
            for param in params:
                param_name = param.get('name', '')
                if 'Id' in param_name or 'Name' in param_name:
                    query_params[param_name] = '1'  # 默认ID值
                else:
                    query_params[param_name] = 'test'
            return query_params
        
        return None
    
    def test_api(self, api: Dict) -> Dict:
        """测试单个API"""
        result = {
            'api': api,
            'timestamp': datetime.now().isoformat(),
            'status_code': None,
            'biz_code': None,
            'biz_msg': None,
            'response_data': None,
            'test_result': 'UNKNOWN',
            'error': None
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
                    # 根据参数类型提供合理的测试值
                    if 'Id' in param_name:
                        path = path.replace(f"{{{param_name}}}", '1')
                    elif 'Name' in param_name:
                        path = path.replace(f"{{{param_name}}}", 'admin')
                    else:
                        path = path.replace(f"{{{param_name}}}", 'test')
            
            full_url = f"{self.base_url}{path}"
            
            # 准备请求数据
            payload = self.generate_valid_payload(api)
            
            print(f"[TEST] {method} {path}")
            
            # 发送请求
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
                    
                    # 判定业务逻辑是否成功
                    if result['biz_code'] == 200:
                        result['test_result'] = 'PASS'
                    else:
                        result['test_result'] = 'FAIL'
                        result['error'] = f"业务逻辑失败: {result['biz_msg']}"
                        
                except json.JSONDecodeError:
                    result['test_result'] = 'FAIL'
                    result['error'] = '响应不是有效的JSON格式'
            else:
                result['test_result'] = 'FAIL'
                result['error'] = f'HTTP状态码异常: {response.status_code}'
                
        except requests.exceptions.RequestException as e:
            result['test_result'] = 'ERROR'
            result['error'] = f'请求异常: {str(e)}'
        except Exception as e:
            result['test_result'] = 'ERROR'
            result['error'] = f'测试异常: {str(e)}'
        
        return result
    
    def parse_response(self, response: requests.Response) -> Dict:
        """解析响应结果"""
        result = {
            'status_code': response.status_code,
            'biz_code': None,
            'biz_msg': None,
            'risk_level': 'SAFE',
            'evidence': ''
        }
        
        # 第一层：网络关
        if response.status_code != 200:
            result['evidence'] = f'HTTP Error: {response.status_code}'
            return result
        
        # 第二层：格式关
        try:
            data = response.json()
            result['biz_code'] = data.get('code')
            result['biz_msg'] = data.get('msg', '')
        except ValueError:
            result['evidence'] = 'Response is not valid JSON'
            return result
        
        # 第三层：业务逻辑判定
        if result['biz_code'] == 200:
            result['risk_level'] = 'PASS'
            result['evidence'] = 'Business logic success'
        else:
            result['risk_level'] = 'FAIL'
            result['evidence'] = f'Business logic failed: {result["biz_msg"]}'
        
        return result
    
    def run_baseline_tests(self) -> bool:
        """运行基准测试"""
        print("[INFO] 开始执行基准功能测试...")
        
        # 加载配置和API
        if not self.load_config():
            return False
        
        apis = self.load_apis()
        if not apis:
            return False
        
        self.setup_session()
        
        # 执行测试
        success_count = 0
        fail_count = 0
        error_count = 0
        
        for i, api in enumerate(apis, 1):
            print(f"\n[{i}/{len(apis)}] ", end='')
            result = self.test_api(api)
            self.results.append(result)
            
            if result['test_result'] == 'PASS':
                success_count += 1
                print(f"[PASS] {api['method']} {api['path']}")
            elif result['test_result'] == 'FAIL':
                fail_count += 1
                print(f"[FAIL] {api['method']} {api['path']}: {result.get('error', 'Unknown error')}")
            else:
                error_count += 1
                print(f"[ERROR] {api['method']} {api['path']}: {result.get('error', 'Unknown error')}")
            
            # 避免请求过快
            time.sleep(0.1)
        
        # 生成测试报告
        self.generate_report(success_count, fail_count, error_count)
        
        # 保存结果
        return self.save_results()
    
    def generate_report(self, success_count: int, fail_count: int, error_count: int):
        """生成测试报告"""
        total = success_count + fail_count + error_count
        print(f"\n{'='*60}")
        print("基准功能测试报告")
        print(f"{'='*60}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总接口数: {total}")
        print(f"通过数: {success_count} ({success_count/total*100:.1f}%)")
        print(f"失败数: {fail_count} ({fail_count/total*100:.1f}%)")
        print(f"错误数: {error_count} ({error_count/total*100:.1f}%)")
        print(f"{'='*60}")
    
    def save_results(self) -> bool:
        """保存测试结果"""
        try:
            output_file = os.path.join(self.work_dir, "results_baseline.json")
            
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
    print("[WARNING] 仅限授权测试！开始基准功能测试...")
    print("=" * 60)
    
    tester = BaselineAPITester()
    success = tester.run_baseline_tests()
    
    if success:
        print("\n[SUCCESS] 基准功能测试完成！")
        return True
    else:
        print("\n[ERROR] 基准功能测试失败！")
        return False

if __name__ == "__main__":
    main()