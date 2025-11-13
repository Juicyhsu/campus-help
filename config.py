"""
配置檔案 - Campus Help (更新版)
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """應用配置"""
    
    # 應用資訊
    APP_NAME = "Campus Help"
    APP_SLOGAN = "有空幫一下，校園時間銀行"
    VERSION = "2.0 Streamlit Enhanced"
    
    # 資料庫
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///campus_help.db')
    
    # Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # 任務分類
    CATEGORIES = [
        "日常支援",
        "學習互助", 
        "校園協助",
        "技能交換",
        "情境陪伴"
    ]
    
    # 🔧 新增：校區選項 + 校外
    CAMPUSES = [
        "外雙溪校區",
        "城中校區",
        "校外",  # 新增
        "線上"
    ]
    
    # 點數範圍
    POINTS_MIN = 10
    POINTS_MAX = 500
    POINTS_DEFAULT = 50
    
    # 媒合權重
    MATCHING_WEIGHTS = {
        'skill': 0.4,
        'time': 0.2,
        'rating': 0.2,
        'location': 0.2
    }
    
    # 🔧 更新：安全關鍵字（與 AI Service 同步）
    DANGER_KEYWORDS = {
        'critical': [
            '代考', '代寫', '代寫報告', '代寫作業',
            '代購菸', '代購酒', '代買菸', '代買酒',
            '借錢', '貸款', '放貸', '高利貸',
            '色情', '援交', '約炮',
            '毒品', '大麻', '搖頭丸',
            '賭博', '線上賭場'
        ],
        'high': [
            '幫寫', '幫做作業', '期末報告', '期中考',
            '成人', '18禁', '裸露',
            '現金交易', '大量現金', '匯款',
            '非法', '違法', '犯罪', '詐騙'
        ],
        'medium': [
            '代買', '代購', '代領',
            '深夜', '半夜', '凌晨',
            '陪伴', '陪聊',
            '私人住處', '家裡', '宿舍房間'
        ]
    }
    
    # 🔧 新增：平台警語
    PLATFORM_WARNING = """
    ⚠️ **平台使用警語**
    
    **重要提醒：**
    本平台僅提供媒介服務，所有交易由使用者自行負責。請雙方仔細評估確認再行接洽，注意安全以避免糾紛。

    1. **嚴禁事項**：
    以下行為將導致永久停權：
       - 代考、代寫作業報告、學術不誠信
       - 代購菸酒、毒品等違禁品
       - 涉及金錢借貸、詐騙
       - 色情、賭博相關任務
       - 其他違法或危害他人行為

    2. **安全提醒**：
       - 避免深夜或私人場所見面
       - 避免私下大額現金交易
       - **如遇可疑任務，請立即檢舉**

        **📞 聯絡平台方式：**
        (待定)
    
    3. **違規處理**：
       - 初次違規：警告並暫停服務 7 天
       - 重複違規：永久停權並留存紀錄
       - 嚴重違規：移送校方或法律單位處理
    
    4. **人工審核**：
       - 高風險任務將進入人工審核流程
       - 如認為系統誤判，可點擊「申訴」按鈕
       - 申訴將由真人審核，1-3 個工作天回覆
       - 如有緊急需求，請於服務時間連繫平台
    
    ✅ 使用平台即表示您已閱讀並同意以上條款
    """


if __name__ == '__main__':
    print("配置資訊:")
    print(f"應用名稱: {Config.APP_NAME}")
    print(f"版本: {Config.VERSION}")
    print(f"資料庫: {Config.DATABASE_URL}")
    print(f"Gemini API: {'已設定' if Config.GEMINI_API_KEY else '未設定'}")
    print(f"\n校區選項: {', '.join(Config.CAMPUSES)}")