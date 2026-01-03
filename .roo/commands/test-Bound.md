---
description: "用于执行后端边界值测试，验证API对极值参数的处理逻辑"
---

- 读取 {work_dir}/apis.json 识别参数类型（如 int, string）获取智能载荷 (smart_payload)

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 读取 3.4.后端边界值测试.md 中的核心测试逻辑

- 创建 step2_4_boundary.py 脚本

- 实现类型推断与精确测试：
 
   - 解析 smart_payload 中字段的数据类型 (int/str/list)

   - 针对 int 生成 MaxInt/MinInt/Zero；针对 str 生成空串/超长串/Null
- 实现 精确边界模拟：针对特定类型生成边界值（如 int 类型的 2147483647，string 类型的空字符或超长字符）

- 严格遵循单一变量原则：每次请求仅修改一个字段为边界值，保持其余字段为合法默认值，确保测试结果可追溯

- 异常识别：重点记录 biz_code == 500 的情况（视为漏洞），忽略 400 Bad Request（视为防御成功）

- 切换至 debugger 模式 执行脚本并进行流程自检（若 Token 失效需自动重获、检查 JSON 解析错误、确保日志脱敏）

- 输出测试结果写入 {work_dir}/results_boundary.json

- 一个工作流完成后才能执行下一个工作流，禁止同时执行