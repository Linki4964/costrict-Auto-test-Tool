import os
import re
import csv
from collections import Counter

# ====== 项目根路径 ======
PROJECT_ROOT = r"./RuoYi-Vue-master"  # 改成你的项目根路径

# ====== 前端正则 ======
frontend_url_pattern = re.compile(r"url\s*:\s*['\"]([^'\"]+)['\"]", re.I)
frontend_method_pattern = re.compile(r"method\s*:\s*['\"]([^'\"]+)['\"]", re.I)

# ====== 后端正则 ======
class_mapping_pattern = re.compile(
    r'@RequestMapping\s*\(\s*(?:value|path)?\s*=?\s*["\']([^"\']+)["\']',
    re.I
)

# 方法级注解
method_mapping_pattern = re.compile(
    r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\((.*?)\)',
    re.I | re.S  # re.S 支持跨行匹配
)

# RequestMethod.GET/POST/PUT/DELETE
http_method_pattern = re.compile(r'RequestMethod\.(GET|POST|PUT|DELETE|PATCH)', re.I)

apis = set()
method_counter = Counter()

# ====== 扫描项目 ======
for root, _, files in os.walk(PROJECT_ROOT):
    for file in files:
        path = os.path.join(root, file)

        # ----- 前端 -----
        if file.endswith((".js", ".vue")):
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except:
                continue

            urls = frontend_url_pattern.findall(content)
            methods = frontend_method_pattern.findall(content)
            if len(methods) < len(urls):
                methods += ["get"] * (len(urls) - len(methods))

            for i, url in enumerate(urls):
                method = methods[i].upper()
                apis.add(("FRONTEND", method, url))
                method_counter[method] += 1

        # ----- 后端 -----
        elif file.endswith(".java"):
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except:
                continue

            # 类级前缀
            class_prefix = ""
            class_match = class_mapping_pattern.search(content)
            if class_match:
                class_prefix = class_match.group(1)

            # 方法级注解
            for m in method_mapping_pattern.finditer(content):
                mapping_type = m.group(1)
                body = m.group(2)  # 括号内内容

                # 提取路径（支持数组 {"a","b"} 或单路径）
                paths = re.findall(r'["\']([^"\']+)["\']', body)
                if not paths:
                    paths = [""]  # 没写路径默认空

                # 提取方法
                if mapping_type.lower() == "requestmapping":
                    methods = http_method_pattern.findall(body)
                    if not methods:
                        methods = ["GET"]
                else:
                    methods = [mapping_type.replace("Mapping", "").upper()]

                # 组合类级 + 方法级路径
                for path_suffix in paths:
                    for method in methods:
                        full_path = f"{class_prefix}/{path_suffix}".replace("//", "/")
                        apis.add(("BACKEND", method.upper(), full_path))
                        method_counter[method.upper()] += 1

# ====== 拆分前后端 ======
frontend_apis = {(method, url) for src, method, url in apis if src == "FRONTEND"}
backend_apis  = {(method, url) for src, method, url in apis if src == "BACKEND"}

common_apis   = frontend_apis & backend_apis
frontend_only = frontend_apis - backend_apis
backend_only  = backend_apis - frontend_apis

# ====== 输出统计 ======
print(f"前端接口总数：{len(frontend_apis)}")
print(f"后端接口总数：{len(backend_apis)}")
print(f"前后端共有接口：{len(common_apis)}")
print(f"前端独有接口：{len(frontend_only)}")
print(f"后端独有接口：{len(backend_only)}")

# ====== 导出整合 CSV ======
with open("api_comparison.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["METHOD", "URL", "FRONTEND", "BACKEND"])
    all_apis = frontend_apis | backend_apis
    for method, url in sorted(all_apis):
        writer.writerow([
            method,
            url,
            "Y" if (method, url) in frontend_apis else "X",
            "Y" if (method, url) in backend_apis else "X"
        ])

print("\n已生成对比表：api_comparison.csv")
