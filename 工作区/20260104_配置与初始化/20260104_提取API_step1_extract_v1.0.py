# -*- coding: utf-8 -*-
"""
后端 API 提取脚本 - Java Spring Boot
功能：静态分析源代码，提取 API 接口定义并生成 apis.json
"""

import os
import re
import json


def parse_dto_fields(class_name, source_root):
    """
    解析 Java DTO 实体类字段
    
    Args:
        class_name: 类名（如 SysUser）
        source_root: 源码根目录
    
    Returns:
        dict: 字段名到默认值的映射
    """
    fields = {}
    for root, dirs, files in os.walk(source_root):
        # 跳过不需要扫描的目录
        if 'target' in dirs:
            dirs.remove('target')
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if file == f"{class_name}.java":
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # 匹配 private/public/protected 类型的字段
                    # 排除 static、final、transient 字段
                    pattern = r'(?:private|public|protected)\s+static\s+(?:final\s+)?(\w+)\s+(\w+)\s*=;'
                    if not re.findall(pattern, content):
                        # 正常字段匹配
                        matches = re.findall(r'(?:private|public|protected)\s+([^\s]+)\s+(\w+)\s*;', content)
                        
                        for f_type, f_name in matches:
                            # 过滤注解字段
                            if f_type.startswith('@'):
                                continue
                            # 根据类型生成默认值
                            if f_type in ['String', 'char']:
                                fields[f_name] = "test_data"
                            elif f_type in ['Integer', 'int', 'Long', 'long', 'Short', 'short']:
                                fields[f_name] = 1
                            elif f_type in ['Boolean', 'boolean']:
                                fields[f_name] = False
                            elif f_type in ['Double', 'double', 'Float', 'float']:
                                fields[f_name] = 0.0
                            elif f_type in ['LocalDateTime', 'Date', 'Timestamp']:
                                fields[f_name] = "2026-01-04 00:00:00"
                            elif f_type in ['List', 'ArrayList']:
                                fields[f_name] = []
                            else:
                                fields[f_name] = f"{f_type}_value"
                    
                    return fields
                except Exception as e:
                    print(f"警告: 读取文件 {filepath} 失败: {str(e)}")
                    continue
    
    return {"unknown_field": "unknown_value"}


def extract_java_apis(source_root):
    """
    提取 Java Spring Boot 项目的 API 接口
    
    Args:
        source_root: 源码根目录
    
    Returns:
        list: API 接口列表
    """
    apis = []
    
    # 匹配 Controller 类级路径
    class_re = re.compile(r'@RequestMapping\(?["\']([^"\']*)["\']\)?')
    
    # 匹配方法级注解和参数
    # 捕获：(MethodType, MethodPath, ParameterString)
    method_re = re.compile(
        r'@(Get|Post|Put|Delete|Request)Mapping\(?["\']([^"\']*)["\']\)?.*?public.*?\((.*?)\)',
        re.DOTALL
    )
    
    controller_count = 0
    
    for root, dirs, files in os.walk(source_root):
        # 跳过不需要扫描的目录
        if 'target' in dirs:
            dirs.remove('target')
        if '.git' in dirs:
            dirs.remove('.git')
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
            
        for file in files:
            if not file.endswith(".java"):
                continue
            
            # 只扫描 Controller 类
            if "Controller" not in file and "controller" not in root.replace("\\", "/"):
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # A. 提取类级路径前缀
                class_matches = class_re.findall(content)
                base_path = class_matches[0].strip("/") if class_matches else ""
                
                controller_count += 1
                print(f"  正在扫描 Controller: {file}")
                
                # B. 提取方法级接口
                for m_type, m_path, m_params in method_re.findall(content):
                    # --- 修复 1: 路径拼接逻辑 ---
                    # 避免 "/monitor/server" + "/monitor/server" 的重复
                    clean_sub = m_path.strip("/")
                    
                    if not clean_sub:
                        full_path = f"/{base_path}"
                    else:
                        if base_path and not clean_sub.startswith(base_path.replace("/", "")):
                            # 检查是否包含类路径的前缀，避免重复拼接
                            if base_path in clean_sub:
                                full_path = f"/{clean_sub}"
                            else:
                                full_path = f"/{base_path}/{clean_sub}"
                        else:
                            full_path = f"/{clean_sub}"
                    
                    # 清理多余斜杠
                    full_path = full_path.replace("//", "/").replace("/+", "/")
                    
                    # --- 修复 2: 智能载荷生成 ---
                    payload = {}
                    content_type = "application/json"
                    
                    # 检查是否为文件上传接口
                    if "MultipartFile" in m_params or "file" in m_params.lower():
                        content_type = "multipart/form-data"
                        payload = {"file": "(binary_file_content)"}
                    
                    # 检查 @RequestBody 并尝试解析 DTO
                    m_type_upper = m_type.upper()
                    if "@RequestBody" in m_params and m_type_upper in ["POST", "PUT", "PATCH"]:
                        # 提取参数类型
                        param_match = re.search(r'@RequestBody\s+(\w+)', m_params)
                        if param_match:
                            dto_class = param_match.group(1)
                            print(f"    检测到 DTO: {dto_class}")
                            # 递归解析 DTO 字段
                            payload = parse_dto_fields(dto_class, source_root)
                        else:
                            payload = {"generic_param": "data"}
                    
                    # 检查 @RequestParam 参数
                    request_params = []
                    param_list = re.findall(r'@RequestParam\s*\([^)]*\)\s+(\w+)\s+(\w+)', m_params)
                    for p_type, p_name in param_list:
                        default_val = "test_data" if p_type == "String" else 1
                        request_params.append({
                            "name": p_name,
                            "type": p_type,
                            "required": True
                        })
                        payload[p_name] = default_val
                    
                    # 检查 @PathVariable 路径变量
                    path_vars = re.findall(r'@PathVariable\s*(?:\([^)]*\)\s+)?(\w+)\s+(\w+)', m_params)
                    for v_type, v_name in path_vars:
                        request_params.append({
                            "name": v_name,
                            "type": v_type,
                            "in": "path",
                            "required": True
                        })
                    
                    api_item = {
                        "path": full_path,
                        "method": m_type_upper,
                        "params": m_params.strip(),
                        "content_type": content_type,
                        "payload": payload
                    }
                    
                    if request_params:
                        api_item["parameters"] = request_params
                    
                    apis.append(api_item)
                    
            except Exception as e:
                print(f"警告: 处理文件 {filepath} 时出错: {str(e)}")
                continue
    
    print(f"\n共扫描 {controller_count} 个 Controller 类")
    return apis


def run_extraction(config_path):
    """
    统一调度器：根据配置执行 API 提取
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        tuple: (API列表, 工作目录)
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    src = config.get('source_path', '')
    lang = config.get('tech_stack', {}).get('language', '')
    work_dir = config.get('work_dir', '.')
    
    print("="*60)
    print("开始提取 API 接口")
    print("="*60)
    print(f"源码路径: {src}")
    print(f"技术栈语言: {lang}")
    print(f"工作目录: {work_dir}")
    print()
    
    # 语言路由
    raw_results = []
    if lang.lower() == "java":
        print("使用 Java 解析器...")
        raw_results = extract_java_apis(src)
    elif lang.lower() == "python":
        print("Python 解析器暂未实现")
        return [], work_dir
    else:
        print(f"不支持的编程语言: {lang}")
        return [], work_dir
    
    print()
    print(f"提取到 {len(raw_results)} 个 API 接口")
    
    # 去重处理：基于 Method + Path 唯一性
    unique_data = {f"{a['method']}{a['path']}": a for a in raw_results}.values()
    final_apis = list(unique_data)
    
    print(f"去重后剩余 {len(final_apis)} 个唯一接口")
    print("="*60)
    
    return final_apis, work_dir


def generate_swagger_doc(apis, work_dir):
    """
    生成 Swagger 风格的 API 文档
    
    Args:
        apis: API 列表
        work_dir: 工作目录
    """
    doc_path = os.path.join(work_dir, "Final_Report.md")
    
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write("# API 接口集成文档\n\n")
        f.write(f"> 源码静态分析结果\n\n")
        f.write(f"## 统计信息\n\n")
        f.write(f"- **接口总数**: {len(apis)}\n\n")
        
        # 按方法分组统计
        method_stats = {}
        for api in apis:
            method = api['method']
            method_stats[method] = method_stats.get(method, 0) + 1
        
        f.write(f"- **接口分布**:\n")
        for method, count in sorted(method_stats.items()):
            emoji = {"GET": "🔍", "POST": "➕", "PUT": "✏️", "DELETE": "🗑️"}.get(method, "📡")
            f.write(f"  - {emoji} {method}: {count} 个\n")
        
        f.write(f"\n## 接口列表\n\n")
        
        for api in apis:
            f.write(f"---\n### 📍 `{api['method']} {api['path']}`\n\n")
            f.write(f"- **方法**: `{api['method']}`\n")
            f.write(f"- **路径**: `{api['path']}`\n")
            f.write(f"- **Content-Type**: `{api['content_type']}`\n")
            
            if 'parameters' in api and api['parameters']:
                f.write(f"- **参数**:\n")
                for param in api['parameters']:
                    in_type = param.get('in', 'query')
                    f.write(f"  - `{param['name']}` ({param.get('type', 'String')}) - {in_type} - 必填\n")
            
            if api['payload']:
                f.write(f"- **请求体示例**:\n```json\n{json.dumps(api['payload'], indent=2, ensure_ascii=False)}\n```\n")
            
            f.write("\n")
    
    print(f"Swagger 文档已生成: {doc_path}")


if __name__ == "__main__":
    try:
        # 配置文件路径
        config_path = "d:\\desktop\\AI Coding\\costrict-Auto-test-Tool\\project_config.json"
        
        # 1. 执行提取逻辑
        final_apis, work_dir = run_extraction(config_path)
        
        if not final_apis:
            print("未提取到任何 API 接口，程序退出")
            exit(0)
        
        # 2. 写入 apis.json (供后续任务使用)
        apis_path = os.path.join(work_dir, "apis.json")
        with open(apis_path, 'w', encoding='utf-8') as f:
            json.dump(final_apis, f, indent=2, ensure_ascii=False)
        
        print(f"API 数据已保存: {apis_path}")
        
        # 3. 生成 Swagger 风格文档
        generate_swagger_doc(final_apis, work_dir)
        
        print("\n" + "="*60)
        print("API 提取任务完成")
        print("="*60)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()