"""
AI 服務模組 - Campus Help (最終穩定版)
修正：
1. 使用穩定模型 gemini-2.0-flash
2. 降低 AI 溫度避免過度優化
3. 加強 Prompt 約束力
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 🔧 Demo 模式開關
DEMO_MODE = False  # False 關閉 Demo 模式

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  警告: google-generativeai 未安裝，AI 功能將使用模擬模式")


class AIService:
    """AI 服務類別"""
    
    # 敏感關鍵字清單
    DANGER_KEYWORDS = {
        'critical': [
            '代考', '代寫', '代寫報告', '代寫作業', '幫寫報告',
            '代購菸', '代購酒', '代買菸', '代買酒', '買菸', '買酒',
            '借錢', '貸款', '放貸', '高利貸', '借款', '急需用錢',
            '色情', '援交', '約炮', '一夜情', '陪睡',
            '毒品', '大麻', '搖頭丸', 'K他命',
            '賭博', '線上賭場', '簽賭', '六合彩'
        ],
        'high': [
            '幫寫', '幫做作業', '期末報告', '期中考', '考試答案',
            '成人', '18禁', '裸露', '性感',
            '現金交易', '大量現金', '匯款', '轉帳',
            '非法', '違法', '犯罪', '詐騙'
        ],
        'medium': [
            '代買', '代購', '代領', '幫買東西',
            '深夜', '半夜', '凌晨',
            '陪伴', '陪聊', '陪吃飯',
            '私人住處', '家裡', '宿舍房間'
        ]
    }
    
    def __init__(self):
        """初始化 AI 服務"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if DEMO_MODE:
            print("⚠️ AI Demo 模式已啟用（不呼叫真實 API）")
            return
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    'gemini-2.0-flash',
                    generation_config={'temperature': 0.5}
                )
                print("✅ Gemini AI 已啟用 (gemini-2.0-flash, temperature=0.3)")
            except Exception as e:
                print(f"⚠️  Gemini 初始化失敗: {e}")
                self.model = None
        else:
            print("⚠️  Gemini API Key 未設定，使用模擬模式")
    
    @staticmethod
    def optimize_task_description(description):
        """優化任務描述（保守版，避免過度腦補）"""
        if DEMO_MODE:
            return {
                'success': True,
                'optimized_description': f"{description}\n\n✨ **AI 優化建議（Demo 模式）**：\n• 建議加上具體時間需求（例：週三下午2點）\n• 建議說明任務難度與所需技能\n• 建議提供聯絡方式或集合地點"
            }
        
        service = AIService()
        
        if not service.model:
            return {
                'success': True,
                'optimized_description': f"{description}\n\n💡 [AI 建議] 可以補充任務的具體要求、注意事項或期望成果，讓幫助者更容易理解。"
            }
        
        try:
            # 🔧 修改：加強 Prompt 約束，避免過度優化
            prompt = f"""
你是一個任務描述優化助手。請**謹慎優化**以下任務描述，保持原意並補充必要資訊。

【原始描述】
{description}

【優化規則】
1. ✅ **保持原意**：不要改變任務本質和內容
2. ✅ **補充細節**：可以適度補充任務的具體要求、注意事項或期望成果
3. ✅ **簡潔表達**：優化後的長度不超過原文的 1.3 倍
4. ❌ **禁止腦補**：不要編造日期、地址、金額、飲料口味等具體細節
5. ❌ **禁止誇飾**：不要加入「急需」「動作快」「準時」等誇張用詞
6. ❌ **禁止提及**：不要提「時間」「地點」「報酬」「點數」（這些已在表單其他欄位填寫）

【輸出格式】
直接輸出優化後的描述，不要加前綴或說明。如果原描述已經很清楚，可以只做微調。

【範例】
輸入：週三下午幫我買便當買飲料
輸出：幫忙購買午餐便當和飲料，希望能順便幫忙確認店家營業時間

現在請優化上面的任務描述：
"""
            
            response = service.model.generate_content(prompt)
            optimized = response.text.strip()
            
            '''
            # 🔧 防呆機制：如果優化結果太長（超過 2 倍），才返回建議
            if len(optimized) > len(description) * 2.0:
                return {
                    'success': True,
                    'optimized_description': f"{description}\n\n💡 **AI 建議**：可以補充具體時間、地點和預算，讓幫助者更容易評估。"
                }
            '''
            
            return {
                'success': True,
                'optimized_description': optimized
            }
        
        except Exception as e:
            print(f"AI 優化失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def risk_assessment(description, category):
        """任務風險審查"""
        service = AIService()
        
        # 關鍵字檢測（不變）
        critical_flags = []
        high_flags = []
        medium_flags = []
        
        desc_lower = description.lower()
        
        for keyword in service.DANGER_KEYWORDS['critical']:
            if keyword in desc_lower:
                critical_flags.append(keyword)
        
        for keyword in service.DANGER_KEYWORDS['high']:
            if keyword in desc_lower:
                high_flags.append(keyword)
        
        for keyword in service.DANGER_KEYWORDS['medium']:
            if keyword in desc_lower:
                medium_flags.append(keyword)
        
        if critical_flags:
            return {
                'success': True,
                'data': {
                    'risk_level': 'critical',
                    'risk_score': 1.0,
                    'recommendation': '自動拒絕',
                    'reason': f'偵測到嚴重違規內容：{", ".join(critical_flags[:3])}',
                    'flags': critical_flags,
                    'can_appeal': False,
                    'warning': '⚠️ 嚴重違規：此任務涉及違反校規或法律，已被系統自動拒絕。'
                }
            }
        
        if high_flags:
            return {
                'success': True,
                'data': {
                    'risk_level': 'high',
                    'risk_score': 0.8,
                    'recommendation': '需人工審核',
                    'reason': f'偵測到高風險內容：{", ".join(high_flags[:3])}',
                    'flags': high_flags,
                    'can_appeal': True,
                    'warning': '⚠️ 高風險：任務已送交人工審核，如有誤判可點擊「申訴」按鈕。'
                }
            }
        
        if medium_flags:
            return {
                'success': True,
                'data': {
                    'risk_level': 'medium',
                    'risk_score': 0.5,
                    'recommendation': '警告但允許',
                    'reason': f'偵測到需注意事項：{", ".join(medium_flags[:3])}',
                    'flags': medium_flags,
                    'can_appeal': True,
                    'warning': '⚠️ 溫馨提醒：請確保任務內容合法且安全，避免私下金錢交易或深夜見面。'
                }
            }
        
        if DEMO_MODE or not service.model:
            return {
                'success': True,
                'data': {
                    'risk_level': 'safe',
                    'risk_score': 0.1,
                    'recommendation': '自動通過',
                    'reason': '未發現明顯風險',
                    'flags': [],
                    'can_appeal': False,
                    'warning': None
                }
            }
        
        # AI 語意分析（不變）
        try:
            prompt = f"""
你是一個內容安全審查專家。請評估以下任務是否違反平台規範。

任務分類：{category}
任務描述：
{description}

平台禁止事項：
1. 代考、代寫報告（違反學術誠信）
2. 代購菸酒、成人內容（法律限制）
3. 金錢借貸相關（超出服務範圍）
4. 危險或違規活動（安全考量）
5. 深夜私人場所見面（安全風險）

請以 JSON 格式回應：
{{
  "risk_level": "safe/low/medium/high/critical",
  "risk_score": 0.0-1.0,
  "recommendation": "自動通過/警告但允許/需人工審核/自動拒絕",
  "reason": "簡短說明",
  "flags": ["風險標記列表"],
  "hidden_risk": "是否有隱藏的違規暗示"
}}

只輸出 JSON，不要其他文字。
"""
            
            response = service.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            import json
            data = json.loads(result_text)
            data['can_appeal'] = data['risk_level'] in ['medium', 'high']
            
            return {
                'success': True,
                'data': data
            }
        
        except Exception as e:
            print(f"AI 風險審查失敗: {e}")
            return {
                'success': True,
                'data': {
                    'risk_level': 'safe',
                    'risk_score': 0.2,
                    'recommendation': '自動通過',
                    'reason': 'AI 審查暫時無法使用，已通過關鍵字檢測',
                    'flags': [],
                    'can_appeal': False
                }
            }
    
    @staticmethod
    def parse_task_description(description):
        """解析任務描述（保留，但可選用）"""
        if DEMO_MODE:
            return {
                'success': True,
                'data': {
                    'required_skills': ['通用技能'],
                    'estimated_time': '未指定',
                    'location_type': '實體',
                    'urgency': 'normal'
                }
            }
        
        service = AIService()
        
        if not service.model:
            return {
                'success': True,
                'data': {
                    'required_skills': ['通用技能'],
                    'estimated_time': '未指定',
                    'location_type': '實體',
                    'urgency': 'normal'
                }
            }
        
        try:
            prompt = f"""
請分析以下任務描述，提取關鍵資訊。

任務描述：
{description}

請以 JSON 格式回應：
{{
  "required_skills": ["所需技能列表"],
  "estimated_time": "預估時長",
  "location_type": "實體/線上/混合",
  "urgency": "low/normal/high",
  "key_points": ["關鍵要點列表"]
}}

只輸出 JSON，不要其他文字。
"""
            
            response = service.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            import json
            data = json.loads(result_text)
            
            return {
                'success': True,
                'data': data
            }
        
        except Exception as e:
            print(f"AI 解析失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }


if __name__ == '__main__':
    print("測試 AI 服務...")
    
    # 測試 1: 安全任務
    print("\n1. 測試安全任務:")
    result = AIService.risk_assessment("幫忙搬宿舍行李，約20分鐘", "日常支援")
    print(f"   風險等級: {result['data']['risk_level']}")
    print(f"   建議: {result['data']['recommendation']}")
    
    # 測試 2: 嚴重違規
    print("\n2. 測試嚴重違規:")
    result = AIService.risk_assessment("幫我代考期末考", "學習互助")
    print(f"   風險等級: {result['data']['risk_level']}")
    print(f"   建議: {result['data']['recommendation']}")
    print(f"   可申訴: {result['data']['can_appeal']}")
    
    # 測試 3: AI 優化描述
    print("\n3. 測試 AI 優化:")
    result = AIService.optimize_task_description("週三下午幫我買便當買飲料")
    if result['success']:
        print(f"   優化結果: {result['optimized_description']}")