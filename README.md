🎓 Campus Help - 校園共享幫幫平台
有空幫一下，校園時間銀行
東吳大學校園互助平台 - 讓學生透過點數交換技能與服務


📖 專案簡介
Campus Help（校園共享幫幫平台） 是一個基於「時間銀行」概念的校園互助系統，讓東吳大學學生能夠透過點數經濟，交換彼此的技能、時間和服務。平台整合 Google Gemini AI 進行智慧安全審查與任務推薦，並提供完善的三層安全機制，打造安全、高效、有溫度的校園共享經濟。
🎯 核心理念

互助共享：將閒置時間轉化為互助資源
技能交換：用自己擅長的幫助需要的人
安全保障：AI 審查 + 身份驗證 + 交易保護
信任建立：評分系統建立校園信任網絡


✨ 核心功能
🛡️ 三層安全機制

身份驗證層

東吳大學學校信箱驗證（@scu.edu.tw）
校區、科系、年級資訊確認
防止外部人員進入


AI 內容審查層

Google Gemini AI 自動風險評估
多級關鍵字檢測（嚴重違規/高風險/中等風險）
語意分析識別隱藏違規內容
自動攔截：代考、代購菸酒、金錢借貸、危險活動


交易保護層

發布任務時預扣點數（防跑單）
完成確認後才轉移點數
5 天自動完成機制（防止惡意不確認）
爭議申訴系統



🤖 AI 智慧功能

智慧任務推薦：基於技能、時間、地點、評分的多維度匹配算法
任務描述優化：AI 協助優化任務描述，提高媒合成功率
風險分級審查：

🟢 安全（自動通過）
🟡 低風險（自動通過 + 提醒）
🟠 中等風險（警告但允許發布）
🔴 高風險（需人工審核 + 可申訴）
⛔ 嚴重違規（自動拒絕 + 不可申訴）



📋 任務管理

發布任務：

標題、描述、分類、地點、校區
任務預定日期、開始時間、預估時長
點數設定（10-500 點）
急件標記
AI 優化建議


申請任務：

瀏覽所有開放任務
查看發布者資訊（評分、完成數、信任值）
一鍵申請
追蹤申請狀態


任務狀態：

🟢 開放中（Open）
🟡 進行中（In Progress）
✅ 已完成（Completed）
❌ 已取消（Cancelled）



⭐ 評價系統

任務完成後雙向評價（1-5 星 + 評論）
自動計算平均評分
信任值動態更新（評分 70% + 完成率 30%）
評價記錄永久保存

🛠️ 技能管理

自訂技能標籤
快速選擇常用技能（攝影、程式設計、搬運等）
技能匹配提升推薦精準度

📊 平台統計

總使用者數、總任務數、完成率
任務狀態分布（圓餅圖）
任務分類統計（長條圖）
校區活躍度分析
Top 3 活躍使用者排行榜


🏗️ 技術架構
前端

Streamlit 1.28+：快速建構互動式 Web 應用
Plotly：資料視覺化圖表
自訂 CSS：精美的介面設計

後端

SQLAlchemy：ORM 資料庫管理
SQLite：輕量化資料庫
Python 3.8+：核心邏輯開發

AI 整合

Google Gemini AI (gemini-2.5-flash)：

內容風險評估
任務描述優化
語意分析
Temperature = 0.5（平衡創造力與準確性）



資料庫設計
users (使用者)
├── id, email, name, department, grade, campus
├── skills (JSON), points, avg_rating, completed_tasks, trust_score
└── willing_cross_campus, status, created_at

tasks (任務)
├── id, title, description, category, location, campus
├── points_offered, is_urgent, status
├── accept_deadline, task_start_time, task_duration
├── publisher_id, accepted_user_id, accepted_at
├── helper_notified_completion, created_at, completed_at
└── relationships: publisher, accepted_user

task_applications (申請記錄)
├── id, task_id, applicant_id
├── status (pending/accepted/rejected)
└── applied_at

reviews (評價)
├── id, task_id, reviewer_id, reviewee_id
├── rating (1.0-5.0), comment
└── created_at

🚀 快速開始
環境需求

Python 3.8 或以上
pip 套件管理器
Google Gemini API Key（免費版即可）

安裝步驟

克隆專案

bashgit clone https://github.com/yourusername/campus-help.git
cd campus-help

建立虛擬環境

bashpython -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

安裝依賴套件

bashpip install -r requirements.txt

設定環境變數

建立 .env 檔案：
envGEMINI_API_KEY=your_gemini_api_key_here

🔑 取得 Gemini API Key：https://ai.google.dev/


初始化資料庫

bashpython database.py
這會建立測試資料，包含：

4 位測試使用者
6 個範例任務


啟動應用程式

bashstreamlit run app.py
```

應用程式將在 `http://localhost:8501` 啟動

---

## 📁 專案結構
```
campus-help/
├── app.py                  # 主應用程式（Streamlit UI）
├── database.py             # 資料庫模型與操作
├── ai_service.py          # AI 服務（Gemini 整合）
├── matching_engine.py     # 智慧媒合演算法
├── config.py              # 設定檔（分類、校區等）
├── requirements.txt       # Python 依賴套件
├── .env                   # 環境變數（需自行建立）
├── campus_help.db         # SQLite 資料庫（自動生成）
└── README.md              # 專案說明文件
```

---

## 🎮 使用指南

### 1. 選擇使用者身份

在側邊欄選擇測試使用者：
- 王小美（資管系）
- 李大明（企管系）
- 陳小華（英文系）
- 張志明（數學系）

### 2. 發布任務

1. 點擊「➕ 發布任務」
2. 填寫任務資訊：
   - 標題、描述、分類、地點、校區
   - 任務預定日期、開始時間、時長
   - 提供點數（會從你的帳戶預扣）
3. （可選）點擊「🤖 AI 優化描述」改善文案
4. 點擊「🚀 發布任務」
5. 系統會進行 AI 安全審查

### 3. 申請任務

1. 在「🏠 首頁」瀏覽任務
2. 使用篩選器（分類、校區、關鍵字）
3. 查看任務詳情與發布者資訊
4. 點擊「✅ 申請任務」

### 4. 管理任務

**我發布的任務**：
- 查看申請者列表
- 接受適合的申請者（任務進入「進行中」）
- 確認任務完成（點數轉移給幫助者）
- 若有爭議可點擊「申訴」

**我接的任務**：
- 查看任務狀態
- 完成後點擊「📢 通知已完成任務」（黃色按鈕）
- 等待發布者確認（或 5 天後自動完成）

### 5. AI 智慧推薦

點擊「🤖 AI 推薦」查看：
- 個人化推薦任務（基於技能、地點、評分）
- 媒合度百分比
- 推薦理由分析
- 權重分布圖表

### 6. 評價與信任

任務完成後：
1. 雙方可互相評價（1-5 星 + 評論）
2. 評分影響平均評價與信任值
3. 信任值計算：評分 70% + 完成率 30%

---

## 🔐 安全機制詳解

### AI 風險評估流程
```
使用者提交任務描述
        ↓
第一階段：關鍵字檢測
├─ 嚴重違規詞（代考、借錢等）→ 🚫 自動拒絕
├─ 高風險詞（幫寫報告等）→ ⚠️ 需人工審核
└─ 中等風險詞（深夜、代買等）→ ⚠️ 警告但允許
        ↓
第二階段：AI 語意分析
├─ 使用 Gemini 2.5 Flash
├─ Temperature = 0.5（平衡模式）
└─ 識別隱藏違規內容
        ↓
第三階段：綜合判定
├─ Safe/Low → ✅ 自動通過
├─ Medium → ⚠️ 警告但允許 + 可申訴
├─ High → 📋 需人工審核 + 可申訴
└─ Critical → 🚫 自動拒絕 + 不可申訴
點數保護機制

發布時預扣：防止發布者無點數卻發布任務
取消任務返還：未接受前可取消並退回點數
完成確認轉移：發布者確認後才給予幫助者
5 天自動完成：防止惡意不確認

申訴機制

適用情境：AI 誤判、任務未完成、品質不佳
聯絡方式：

📞 電話：(02) 2881-9471 轉 6123
📧 Email: campushelp@scu.edu.tw
💬 LINE: @campushelp


處理時間：1-3 個工作天


📊 Demo 模式
如果 Gemini API 配額用完或需要展示，可啟用 Demo 模式：
修改 ai_service.py 第 15 行：
pythonDEMO_MODE = True  # 改成 True 啟用 Demo 模式
Demo 模式特性：

✅ 關鍵字檢測仍正常運作（代考等違規詞會被攔截）
✅ 任務發布、申請、完成等功能完全正常
✅ AI 優化會返回固定建議
✅ 風險評估自動通過（除非觸發關鍵字）
❌ 不呼叫真實 Gemini API（不消耗配額）


🎯 UN SDGs 對應
本專案符合聯合國永續發展目標（SDGs）：
SDG 3：良好健康與福祉

減少學生壓力（互助機制）
促進校園心理健康（社群連結）

SDG 8：合適的工作與經濟成長

創造校園微型經濟
培養學生技能交換與時間管理能力

SDG 11：永續城市與社區

建立更安全、包容的校園社群
促進資源共享與循環經濟


🧪 測試帳號
系統預設建立 4 個測試使用者：
姓名科系校區初始點數技能王小美資訊管理學系外雙溪200攝影、影片剪輯、平面設計李大明企業管理學系城中350搬運、組裝家具、修理電腦陳小華英文學系外雙溪150英文教學、簡報製作、翻譯張志明數學系外雙溪500數學教學、程式設計、資料分析

🛠️ 依賴套件
txtstreamlit==1.28.0
sqlalchemy==2.0.23
pandas==2.1.3
plotly==5.18.0
python-dotenv==1.0.0
google-generativeai==0.3.1
```

完整清單請見 `requirements.txt`

---

## 🚧 已知限制

1. **Gemini API 配額**：
   - 免費版：15 次/分鐘，1,500 次/天
   - 建議：展示時使用 Demo 模式

2. **單機運行**：
   - 目前使用 SQLite，不支援多人同時編輯
   - 生產環境建議改用 PostgreSQL/MySQL

3. **身份驗證**：
   - 目前為模擬驗證（選擇使用者）
   - 生產環境需整合學校 SSO 系統

---

## 🔮 未來展望

### 短期目標（1-3 個月）

- [ ] 整合東吳大學 SSO 單一登入
- [ ] Email 通知系統（申請、接受、完成）
- [ ] LINE Bot 整合（即時通知）
- [ ] 手機版 RWD 優化

### 中期目標（3-6 個月）

- [ ] 多校區擴展（政大、世新、台北大學）
- [ ] 任務分類細化（增加更多類別）
- [ ] 技能認證系統（官方技能徽章）
- [ ] 排行榜與成就系統

### 長期目標（6-12 個月）

- [ ] 跨校互助網絡
- [ ] 企業合作（實習媒合）
- [ ] 點數商城（兌換實體商品）
- [ ] AI 聊天機器人客服

---


🎓 黑客松展示要點
核心亮點（8 分鐘展示）

問題陳述（30 秒）

校園資源不對稱
學生技能閒置
缺乏安全互助機制


解決方案（1 分鐘）

時間銀行點數經濟
AI 三層安全防護
智慧媒合推薦


Live Demo（4 分鐘）

發布任務 → AI 審查 → 通過
測試違規內容 → 自動攔截
AI 推薦 → 媒合度計算
完成任務 → 點數轉移


技術架構（1.5 分鐘）

Streamlit + SQLAlchemy
Gemini AI 整合
資料庫設計


社會影響（1 分鐘）

SDGs 對應
使用者回饋
未來展望


💜 有空幫一下，讓校園更有溫度！