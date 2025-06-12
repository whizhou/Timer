import re

class AIIntentResult:
    """AI意图识别结果数据类"""
    def __init__(self, intent_type: str, original_text: str):
        self.intent_type = intent_type
        self.original_text = original_text

class IntentClassifier:
    """意图分类器（重用你之前的代码）"""
    CREATE_PATTERNS = [r'创建', r'新建', r'添加', r'create', r'add', r'make']
    MODIFY_PATTERNS = [r'修改', r'更新', r'编辑', r'modify', r'update', r'edit']
    DELETE_PATTERNS = [r'删除', r'移除', r'去掉', r'delete', r'remove', r'del']

    @classmethod
    def classify_user_intent(cls, user_input: str) -> AIIntentResult:
        """
        分类用户意图（只做识别，不生成响应）
        
        参数:
            user_input: 用户输入的文本
            
        返回:
            AIIntentResult对象（总是返回意图结果，不直接生成响应）
        """
        normalized_input = user_input.lower()
        
        if cls._matches_pattern(normalized_input, cls.CREATE_PATTERNS):
            return AIIntentResult(intent_type="CREATE", original_text=user_input)
        
        if cls._matches_pattern(normalized_input, cls.MODIFY_PATTERNS):
            return AIIntentResult(intent_type="MODIFY", original_text=user_input)
        
        if cls._matches_pattern(normalized_input, cls.DELETE_PATTERNS):
            return AIIntentResult(intent_type="DELETE", original_text=user_input)
        
        return AIIntentResult(intent_type="GENERAL", original_text=user_input)

    @staticmethod
    def _matches_pattern(text: str, patterns: list) -> bool:
        """检查文本是否匹配任一意图模式"""
        return any(re.search(pattern, text) for pattern in patterns)