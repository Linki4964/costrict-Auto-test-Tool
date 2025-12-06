import os
import re
import requests
import sys
from typing import List, Set
from datetime import datetime

requests.packages.urllib3.disable_warnings()


# ========== 第一步：从 Java 源码提取 API 路径 ==========
def extract_apis_from_java_source(source_root: str) -> List[dict]:
    apis = []
    controller_pattern = re.compile(r'@(RestController|Controller)')
    request_mapping_class = re.compile(r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']\s*\)')
    request_mapping_class_array = re.compile(r'@RequestMapping\s*\(\s*\{\s*([^}]+)\s*\}\s*\)')

    method_map = {
        '@GetMapping': 'GET',
        '@PostMapping': 'POST',
        '@PutMapping': 'PUT',
        '@DeleteMapping': 'DELETE',
        '@RequestMapping': 'UNKNOWN'
    }

    for root, _, files in os.walk(source_root):
        for file in files:
            if not file.endswith('.java'):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except:
                continue

            if not any(controller_pattern.search(line) for line in lines):
                continue

            class_paths = []
            for line in lines:
                m1 = request_mapping_class.search(line)
                if m1:
                    class_paths.append(m1.group(1))
                    continue
                m2 = request_mapping_class_array.search(line)
                if m2:
                    arr_str = m2.group(1)
                    paths_in_array = re.findall(r'["\']([^"\']+)["\']', arr_str)
                    class_paths.extend(paths_in_array)

            if not class_paths:
                class_paths = [""]

            for i, line in enumerate(lines):
                for anno, method in method_map.items():
                    pattern = re.compile(rf'{anno}\s*\(\s*["\']([^"\']*)["\']\s*\)')
                    m = pattern.search(line)
                    if m:
                        method_path = m.group(1).strip() or ""
                        for cp in class_paths:
                            full_path = '/' + (cp.rstrip('/') + '/' + method_path.lstrip('/')).lstrip('/')
                            if full_path.startswith('/') and len(full_path) > 2:
                                apis.append({
                                    "path": full_path,
                                    "method_hint": method
                                })
                        break
    seen = set()
    unique = []
    for api in apis:
        key = (api["path"], api["method_hint"])
        if key not in seen:
            seen.add(key)
            unique.append(api)
    return sorted(unique, key=lambda x: x["path"])


# ========== 第二步：四维测试 ==========
def test_single_api(base_url: str, path: str, method_hint: str, valid_token: str):
    url = base_url.rstrip('/') + '/prod-api' + path
    headers_valid = {"Authorization": f"Bearer {valid_token}"}
    headers_invalid = {"Authorization": "Bearer invalid.token.xxxx"}

    result = {
        "url": url,
        "path": path,
        "method": method_hint,
        "normal_success": False,
        "no_auth_blocked": False,
        "invalid_token_blocked": False,
        "robustness_ok": True,
        "notes": []
    }

    # --- 1. 正常请求 ---
    method = method_hint if method_hint != "UNKNOWN" else "GET"
    try:
        if method == "POST":
            resp = requests.post(url, headers=headers_valid, json={}, timeout=6, verify=False)
        else:
            resp = requests.get(url, headers=headers_valid, timeout=6, verify=False)

        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get("code") == 200:
                    result["normal_success"] = True
                else:
                    result["notes"].append(f"业务错误 code={data.get('code')}")
            except:
                result["normal_success"] = True
        else:
            result["notes"].append(f"状态码 {resp.status_code}")
    except Exception as e:
        result["notes"].append(f"请求异常: {str(e)[:50]}")

    # --- 2. 无 Token ---
    try:
        if method == "POST":
            resp = requests.post(url, json={}, timeout=6, verify=False)
        else:
            resp = requests.get(url, timeout=6, verify=False)
        if resp.status_code in (401, 403):
            result["no_auth_blocked"] = True
        elif resp.status_code == 200:
            try:
                if resp.json().get("code") in (401, 403):
                    result["no_auth_blocked"] = True
                else:
                    result["notes"].append("无 Token 返回成功！")
            except:
                pass
    except:
        result["no_auth_blocked"] = True

    # --- 3. 无效 Token ---
    try:
        if method == "POST":
            resp = requests.post(url, headers=headers_invalid, json={}, timeout=6, verify=False)
        else:
            resp = requests.get(url, headers=headers_invalid, timeout=6, verify=False)
        if resp.status_code in (401, 403):
            result["invalid_token_blocked"] = True
        elif resp.status_code == 200:
            try:
                if resp.json().get("code") in (401, 403):
                    result["invalid_token_blocked"] = True
                else:
                    result["notes"].append("无效 Token 返回成功！")
            except:
                pass
    except:
        result["invalid_token_blocked"] = True

    # --- 4. 异常请求（健壮性）---
    robust_tests = [
        ("路径穿越", lambda: requests.get(url + "/../etc/passwd", timeout=3, verify=False)),
        ("超长 JSON", lambda: requests.post(url, data="{" * 1000, timeout=3, verify=False)),
        ("错误方法 PUT", lambda: requests.put(url, timeout=3, verify=False)),
    ]
    for name, test_func in robust_tests:
        try:
            r = test_func()
            if r.status_code == 500:
                result["robustness_ok"] = False
                result["notes"].append(f"{name} 触发 500")
                break
        except:
            continue

    return result


def comprehensive_test(base_url: str, valid_token: str, apis: List[dict]):
    print(f"\n🧪 开始对 {len(apis)} 个接口进行四维安全测试...\n")
    results = []

    for api in apis:
        res = test_single_api(base_url, api["path"], api["method_hint"], valid_token)
        results.append(res)

        status_icons = []
        if res["normal_success"]: status_icons.append("✅")
        if res["no_auth_blocked"]: status_icons.append("🔒")
        if res["invalid_token_blocked"]: status_icons.append("🛡️")
        if res["robustness_ok"]: status_icons.append("⚡")
        print(f"{''.join(status_icons)} {res['path']}")

    return results


# ========== 第三步：生成 Markdown 报告 ==========
def generate_markdown_report(
        report_path: str,
        base_url: str,
        source_path: str,
        total_apis: int,
        results: List[dict],
        start_time: datetime
):
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # 统计
    normal_ok = sum(1 for r in results if r["normal_success"])
    auth_ok = sum(1 for r in results if r["no_auth_blocked"] and r["invalid_token_blocked"])
    robust_ok = sum(1 for r in results if r["robustness_ok"])
    risky = [r for r in results if r["normal_success"] and not (r["no_auth_blocked"] and r["invalid_token_blocked"])]
    fragile = [r for r in results if not r["robustness_ok"]]

    md = []
    md.append("# 若依系统后端接口安全测试报告\n")
    md.append(f"- **扫描时间**: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`")
    md.append(f"- **耗时**: `{duration:.1f} 秒`")
    md.append(f"- **目标地址**: `{base_url}`")
    md.append(f"- **源码路径**: `{source_path}`")
    md.append(f"- **发现接口数**: `{total_apis}`\n")

    md.append("## 📊 测试概览\n")
    md.append("| 测试维度 | 通过数 | 总数 | 通过率 |")
    md.append("|----------|--------|------|--------|")
    md.append(f"| 正常请求成功 | {normal_ok} | {total_apis} | {normal_ok / total_apis * 100:.1f}% |")
    md.append(f"| 鉴权机制有效 | {auth_ok} | {total_apis} | {auth_ok / total_apis * 100:.1f}% |")
    md.append(f"| 健壮性良好 | {robust_ok} | {total_apis} | {robust_ok / total_apis * 100:.1f}% |\n")

    if risky:
        md.append("## ⚠️ 高风险接口（鉴权可能失效）\n")
        md.append("| 接口路径 | 完整 URL | 问题说明 |")
        md.append("|----------|----------|----------|")
        for r in risky:
            notes = "; ".join(r["notes"]) if r["notes"] else "无 Token 或无效 Token 可访问"
            md.append(f"| `{r['path']}` | [{r['url']}]({r['url']}) | {notes} |")
        md.append("")

    if fragile:
        md.append("## 💥 健壮性差的接口（可能触发 500）\n")
        md.append("| 接口路径 | 完整 URL |")
        md.append("|----------|----------|")
        for r in fragile:
            md.append(f"| `{r['path']}` | [{r['url']}]({r['url']}) |")
        md.append("")

    md.append("## 📋 详细测试结果\n")
    md.append("| 接口路径 | 方法 | 正常 | 无 Token | 无效 Token | 健壮 | 备注 |")
    md.append("|----------|------|:----:|:--------:|:-----------:|:----:|------|")
    for r in results:
        normal = "✅" if r["normal_success"] else "❌"
        no_auth = "✅" if r["no_auth_blocked"] else "❌"
        invalid_tok = "✅" if r["invalid_token_blocked"] else "❌"
        robust = "✅" if r["robustness_ok"] else "❌"
        notes = "<br>".join(r["notes"]) if r["notes"] else "-"
        md.append(f"| `{r['path']}` | {r['method']} | {normal} | {no_auth} | {invalid_tok} | {robust} | {notes} |")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"\n✅ Markdown 报告已生成: {report_path}")


# ========== 主流程 ==========
def main():
    print("🔍 若依后端源码 API 四维安全测试 + Markdown 报告")
    print("--------------------------------------------------")

    source_path = input("📂 请输入 Java 源码根目录（含 controller）:\n").strip()
    if not os.path.isdir(source_path):
        print("❌ 源码路径无效！")
        sys.exit(1)

    base_url = input("\n🌐 请输入系统地址（如 http://192.168.236.141）:\n").strip()
    if not base_url.startswith(("http://", "https://")):
        base_url = "http://" + base_url

    token_input = input("\n🔐 请输入有效 Bearer Token:\n").strip()
    if not token_input:
        print("❌ Token 不能为空！")
        sys.exit(1)
    token = token_input[7:] if token_input.lower().startswith("bearer ") else token_input

    start_time = datetime.now()
    report_file = f"ruoyi_security_report_{start_time.strftime('%Y%m%d_%H%M%S')}.md"

    # Step 1: 提取
    print("\n🔍 扫描源码中...")
    apis = extract_apis_from_java_source(source_path)
    if not apis:
        print("🛑 未发现任何 Controller 接口！")
        sys.exit(1)
    print(f"✅ 提取到 {len(apis)} 个接口")

    # Step 2: 测试
    results = comprehensive_test(base_url, token, apis)

    # Step 3: 生成报告
    generate_markdown_report(report_file, base_url, source_path, len(apis), results, start_time)

    print("\n🔚 全部完成！")


if __name__ == "__main__":
    main()