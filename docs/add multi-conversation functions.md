# add multi-conversation functions

本次更新说明：

1. **deepseek_chat.py**：是新建的包含一个管理对话上下文的类。其中的常量值有待商榷，测试者可以尝试更改。
    1. （而且采用的是删除的时候重建整个_dialog_pairs列表的形式，可以考虑将_conversation_history, _dialogs_pairs改为更高效的数据结构：比如队列）
    
2. **ai_scheduler.py**：
    1. 更新了内部逻辑，修正了相关代码错误。采用了在处理函数中将deepseek_api所需message打包好传递的方式。
    2. 同时更新了`user_input`为Dict，但是大部分依然是简单转换为str的`user_input`处理。
    
    （其中，通用对话没有传递进入历史记录中，如果需要的话，可以仿照上述处理日志意图调用deepseek_chat类的相应两个函数即可。）
    
    （如果后续对`user_input`的Dict类型需要改进的话，还需要再加以调整）
    
3. **ai_scheduler_manager.py**：
    1. 调整了处理函数的参数类型，从接受用户输入，改为了直接接收调用deepseek_api接口时的  ”message”项`prompt_content`。
    2. 同时将`system_prompt`与对话历史分开，使deepseek_api接口能更明晰自己的职责。
    
4. **intent_classifier.py**：
    1. 根据预设的`user_input`的Dict类型进行调整和改进了。如果预设的三个键缺少的话就会出问题。
    2. （如果需要调整，可以直接转`user_input`为str类型的user_text然后交给`intent_classifier`进行识别）
5. **prompt_generator.py**
    1. 修改的响应更改为返回`original`和`modified`的完整日志的json形式，便于前后端接口。

关于问题（就是你给我response后，我选择哪部分留下来作为上文）的回答：

目前的deepseek_api的设定是能基本完成的，对应的response即使只是json，然后直接压入历史对话列表`_conversation_history`，也是符合对话的形式，是合理的message形式。

个人认为：

1. 如果对response需要补充部分信息的话，可以考虑加一个操作类型的键。
    1. 比如delete的`deletion_result` = {id, title}，可以考虑assistant_message = `f”delete, {deletion}”`
2. 或者什么都不做，因为对话包含user和assistant两个方面，其实不必要添加更多的项，直接把response丢回去就好（更倾向这个）