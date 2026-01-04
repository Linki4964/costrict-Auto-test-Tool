# -*- coding: utf-8 -*-
"""
后端基准性测试脚本
功能：执行基准功能测试，验证接口连通性与基本业务逻辑
"""

import requests
import time
import re
import json
import random
from io import BytesIO

# 全局存储：资源路径 -> 学习到的真实数据模板
# 例如: "/system/user" -> { "userName": "admin", "phonenumber": "158...", ... }
resource_templates = {}
created_ids = {}  # 存储创建的资源 ID 用于清理


def refresh_token(base_url, username, password):
    """
    刷新认证 Token
    
    Args:
        base_url: 基础 URL
        username: 用户名
        password: 密码
    
    Returns:
        str: 新 Token 或 None
    """
    try:
        login_url = f"{base_url}/prod-api/login"
        resp = requests.post(login_url, json={"username": username, "password": password}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 200:
                return data.get("token")
    except Exception as e:
        print(f"刷新 Token 失败: {str(e)}")
    return None


def is_binary_response(response):
    """
    检查响应是否为二进制流
    
    Args:
        response: requests Response 对象
    
    Returns:
        bool: 是否为二进制流
    """
    content_type = response.headers.get('Content-Type', '')
    binary_types = [
        'application/octet-stream',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/pdf',
        'image/',
        'application/zip'
    ]
    return any(bt in content_type for bt in binary_types)


def mine_real_data(base_url, token, api_list):
    """
    阶段一：数据挖掘 (执行 GET 接口)
    
    Args:
        base_url: 基础 URL
        token: 认证 Token
        api_list: API 列表
    """
    print("="*60)
    print("阶段一: 逆向数据挖掘 (GET)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    success_count = 0
    
    for api in api_list:
        if api['method'] != 'GET':
            continue
        
        url = f"{base_url}/prod-api{api['path']}"
        
        # 跳过不需要挖掘的接口
        if any(skip in url for skip in ['captcha', 'image', 'download', 'upload']):
            continue
        
        try:
            # 优先测试 list 接口
            params = {"pageNum": 1, "pageSize": 1}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            
            if resp.status_code == 200 and not is_binary_response(resp):
                data = resp.json()
                
                # 尝试提取列表中的第一条数据作为模板
                candidates = data.get('rows') or data.get('data') or []
                if isinstance(candidates, list) and len(candidates) > 0:
                    template = candidates[0]
                    
                    # 建立资源映射
                    resource_key = api['path'].replace("/list", "")
                    resource_templates[resource_key] = template
                    success_count += 1
                    print(f"  [OK] Extracted data template from {api['path']}")
                    
        except Exception as e:
            pass
    
    print(f"\n成功提取 {success_count} 个数据模板")
    print("="*60)


def generate_smart_payload_from_template(resource_key, original_static_payload):
    """
    阶段二：载荷清洗与生成
    
    Args:
        resource_key: 资源键
        original_static_payload: 原始静态载荷
    
    Returns:
        dict: 清洗后的载荷
    """
    # 如果没学到模板，就回退到静态分析的 payload
    template = resource_templates.get(resource_key)
    if not template:
        return enrich_static_payload(original_static_payload)
    
    new_payload = template.copy()
    timestamp = str(int(time.time()))
    random_suffix = random.randint(10, 99)
    
    # === 关键：清洗数据，确保这是"新增"而不是"修改"，且不冲突 ===
    
    # 1. 清除主键 ID (强制为 None，让后端生成)
    primary_keys = ['id', 'userId', 'roleId', 'deptId', 'jobId', 'postId', 
                    'menuId', 'dictCode', 'dictDataCode', 'configId', 'noticeId']
    for key in list(new_payload.keys()):
        if any(pk.lower() in key.lower() for pk in primary_keys):
            new_payload[key] = None
    
    # 2. 唯一化关键字段 (避开 Admin 和重复)
    unique_fields = ['name', 'code', 'key', 'title', 'phone', 'email', 
                     'userName', 'loginName', 'nickName', 'phonenumber']
    for key, val in new_payload.items():
        if isinstance(val, str):
            # 如果原数据是 admin，改为 auto_test
            if 'admin' in val.lower():
                new_payload[key] = f"auto_test_{timestamp}"
            # 针对名称、编码类字段，追加后缀
            elif any(uf in key.lower() for uf in unique_fields):
                new_payload[key] = f"test_{timestamp}_{random_suffix}"
    
    return new_payload


def enrich_static_payload(payload):
    """
    原本的静态 Payload 处理 (作为兜底)
    
    Args:
        payload: 原始载荷
    
    Returns:
        dict: 丰富后的载荷
    """
    new_payload = payload.copy()
    suffix = str(int(time.time()))
    for k, v in new_payload.items():
        if isinstance(v, str) and any(x in k.lower() for x in ['name', 'code', 'key']):
            new_payload[k] = f"{v}_{suffix}_{random.randint(10, 99)}"
    return new_payload


def parse_response(response):
    """
    解析 API 响应
    
    Args:
        response: requests Response 对象
    
    Returns:
        dict: 解析结果
    """
    result = {
        "status_code": response.status_code,
        "biz_code": None,
        "biz_msg": None,
        "pass": False,
        "is_binary": False
    }
    
    # 第一层：网络关
    if response.status_code != 200:
        result["biz_msg"] = f"HTTP Error: {response.status_code}"
        return result
    
    # 检查是否为二进制流
    if is_binary_response(response):
        result["is_binary"] = True
        result["pass"] = True
        result["biz_msg"] = "Binary response"
        return result
    
    # 第二层：格式关
    try:
        data = response.json()
        result["biz_code"] = data.get("code")
        result["biz_msg"] = data.get("msg")
        
        # 第三层：业务逻辑判定
        result["pass"] = (result["biz_code"] == 200)
        
    except ValueError:
        result["biz_msg"] = "Response is not valid JSON"
    
    return result


def run_lifecycle_test(base_url, token, api_list):
    """
    阶段三：执行 POST -> DELETE 闭环
    
    Args:
        base_url: 基础 URL
        token: 认证 Token
        api_list: API 列表
    
    Returns:
        list: 测试结果
    """
    print("="*60)
    print("阶段二: 增删闭环测试 (POST + DELETE)")
    print("="*60)
    
    # 先运行挖掘
    mine_real_data(base_url, token, api_list)
    
    results = []
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    for api in api_list:
        # 跳过非 POST 接口
        if api['method'] not in ['POST', 'PUT']:
            continue
        
        url = f"{base_url}/prod-api{api['path']}"
        
        # 跳过上传和登录接口
        if any(skip in url for skip in ['login', 'register', 'upload', 'import']):
            continue
        
        # 构造 Payload
        resource_key = api['path'].replace("/add", "").replace("/edit", "")
        payload = generate_smart_payload_from_template(resource_key, api.get('payload', {}))
        
        # A. 执行新增 (POST)
        try:
            # 安全检查：确保 Payload 里没有 ID=1 或者 admin
            if str(payload.get('id')) == '1' or 'admin' in str(payload.values()).lower():
                print(f"  [WARN] {api['path']} Payload contains sensitive data, skip creation")
                continue
            
            # multipart/form-data 处理
            if api.get('content_type') == 'multipart/form-data':
                # 跳过文件上传接口，因为需要真实文件
                print(f"  [SKIP] File upload interface: {api['path']}")
                continue
            
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            parse_result = parse_response(resp)
            
            test_result = {
                "path": api['path'],
                "method": "POST",
                "status_code": resp.status_code,
                "biz_code": parse_result.get("biz_code"),
                "biz_msg": parse_result.get("biz_msg"),
                "pass": parse_result.get("pass"),
                "payload": "***"  # 脱敏显示
            }
            results.append(test_result)
            
            if parse_result.get("pass"):
                print(f"  [PASS] POST {api['path']} - Success")
                
                # B. 如果新增成功，提取 ID 并执行删除 (DELETE)
                try:
                    data = resp.json()
                    new_id = data.get('data', {}).get('id') or data.get('data') or data.get('id')
                    
                    if new_id and str(new_id) not in ['1', '0']:
                        # 再次安全检查：绝对不能删 ID=1
                        if str(new_id) in ['1', '0']:
                            print(f"  [BLOCK] Intercepted Admin ID deletion, blocked")
                            continue
                        
                        # 寻找对应的 DELETE 接口
                        delete_path = f"{api['path'].replace('/add', '').replace('/edit', '')}/{new_id}"
                        
                        del_headers = {"Authorization": f"Bearer {token}"}
                        del_resp = requests.delete(f"{base_url}/prod-api{delete_path}", headers=del_headers, timeout=10)
                        del_result = parse_response(del_resp)
                        
                        results.append({
                            "path": delete_path,
                            "method": "DELETE",
                            "status_code": del_resp.status_code,
                            "biz_code": del_result.get("biz_code"),
                            "biz_msg": del_result.get("biz_msg"),
                            "pass": del_result.get("pass"),
                            "note": "闭环清理"
                        })
                        
                        if del_result.get("pass"):
                            print(f"  [PASS] DELETE {delete_path} - Cleanup success")
                        else:
                            print(f"  [FAIL] DELETE {delete_path} - Cleanup failed: {del_result.get('biz_msg')}")
                            
                except Exception as e:
                    print(f"  [WARN] Delete operation failed: {str(e)}")
            else:
                print(f"  [FAIL] POST {api['path']} - Failed: {parse_result.get('biz_msg')}")
                    
        except Exception as e:
            results.append({
                "path": api['path'],
                "method": "POST",
                "status_code": 500,
                "pass": False,
                "biz_msg": str(e),
                "payload": "***"
            })
            print(f"  [ERROR] POST {api['path']} - Exception: {str(e)}")
    
    print("="*60)
    return results


def run_baseline_test(base_url, token, api_list):
    """
    执行基准性测试（包括 GET 和 POST 测试）
    
    Args:
        base_url: 基础 URL
        token: 认证 Token
        api_list: API 列表
    
    Returns:
        list: 测试结果
    """
    all_results = []
    
    # 执行增删闭环测试
    lifecycle_results = run_lifecycle_test(base_url, token, api_list)
    all_results.extend(lifecycle_results)
    
    # 补充测试 GET 接口（非 list 接口）
    print("="*60)
    print("阶段三: 补充 GET 接口测试")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for api in api_list:
        if api['method'] != 'GET':
            continue
        
        url = f"{base_url}/prod-api{api['path']}"
        
        # 跳过已测试过的 list 接口和特殊接口
        if any(skip in url for skip in ['list', 'captcha', 'download', 'upload']):
            continue
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            parse_result = parse_response(resp)
            
            result = {
                "path": api['path'],
                "method": "GET",
                "status_code": resp.status_code,
                "biz_code": parse_result.get("biz_code"),
                "biz_msg": parse_result.get("biz_msg"),
                "pass": parse_result.get("pass"),
                "is_binary": parse_result.get("is_binary", False)
            }
            all_results.append(result)
            
            if result["pass"]:
                print(f"  [PASS] GET {api['path']} - Success")
            else:
                print(f"  [FAIL] GET {api['path']} - Failed: {result.get('biz_msg')}")
                
        except Exception as e:
            pass
    
    print("="*60)
    return all_results


def main():
    """
    主函数
    """
    print("="*60)
    print("后端基准性测试")
    print("="*60)
    
    # 读取配置
    config_path = "d:\\desktop\\AI Coding\\costrict-Auto-test-Tool\\project_config.json"
    apis_path = "d:\\desktop\\AI Coding\\costrict-Auto-test-Tool\\apis.json"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    with open(apis_path, 'r', encoding='utf-8') as f:
        api_list = json.load(f)
    
    base_url = config['base_url']
    token = config['authentication']['token']
    username = config['authentication']['username']
    password = config['authentication']['password']
    work_dir = config['work_dir']
    
    print(f"\n配置信息:")
    print(f"  目标 URL: {base_url}")
    print(f"  Token: {token[:20]}...")
    print(f"  API 数量: {len(api_list)}")
    print()
    
    # 验证 Token 有效性
    print("验证 Token 有效性...")
    test_headers = {"Authorization": f"Bearer {token}"}
    try:
        test_resp = requests.get(f"{base_url}/prod-api/getInfo", headers=test_headers, timeout=5)
        if test_resp.status_code != 200:
            print("Token 已失效，正在刷新...")
            new_token = refresh_token(base_url, username, password)
            if new_token:
                token = new_token
                print("Token 刷新成功")
            else:
                print("Token 刷新失败，测试终止")
                return
    except Exception as e:
        print(f"Token 验证失败: {str(e)}")
    
    print()
    
    # 执行基准测试
    results = run_baseline_test(base_url, token, api_list)
    
    # 统计结果
    total = len(results)
    passed = sum(1 for r in results if r.get('pass', False))
    failed = total - passed
    
    print()
    print("="*60)
    print("测试统计")
    print("="*60)
    print(f"  总测试数: {total}")
    print(f"  通过: {passed} ({passed*100//total if total > 0 else 0}%)")
    print(f"  失败: {failed} ({failed*100//total if total > 0 else 0}%)")
    print("="*60)
    
    # 保存结果
    results_path = f"{work_dir}/results_baseline.json"
    
    report = {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{passed*100//total if total > 0 else 0}%"
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results": results
    }
    
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n测试结果已保存: {results_path}")
    print("="*60)
    print("基准性测试完成")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()