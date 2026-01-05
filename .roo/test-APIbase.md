---
description: "【指令】基准测试 -> 黄金闭环 -> 安全防御 (Step 2)"
---

- 读取 {work_dir}/apis.json 解析目标 Base URL 与认证凭据

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 3.1.后端基准性测试.md 中的核心测试逻辑

- 创建 step2_1_baseline.py 脚本

- **核心指令一：黄金闭环 (Golden Loop)**
   - 脚本必须识别核心资源（如 `/system/user`），执行 **POST(Create) -> PUT(Update) -> DELETE(Delete)** 的完整闭环。
   - **Payload 策略**：优先使用脚本内置的 `GOLDEN_PAYLOADS`；若未匹配，则**必须**使用 `apis.json` 中提取的 `smart_payload`。
   - **动态处理**：发送前必须在 Payload 中注入时间戳（`{ts}`），防止唯一性约束报错。
   - 必须内置 `GOLDEN_PAYLOADS`（同源基准）。
   - **修复 User PUT**：Payload 中**移除 `userName`**。
   - **修复 Role PUT**：Payload 中**添加 `menuIds: [1]`**。
   - 执行 `GET List -> POST -> PUT -> DELETE`。
- **核心指令二：降级执行策略 (Fallback Execution)**
   - 在执行闭环时，若 POST 操作成功但未返回 ID，或者 POST 失败，脚本**必须**尝试调用 `get_sample_id` 从 `/list` 接口获取一个现有的测试 ID。
   - 确保 PUT 和 DELETE 操作使用的是 `target_id`（新 ID 或 样本 ID），而不是依赖于 `created_id`，防止闭环提前中断。

- **核心指令三：管理员保护盾 (Admin Shield)**
   - 在执行 DELETE 操作前，**必须**检查 `target_id`。
   - 若 ID 为 `1` (Admin), `100` (根部门) 或 `None`，**强制跳过**删除操作，并标记为 SKIPPED。

- **核心指令四：严格结果判定**
   - 判定通过标准：HTTP 200 且 业务响应 `code == 200`。
   - 特殊情况：若 DELETE 返回“存在下级/不允许删除”等业务规则拦截信息，可视为逻辑正确（SKIPPED/SUCCESS）。

- 切换至 debugger 模式 执行脚本并进行流程自检

- 输出测试结果写入 {work_dir}/results_baseline.json

- 一个工作流完成后才能执行下一个工作流，禁止同时执行