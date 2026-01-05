---
description: "执行鉴权绕过测试，集成敏感资源保护盾"
---

- 读取 {work_dir}/apis.json 获取目标 API 列表和智能载荷 (smart_payload)

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 3.2.后端鉴权绕过测试.md 中的核心测试逻辑

- 创建 step2_2_auth.py 脚本

- **实现 管理员保护盾 (Admin Shield)**
   - 针对 `DELETE`/`PUT` 请求，在发送前检查 URL 是否包含 `/1`、`/0` 或 `/admin`。若包含，**强制跳过**该接口的越权测试

- **实现 核心检测逻辑**
   - 使用无效 Token 发送请求
   - 判定标准：Code 200 为高危漏洞；Code 401/403 为安全

- 切换至 debugger 模式 执行脚本并进行流程自检

- 输出测试结果写入 {work_dir}/results_auth_bypass.json

- 一个工作流完成后才能执行下一个工作流，禁止同时执行