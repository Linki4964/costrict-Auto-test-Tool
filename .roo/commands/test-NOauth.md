---
description: "用于执行鉴权绕过（越权）测试，检测未授权访问漏洞"
---

- 读取 {work_dir}/apis.json 获取目标 API 列表和有效载荷结构

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 3.2.后端鉴权绕过测试.md 中的核心测试逻辑

- 创建 step2_2_auth.py 脚本

- 请求构造：使用 API 定义中的有效载荷，确保请求能穿透前端校验到达后端

- 实现核心检测逻辑：不携带 Token 或使用 伪造/过期 Token 发送请求

- 实现判定标准：biz_code 返回 401/403 判定为安全；返回 200 且包含有效数据判定为 越权漏洞 (High Risk)

- 切换至 debugger 模式 执行脚本并进行流程自检（若 Token 失效需自动重获、检查 JSON 解析错误、确保日志脱敏）

- 输出测试结果写入 {work_dir}/results_auth_bypass.json

- 一个工作流完成后才能执行下一个工作流，禁止同时执行