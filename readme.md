# 项目简介

## 虚拟机镜像

账号:debian<br>
密码:debian

mysql:<br>
账号:root<br>
密码:root

使用步骤:
1. 用wmare打开虚拟机
2. 登录debian用户
3. ip ad查看一下ip地址，保证虚拟机可以联网（我没有装ipconfig）
4. 在~/RuoYi-Vue/ruoyi-admin下面运行 `mvn spring-boot:run`
![alt text](image/image.png)
看到这个就是成功了
5. 然后用物理机或者虚拟机可以连通该虚拟机的机器的浏览器访问 `http://ip/即可
![alt text](/image/image1.png)

## CoStrict Ai使用说明
 ![alt text](/image/image3.png)
 在vs  code上进行下载

 使用说明连接:[COSTRICT 入门文档](https://docs.costrict.ai/guide/feature)

## 基础功能
1. 智能对话
2. 代码自动补全，需要先关闭vs自带的AI,不然会被屏蔽掉
![alt text](/image/image4.png)
3. 可以右键进行主动执行

## 有关自动化测试流程的功能

1. Strict Mode严肃编程模式
会自动检测文本的任务单，接着会自动化执行任务流程
2. Rules
可以添加自定义说明
* 工作区rules：仅适用于当前项目，若与全局rules存在冲突，优先于全局规则。
目录(.roo/rules)
```
├── .roo/

│ └── rules/ \# 工作区全局规则

│ ├── 01-general.md

│ └── 02-coding-style.txt

└── ... (其他项目文件)
```
* 特定模式rules：仅适用于特定模式（例如code模式）。
目录 (.roo/rules-{modeSlug}/).
```
├── .roo/

│ └── rules-code/ \# code模式规则

│ ├── 01-js-style.md

│ └── 02-ts-style.md

└── ... (其他项目文件)
```
3. Todo List
这是一个待办事项表，可以通过这个来定义AI的工作流，他会自动检测，我们需要在任务描述文档里添加即可

4. Prompt提示词
5. MCP
模型上下文协议 (MCP) 是一个通过连接外部工具和服务器来扩展 CoStrict 能力的标准。MCP 服务器提供额外的工具和资源，帮助 CoStrict 完成超出其内置功能的任务，例如访问数据库、自定义 API 和专用功能。
6. 斜杠命令
使用简单的 Markdown 文件创建自定义斜杠命令，以自动化重复任务并扩展 CoStrict 的功能。
快速开始在聊天中输入 / 来选择命令。要创建或管理命令，请打开 设置 > 斜杠命令。您仍然可以将命令存储在 .roo/commands/（项目）或 ~/.roo/commands/（全局）中。