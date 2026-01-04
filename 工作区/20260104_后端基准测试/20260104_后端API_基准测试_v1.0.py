# -*- coding: utf-8 -*-
import requests
import json
import time
import re
import os

def enrich_payload(payload):
    """动态唯一化 Payload - 解决重复键冲突"""
    new_payload = payload.copy()
    suffix = str(int(time.time()))
    
    for k, v in new_payload.items():
        # 对 name, code, key, title 等关键字段追加时间戳
        if isinstance(v, str) and any(x in k.lower() for x in ['name', 'code', 'key', 'title']):
            # 如果值已经是 test_data 或 placeholder，则替换
            if v in ['test_data', 'placeholder'] or v.startswith('placeholder_'):
                new_payload[k] = f"test_{k}_{suffix}"
            else:
                new_payload[k] = f"{v}_{suffix}"
    
    return new_payload

def is_protected_resource(url, method, payload=None):
    """管理员保护盾 - 拦截针对敏感ID的破坏性操作"""
    if method in ['DELETE', 'PUT']:
        # 检查 URL 结尾是否包含敏感 ID
        if re.search(r'/(1|0|admin|system)$', url):
            return True
        # 检查 URL 路径中是否包含 /1/ 或 /0/
        if re.search(r'/[10](/|$|\\?)', url):
            return True
        # 检查 Payload 是否包含敏感关键词
        if payload:
            payload_str = str(payload).lower()
            if 'admin' in payload_str and any(x in payload_str for x in ['delete', 'remove', 'id']):
                return True
    return False

def parse_response(resp):
    """解析响应并统一格式"""
    result = {
        "http_code": resp.status_code,
        "biz_code": None,
        "biz_msg": "",
        "data": None,
        "is_binary": False,
        "error": None
    }
    
    # 检查是否为二进制流
    content_type = resp.headers.get('Content-Type', '').lower()
    binary_types = ['stream', 'excel', 'pdf', 'image', 'octet', 'download']
    
    if any(t in content_type for t in binary_types):
        result['is_binary'] = True
        result['biz_code'] = 200
        result['biz_msg'] = "Binary/Stream Response"
        return result
    
    # 解析 JSON 响应
    try:
        json_data = resp.json()
        result['biz_code'] = json_data.get('code', 0)
        result['biz_msg'] = json_data.get('msg', '')
        result['data'] = json_data.get('data')
    except:
        result['error'] = "Failed to parse JSON response"
    
    return result

def run_lifecycle_test(base_url, token, api_config):
    """执行单次生命周期测试"""
    # 规范化 base_url - 移除尾部斜杠
    clean_base_url = base_url.rstrip('/')
    
    # 规范化 path - 确保以斜杠开头
    path = api_config['path']
    if not path.startswith('/'):
        path = '/' + path
    
    # 拼接完整 URL - 插入 /prod-api 前缀（若依框架标准路径）
    if '/prod-api' not in clean_base_url and not path.startswith('/prod-api'):
        full_url = f"{clean_base_url}/prod-api{path}"
    else:
        full_url = f"{clean_base_url}{path}"
    
    url = full_url
    method = api_config['method']
    
    # 构造请求头
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 准备 Payload
    payload = api_config.get('smart_payload', {})
    
    # A. 针对 POST 请求：动态唯一化
    if method == 'POST' and api_config.get('content_type') == 'application/json':
        final_payload = enrich_payload(payload)
    else:
        final_payload = payload
    
    # B. 针对 DELETE/PUT 请求：管理员保护
    if is_protected_resource(url, method, final_payload):
        return {
            "method": method,
            "path": api_config['path'],
            "url": url,
            "status": "SKIPPED_SAFE",
            "message": "触发管理员保护盾",
            "http_code": 999,
            "biz_code": 999,
            "biz_msg": "Admin Shield: Protected resource"
        }
    
    # C. 发送请求 (含 Upload/Download 自适应)
    try:
        # 处理 multipart/form-data 文件上传
        if api_config.get('content_type') == 'multipart/form-data':
            files = {
                'file': ('test_file.txt', b'AI Automated Test Content - ' + str(time.time()).encode(), 'text/plain')
            }
            resp = requests.request(method, url, headers=headers, files=files, timeout=10)
        else:
            # 处理 application/json
            headers['Content-Type'] = 'application/json'
            resp = requests.request(method, url, headers=headers, json=final_payload, timeout=10)
        
        # D. 解析响应
        parsed_result = parse_response(resp)
        
        # E. 生命周期闭环 - 记录创建的 ID
        created_id = None
        if method == 'POST' and parsed_result['http_code'] == 200:
            if not parsed_result['is_binary'] and parsed_result['biz_code'] == 200:
                data = parsed_result.get('data', {})
                if isinstance(data, dict):
                    created_id = data.get('id') or data.get('userId') or data.get('dataId')
                elif isinstance(data, (int, str)):
                    created_id = data
        
        # 判定测试结果
        status = "PASS"
        if parsed_result['http_code'] == 200:
            if parsed_result['is_binary']:
                status = "PASS"  # 二进制流直接通过
            elif parsed_result['biz_code'] == 200:
                status = "PASS"  # 业务成功
            elif parsed_result['biz_code'] in [401, 403]:
                status = "AUTH_FAIL"
            else:
                status = "BIZ_FAIL"
        else:
            status = "HTTP_FAIL"
        
        result = {
            "method": method,
            "path": api_config['path'],
            "name": api_config.get('name', 'unknown'),
            "url": url.replace('//', '/'),  # 修复显示中的双斜杠
            "status": status,
            "http_code": parsed_result['http_code'],
            "biz_code": parsed_result['biz_code'],
            "biz_msg": parsed_result['biz_msg'],
            "created_id": created_id,
            "is_binary": parsed_result['is_binary'],
            "content_type": api_config.get('content_type', 'application/json')
        }
        
        if created_id:
            result['message'] = f"CREATED_ID: {created_id}"
        
        if parsed_result['error']:
            result['error'] = parsed_result['error']
        
        return result
        
    except requests.exceptions.Timeout:
        return {
            "method": method,
            "path": api_config['path'],
            "url": url,
            "status": "TIMEOUT",
            "http_code": 0,
            "biz_code": 0,
            "biz_msg": "Request timeout",
            "message": "请求超时"
        }
    except requests.exceptions.ConnectionError:
        return {
            "method": method,
            "path": api_config['path'],
            "url": url,
            "status": "CONN_ERROR",
            "http_code": 0,
            "biz_code": 0,
            "biz_msg": "Connection failed",
            "message": "连接失败"
        }
    except Exception as e:
        return {
            "method": method,
            "path": api_config['path'],
            "url": url,
            "status": "ERROR",
            "http_code": 0,
            "biz_code": 0,
            "biz_msg": str(e),
            "message": f"请求异常: {str(e)}"
        }

def run_baseline_test():
    """执行基准性测试主流程"""
    print("[START] 开始执行后端基准性测试...")
    
    # 读取配置
    config_path = "project_config.json"
    if not os.path.exists(config_path):
        print(f"[ERROR] 配置文件不存在: {config_path}")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    base_url = config['auth']['base_url']
    token = config['auth']['auth_token']
    work_dir = config['workspace']['work_dir']
    username = config['auth']['username']
    password = config['auth']['password']
    
    # 读取 API 列表
    apis_json_path = os.path.join(work_dir, "apis.json")
    if not os.path.exists(apis_json_path):
        print(f"[ERROR] API文件不存在: {apis_json_path}")
        return
    
    with open(apis_json_path, 'r', encoding='utf-8') as f:
        apis = json.load(f)
    
    print(f"[INFO] 目标URL: {base_url}")
    print(f"[INFO] 测试接口数: {len(apis)}")
    
    # 执行测试
    results = []
    created_ids = {}  # 记录创建的资源 ID，用于后续清理测试
    
    for i, api in enumerate(apis, 1):
        print(f"[{i}/{len(apis)}] 测试 {api['method']} {api['path']}...")
        
        result = run_lifecycle_test(base_url, token, api)
        results.append(result)
        
        # 记录创建的资源
        if result.get('status') == 'PASS' and result.get('created_id'):
            resource_key = f"{result['path'].split('/')[-1]}"
            created_ids[resource_key] = result['created_id']
            print(f"  -> 记录创建的资源ID: {result['created_id']}")
        
        status_symbol = {
            'PASS': '[OK]',
            'SKIPPED_SAFE': '[SKIP]',
            'AUTH_FAIL': '[AUTH]',
            'BIZ_FAIL': '[FAIL]',
            'HTTP_FAIL': '[FAIL]',
            'TIMEOUT': '[TIME]',
            'CONN_ERROR': '[CONN]',
            'ERROR': '[ERROR]'
        }.get(result['status'], '[?]')
        
        print(f"  -> {status_symbol} {result['status']} | HTTP: {result['http_code']} | BIZ: {result['biz_code']} | {result['biz_msg']}")
    
    # 统计结果
    stats = {
        'total': len(results),
        'pass': sum(1 for r in results if r['status'] == 'PASS'),
        'skipped': sum(1 for r in results if r['status'] == 'SKIPPED_SAFE'),
        'auth_fail': sum(1 for r in results if r['status'] == 'AUTH_FAIL'),
        'biz_fail': sum(1 for r in results if r['status'] in ['BIZ_FAIL', 'HTTP_FAIL']),
        'error': sum(1 for r in results if r['status'] in ['TIMEOUT', 'CONN_ERROR', 'ERROR'])
    }
    
    print("\n" + "=" * 60)
    print("[SUMMARY] 测试结果统计")
    print("=" * 60)
    print(f"总计:      {stats['total']} 个测试")
    print(f"通过:      {stats['pass']} 个")
    print(f"跳过:      {stats['skipped']} 个 (受保护)")
    print(f"失败:      {stats['biz_fail']} 个")
    print(f"认证失败:  {stats['auth_fail']} 个")
    print(f"其他错误:  {stats['error']} 个")
    print(f"成功率:    {stats['pass']/stats['total']*100:.1f}%")
    
    # 保存结果
    result_data = {
        "test_type": "Baseline Test",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "base_url": base_url,
        "config": {
            "username": username,
            "password": "***REDACTED***"
        },
        "statistics": stats,
        "created_resources": created_ids,
        "results": results
    }
    
    output_path = os.path.join(work_dir, "results_baseline.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SUCCESS] 测试结果已保存至: {output_path}")

if __name__ == "__main__":
    run_baseline_test()