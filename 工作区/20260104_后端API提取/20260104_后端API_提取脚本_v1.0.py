# -*- coding: utf-8 -*-
import os
import re
import json

def parse_dto_fields(class_name, source_root):
    """解析Java DTO实体类字段生成智能Payload"""
    fields = {}
    
    # 标准化类名，移除包路径前缀
    clean_name = class_name.split('.')[-1]
    
    for root, _, files in os.walk(source_root):
        for file in files:
            if file == f"{clean_name}.java":
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # 匹配 private 字段，排除 static final 常量
                    matches = re.findall(r'\b(?:public|protected|private)\s+(?:static\s+)?(?:final\s+)?(\w+)\s+(\w+)\s*;', content)
                    
                    for f_type, f_name in matches:
                        # 根据类型生成默认值
                        if f_type in ['String']:
                            fields[f_name] = "test_data"
                        elif f_type in ['Integer', 'int', 'Long', 'long']:
                            fields[f_name] = 1
                        elif f_type in ['Boolean', 'boolean']:
                            fields[f_name] = False
                        elif f_type in ['Double', 'double', 'Float', 'float']:
                            fields[f_name] = 1.5
                        elif f_type in ['Date']:
                            fields[f_name] = "2026-01-04 12:00:00"
                        else:
                            fields[f_name] = f"placeholder_{f_name}"
                    
                    print(f"[DEBUG] 解析DTO {clean_name}: 找到 {len(fields)} 个字段")
                    return fields
                    
                except Exception as e:
                    print(f"[WARN] 读取 {file_path} 失败: {str(e)}")
                    continue
    
    print(f"[WARN] 未找到DTO定义: {clean_name}")
    return {"unknown_field": "placeholder"}

def extract_java_apis(source_root):
    """提取Java Spring Boot Controller中的API接口"""
    apis = []
    
    # 匹配类级别的RequestMapping
    class_re = re.compile(r'@RequestMapping\s*\(\s*["\']([^"\']*)["\']')
    
    # 匹配方法级别的Mapping及签名
    # 支持多行匹配方法签名
    method_re = re.compile(
        r'@(Get|Post|Put|Delete|Patch)Mapping\s*\(\s*["\']?([^"\'\)]*)["\']?\s*\)\s*'
        r'(?:(?:public|protected|private)\s+)?(?:static\s+)?\w+\s+(?:<[^>]+>\s+)?(\w+)\s*\(([^)]*)\)',
        re.MULTILINE
    )
    
    for root, _, files in os.walk(source_root):
        for file in files:
            if not file.endswith(".java") or "Controller" not in file:
                continue
            
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 提取类路径前缀
                class_matches = class_re.findall(content)
                base_path = class_matches[0].strip("/") if class_matches else ""
                
                # 提取方法级接口
                for m_type, m_path, method_name, m_params in method_re.findall(content):
                    # 智能路径拼接 - 避免重复
                    clean_sub = m_path.strip("/")
                    if not clean_sub:
                        full_path = f"/{base_path}" if base_path else "/"
                    else:
                        if base_path:
                            # 检查是否是完整路径
                            if clean_sub.startswith(base_path):
                                full_path = f"/{clean_sub}"
                            else:
                                full_path = f"/{base_path}/{clean_sub}"
                        else:
                            full_path = f"/{clean_sub}"
                    
                    # 清理斜杠
                    full_path = full_path.replace("//", "/")
                    if not full_path.startswith("/"):
                        full_path = "/" + full_path
                    
                    # 智能载荷生成
                    payload = {}
                    content_type = "application/json"
                    http_method = m_type.upper()
                    
                    # 检查是否为文件上传接口
                    if "MultipartFile" in m_params:
                        content_type = "multipart/form-data"
                        payload = {"file": "(binary_file_content)"}
                    
                    # 检查 @RequestBody 并解析 DTO
                    elif "@RequestBody" in m_params and http_method in ["POST", "PUT", "PATCH"]:
                        param_match = re.search(r'@RequestBody\s+(?:[\w<>]+\s+)?(\w+)', m_params)
                        if param_match:
                            dto_class = param_match.group(1)
                            payload = parse_dto_fields(dto_class, source_root)
                        else:
                            payload = {"data": "placeholder"}
                    
                    # 检查 @PathVariable 和 @RequestParam
                    elif "@PathVariable" in m_params or "@RequestParam" in m_params:
                        params = re.findall(r'@(PathVariable|RequestParam)\s*(?:\([^)]+\))?\s*([\w<>]+\s+)?(\w+)', m_params)
                        if params:
                            for prefix, p_type, p_name in params:
                                if prefix == "PathVariable":
                                    full_path = full_path.replace(f"{{{p_name}}}", "1")
                                else:
                                    payload[p_name] = "test_value"
                    
                    apis.append({
                        "path": full_path,
                        "method": http_method,
                        "name": method_name,
                        "params": m_params.strip(),
                        "content_type": content_type,
                        "smart_payload": payload
                    })
                    
            except Exception as e:
                print(f"[WARN] 解析 {file_path} 失败: {str(e)}")
                continue
    
    return apis

def run_extraction(config_path):
    """执行API提取流程"""
    print("[START] 开始执行API提取...")
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    src = config['source_analysis']['source_path']
    lang = config['source_analysis']['tech_stack']['language']
    work_dir = config['workspace']['work_dir']
    
    print(f"[INFO] 源码路径: {src}")
    print(f"[INFO] 技术栈: {lang}")
    print(f"[INFO] 工作目录: {work_dir}")
    
    # 语言路由
    raw_results = []
    if lang.lower() == "java":
        print("[INFO] 使用Java解析器...")
        raw_results = extract_java_apis(src)
    else:
        print(f"[ERROR] 不支持的语言: {lang}")
        return [], work_dir
    
    # 去重处理（基于 Method + Path）
    unique_keys = {}
    for api in raw_results:
        key = f"{api['method']}:{api['path']}"
        if key not in unique_keys:
            unique_keys[key] = api
        else:
            # 保留有payload的版本
            if api['smart_payload'] and not unique_keys[key]['smart_payload']:
                unique_keys[key] = api
    
    final_apis = list(unique_keys.values())
    
    print(f"[SUCCESS] 提取完成，共找到 {len(final_apis)} 个唯一接口（原始 {len(raw_results)} 个）")
    
    return final_apis, work_dir

if __name__ == "__main__":
    try:
        config_path = "project_config.json"
        
        if not os.path.exists(config_path):
            print(f"[ERROR] 配置文件不存在: {config_path}")
            exit(1)
        
        # 1. 执行提取逻辑
        final_apis, work_dir = run_extraction(config_path)
        
        # 2. 写入 apis.json
        os.makedirs(work_dir, exist_ok=True)
        api_json_path = os.path.join(work_dir, "apis.json")
        with open(api_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_apis, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] 已生成 {len(final_apis)} 条接口记录至 {api_json_path}")
        
        # 3. 生成 Final_Report.md (Swagger 风格文档)
        report_path = os.path.join(work_dir, "Final_Report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# API Interface Documentation\n\n")
            f.write(f"> **API Count: {len(final_apis)}**\n\n")
            f.write(f"> **Generated Time: 2026-01-04**\n\n")
            f.write("---\n\n")
            
            # 按HTTP方法分组统计
            method_stats = {}
            for api in final_apis:
                method = api['method']
                method_stats[method] = method_stats.get(method, 0) + 1
            
            f.write("## Statistics\n\n")
            for method, count in sorted(method_stats.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{method}**: {count}\n")
            f.write("\n---\n\n")
            
            # 详细接口列表
            f.write("## API Details\n\n")
            
            for idx, api in enumerate(final_apis, 1):
                f.write(f"### {idx}. {api['method']} `{api['path']}`\n\n")
                f.write(f"**Method Name**: `{api['name']}`\n\n")
                f.write(f"**Content-Type**: `{api['content_type']}`\n\n")
                
                if api['params']:
                    f.write(f"**Parameters**:\n```java\n{api['params']}\n```\n\n")
                
                if api['smart_payload']:
                    f.write(f"**Smart Payload**:\n```json\n{json.dumps(api['smart_payload'], indent=2)}\n```\n\n")
                
                f.write("---\n\n")
        
        print(f"[SUCCESS] 已生成接口文档至 {report_path}")
        
    except Exception as e:
        print(f"[ERROR] 运行出错: {str(e)}")
        import traceback
        traceback.print_exc()