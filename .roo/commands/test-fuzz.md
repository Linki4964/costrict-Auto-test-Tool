---
description: "用于执行健壮性模糊测试，检测特殊输入下的系统崩溃与异常堆栈泄露"
---

- 读取 {work_dir}/apis.json 获取接口定义、content_type 及智能种子载荷 (smart_payload)

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 3.3.后端健壮性测试.md 中的核心测试逻辑

- 创建 step2_3_fuzz.py 脚本

- 实现载荷继承：基于 extract 阶段获取的合法 DTO 结构进行字段变异，避免因缺少必要参数导致的无效 NPE

- 实现多态 Fuzz 逻辑：

   - 场景 A (JSON): 对字符串字段注入 SQL 字符 (' OR 1=1)，对数字字段注入超大整数

   - 场景 B (Upload): 若 content_type 为 multipart/form-data，构造恶意文件名 (.jsp, ../../config) 和空文件内容进行测试

- 实现 熔断机制：针对 DELETE 方法或包含 DROP 关键字的接口强制跳过，防止误删数据

- 实现 异常识别：判定 biz_code == 500 且响应中包含堆栈信息（Stack Trace）为失败,并记录具体的 Fuzz 向量（是哪个字段导致的崩溃）

- 切换至 debugger 模式 执行脚本并进行流程自检（若 Token 失效需自动重获、检查 JSON 解析错误、确保日志脱敏）

- 输出测试结果写入 {work_dir}/results_fuzzing.json

- 一个工作流完成后才能执行下一个工作流，禁止同时执行