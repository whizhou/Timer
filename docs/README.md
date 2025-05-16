主要存放开发过程中的各种文档，如需求文档、协作开发手册、P/R 工作流教程等。

开始开发前请先阅读 [Dev_Guide.md](./Dev_Guide.md)

[PR_WorkFlow.md](/docs/PR_WorkFlow.md) 使用 Deepseek 生成，目前只作参考。

[schedule_format.json](./schedule_format.json) 包含了日程存储的具体格式，也是后端接受和返回的日程 json 格式，大致格式为 Additional Infomation + Main Content。日程分为两类：

+ "schedule": 日程，持续一段时间，如一门课，一次会议；
+ "reminder": 提醒事项，一个截止时间，如 DDL。
