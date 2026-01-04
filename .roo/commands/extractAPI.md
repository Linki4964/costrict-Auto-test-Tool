---
description: "用于静态分析源代码，提取API接口定义并生成初始测试文档"
---

- 读取上一任务生成的 project_config.json 获取源码路径和技术栈语言（如 Java）

- 确认模型对技术栈的识别结果，锁定当前脚本为指定语言（如 Java）的提取逻辑

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 2.后端API提取.md 中的 API 提取逻辑

- 创建 step1_extract.py 脚本，硬编码源码根目录路径

- **核心实现一：深度 DTO 解析**
   - 扫描 Java 实体类与父类（如 BaseEntity），提取真实字段名与类型生成 `smart_payload`，解决参数缺失问题

- **核心实现二：精准方法识别**
   - 优化正则逻辑，正确区分 `@GetMapping`, `@PostMapping`, `@PutMapping` 及 `@RequestMapping(method=...)`，严防将 PUT 误判为 POST

- **核心实现三：路径参数提取**
   - 识别 URL 中的占位符（如 `/user/{userId}`），并在 `params` 字段中标记，为后续动态填充做准备

- **核心实现四：上传接口识别**
   - 检测参数中是否包含 `MultipartFile`，若有则将 content_type 标记为 `multipart/form-data`

- 实现接口去重逻辑（基于 Method + Path）并统一数据结构

- 切换至 debugger 模式 执行脚本，生成包含 content_type 和 smart_payload 的 {work_dir}/apis.json

- 将 apis.json 数据文件写入 Swagger 风格的接口列表头

- 一个工作流完成后才能执行下一个工作流，禁止同时执行