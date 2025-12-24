

# AI 自动化测试开发任务清单

> **角色**: 高级开发工程师（DevSecOps）  
> **目标**: 构建通用、模块化、生产就绪的后端接口测试框架  
> **原则**: 多语言支持、可配置、健壮、合规（仅限授权测试）


---

## 🔧 前置任务：配置与初始化（`configure.py` 核心逻辑）

### 功能目标
- 收集必要上下文信息
- 触发后续脚本生成流程

### 关键输入（必须在这一步向用户请求参数）！！！
先向用户提供填写模板
1. **源码根路径**（用于静态分析）
2. **目标系统 Base URL**
3. **认证凭据头**（如 `Authorization: Bearer ...`）
4. **工作目录**（用于存储中间结果）

在获取完这些信息后再进行configure.py脚本的编写！！！

### 输出
1. 生成 project_config.json 配置文件
2. 包含：源码路径、目标URL、认证信息、工作目录等
### 核心操作

```python

def capture_project_structure(source_path: str):
    # 在当前工作目录执行系统命令：
    #   dir "{source_path}" /s 
    # 目的：生成模型可读的目录与文件清单，用于技术栈识别
    pass
```
> ⚠️ 注意：此步骤需在写完configure.py脚本后立即运行，因为此步骤需要脚本的结果需要给予模型识别并解析，为任务一及后续的任务提供依据！！！

> ⚠️ 注意：此步骤需由模型自行确认技术栈，并返回对应解析器 

---

## 🟢 任务一：多语言 API 提取 (`step1_extract.py`)

### 📝 待执行指令：
- [ ] 确认上一步骤中所得到的模型识别结果，确定当前需要识别的 API 语言，在这一步骤仅完成指定语言的API 提取(脚本中不涉及到其他语言的API提取逻辑)
- [ ] 创建 `step1_extract.py`
- [ ] 将最初传入的源代码根目录路径硬编码进函数中
- [ ] 实现主函数 （这里以java为例，其他语言同理）
- [ ] 获取源代码根目录路径实现常见 API 路径模式探测功能
- [ ] 实现多方法探测（GET/POST/PUT/DELETE 等）
- [ ] 将探测结果与静态分析结果合并
- [ ] 在 step1_extract.py 中集成动态探测结果
```PYTHON
def extract_apis_from_java_source(source_root: str) -> List[Dict]:
    """
    遍历 .java 文件，识别以下元素：
      - @Controller 或 @RestController 类
      - 类级 @RequestMapping（支持单路径与数组）
      - 方法级映射注解（@GetMapping, @PostMapping 等）
    返回格式示例：
      [{"path": "/system/user/list", "method_hint": "GET"}, ...]
    """
    pass
```
- [ ] 根据 上一步骤中模型识别结果，调用以下解析器： 
  - `extract_java_apis(root)`
  - `extract_python_apis(root)`
  - `extract_node_apis(root)`
  - （其他语言可后续扩展）
- [ ] 需要对结果接口进行去重处理，避免重复提取，统计接口数量出错，导致测试结果错误
- [ ] 每个解析器需返回统一结构：

```python
[
  {
    "path": "/api/users/{id}",
    "method": "GET",   #根据请求方法，返回对应的 HTTP 方法
    "params": [
      {"name": "id", "in": "path", "required": true},
      {"name": "role", "in": "query", "required": false}
    ]
  },
  ...
]
```

- [ ] 将结果写入 `{work_dir}/apis.json`
- [ ] 初始化 `{work_dir}/Final_Report.md`，写入：



---

## 🟡 任务二：业务感知型四维测试 (`step2_security_test.py`)

### 📝 待执行指令：
- [ ] 创建 `step2_security_test.py`
- [ ] 读取 `{work_dir}/apis.json`
- [ ] 获取源代码目标 Base URL、认证凭据(token/api-key/cookie)
- [ ] 核心组件：响应解析器实现
```
实现辅助函数 parse_response(http_response) -> dict，逻辑如下：

第一层（网络关）：检查 http_response.status_code。如果不等于 200，直接标记为 NETWORK_FAIL（网络或网关错误）。

第二层（格式关）：尝试 http_response.json()。如果解析失败（返回了 HTML 或空），标记为 JSON_PARSE_FAIL。

第三层（业务关 - 关键！）：从 JSON 中提取核心字段：

biz_code：读取 code 字段（作为判定依据）。

biz_msg：读取 msg 字段（作为失败证据，如“认证失败”）。

biz_data：读取 data 或 rows（用于验证是否有敏感数据泄露）。
```

- [ ] 支持多种鉴权方式（通过命令行参数指定）：
  - `--auth-type Authorization`（Header: `Authorization`）（默认）
  - `--auth-type api-key`（Header: `X-API-Key`）
  - `--auth-type cookie`（需提供 session cookie）

- [ ] 为每个 API 生成多种测试用例类型：
- [ ] 基准测试用例（带认证）
- [ ] 无认证测试用例（越权测试）
- [ ] 健壮性测试用例（模糊测试）
- [ ] 边界值测试用例
- [ ] 生成测试用例 ID 和描述
- [ ] 为不同参数类型生成合适的测试值
- [ ] 将测试用例保存为 {work_dir}/test_cases.json

- [ ] **测试场景 1：基准测试 (Authorized / 有凭证)**
```
操作：携带有效 Token 发送请求。

通过标准：biz_code == 200。

失败标准：

biz_code == 401/403（Token 可能失效）。

biz_code == 500（服务端业务逻辑报错）。

记录数据：记录返回的 biz_msg（如“查询成功或者返回相关数据”）以证明功能正常。
```

- [ ] **测试场景 2：越权/鉴权绕过测试 (Unauthorized / 无凭证)**
```
操作：不携带 Token（或使用伪造 Token）发送请求。

通过标准：biz_code == 401 或 biz_code == 403（服务端正确拦截了请求，且返回了明确的错误码）。

失败标准（高危漏洞）：

🔴 biz_code == 200：严重警告！ 不带 Token 竟然返回了 200 业务码。

biz_data 非空：不带 Token 竟然返回了数据（如用户列表）。

记录数据：

若失败（即漏防），必须记录 biz_msg（如“操作成功”）和部分 biz_data 作为实锤证据。

若通过（即安全），记录 biz_msg（如“认证失败”）作为安全证明。
```

- [ ] **测试场景 3：健壮性测试 (Fuzzing)**
```
操作：发送特殊字符、超长字符串等 Payload。

通过标准：biz_code != 500（系统捕获了异常，返回了 400 或通用错误提示）。

失败标准：

biz_code == 500：系统未捕获异常。

biz_msg 包含代码堆栈信息（如 java.lang.NullPointerException）。

记录数据：记录导致 500 的具体 Payload。
```

- [ ] **参数填充逻辑**：
  - 实现 `def intelligent_fuzz(url, params_meta)`：
  - 遇到路径参数 `{id}`，尝试分别替换为 `1` (Integer) 和 `test_string` (String) 进行两次测试。
- [ ] **安全分级**：
  - 针对 `DELETE` 和 `DROP` 关键字的接口，**跳过** 模糊测试，仅做鉴权测试（防止误删数据）。
- [ ] 记录每项测试的：
  - URL、方法、测试类型
  - 请求头/体（脱敏！Token 替换为 `<REDACTED>`）
  - 响应状态码、响应时间、是否异常
- [ ] 输出 `{work_dir}/test_results.json`
- [ ] 向 `{work_dir}/Final_Report.md` 追加：



---

## 🔴 任务三：智能报告生成 (`step3_report.py`)

### 📝 待执行指令：
- [ ] 创建 `step3_report.py`
- [ ] 读取 `{work_dir}/test_results.json` 和 `{work_dir}/apis.json`
- [ ] 计算：
  - 接口覆盖率 = 已测接口数 / 总接口数
  - 鉴权绕过数：测试2或3返回 2xx 的接口
  - 崩溃接口数：测试4返回 500 的接口
- [ ] 向 `{work_dir}/Final_Report.md` 追加以下内容：
- [ ] 核心指标统计逻辑 (Metrics Logic)

  - 遍历测试结果，计算以下计数器：

    - Total Requests: 总请求数。

    - Network Fail: HTTP 状态非 200 的数量（环境问题）。

    - High Risk (Auth Bypass): 统计 test_type="no_auth" 且 business_code == 200 的数量（这是最严重的越权漏洞）。

    - System Crash: 统计 business_code == 500 的数量。

    - Pass Rate: (符合预期的用例数 / 总用例数) * 100%。

      - 注意：对于无鉴权测试，code 401 算“符合预期 (Pass)”，code 200 算“失败 (Fail)”。

---
---
### 📄 报告生成模板 (Markdown Template)
你的 Python 脚本应该动态填充 {} 中的变量。以下是最终生成的 Markdown 文件结构示例：
```markdown

# 🛡️ 自动化后端接口安全测试报告

> **生成时间**: {report_time}
> **目标系统**: {base_url}
> **检测引擎**: AI-DevSecOps-Bot 

---

## 1. 测试概览 (Executive Summary)
| 核心指标 | 数值 | 说明 |
| :--- | :--- | :--- |
| **接口总数** | {total_apis} | 扫描到的 API 数量 |
| **执行用例** | {total_cases} | 实际发起的测试请求总数 |
| **通过率** | **{pass_rate}%** | 符合预期的测试比例 |
| **🔴 高危漏洞** | **{high_risk_count}** | **鉴权绕过 (越权) 数量** |
| **🟡 系统崩溃** | {crash_count} | 业务返回 Code 500 的数量 |
| **⚠️ 网络错误** | {net_err_count} | HTTP 层非 200 的数量 |

---

## 2. 测试用例统计概览
| 测试类型	|总数	|通过数	|失败数	|通过率 |
| :--- | :--- | :--- | :--- | :--- |
| 基准测试 (basic_auth)	|{metrics['type_stats'].get('basic_auth', {}).get('total', 0)}	|{metrics['type_stats'].get('basic_auth', {}).get('passed', 0)}	|{metrics['type_stats'].get('basic_auth', {}).get('failed', 0)}	|{metrics['type_stats'].get('basic_auth', {}).get('rate', 0)}%|
| 越权测试 (no_auth)	|{metrics['type_stats'].get('no_auth', {}).get('total', 0)}	|{metrics['type_stats'].get('no_auth', {}).get('passed', 0)}	|{metrics['type_stats'].get('no_auth', {}).get('failed', 0)}	|{metrics['type_stats'].get('no_auth', {}).get('rate', 0)}%
| 健壮性测试 (fuzz)	|{metrics['type_stats'].get('fuzz', {}).get('total', 0)}	|{metrics['type_stats'].get('fuzz', {}).get('passed', 0)}	|{metrics['type_stats'].get('fuzz', {}).get('failed', 0)}	|{metrics['type_stats'].get('fuzz', {}).get('rate', 0)}%
| 边界值测试 (boundary)	|{metrics['type_stats'].get('boundary', {}).get('total', 0)}	|{metrics['type_stats'].get('boundary', {}).get('passed', 0)}	|{metrics['type_stats'].get('boundary', {}).get('failed', 0)}	|{metrics['type_stats'].get('boundary', {}).get('rate', 0)}%
| 总计	|{metrics['total_requests]}	|{metrics['overall_passed']}	|{metrics['overall_failed']}	|{metrics['overall_rate']}%

---

## 3. 系统健壮性 / 500 错误 (Warning)
**风险定义**: 特殊输入导致服务端抛出异常 (Code 500)，可能暴露堆栈信息。
| 接口路径 | Payload (复现参数) | 实际业务码 | 服务端提示 |
| :--- | :--- | :--- | :--- |
| `/api/user/list` | `id=1' OR '1'='1` | 🟡 500 | `"java.sql.SQLException..."` |

## 3. 详细测试结果
### 3.1 通过用例概况
成功请求: {metrics['success_requests']} 次 (HTTP 200 且业务码正常)
鉴权通过: {metrics['auth_passed']} 次 (带认证请求正常返回)
异常请求处理正常: {metrics['exception_handled']} 次 (异常输入被正确处理)
无权限验证正确: {metrics['no_auth_correct']} 次 (无认证请求正确返回401/403)
### 3.2 失败用例与失败描述
#### 3.2.1 高风险接口详情
|接口路径 (URL)	方法	|测试类型	|实际业务码	|服务端提示 (Evidence)	|风险描述|
|            |          |              |           | {high_risk_details}|					
##### 3.2.2 系统健壮性问题
风险定义: 特殊输入导致服务端抛出异常 (Code 500)，可能暴露堆栈信息。

|接口路径 (URL)	方法	|测试类型	|Payload (复现参数)	|实际业务码	|服务端提示
{crash_details}				
#### 3.2.3 其他失败用例
|接口路径 (URL)	方法	|测试类型	|	预期结果	|实际结果	|失败描述
{other_failure_rows}					

---

## 4. 🛡️ 安全结论与建议

### 4.1 鉴权逻辑分析
* **预期行为**: 未登录访问应返回 `Code: 401`, Msg: `"认证失败"`。
* **实际发现**: 共发现 **{high_risk_count}** 个接口不符合预期。

### 4.2 修复建议
1. **强制鉴权**: 检查 `Shiro/SpringSecurity` 配置，确保上述接口未被排除在过滤器之外。
2. **异常捕获**: 对 500 错误接口增加全局异常处理 (GlobalExceptionHandler)，避免堆栈外露。

---
```

### 💡 关键点解析 (对于 Python 实现)
在编写 step3_report.py 生成上述 Markdown 表格时，重点关注 2.1 鉴权绕过 表格的这一行逻辑：

```Python
# 伪代码：如何决定是否将一条结果写入"鉴权绕过"表格
if result['test_type'] == 'no_auth':
    if result['business_code'] == 200:
        # 这是一个漏洞！写入表格
        write_row(
            url=result['url'],
            code=f"🔴 {result['business_code']}", 
            evidence=f"\"{result['server_message']}\"", # 加上引号强调
            desc="未鉴权操作成功"
        )
    elif result['business_code'] == 401:
        # 这是安全的，不写入"失败详情"表，计入通过率即可
        pass

```
- [ ] 打印完成提示：`✅ 报告已生成：{work_dir}/Final_Report.md`

---

## 🔴 任务四：自动化流水线整合 (`run.bat`)

### 📝 待执行指令：
- [ ] 创建批处理脚本 `run.bat`，用于依次调用各 Python 脚本：
  ```bat
  @echo off
  chcp 65001 >nul
  cls

  echo =============================================
  echo   🚀 AI 自动化渗透测试工具 (分步执行版)
  echo   ⚠️  仅限授权测试！
  echo =============================================


  echo.
  echo [+] 开始执行任务一：API 提取...
  python step1_extract.py "%WORK_DIR%/project_config.json" "%WORK_DIR%"
  if errorlevel 1 goto :error

  echo.
  echo [+] 开始执行任务二：安全测试...
  python step2_security_test.py "%WORK_DIR%/apis.json" "%BASE_URL%" "%TOKEN%" "%AUTH_TYPE%" "%WORK_DIR%"
  if errorlevel 1 goto :error

  echo.
  echo [+] 开始执行任务三：生成报告...
  python step3_report.py "%WORK_DIR%"
  if errorlevel 1 goto :error

  echo.
  echo ✅ 全流程完成！报告位置: %WORK_DIR%/Final_Report.md
  goto :end

  :error
  echo.
  echo 💥 某一步骤执行失败，请检查日志。
  exit /b 1

  :end
  pause
  ```

---

## 📦 附：工程规范要求
为了保证测试脚本的开发效率:大部分脚本都使用python编写


| 项目 | 要求 |
|------|------|
| **错误处理** | 所有脚本必须包含 try-except，避免中断 |
| **日志脱敏** | 任何日志/报告中不得明文打印 Token、Cookie |
| **合规声明** | 在 README 和脚本启动时打印：⚠️ 仅限授权测试！ |
| **依赖管理** | 提供 `requirements.txt` |
| **可测试性** | 每个核心函数需可独立调用（便于单元测试） |
| **精简代码** | 避免使用 unnecessary code |
| **编码兼容** | 尽量去除 UTF-8 编码的内容，在windows下cmd需设置chcp 65001或者使用gbk编码 |
| **无代码交互**| 脚本中不得有交互式输入，如：input()，所有交互由ai接受用户输入完成 |
|  **运行次序** | 前置步骤的代码需要先运行，后面的任务一二三需要在.bat脚本运行完成后才能运行 |