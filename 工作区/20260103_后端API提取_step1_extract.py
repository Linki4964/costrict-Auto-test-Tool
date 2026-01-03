import os
import re
import json
import requests
from pathlib import Path

class JavaAPIExtractor:
    def __init__(self, source_root, config_path=None):
        self.source_root = source_root
        self.config_path = config_path or "project_config.json"
        self.work_dir = os.path.dirname(os.path.abspath(config_path)) if config_path else "."
        
    def extract_java_apis(self):
        """从Java源码中提取API接口定义"""
        apis = []
        
        # 正则表达式模式
        class_mapping_re = re.compile(r'@RequestMapping\s*\(\s*"([^"]*)"\s*\)|@RequestMapping\s*\(\s*value\s*=\s*"([^"]*)"\s*\)')
        method_mapping_re = re.compile(r'@(\w+Mapping)\s*\(\s*"([^"]*)"\s*\)|@(\w+Mapping)\s*\(\s*value\s*=\s*"([^"]*)"\s*\)')
        rest_controller_re = re.compile(r'@RestController|@Controller')
        
        for root, dirs, files in os.walk(self.source_root):
            for file in files:
                if not file.endswith(".java"):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # 检查是否为Controller类
                    if not rest_controller_re.search(content):
                        continue
                        
                    # 提取类级别的RequestMapping
                    class_base_path = ""
                    class_matches = class_mapping_re.findall(content)
                    if class_matches:
                        # 取第一个非空的匹配项
                        class_base_path = next((match[0] or match[1] for match in class_matches if any(match)), "")
                        class_base_path = class_base_path.strip("/")
                    
                    # 提取方法级别的映射
                    method_matches = method_mapping_re.findall(content)
                    for match in method_matches:
                        # match格式：(完整匹配, mapping类型, 路径) 或 (mapping类型, 路径, 空, 空)
                        if match[1]:  # 第一种格式
                            mapping_type = match[0].replace("Mapping", "").upper()
                            path = match[1]
                        elif match[3]:  # 第二种格式
                            mapping_type = match[2].replace("Mapping", "").upper()
                            path = match[3]
                        else:
                            continue
                            
                        # 构建完整路径
                        full_path = self._build_full_path(class_base_path, path)
                        
                        # 提取路径参数
                        path_params = self._extract_path_params(path)
                        
                        # 构建API定义
                        api_def = {
                            "path": full_path,
                            "method": mapping_type,
                            "file": file_path.replace(self.source_root, "").lstrip("\\"),
                            "params": path_params,
                            "payload": self._generate_payload_example(mapping_type)
                        }
                        
                        apis.append(api_def)
                        
                except Exception as e:
                    print(f"[ERROR] 处理文件 {file_path} 时出错: {str(e)}")
                    continue
        
        return apis
    
    def _build_full_path(self, class_base, method_path):
        """构建完整的API路径"""
        class_base = class_base.strip("/")
        method_path = method_path.strip("/")
        
        if class_base and method_path:
            return f"/{class_base}/{method_path}".replace("//", "/")
        elif class_base:
            return f"/{class_base}"
        elif method_path:
            return f"/{method_path}"
        else:
            return "/"
    
    def _extract_path_params(self, path):
        """提取路径参数"""
        params = []
        # 匹配 {paramName} 格式的路径参数
        param_matches = re.findall(r'\{([^}]+)\}', path)
        for param in param_matches:
            params.append({
                "name": param,
                "in": "path",
                "required": True,
                "type": "string"
            })
        return params
    
    def _generate_payload_example(self, method):
        """为POST/PUT方法生成请求体示例"""
        if method in ["POST", "PUT"]:
            return {
                "example": {
                    "field1": "string",
                    "field2": 123,
                    "field3": True
                }
            }
        return None
    
    def run_extraction(self):
        """执行API提取并返回结果"""
        print(f"[INFO] 开始分析Java源码目录: {self.source_root}")
        
        # 提取API
        apis = self.extract_java_apis()
        
        # 去重处理：基于 Method + Path
        unique_apis = {}
        for api in apis:
            key = f"{api['method']}:{api['path']}"
            if key not in unique_apis:
                unique_apis[key] = api
        
        final_apis = list(unique_apis.values())
        
        print(f"[SUCCESS] API提取完成，发现 {len(final_apis)} 个唯一接口")
        
        return final_apis, self.work_dir
    
    def save_results(self, apis, work_dir):
        """保存提取结果"""
        try:
            # 确保工作目录存在
            os.makedirs(work_dir, exist_ok=True)
            
            # 保存JSON格式
            apis_file = os.path.join(work_dir, "apis.json")
            with open(apis_file, 'w', encoding='utf-8') as f:
                json.dump(apis, f, indent=2, ensure_ascii=False)
            
            # 生成Swagger风格的Markdown文档
            md_file = os.path.join(work_dir, "API文档_Swagger风格.md")
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"# 📖 API接口文档\n\n")
                f.write(f"> 统计：共发现 **{len(apis)}** 个有效接口\n\n")
                f.write(f"> 生成时间：{self._get_current_time()}\n\n")
                
                # 按方法类型分组
                method_groups = {}
                for api in apis:
                    method = api['method']
                    if method not in method_groups:
                        method_groups[method] = []
                    method_groups[method].append(api)
                
                # 按组输出
                for method in sorted(method_groups.keys()):
                    f.write(f"\n## {method} 接口\n\n")
                    for api in method_groups[method]:
                        f.write(f"---\n")
                        f.write(f"### 📍 `{api['path']}`\n")
                        f.write(f"- **方法**: `{api['method']}`\n")
                        f.write(f"- **源文件**: `{api['file']}`\n")
                        
                        if api['params']:
                            f.write("- **路径参数**:\n")
                            for param in api['params']:
                                f.write(f"  - `{param['name']}` ({param['type']})\n")
                        
                        if api['payload']:
                            f.write(f"- **请求体示例**:\n```json\n{json.dumps(api['payload'], indent=2, ensure_ascii=False)}\n```\n")
                        
                        f.write("\n")
            
            print(f"[SUCCESS] 结果已保存至：")
            print(f"  - API数据: {apis_file}")
            print(f"  - 接口文档: {md_file}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 保存结果失败: {str(e)}")
            return False
    
    def _get_current_time(self):
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数：执行API提取"""
    # 读取配置文件
    config_path = "project_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        source_path = config.get('source_path', r"E:\project\Costric\RuoYi-Vue")
        work_dir = config.get('work_dir', ".")
        
    except FileNotFoundError:
        print(f"[WARNING] 配置文件 {config_path} 不存在，使用默认参数")
        source_path = r"E:\project\Costric\RuoYi-Vue"
        work_dir = "."
    except Exception as e:
        print(f"[ERROR] 读取配置文件失败: {str(e)}，使用默认参数")
        source_path = r"E:\project\Costric\RuoYi-Vue"
        work_dir = "."
    
    print("[WARNING] 仅限授权测试！开始API提取...")
    print("=" * 50)
    
    # 创建提取器实例
    extractor = JavaAPIExtractor(source_path, config_path)
    
    # 执行提取
    apis, output_dir = extractor.run_extraction()
    
    if apis:
        # 保存结果
        success = extractor.save_results(apis, output_dir)
        if success:
            print(f"\n[SUCCESS] API提取任务完成！共提取 {len(apis)} 个接口")
            return True
        else:
            print("\n[ERROR] 结果保存失败")
            return False
    else:
        print("\n[WARNING] 未提取到任何API接口")
        return False

if __name__ == "__main__":
    main()