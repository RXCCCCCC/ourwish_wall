"""
文本过滤服务 - 敏感词检测
⚠️ 请根据实际需求添加或调整敏感词列表
"""


class TextFilter:
    """文本过滤器 - 用于敏感词检测和内容审核"""
    
    # ⚠️ 敏感词列表 - 请根据实际需求补充
    # 这里只提供示例, 实际使用时应该维护一个更完善的敏感词库
    SENSITIVE_WORDS = {
        # 示例敏感词 - 请根据实际情况调整
        '测试敏感词1',
        '测试敏感词2',
        # 可以添加更多...
    }
    
    # 替换字符
    REPLACE_CHAR = '*'
    
    @classmethod
    def contains_sensitive_words(cls, text):
        """
        检查文本是否包含敏感词
        
        Args:
            text: 待检查的文本
            
        Returns:
            bool: 如果包含敏感词返回 True, 否则返回 False
        """
        if not text:
            return False
        
        text_lower = text.lower()
        for word in cls.SENSITIVE_WORDS:
            if word.lower() in text_lower:
                return True
        return False
    
    @classmethod
    def filter_text(cls, text):
        """
        过滤文本中的敏感词 (用 * 替换)
        
        Args:
            text: 待过滤的文本
            
        Returns:
            str: 过滤后的文本
        """
        if not text:
            return text
        
        filtered_text = text
        for word in cls.SENSITIVE_WORDS:
            if word in filtered_text:
                filtered_text = filtered_text.replace(
                    word, 
                    cls.REPLACE_CHAR * len(word)
                )
        
        return filtered_text
    
    @classmethod
    def validate_content(cls, content, max_length=500):
        """
        验证内容是否合法
        
        Args:
            content: 待验证的内容
            max_length: 最大长度限制
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, '内容不能为空'
        
        if len(content) > max_length:
            return False, f'内容长度不能超过 {max_length} 字'
        
        if cls.contains_sensitive_words(content):
            return False, '内容包含敏感词, 请修改后重试'
        
        return True, None
    
    # ⚠️ 高级功能 (可选): 接入第三方内容审核 API
    """
    如果需要更完善的内容审核, 可以接入阿里云、腾讯云等平台的内容安全 API
    
    @classmethod
    def check_with_api(cls, text):
        '''
        使用第三方 API 进行内容审核
        '''
        # 示例代码 - 需要根据实际 API 文档实现
        import requests
        
        try:
            response = requests.post(
                'https://api.example.com/content-check',
                json={'text': text},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('is_safe', True), result.get('reason', '')
            
            return True, ''  # API 失败时默认通过
            
        except Exception as e:
            print(f'内容审核 API 调用失败: {e}')
            return True, ''  # 异常时默认通过
    """
