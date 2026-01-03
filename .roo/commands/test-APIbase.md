---
description: "用于执行后端基准功能测试，验证接口连通性与基本业务逻辑"
---

- 读取 {work_dir}/apis.json 解析目标 Base URL 与认证凭据（Auth Token）

- 确认前置任务 /extract 已完成且存在有效的 API 列表

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 3.1.后端基准性测试.md 中的核心测试逻辑

- 创建 step2_1_baseline.py 脚本

- 实现测试逻辑：携带有效 Token，使用 API 定义中的有效载荷发送标准请求

- 实现结果判定：biz_code == 200 视为通过，记录 biz_msg 作为证据

- 输出测试结果写入 {work_dir}/results_baseline.json

- 切换至 debugger 模式 执行脚本并进行流程自检（若 Token 失效需自动重获、检查 JSON 格式错误、确保日志脱敏）

- 一个工作流完成后才能执行下一个工作流，禁止同时执行