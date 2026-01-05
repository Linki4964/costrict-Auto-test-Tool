---
description: "进入配置模式"
---


- 进入此模式你需要询问用户进入前端模式还是后端模式

## 前端模式

- 你需要进入`to_do-list`获取前端匹配模式任务清单，并且开始引导用户配置

## 后端模式

- 读取或请求用户输入必要参数：{source_path} (源码路径), {base_url} (目标地址), {work_dir} (工作目录), {credentials} (账号密码)
- 检测若当前目录下已存在项目信息的配置文件，则询问用户是否直接读取，否则输出填写模板
- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！
- 读取 `1.配置与初始化.md` 中的核心操作逻辑
- 编写 configure.py 脚本，必须包含 fetch_and_save_token (获取鉴权Token) 和 capture_project_structure (源码目录分析) 函数
- 执行脚本写入到 [project_config.json] 配置文件
- 根据脚本运行结果确认技术栈（如 Java/Spring），为后续 API 提取任务提供依据
- 一个工作流完成后才能执行下一个工作流，禁止同时执行