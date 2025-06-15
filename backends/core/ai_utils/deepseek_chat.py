class DeepSeekChat:
    def __init__(self):
        self._conversation_history = []
        self._dialog_pairs = []
        self.MAX_DIALOG_PAIRS = 10 
        self.TRIM_HISTORY_THRESHOLD = 15

    def _add_user_message(self, content: str):
        """添加用户消息到对话历史"""
        self._conversation_history.append({
            "role": "user",
            "content": content
        })
        self._dialog_pairs.append((len(self._conversation_history)-1, None))
        
        if len(self._dialog_pairs) > self.MAX_DIALOG_PAIRS:
            remove_success = self._remove_oldest_complete_pair()
            if not remove_success and len(self._dialog_pairs) > self.TRIM_HISTORY_THRESHOLD :
                self._trim_history()
            

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
        if not self._dialog_pairs or self._dialog_pairs[0][1] is None:
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

    @property
    def conversation_history(self):
        """只读属性访问对话历史"""
        return self._conversation_history.copy()