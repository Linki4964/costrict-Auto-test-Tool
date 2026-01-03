---
description: "用于执行健壮性模糊测试，检测特殊输入下的系统崩溃与异常堆栈泄露"
---

- 读取 {work_dir}/apis.json 获取接口定义与参数类型

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 3.3.后端健壮性测试.md 中的核心测试逻辑

- 创建 step2_3_fuzz.py 脚本

- 实现 智能载荷填充 (Intelligent Fuzz)：基于合法载荷注入特殊字符，降低因 JSON 格式错误导致的无效测试

- 实现 熔断机制：针对 DELETE 方法或包含 DROP 关键字的接口强制跳过，防止误删数据

- 实现 异常识别：判定 biz_code == 500 且响应中包含堆栈信息（Stack Trace）为失败

- 切换至 debugger 模式 执行脚本并进行流程自检（若 Token 失效需自动重获、检查 JSON 解析错误、确保日志脱敏）

- 输出测试结果写入 {work_dir}/results_fuzzing.json

- 一个工作流完成后才能执行下一个工作流，禁止同时执行