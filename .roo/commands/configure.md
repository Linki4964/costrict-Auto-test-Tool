---
description: "用于初始化自动化测试环境，生成配置文件并识别技术栈"
---

- 读取或请求用户输入必要参数：{source_path} (源码路径), {base_url} (目标地址), {work_dir} (工作目录), {credentials} (账号密码)
- 检测若当前目录下已存在项目信息的配置文件，则询问用户是否直接读取，否则输出填写模板
- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！
- 读取 1.配置与初始化.md 中的核心操作逻辑
- 编写 configure.py 脚本，必须包含 fetch_and_save_token (获取鉴权Token) 和 capture_project_structure (源码目录分析) 函数
- 执行脚本生成 project_config.json 配置文件
- 根据脚本运行结果确认技术栈（如 Java/Spring），为后续 API 提取任务提供依据
- 一个工作流完成后才能执行下一个工作流，禁止同时执行