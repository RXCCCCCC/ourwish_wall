"""
AI 数字回响生成服务
当前实现: 基于规则库的 Mock 实现
⚠️ 如需接入真实 LLM (通义千问/文心一言), 请查看注释并修改相应代码
"""
import random


class AIService:
    """AI 回复生成服务"""
    
    # 红色文化语录库 - 按类别分类
    RESPONSE_LIBRARY = {
        '红色传承': [
            '星星之火，可以燎原。您的心愿是传承的火种。',
            '红色基因代代相传，您的愿望照亮前行的路。',
            '历史不会忘记，传承永不停歇，感谢您的守护。',
            '每一份对红色文化的热爱，都是对历史最好的致敬。',
            '薪火相传，生生不息，您的心愿温暖人心。',
            '铭记历史，开创未来，您的愿望振奋人心。',
            '传承红色精神，书写时代新篇，向您致敬！',
            '红色记忆，永不褪色，您的心愿意义深远。',
            '革命精神代代传，您的愿望值得铭记。',
            '历史的长河中，您的心愿闪耀着光芒。'
        ],
        '乡村建设': [
            '乡村振兴，未来可期，您的建议充满智慧。',
            '美好生活，从每一个心愿开始，感谢您的关注。',
            '建设美丽乡村，您的愿望让人温暖。',
            '乡村的未来因您的期盼而更加美好。',
            '每一份对家乡的热爱，都是建设的动力。',
            '振兴乡村，共创美好，您的心愿充满力量。',
            '绿水青山，美丽家园，期待您的愿望成真。',
            '乡村建设需要您这样的有心人，致敬！',
            '家乡的明天会更好，感谢您的关心。',
            '建设新农村，您的心愿指引方向。'
        ],
        '产业发展': [
            '科技赋能，产业兴旺，您的想法很有远见。',
            '创新驱动发展，您的愿望充满希望。',
            '产业振兴，富民强县，您的建议值得推广。',
            '发展的道路上，您的心愿是前进的动力。',
            '经济腾飞，未来可期，感谢您的智慧分享。',
            '产业兴则百姓富，您的愿望令人振奋。',
            '创新发展，您的心愿为德兴增添活力。',
            '产业升级的路上，需要您这样的智者。',
            '共同富裕，从每一个好想法开始。',
            '发展产业，造福百姓，您的心愿很有价值。'
        ],
        '生态环保': [
            '绿水青山就是金山银山，您的愿望让人敬佩。',
            '守护生态，功在千秋，感谢您的环保之心。',
            '生态文明建设，您的心愿意义重大。',
            '保护环境，从每一个心愿开始。',
            '绿色发展，您的愿望为地球添彩。',
            '生态德兴，美丽家园，您的心愿充满温情。',
            '环保路上，您的坚持让人感动。',
            '守护碧水蓝天，您的愿望值得称赞。',
            '生态优先，绿色发展，向您致敬！',
            '美丽中国梦，从您的心愿开始。'
        ],
        'default': [
            '您的心愿已被数字时光记录，愿未来如您所愿。',
            '科技让愿望永存，您的心声我们听到了。',
            '数字传承，连接过去与未来，感谢您的分享。',
            '每一个心愿都值得被铭记，您的愿望很美好。',
            '在数字世界里，您的心愿永不消逝。',
            '红土地上的愿望，终将开花结果。',
            '德兴的未来因您的期盼而更加光明。',
            '心愿汇聚成光，照亮前行的路。',
            '您的愿望是建设德兴的宝贵财富。',
            '感谢您对德兴的热爱与期盼。'
        ]
    }
    
    @classmethod
    def generate_response(cls, wish_content, category):
        """
        生成 AI 数字回响
        
        Args:
            wish_content: 心愿内容
            category: 心愿类别
            
        Returns:
            str: 生成的回复文本
        """
        # 阶段一: 基于规则库的实现
        responses = cls.RESPONSE_LIBRARY.get(category, cls.RESPONSE_LIBRARY['default'])
        return random.choice(responses)
    
    # ⚠️ 阶段二: 接入真实 LLM API (可选实现)
    # 如果要使用通义千问或文心一言, 请取消下方注释并配置 config.py 中的 API 密钥
    """
    @classmethod
    def generate_response_with_llm(cls, wish_content, category):
        '''
        使用 LLM API 生成回复 (需要配置 API Key)
        
        示例: 通义千问 API 调用
        '''
        from config import Config
        import requests
        
        if not Config.AI_SERVICE_ENABLED or not Config.AI_API_KEY:
            # 如果未启用或未配置, 回退到规则库
            return cls.generate_response(wish_content, category)
        
        try:
            # ⚠️ 以下是通义千问 API 的示例代码, 需要根据实际 API 文档调整
            prompt = f'''用户是一个关注德兴发展的建设者,他许愿说: "{wish_content}"。
请以"数字红色助手"的身份,用温暖、充满希望的语气写一句简短的回复(30字以内)。'''
            
            headers = {
                'Authorization': f'Bearer {Config.AI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'qwen-turbo',  # 模型名称
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 100,
                'temperature': 0.7
            }
            
            response = requests.post(
                Config.AI_API_ENDPOINT,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_reply = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                if ai_reply:
                    return ai_reply.strip()
            
            # API 调用失败, 回退到规则库
            return cls.generate_response(wish_content, category)
            
        except Exception as e:
            print(f'AI API 调用失败: {e}')
            # 发生异常, 回退到规则库
            return cls.generate_response(wish_content, category)
    """
