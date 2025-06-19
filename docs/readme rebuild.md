# ai_scheduler.py

注：ai_scheduler.py 与 ai_scheduler2.py并没有结构不同，唯一不同的点在于我三种处理函数中，在ai_scheduler2.py尝试了调用日程库的接口函数。但是好像不是很有效。

- 接口与功能：
    - _setup_intent_handlers
    - process_user_request
        
        主接口，用于处理用户输入请求的主入口函数；
        
        先调用**intent_classifie**r类识别关键词，
        
        if 匹配的情况下直接进入对应日程相应函数。
        
        else 调用本类的**`_handle_general_intent`**处理。
        
        日程相关的对话返回Dict：
        
        1. CREATE返回：创建日程的类型，标题，开始时间（如果有），结束时间，（提醒开始时间，提醒提前时间）
        2. MODIFY返回：原日程信息original字段，修改后的日程信息modified字段
        3. DELETE返回：将要删除的日程id，相应日程的标题
        
        通用问答返回str：
        
    - _handle_create_intent
        
        prompt来自GeneratePrompt的**`_parse_creation`**
        
        调用的是AIScheduleManager的**`_handle_creation_response`**
        
        主要是**`schedule_data`**字段
        
    - _handle_modify_intent
        
        prompt来自GeneratePrompt的**`_parse_modification`**
        
        调用的是AIScheduleManager的**`_handle_modification_response`**
        
        主要是**`original`**和**`modified`** 字段
        
    - _handle_delete_intent
        
        prompt来自GeneratePrompt的**`_parse_delete`**
        
        调用的是AIScheduleManager的**`_handle_deletion_response`**
        
        主要是**`schedule_id`**和**`schedule_title`**
        
    - _handle_general_intent
        
        调用**AIScheduleManager**类中的**`analyze_semantic_intent`** 进行语义分析。
        
        根据语义的分析结果，如果为日程相关的三种模式则调用上述三个处理函数。
        
        如果分析结果为**“GENERAL”**，那么调用**`_handle_conservation_intent`**
        
    - _handle_conservation_intent
        
        prompt来自GeneratePrompt的**`_generate_general_prompt`**
        
        调用的是AIScheduleManager的**`_handle_general_respond`**

# zhm_test.py

我在这里使用的是 **`ai_scheduler2.py`** 如果先不使用日程库可以修改为**`ai_scheduler.py`**

- FIXME:
    
    我的copilot在帮我修改测试函数的时候，对于**`create_schedule`**的赋值id失败的情况，它试图修改**`schedule_manager.py`**中的函数，但是我没有改动对应代码。
    
    而且我也不是很清楚怎么给日程库添加一些已有日程来进行测试。
    
    所以测试效果并不是很好，有些时候会识别不到。如果有任何问题可以直接修动我的测试代码结构。