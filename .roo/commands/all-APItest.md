---
description: "一键串行执行所有四个维度的后端API测试（基准、鉴权、健壮性、边界值），实现全自动化扫描"
---

- 读取 {work_dir}/apis.json 确认测试目标与前置条件满足

- 必须切换至 script engineer 模式开始 必须切换 必须切换！！！！！！

- 依次读取 3.1 至 3.4 的所有测试文档，确保以下脚本均已正确创建（若不存在则即时创建）：

- step2_1_baseline.py (基准测试)

- step2_2_auth.py (鉴权绕过)

- step2_3_fuzz.py (健壮性Fuzz)

- step2_4_boundary.py (边界值测试)

- 切换至 debugger 模式 依次执行上述脚本

- 严格执行顺序约束：

- 第1步：执行 step2_1_baseline.py -> 生成 results_baseline.json -> 等待结束

- 第2步：执行 step2_2_auth.py -> 生成 results_auth_bypass.json -> 等待结束

- 第3步：执行 step2_3_fuzz.py -> 生成 results_fuzzing.json -> 等待结束

- 第4步：执行 step2_4_boundary.py -> 生成 results_boundary.json -> 等待结束

- 一个工作流完成后才能执行下一个工作流，禁止同时执行

- 监控全流程日志，若任一步骤出现 Token 失效，立即触发自动重连机制