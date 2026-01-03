---
description: "【全自动闭环】一键执行环境配置 -> 智能提取 -> 熔断检查 -> 四维安全测试 "
---

- **阶段一：环境初始化 (Configure)**
   - 读取或请求用户输入必要参数：{source_path}, {base_url}, {work_dir}, {credentials}
    - 检测若当前目录下已存在 `project_config.json`，则询问用户是否直接读取，否则输出填写模板
    - **必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！**
    - 编写 `configure.py`，包含 `fetch_and_save_token` 和 `capture_project_structure`
    - 执行脚本生成配置文件并确认技术栈（如 Java/Spring）
- **阶段二：智能API提取与熔断检查 (Extract & Check)**
    - 读取 `project_config.json`，锁定目标语言提取逻辑
    - 创建 `step1_extract.py`，实现以下核心升级逻辑：
        - **智能路径拼接**：严防类路径与方法路径重复拼接
        - **DTO 解析器**：扫描 Java 实体类，提取真实字段名生成 `smart_payload`
        - **上传识别**：检测 `MultipartFile` 参数，标记 `content_type` 为 `multipart/form-data`
    - **切换至 debugger 模式** 执行脚本，生成包含智能载荷的 `{work_dir}/apis.json`
- **阶段三：串行自动化测试 (Test Suite)**
    - **前提**：仅当阶段二成功且接口数 > 0 时继续。
    - **必须切换至 script engineer 模式** 依次创建以下脚本，**每创建一个脚本后立即切换至 debugger 模式执行**：

   - **必须切换至 script engineer 模式** 依次创建以下脚本，**每创建一个脚本后立即切换至 debugger 模式执行并等待完成，再进行下一步**：

    1.  **基准功能测试 (`step2_1_baseline.py`)**
        - 读取 `apis.json`，实现**自适应请求**（自动区分 JSON 与 File Upload）
        - 实现**自适应响应**（自动跳过二进制流解析，仅校验 JSON 状态码）
        - 输出：`{work_dir}/results_baseline.json`

    2.  **鉴权绕过测试 (`step2_2_auth.py`)**
        - 构造无 Token 或伪造 Token 请求
        - 判定：Code 200 且含有效数据为**高危漏洞**
        - 输出：`{work_dir}/results_auth_bypass.json`

    3.  **多态健壮性测试 (`step2_3_fuzz.py`)**
        - **载荷继承**：基于 `smart_payload` 进行字段变异
        - **多态攻击**：针对 JSON 注入 SQL/溢出；针对 Upload 注入恶意后缀/空文件
        - **异常识别**：捕获 Code 500 + Stack Trace
        - 输出：`{work_dir}/results_fuzzing.json`

    4.  **精确边界值测试 (`step2_4_boundary.py`)**
        - **类型推断**：识别 `apis.json` 中字段类型 (int/str)
        - **单一变量原则**：每次仅测试一个字段的极值 (MaxInt, EmptyStr)，保持其他字段合法
        - 输出：`{work_dir}/results_boundary.json`
    - **并发控制**：严格遵守一个脚本执行完毕并生成 JSON 后，才能开始下一个脚本的编写与执行。

- **全局安全与风控**
    - 严格遵守：**一个工作流（脚本执行）完成后才能执行下一个工作流，禁止同时执行**
    - 全程监控：若任一步骤 Token 失效，自动触发 `fetch_and_save_token` 重连

    - 数据脱敏：确保所有日志输出中的 Token 均已脱敏处理
