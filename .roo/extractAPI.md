---
description: "【指令】提取后端接口 -> 深度DTO解析 -> 扩容筛选 (Step 1)"
---

- 读取上一任务生成的 project_config.json 获取源码路径

- 必须切换至 script engineer 模式开始

- 读取 2.后端API提取.md 中的逻辑

- 创建 step1_extract.py 脚本

- **核心指令一：深度 DTO 解析**
   - 必须递归解析 Java 实体类，生成饱满的 `smart_payload`。
   - 禁止生成空 Payload，否则视为失败。

- **核心指令二：Top 8 扩容筛选**
   - 实现 `filter_high_value_apis`。
   - 将筛选阈值设定为 **Top 8** 个资源组（如 User, Dept, Role, Post, Config, Menu, Dict, Notice）。
   - 目标是输出至少 **25-40 个** 高质量接口，为后续“多维度一致性测试”打好基础。

- 切换至 debugger 模式 执行脚本，生成 {work_dir}/apis.json

- 验证：检查 `apis.json` 中接口数量是否大于 20，且 `smart_payload` 非空。