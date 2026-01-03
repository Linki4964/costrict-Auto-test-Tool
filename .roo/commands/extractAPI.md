---
description: "用于静态分析源代码，提取API接口定义并生成初始测试文档"
---

- 读取上一任务生成的 project_config.json 获取源码路径和技术栈语言（如 Java）

- 确认模型对技术栈的识别结果，锁定当前脚本为指定语言（如 Java）的提取逻辑

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 2.后端API提取.md 中的 API 提取逻辑

- 创建 step1_extract.py 脚本，硬编码源码根目录路径

- 实现 extract_java_apis 函数，利用正则（Regex）匹配 @RequestMapping、@PostMapping 等注解

- 实现接口去重逻辑（基于 Method + Path）并统一数据结构

- 切换至 debugger 模式 执行脚本，生成 {work_dir}/apis.json 数据文件

- 将 apis.json 数据文件写入 Swagger 风格的接口列表头

- 一个工作流完成后才能执行下一个工作流，禁止同时执行