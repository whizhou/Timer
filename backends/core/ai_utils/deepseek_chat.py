class DeepSeekChat:
    def __init__(self):
        self._conversation_history = []
        self._dialog_pairs = []
        self.MAX_DIALOG_PAIRS = 5 
        self.TRIM_HISTORY_THRESHOLD = 15

    def _add_user_message(self, content: str):
        """添加用户消息到对话历史"""
        self._conversation_history.append({
            "role": "user",
            "content": content
        })
        
        if len(self._dialog_pairs)+1 > self.MAX_DIALOG_PAIRS:
            remove_success = self._remove_oldest_complete_pair()
            if not remove_success and len(self._dialog_pairs)+1 > self.TRIM_HISTORY_THRESHOLD :
                self._trim_history()
        
        self._dialog_pairs.append((len(self._conversation_history)-1, None))
            

    def _add_assistant_message(self, content: str):
        """添加历史回答消息到对话历史"""
        self._conversation_history.append({
            "role": "assistant",
            "content": content
        })
        if self._dialog_pairs and self._dialog_pairs[-1][1] is None:
            user_idx = self._dialog_pairs[-1][0]
            self._dialog_pairs[-1] = (user_idx, len(self._conversation_history)-1)

    def _remove_oldest_complete_pair(self) -> bool:
        if not self._dialog_pairs:
            print("删除最远的对话对失败")
            return False
        
        if self._dialog_pairs[0][1] is None:
            print("删除最远的对话对失败")
            return False
        
        start, end = self._dialog_pairs.pop(0)
        del self._conversation_history[start:end+1]

        offset = end - start + 1
        self._dialog_pairs = [
            (new_start - offset, new_end - offset)
            for new_start, new_end in self._dialog_pairs
        ]
        return True
    
    def _trim_history(self):
        """实在无法缩减时，截断最旧消息的内容"""
        while len(self._dialog_pairs) > self.MAX_DIALOG_PAIRS:
            start, end = self._dialog_pairs.pop(0)
            del self._conversation_history[start:end+1]

            offset = end - start + 1
            self._dialog_pairs = [
                (new_start - offset, new_end - offset)
                for new_start, new_end in self._dialog_pairs
            ]
        return True
    
    def _show_history(self):
        """输出最新的对话内容"""
        print("\n========输出最新对话历史===============\n")
        message = self._conversation_history[-2]
        print(f"role :{message.get('role')}")
        print(f"content: { message.get('content')}"[:200])
        
        print()
        message = self._conversation_history[-1]
        print(f"role :{message.get('role')}")
        print(f"content: { message.get('content')}"[:200])

        print("\n=========结束输出========")

    def _check_dialog_pairs(self):
        """检查并输出_dialog_pairs中的所有对话对"""
        print("\n===== 开始检查_dialog_pairs =====")
        print(f"当前对话历史长度: {len(self._conversation_history)}")
        print(f"当前对话对数量: {len(self._dialog_pairs)}")

        (user_idx, assistant_idx) = self._dialog_pairs[0]

        # 检查用户消息
        if 0 <= user_idx < len(self._conversation_history):
            user_msg = self._conversation_history[user_idx]
            if user_msg['role'] == 'user':
                print(f"(有效) - 内容: {user_msg['content'][:50]}...")
            else:
                print(f"(无效 - 角色不是user)")
        else:
            print(f"(无效 - 索引越界)")

        # 检查助手消息
        print(f"助手消息索引: {assistant_idx}", end=" ")
        if assistant_idx is None:
            print("(未完成对话对)")
        elif 0 <= assistant_idx < len(self._conversation_history):
            assistant_msg = self._conversation_history[assistant_idx]
            if assistant_msg['role'] == 'assistant':
                if not assistant_msg['content'] == None :
                    print(f"(有效) - 内容: {str(assistant_msg['content'])[:100]}...")
                else :
                    print(f"角色内容为空")
            else:
                print(f"(无效 - 角色不是assistant)")
        else:
            print(f"(无效 - 索引越界)")
            
        
        # for i, (user_idx, assistant_idx) in enumerate(self._dialog_pairs, 1):
        #     print(f"\n对话对 #{i}:")
        #     print(f"用户消息索引: {user_idx}", end=" ")
            
        #     # 检查用户消息
        #     if 0 <= user_idx < len(self._conversation_history):
        #         user_msg = self._conversation_history[user_idx]
        #         if user_msg['role'] == 'user':
        #             print(f"(有效) - 内容: {user_msg['content'][:50]}...")
        #         else:
        #             print(f"(无效 - 角色不是user)")
        #     else:
        #         print(f"(无效 - 索引越界)")
            
        #     # 检查助手消息
        #     print(f"助手消息索引: {assistant_idx}", end=" ")
        #     if assistant_idx is None:
        #         print("(未完成对话对)")
        #     elif 0 <= assistant_idx < len(self._conversation_history):
        #         assistant_msg = self._conversation_history[assistant_idx]
        #         if assistant_msg['role'] == 'assistant':
        #             if not assistant_msg['content'] == None :
        #                 print(f"(有效) - 内容: {str(assistant_msg['content'])[:100]}...")
        #             else :
        #                 print(f"角色内容为空")
        #         else:
        #             print(f"(无效 - 角色不是assistant)")
        #     else:
        #         print(f"(无效 - 索引越界)")
        
        print("===== 检查完成 =====\n")
        

    @property
    def conversation_history(self):
        """只读属性访问对话历史"""
        return self._conversation_history.copy()