import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import (
    init_db, get_all_users, get_user_by_name, 
    get_all_tasks, create_task, get_user_tasks, 
    apply_for_task, get_task_applications,
    accept_application, complete_task,
    submit_review, get_reviews_for_user, check_review_status,
    cancel_task, update_user_skills, get_user_by_id
)
from matching_engine import MatchingEngine
from ai_service import AIService
from config import Config
import streamlit.components.v1 as components

# 頁面配置
st.set_page_config(
    page_title="Campus Help - 校園共享幫幫平台",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 🔧 自動初始化資料庫（只在第一次部署時執行） ==========
import os

# 檢查資料庫是否存在且有效
db_exists = os.path.exists('campus_help.db')
db_valid = False

if db_exists:
    # 檢查資料庫是否有效（嘗試查詢）
    try:
        from database import Session, User
        session = Session()
        session.query(User).first()
        session.close()
        db_valid = True
    except:
        db_valid = False

# 如果資料庫不存在或無效，重新初始化
if not db_exists or not db_valid:
    try:
        from database import init_db, seed_test_data
        
        # 如果檔案存在但無效，先刪除
        if db_exists and not db_valid:
            os.remove('campus_help.db')
        
        init_db()
        seed_test_data()
        print("✅ 資料庫初始化完成（含測試資料）")
    except Exception as e:
        print(f"❌ 資料庫初始化失敗：{str(e)}")



# 自訂 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #9333ea;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .task-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #e5e7eb;
        margin-bottom: 1rem;
        background: white;
    }
    .urgent-badge {
        background: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
    }
    .category-badge {
        background: #9333ea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
    }
    .campus-badge {
        background: #3b82f6;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
    }
    .security-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    .risk-safe {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    .risk-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    .risk-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    .risk-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    .risk-critical {
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
    .warning-box {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .verified-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    /* 🔧 新增：AI 推薦任務框框 */
    .ai-recommendation-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 3px solid #9333ea;
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(147, 51, 234, 0.3);
    }
    
    /* 🔧 新增：展開標題放大 */
    .streamlit-expanderHeader {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* 🔧 新增：Tab 標籤放大且顯目 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f9fafb;
        padding: 8px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        background-color: white;
        border-radius: 6px;
        border: 2px solid #e5e7eb;
    }
    .stTabs [aria-selected="true"] {
        background-color: #9333ea !important;
        color: white !important;
        border-color: #9333ea !important;
        box-shadow: 0 4px 6px -1px rgba(147, 51, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 初始化資料庫
init_db()

# 初始化 Session State
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'show_appeal_form' not in st.session_state:
    st.session_state.show_appeal_form = False
if 'previous_user' not in st.session_state:
    st.session_state.previous_user = None

# 🔧 每次載入時檢查並自動完成超時任務
from database import auto_complete_expired_tasks
auto_complete_expired_tasks()

# ========== 輔助函數 ==========
def scroll_to_top_and_rerun():
    """重新運行（放棄滾動功能）"""
    st.rerun()

def get_risk_badge(risk_level):
    """根據風險等級返回徽章 HTML"""
    risk_map = {
        'safe': ('✅ 安全', 'risk-safe'),
        'low': ('🛡️ 低風險', 'risk-low'),
        'medium': ('⚠️ 中等風險', 'risk-medium'),
        'high': ('🚨 高風險', 'risk-high'),
        'critical': ('❌ 嚴重違規', 'risk-critical')
    }
    text, css_class = risk_map.get(risk_level, ('❓ 未知', 'risk-medium'))
    return f"<div class='{css_class}'>{text}</div>"

def show_notification(message, icon="🔔"):
    """顯示即時通知（加長顯示時間）"""
    st.toast(f"{icon} {message}", icon=icon)
    import time
    time.sleep(2)

def get_platform_stats():
    """取得平台統計數據"""
    users = get_all_users()
    all_tasks = get_all_tasks()
    
    total_users = len(users)
    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t['status'] == 'completed'])
    open_tasks = len([t for t in all_tasks if t['status'] == 'open'])
    in_progress_tasks = len([t for t in all_tasks if t['status'] == 'in_progress'])
    
    total_points = sum(u['points'] for u in users)
    points_in_tasks = sum(t['points_offered'] for t in all_tasks if t['status'] == 'open')
    
    category_counts = {}
    for task in all_tasks:
        cat = task['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    campus_counts = {}
    for task in all_tasks:
        campus = task['campus']
        campus_counts[campus] = campus_counts.get(campus, 0) + 1
    
    top_users = sorted(users, key=lambda x: x['completed_tasks'], reverse=True)[:3]
    
    return {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'open_tasks': open_tasks,
        'in_progress_tasks': in_progress_tasks,
        'total_points': total_points,
        'points_in_tasks': points_in_tasks,
        'category_counts': category_counts,
        'campus_counts': campus_counts,
        'top_users': top_users,
        'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }

# ========== 側邊欄 ==========
with st.sidebar:
    st.markdown("### 👤 使用者登入")
    
    try:
        users = get_all_users()
        user_names = [f"{u['name']} ({u['department']})" for u in users]
    except Exception as e:
        st.sidebar.error("❌ 資料庫錯誤，請重新整理頁面")
        st.sidebar.info("🔄 或使用管理員功能重置資料庫")
        st.stop()  # 停止執行，避免更多錯誤
    
    # 找到當前使用者的索引
    current_index = 0
    if st.session_state.current_user:
        current_index = next((i for i, u in enumerate(users) if u['name'] == st.session_state.current_user['name']), 0)
    
    selected_user_display = st.selectbox(
        "選擇身份",
        user_names,
        index=current_index,
        key='user_selector'
    )
    
    # 解析選擇的使用者
    selected_user_name = selected_user_display.split(' (')[0]
    new_user = get_user_by_name(selected_user_name)
    
    # 檢查是否切換使用者
    if st.session_state.previous_user != selected_user_name:
        st.session_state.current_user = new_user
        st.session_state.previous_user = selected_user_name
        st.session_state.page = 'my_tasks'
        st.rerun()
    
    if st.session_state.current_user:
        st.success(f"✅ 已登入為：{st.session_state.current_user['name']}")
        
        # 🔧 修改：右上角 ICON 只顯示一次
        st.markdown(
            "<div class='verified-badge'>"
            "<strong>🛡️ 身份已驗證</strong><br>"
            "<span style='font-size: 0.75rem;'>東吳大學學校信箱認證</span>"
            "</div>",
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        st.markdown("#### 📊 我的資訊")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("點數", f"{st.session_state.current_user['points']} 點")
            st.metric("評分", f"⭐ {st.session_state.current_user['avg_rating']:.1f}")
        with col2:
            st.metric("完成任務", f"{st.session_state.current_user['completed_tasks']} 個")
            st.metric("信任值", f"{st.session_state.current_user['trust_score']:.0%}")
        
        st.markdown(f"**校區**: {st.session_state.current_user['campus']}")
        
        if st.session_state.current_user.get('skills'):
            st.markdown("**我的技能**:")
            skills_html = " ".join([f"<span style='background:#e0e7ff;color:#4338ca;padding:0.25rem 0.5rem;border-radius:0.25rem;margin:0.25rem;display:inline-block;font-size:0.875rem'>{skill}</span>" 
                                   for skill in st.session_state.current_user['skills']])
            st.markdown(skills_html, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🧭 導航")
    
    if st.button("🏠 首頁", use_container_width=True):
        st.session_state.page = 'home'
        scroll_to_top_and_rerun()
    
    if st.button("➕ 發布任務", use_container_width=True):
        st.session_state.page = 'publish'
        scroll_to_top_and_rerun()
    
    if st.button("📋 我的任務", use_container_width=True):
        st.session_state.page = 'my_tasks'
        scroll_to_top_and_rerun()
    
    if st.button("🤖 AI 推薦", use_container_width=True):
        st.session_state.page = 'ai_recommend'
        scroll_to_top_and_rerun()
    
    if st.button("⭐ 我的評價", use_container_width=True):
        st.session_state.page = 'reviews'
        scroll_to_top_and_rerun()
    
    if st.button("🛠️ 技能管理", use_container_width=True):
        st.session_state.page = 'skills'
        scroll_to_top_and_rerun()
    
    if st.button("📊 平台統計", use_container_width=True):
        st.session_state.page = 'statistics'
        scroll_to_top_and_rerun()

    # ========== 🔧 管理員功能（密碼保護） ==========
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 系統管理")

    # 管理員密碼保護
    admin_password = st.sidebar.text_input("管理員密碼", type="password", key="admin_pwd")

    # 從環境變數讀取密碼，預設為 scu2025
    import os
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "scu2025")

    if admin_password == ADMIN_PASSWORD:
        st.sidebar.success("✅ 管理員已登入")
        
        # 重置資料庫按鈕（兩段式確認）
        if 'confirm_reset_step' not in st.session_state:
            st.session_state.confirm_reset_step = 0
        
        if st.session_state.confirm_reset_step == 0:
            # 第一步：初始按鈕
            if st.sidebar.button("🔄 重置資料庫", type="primary", key="reset_db_btn", use_container_width=True):
                st.session_state.confirm_reset_step = 1
                st.rerun()
        
        elif st.session_state.confirm_reset_step == 1:
            # 第二步：確認警告
            st.sidebar.warning("⚠️ 確定要重置資料庫？此操作無法復原！")
            
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("✅ 確定重置", type="primary", key="confirm_yes", use_container_width=True):
                    try:
                        import os
                        
                        st.sidebar.info("🔄 開始重置流程...")
                        
                        # 方法改變：不刪除檔案，而是清空並重建表格
                        from database import Base, engine, seed_test_data
                        
                        # 步驟 1：刪除所有表格
                        Base.metadata.drop_all(engine)
                        st.sidebar.success("✅ 步驟 1/3：已清空舊資料")
                        
                        # 步驟 2：重新建立表格
                        Base.metadata.create_all(engine)
                        st.sidebar.success("✅ 步驟 2/3：資料庫結構已重建")
                        
                        # 步驟 3：填充測試資料
                        seed_test_data()
                        st.sidebar.success("✅ 步驟 3/3：測試資料已填充")
                        
                        st.sidebar.success("🎉 資料庫重置完成！")
                        st.sidebar.info("🔄 正在清空密碼並重新整理頁面...")
                        
                        # ✅ 使用 JavaScript 強制重新整理頁面（這會清空所有輸入框）
                        import streamlit.components.v1 as components
                        components.html(
                            """
                            <script>
                                setTimeout(function() {
                                    window.parent.location.reload();
                                }, 2000);
                            </script>
                            """,
                            height=0,
                        )
                        
                        import time
                        time.sleep(2)
                        
                    except Exception as e:
                        st.sidebar.error(f"❌ 重置失敗：{str(e)}")
                        # 顯示詳細錯誤
                        import traceback
                        with st.sidebar.expander("📋 查看詳細錯誤"):
                            st.code(traceback.format_exc())
                        
                        # 嘗試修復：重建資料庫
                        try:
                            st.sidebar.warning("🔧 嘗試修復資料庫...")
                            from database import init_db, seed_test_data
                            init_db()
                            seed_test_data()
                            st.sidebar.success("✅ 修復成功！請重新整理頁面")
                        except:
                            st.sidebar.error("❌ 自動修復失敗，請使用 Zeabur Console 手動執行：python init_db.py")
                        
                        st.session_state.confirm_reset_step = 0
            
            with col2:
                if st.button("❌ 取消", key="confirm_no", use_container_width=True):
                    st.session_state.confirm_reset_step = 0
                    st.rerun()
        
        # 查看資料庫狀態
        if st.sidebar.button("📊 查看資料庫狀態", key="view_db_status", use_container_width=True):
            try:
                from database import Session, User, Task, TaskApplication
                session = Session()
                
                user_count = session.query(User).count()
                task_count = session.query(Task).count()
                app_count = session.query(TaskApplication).count()
                
                session.close()
                
                st.sidebar.info(f"""
                **📊 資料庫狀態**
                - 使用者數：{user_count} 位
                - 任務數：{task_count} 個
                - 申請數：{app_count} 筆
                """)
            except Exception as e:
                st.sidebar.error(f"❌ 查詢失敗：{str(e)}")
        
        # 詳細資料庫資訊（展開式）
        with st.sidebar.expander("🔍 詳細資料庫資訊"):
            try:
                from database import Session, User, Task, TaskApplication
                session = Session()
                
                # 統計資訊
                users = session.query(User).all()
                tasks = session.query(Task).all()
                apps = session.query(TaskApplication).all()
                
                st.write(f"**👥 使用者**：{len(users)} 位")
                for user in users[:5]:  # 只顯示前 5 位
                    st.text(f"  - {user.name} ({user.points} 點)")
                
                if len(users) > 5:
                    st.text(f"  ... 還有 {len(users) - 5} 位")
                
                st.write(f"**📋 任務**：{len(tasks)} 個")
                for task in tasks[:5]:
                    st.text(f"  - {task.title} ({task.status})")
                
                if len(tasks) > 5:
                    st.text(f"  ... 還有 {len(tasks) - 5} 個")
                
                st.write(f"**✉️ 申請**：{len(apps)} 筆")
                
                session.close()
            except Exception as e:
                st.error(f"查詢失敗：{str(e)}")

    elif admin_password:
        st.sidebar.error("❌ 密碼錯誤")


# ========== 主標題 ==========
st.markdown('<h1 class="main-header">💎 校園共享幫幫平台 Campus Help</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">有空幫一下，校園時間銀行</p>', unsafe_allow_html=True)

# ✅ 主導航按鈕（在頁面上方）
st.markdown("---")
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    if st.button("🏠 首頁", key="nav_home", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()

with col2:
    if st.button("➕ 發布任務", key="nav_publish", use_container_width=True):
        st.session_state.page = 'publish'
        st.rerun()

with col3:
    if st.button("📋 我的任務", key="nav_my_tasks", use_container_width=True):
        st.session_state.page = 'my_tasks'
        st.rerun()

with col4:
    if st.button("🤖 AI 推薦", key="nav_ai", use_container_width=True):
        st.session_state.page = 'ai_recommend'
        st.rerun()

with col5:
    if st.button("⭐ 我的評價", key="nav_reviews", use_container_width=True):
        st.session_state.page = 'reviews'
        st.rerun()

with col6:
    if st.button("🛠️ 技能管理", key="nav_skills", use_container_width=True):
        st.session_state.page = 'skills'
        st.rerun()

with col7:
    if st.button("📊 平台統計", key="nav_stats", use_container_width=True):
        st.session_state.page = 'statistics'
        st.rerun()

st.markdown("---")

# ========== 頁面路由 ==========

# 首頁 - 任務列表
if st.session_state.page == 'home':
    st.markdown("## 📋 所有任務")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_query = st.text_input("🔍 搜尋任務", placeholder="輸入關鍵字...")
    with col2:
        filter_category = st.selectbox(
            "分類篩選",
            ["全部"] + Config.CATEGORIES
        )
    with col3:
        filter_campus = st.selectbox(
            "校區篩選",
            ["全部"] + Config.CAMPUSES
        )
    
    tasks = get_all_tasks(
        status='open',
        exclude_user_id=st.session_state.current_user['id'] if st.session_state.current_user else None
    )
    
    if search_query:
        tasks = [t for t in tasks if search_query.lower() in t['title'].lower() or 
                                     search_query.lower() in t['description'].lower()]
    if filter_category != "全部":
        tasks = [t for t in tasks if t['category'] == filter_category]
    if filter_campus != "全部":
        tasks = [t for t in tasks if t['campus'] == filter_campus]
    
    st.markdown(f"找到 **{len(tasks)}** 個任務 | 🛡️ 所有任務已通過安全審查")
    
    if tasks:
        for task in tasks:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    badge_html = f"<span class='category-badge'>{task['category']}</span> "
                    badge_html += f"<span class='campus-badge'>{task['campus']}</span> "
                    badge_html += "<span class='security-badge'>🛡️ 已審查</span>"
                    if task.get('is_urgent'):
                        badge_html += " <span class='urgent-badge'>🔥 急件</span>"
                    
                    st.markdown(f"### {task['title']}")
                    st.markdown(badge_html, unsafe_allow_html=True)
                    st.markdown(f"**描述**: {task['description']}")
                    
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.markdown(f"📍 **地點**: {task['location']}")
                    with col_b:
                        st.markdown(f"👤 **發布者**: {task.get('publisher_name', '未知')}")
                    with col_c:
                        st.markdown(f"⭐ **評價**: {task.get('publisher_rating', 0):.1f}")
                    with col_d:
                        st.markdown(f"👥 **申請數**: {task.get('application_count', 0)} 人")
                    
                    st.markdown(f"🕒 **發布時間**: {task.get('created_at', '未知')}")

                    if task.get('accept_deadline'):
                        st.markdown(f"⏰ **任務預定日期**: {task.get('accept_deadline')}")
                    if task.get('task_start_time'):  # 🔧 新增
                        st.markdown(f"🕐 **開始時間**: {task.get('task_start_time')}")
                    if task.get('task_duration'):
                        st.markdown(f"⏱️ **預估時長**: {task.get('task_duration')}")
                
                with col2:
                    st.markdown(f"### 💰 {task['points_offered']} 點")
                    
                    # 🔧 先放申請任務按鈕
                    if st.button(f"✅ 申請任務", key=f"apply_{task['id']}", use_container_width=True):
                        if st.session_state.current_user:
                            result = apply_for_task(task['id'], st.session_state.current_user['id'])
                            if result:
                                show_notification(f"申請成功！已向 {task.get('publisher_name')} 發送通知", "✅")
                                st.success("✅ 申請成功！")
                                scroll_to_top_and_rerun()
                            else:
                                show_notification("申請失敗", "❌")
                                st.error("申請失敗（可能已申請過或這是您自己的任務）")
                        else:
                            st.warning("請先選擇使用者")
                    
                    # 🔧 查看發布者按鈕（修復版）
                    toggle_key = f"show_publisher_{task['id']}"
                    if toggle_key not in st.session_state:
                        st.session_state[toggle_key] = False
                    
                    # 先檢查狀態，決定按鈕文字
                    button_text = "📦 收起資料" if st.session_state[toggle_key] else "👁️ 查看發布者"
                    
                    if st.button(button_text, key=f"toggle_pub_{task['id']}", use_container_width=True):
                        st.session_state[toggle_key] = not st.session_state[toggle_key]
                        scroll_to_top_and_rerun()  # 🔧 加上這行強制重新渲染
                    
                    if st.session_state[toggle_key]:
                        publisher = get_user_by_id(task['publisher_id'])
                        if publisher:
                            st.info(f"""
                            **發布者資訊**
                            - 姓名：{publisher['name']}
                            - 科系：{publisher['department']}
                            - 校區：{publisher['campus']}
                            - 評分：⭐ {publisher['avg_rating']:.1f}
                            - 完成：{publisher['completed_tasks']} 個
                            - 信任值：{publisher['trust_score']:.0%}
                            """)                                                   
                st.markdown("---")
    else:
        st.info("目前沒有符合條件的任務")

# 發布任務頁面
elif st.session_state.page == 'publish':
    st.markdown("## ➕ 發布新任務")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        with st.expander("⚠️ 使用須知與平台警語（請務必閱讀）", expanded=False):
            st.markdown(Config.PLATFORM_WARNING)
        
        st.info("🛡️ **安全保障**：所有任務將經過 AI 自動審查，確保平台安全")
        st.info(f"💰 您目前有 **{st.session_state.current_user['points']} 點**")
        
        with st.form("publish_task_form"):
            st.markdown("### 任務資訊")
            
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("任務標題 *", placeholder="例：幫忙搬宿舍行李")
                category = st.selectbox("任務分類 *", Config.CATEGORIES, key="category_select")
                location = st.text_input("地點 *", placeholder="例：柚芳樓 → 楓雅樓")
                
                # 🔧 任務預定日期放在地點下方，同一排接任務開始時間和時長
                col_date, col_time, col_duration = st.columns(3)
                
                with col_date:
                    accept_deadline_date = st.date_input(
                        "任務預定日期 *", 
                        value=datetime.now() + timedelta(days=3), 
                        min_value=datetime.now(), 
                        key="deadline_date"
                    )
                
                with col_time:
                    task_start_time = st.time_input(
                        "任務開始時間（選填）",
                        value=None,
                        key="start_time_input"
                    )
                    # 轉換成字串格式 HH:MM
                    if task_start_time:
                        task_start_time = task_start_time.strftime("%H:%M")
                    else:
                        task_start_time = None
                
                with col_duration:
                    task_duration = st.text_input(
                        "預估任務時長（選填）", 
                        placeholder="例：2小時、30分鐘", 
                        key="task_duration_input"
                    )
                    if not task_duration or task_duration.strip() == "":
                        task_duration = None

            with col2:
                campus = st.selectbox("校區 *", Config.CAMPUSES, key="campus_select")
                points_offered = st.number_input(
                    "提供點數 *", 
                    min_value=Config.POINTS_MIN, 
                    max_value=Config.POINTS_MAX, 
                    value=Config.POINTS_DEFAULT, 
                    step=10,
                    key="points_input"
                )
                is_urgent = st.checkbox("急件標記 🔥", key="urgent_check")
            
            if points_offered > st.session_state.current_user['points']:
                st.error(f"❌ 點數不足！您只有 {st.session_state.current_user['points']} 點")
            
            description = st.text_area(
                "詳細描述 *",
                placeholder="請詳細描述任務內容、時間需求、注意事項等...",
                height=150,
                key="description_area"
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                submitted = st.form_submit_button("🚀 發布任務", use_container_width=True)
            with col_b:
                ai_optimize = st.form_submit_button("🤖 AI 優化描述", use_container_width=True)

        # ✅ 表單結束後再處理按鈕邏輯
        if ai_optimize and description:
            with st.spinner("AI 正在優化您的任務描述..."):
                optimized = AIService.optimize_task_description(description)
                if optimized['success']:
                    show_notification("AI 描述優化完成！", "🤖")
                    st.success("✅ AI 優化建議：")
                    st.info(optimized['optimized_description'])
                    st.markdown("**提示**: 您可以複製上面的優化版本重新填入描述欄位")

        if submitted:
            if not all([title, description, category, location, campus]):
                st.error("❌ 請填寫所有必填欄位")
            elif len(description) < 10:
                st.error("❌ 任務描述至少需要 10 個字")
            elif points_offered > st.session_state.current_user['points']:
                st.error("❌ 點數不足，無法發布任務")
            else:
                with st.spinner("🛡️ 正在進行 AI 安全審查..."):
                    risk_check = AIService.risk_assessment(description, category)
                    
                    if risk_check['success']:
                        risk_data = risk_check['data']
                        risk_level = risk_data.get('risk_level', 'medium')
                        
                        st.markdown("### 🛡️ 安全審查結果")
                        st.markdown(get_risk_badge(risk_level), unsafe_allow_html=True)
                        
                        if risk_data.get('recommendation') == '自動拒絕':
                            show_notification("任務被拒絕：包含嚴重違規內容", "🚨")
                            st.error(f"❌ {risk_data.get('reason')}")
                            st.warning("🚨 違規標記：" + ", ".join(risk_data.get('flags', [])))
                            
                            if risk_data.get('warning'):
                                st.markdown(f"<div class='warning-box'>{risk_data.get('warning')}</div>", unsafe_allow_html=True)
                        
                        elif risk_data.get('recommendation') == '需人工審核':
                            st.warning(f"⚠️ {risk_data.get('reason')}")
                            st.warning("🚨 風險標記：" + ", ".join(risk_data.get('flags', [])))
                            
                            st.error("📝 **此任務需要人工審核**")
                            st.info("""
                            **如果您認為系統誤判，可以提交申訴：**
                            
                            **📞 緊急聯絡**：
                            - 電話：(02) 2881-9471 轉 6123
                            - Email: campushelp@scu.edu.tw
                            - LINE: @campushelp
                            
                            **⏰ 審核時間**：1-3 個工作天
                            
                            **📋 申訴流程**：
                            1. 點擊下方「提交申訴」按鈕
                            2. 說明任務內容的合理性
                            3. 等待真人審核
                            4. 審核通過後將通知您
                            """)
                            
                            # ✅ 移到表單外面，使用 session_state 控制
                            if 'show_appeal_form' not in st.session_state:
                                st.session_state.show_appeal_form = False
                            
                            if st.button("📨 提交申訴（示意）", key="appeal_high_risk"):
                                st.session_state.show_appeal_form = True
                            
                            if st.session_state.show_appeal_form:
                                st.success("✅ 申訴已提交！")
                                st.info("📧 您會收到 Email 通知審核結果")
                                st.warning("⏰ 預計 1-3 個工作天內回覆")
                        
                        elif risk_data.get('recommendation') in ['警告但允許', '允許發布', '自動通過']:
                            if risk_level in ['medium', 'low', 'safe']:
                                if risk_level == 'medium':
                                    st.warning(f"⚠️ {risk_data.get('reason')}")
                                if risk_data.get('warning'):
                                    st.markdown(f"<div class='warning-box'>{risk_data.get('warning')}</div>", unsafe_allow_html=True)
                                
                                if risk_level in ['low', 'safe']:
                                    st.success("✅ 任務內容安全，可以發布")
                            
                            task_data = {
                                'title': title,
                                'description': description,
                                'category': category,
                                'location': location,
                                'campus': campus,
                                'points_offered': points_offered,
                                'is_urgent': is_urgent,
                                'publisher_id': st.session_state.current_user['id'],
                                'accept_deadline': accept_deadline_date.strftime("%Y-%m-%d"),
                                'task_start_time': task_start_time,
                                'task_duration': task_duration
                            }
                            
                            task_id = create_task(task_data)
                            if task_id:
                                show_notification(f"任務發布成功！已扣除 {points_offered} 點", "🎉")
                                st.success("✅ 任務發布成功！")
                                st.info(f"💰 已扣除 {points_offered} 點 | 🛡️ 交易安全保護已啟用")
                                st.balloons()
                                st.session_state.current_user = get_user_by_name(st.session_state.current_user['name'])
                                st.info("✨ 3秒後自動跳轉到首頁...")
                                import time
                                time.sleep(3)
                                st.session_state.page = 'home'
                                scroll_to_top_and_rerun()
                            else:
                                show_notification("任務發布失敗（點數可能不足）", "❌")
                                st.error("❌ 發布失敗，請檢查點數是否足夠")

# 我的任務頁面
elif st.session_state.page == 'my_tasks':
    st.markdown("## 📋 我的任務")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        # 🔧 修改：5天自動完成提示
        st.info("💡 **提示**：發布者確認任務完成後，點數將立即轉移。若未即時確認任務完成狀況，點數將在接受後5天直接移轉給幫助者。")
        
        tab1, tab2 = st.tabs(["📤 我發布的", "📥 我接的"])
        
        with tab1:
            my_published = get_user_tasks(st.session_state.current_user['id'], task_type='published')
            
            if my_published:
                for task in my_published:
                    status_icon = {
                        'open': '🟢',
                        'in_progress': '🟡',
                        'completed': '✅',
                        'cancelled': '❌'
                    }.get(task['status'], '❓')
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {status_icon} {task['title']}")
                            st.markdown(f"**描述**: {task['description']}")
                            st.markdown(f"**分類**: {task['category']} | **地點**: {task['location']} | **校區**: {task['campus']}")
                            st.markdown(f"**發布時間**: {task['created_at']}")
                            st.markdown(f"**申請人數**: {task.get('application_count', 0)} 人")
                            
                            if task.get('accept_deadline'):
                                st.markdown(f"⏰ **任務預定日期**: {task.get('accept_deadline')}")
                            if task.get('task_start_time'):
                                st.markdown(f"🕐 **開始時間**: {task.get('task_start_time')}")    
                            if task.get('task_duration'):
                                st.markdown(f"⏱️ **預估時長**: {task.get('task_duration')}")
                            
                            if task.get('accepted_user_name'):
                                st.markdown(f"**✅ 已接受**: {task['accepted_user_name']}")
                            
                            # 🔧 修改：點數交易已完成 + 評價狀態
                            if task.get('completed_at'):
                                st.markdown(f"**完成時間**: {task['completed_at']}")
                                st.success("💎 點數交易已完成")
                                review_status = check_review_status(task['id'], st.session_state.current_user['id'])
                                if review_status['has_reviewed']:
                                    st.success("✅ 您已評價過此任務")
                        
                        with col2:
                            st.markdown(f"### 💰 {task['points_offered']} 點")
                            status_map = {
                                'open': '🟢 開放中',
                                'in_progress': '🟡 進行中',
                                'completed': '✅ 已完成',
                                'cancelled': '❌ 已取消'
                            }
                            st.markdown(f"**狀態**: {status_map.get(task['status'], task['status'])}")
                        
                        if task['status'] == 'open':
                            if st.button(f"❌ 取消任務", key=f"cancel_{task['id']}", use_container_width=True):
                                result = cancel_task(task['id'], st.session_state.current_user['id'])
                                if result:
                                    show_notification(f"任務已取消，返還 {task['points_offered']} 點", "💰")
                                    st.success(f"✅ 任務已取消！返還 {task['points_offered']} 點")
                                    scroll_to_top_and_rerun()
                        
                        # 🔧 修改：確認已完成任務按鈕 + 提示文字
                        if task['status'] == 'in_progress':
                            if task.get('helper_notified_completion'):
                                st.success("✅ 幫助者已通知完成，請確認！")
                            
                            st.info("💡 若未即時確認任務完成狀況，點數將在期限後5天直接移轉")

                            # 🔧 改成：兩個按鈕並排，一樣寬
                            col_confirm, col_appeal = st.columns(2)
                            
                            with col_confirm:
                                if st.button(f"✅ 確認已完成任務", key=f"complete_pub_{task['id']}", use_container_width=True):
                                    result = complete_task(task['id'], st.session_state.current_user['id'])
                                    if result:
                                        show_notification(f"{task['accepted_user_name']} 獲得 {task['points_offered']} 點！", "💰")
                                        st.success(f"✅ 任務已完成！{task['accepted_user_name']} 獲得 {task['points_offered']} 點")
                                        st.info("🛡️ 點數轉移安全完成")
                                        st.balloons()
                                        scroll_to_top_and_rerun()
                            
                            with col_appeal:
                                if st.button(f"⚠️ 任務未完成/申訴", key=f"appeal_pub_{task['id']}", use_container_width=True):
                                    st.warning("📝 **申訴流程**")
                                    st.info("""
                                    **如果幫助者未完成任務或完成品質不佳：**
                                    
                                    1. **緊急情況**：
                                    - 📞 電話：(02) 2881-9471 轉 6123
                                    - 📧 Email: campushelp@scu.edu.tw
                                    - 💬 LINE: @campushelp
                                    
                                    2. **一般申訴**：
                                    - 點擊下方「提交申訴」按鈕
                                    - 平台將在 1-3 個工作天內回覆
                                    - 審核通過後點數將返還
                                    
                                    3. **注意事項**：
                                    - 請提供具體證據（照片、對話記錄）
                                    - 惡意申訴將影響信任值
                                    """)
                                    
                                    if st.button("📨 提交申訴（示意）", key=f"submit_appeal_{task['id']}"):
                                        st.success("✅ 申訴已提交！我們會在 1-3 個工作天內聯繫您。")
                                        st.info("📧 您會收到 Email 確認信")
        
                        
                        # 顯示申請者
                        if task['status'] == 'open':
                            applications = get_task_applications(task['id'])
                            if applications:
                                st.markdown(f"**📝 申請者 ({len(applications)} 人)**:")
                                for app in applications:
                                    col_a, col_b, col_c = st.columns([2, 1, 1])
                                    with col_a:
                                        st.markdown(f"- **{app['applicant_name']}** (評分: {app['applicant_rating']:.1f} ⭐)")
                                        st.markdown(f"  科系: {app['applicant_department']} | 校區: {app['applicant_campus']}")
                                    with col_b:
                                        st.markdown(f"申請時間: {app['applied_at']}")
                                    with col_c:
                                        if st.button(f"✅ 接受", key=f"accept_{task['id']}_{app['applicant_id']}", use_container_width=True):
                                            result = accept_application(
                                                task['id'],
                                                app['applicant_id'],
                                                st.session_state.current_user['id']
                                            )
                                            if result:
                                                show_notification(f"已接受 {app['applicant_name']} 的申請！", "🎉")
                                                st.success("✅ 已接受申請！任務進入進行中")
                                                scroll_to_top_and_rerun()
                                            else:
                                                st.error("❌ 接受失敗（可能已接受過其他人）")

                                        # 🔧 修改：確保可展開收合
                                        view_key = f"view_app_{task['id']}_{app['applicant_id']}"
                                        if view_key not in st.session_state:
                                            st.session_state[view_key] = False
                                        
                                        if st.button(
                                            f"👁️ 查看" if not st.session_state[view_key] else "📦 收起",
                                            key=f"toggle_view_{task['id']}_{app['applicant_id']}",
                                            use_container_width=True
                                        ):
                                            st.session_state[view_key] = not st.session_state[view_key]
                                            scroll_to_top_and_rerun()
                                        
                                        if st.session_state[view_key]:
                                            applicant = get_user_by_id(app['applicant_id'])
                                            if applicant:
                                                st.info(f"""
                                                **申請者完整資訊**
                                                - 姓名：{applicant['name']}
                                                - 科系：{applicant['department']}
                                                - 校區：{applicant['campus']}
                                                - 評分：⭐ {applicant['avg_rating']:.1f}
                                                - 完成任務：{applicant['completed_tasks']} 個
                                                - 信任值：{applicant['trust_score']:.0%}
                                                - 技能：{', '.join(applicant['skills']) if applicant['skills'] else '未設定'}
                                                """)                                                                                                   
                        st.markdown("---")
                        
                        # 🔧 修改：五星評價改為點選星星
                        if task['status'] == 'completed':
                            review_status = check_review_status(task['id'], st.session_state.current_user['id'])
                            if review_status['can_review'] and not review_status['has_reviewed']:
                                st.markdown("---")
                                st.markdown("### ⭐ 評價幫助者")
                                # 🔧 改用拉條 + 星星顯示
                                col_slider, col_empty = st.columns([1, 1])

                                with col_slider:
                                    rating = st.slider(
                                        "評分", 
                                        min_value=1.0, 
                                        max_value=5.0, 
                                        value=5.0, 
                                        step=0.5, 
                                        key=f"rating_slider_pub_{task['id']}"
                                    )
                                    # 🔧 已選擇X星放在拉條下方
                                    st.markdown(f"**已選擇 {rating:.1f} 星** " + "⭐" * int(rating) + ("⭐" if rating % 1 >= 0.5 else ""))

                                with col_empty:
                                    pass  # 空白欄位
                                
                                comment = st.text_area("評價內容（選填）", placeholder="分享您的合作體驗...", key=f"comment_pub_{task['id']}")
                                
                                if st.button(f"提交評價", key=f"submit_review_pub_{task['id']}", use_container_width=True):
                                    result = submit_review(
                                        task['id'],
                                        st.session_state.current_user['id'],
                                        review_status['reviewee_id'],
                                        rating,
                                        comment
                                    )
                                    if result:
                                        show_notification("評價提交成功！", "⭐")
                                        st.success("✅ 評價提交成功！")
                                        scroll_to_top_and_rerun()
            else:
                st.info("您還沒有發布任何任務")
        
        with tab2:
            my_applied = get_user_tasks(st.session_state.current_user['id'], task_type='applied')
            
            if my_applied:
                for task in my_applied:
                    status_icon = {'pending': '⏳', 'accepted': '✅', 'rejected': '❌'}.get(task.get('application_status', 'pending'), '❓')
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {status_icon} {task['title']}")
                            st.markdown(f"**描述**: {task['description']}")
                            st.markdown(f"**發布者**: {task.get('publisher_name', '未知')} ({task.get('publisher_department', '未知')})")
                            st.markdown(f"**地點**: {task['location']} | **校區**: {task['campus']}")
                            st.markdown(f"**申請時間**: {task.get('applied_at', '未知')}")
                            
                            if task.get('accept_deadline'):
                                st.markdown(f"⏰ **任務預定日期**: {task.get('accept_deadline')}")
                            if task.get('task_start_time'):
                                st.markdown(f"🕐 **開始時間**: {task.get('task_start_time')}")
                            if task.get('task_duration'):
                                st.markdown(f"⏱️ **預估時長**: {task.get('task_duration')}")
                        
                        with col2:
                            st.markdown(f"### 💰 {task['points_offered']} 點")
                            status_map = {'pending': '⏳ 待審核', 'accepted': '✅ 已接受', 'rejected': '❌ 已拒絕'}
                            st.markdown(f"**狀態**: {status_map.get(task.get('application_status'), '未知')}")
                            
                            # 🔧 修改：確保可展開收合
                            view_pub_key = f"view_pub_{task['id']}"
                            if view_pub_key not in st.session_state:
                                st.session_state[view_pub_key] = False
                            
                            if st.button(
                                f"👁️ 查看發布者" if not st.session_state[view_pub_key] else "📦 收起資料",
                                key=f"toggle_pub_{task['id']}", 
                                use_container_width=True
                            ):
                                st.session_state[view_pub_key] = not st.session_state[view_pub_key]
                                scroll_to_top_and_rerun()
                            
                            if st.session_state[view_pub_key]:
                                publisher = get_user_by_id(task['publisher_id'])
                                if publisher:
                                    st.info(f"""
                                    **發布者資訊**
                                    - 姓名：{publisher['name']}
                                    - 科系：{publisher['department']}
                                    - 校區：{publisher['campus']}
                                    - 評分：⭐ {publisher['avg_rating']:.1f}
                                    - 完成任務：{publisher['completed_tasks']} 個
                                    - 信任值：{publisher['trust_score']:.0%}
                                    """)
                        
                        if task['status'] == 'in_progress' and task.get('application_status') == 'accepted':
                            if task.get('helper_notified_completion'):
                                st.success("✅ 您已通知發布者任務完成，請等待確認")
                            else:
                                from database import helper_notify_completion

                                # 🔧 只針對「通知已完成任務」按鈕
                                st.markdown(f"""
                                <style>
                                button[key="notify_complete_{task['id']}"] {{
                                    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
                                    color: white !important;
                                    border: none !important;
                                    font-weight: bold !important;
                                }}
                                button[key="notify_complete_{task['id']}"]:hover {{
                                    background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
                                    box-shadow: 0 4px 6px rgba(245, 158, 11, 0.4) !important;
                                }}
                                </style>
                                """, unsafe_allow_html=True)

                                if st.button(f"📢 通知已完成任務", key=f"notify_complete_{task['id']}", use_container_width=True):
                                    result = helper_notify_completion(task['id'], st.session_state.current_user['id'])
                                    if result:
                                        show_notification("已通知發布者，請等待確認！", "📢")
                                        st.success("✅ 已通知發布者確認！")
                                        st.info("💡 發布者確認後，點數將自動轉移給您")
                                        scroll_to_top_and_rerun()
                        
                        # 🔧 修改：五星評價改為點選星星 + 點數交易已完成 + 評價狀態
                        if task['status'] == 'completed' and task.get('application_status') == 'accepted':
                            st.markdown(f"**完成時間**: {task['completed_at']}")
                            st.success("💎 點數交易已完成")
                            review_status = check_review_status(task['id'], st.session_state.current_user['id'])
                            if review_status['has_reviewed']:
                                st.success("✅ 您已評價過此任務")
                            
                            if review_status['can_review'] and not review_status['has_reviewed']:
                                st.markdown("---")
                                st.markdown("### ⭐ 評價發布者")                                
                                
                                # 🔧 改用拉條 + 星星顯示
                                # 🔧 拉條縮短為一半寬度
                                col_slider, col_empty = st.columns([1, 1])

                                with col_slider:
                                    rating = st.slider(
                                        "評分", 
                                        min_value=1.0, 
                                        max_value=5.0, 
                                        value=5.0, 
                                        step=0.5, 
                                        key=f"rating_slider_app_{task['id']}"
                                    )
                                    # 🔧 已選擇X星放在拉條下方
                                    st.markdown(f"**已選擇 {rating:.1f} 星** " + "⭐" * int(rating) + ("⭐" if rating % 1 >= 0.5 else ""))

                                with col_empty:
                                    pass  # 空白欄位
                                
                                comment = st.text_area("評價內容（選填）", placeholder="分享您的合作體驗...", key=f"comment_app_{task['id']}")
                                
                                if st.button(f"提交評價", key=f"submit_review_app_{task['id']}", use_container_width=True):
                                    result = submit_review(
                                        task['id'],
                                        st.session_state.current_user['id'],
                                        review_status['reviewee_id'],
                                        rating,
                                        comment
                                    )
                                    if result:
                                        show_notification("評價提交成功！", "⭐")
                                        st.success("✅ 評價提交成功！")
                                        scroll_to_top_and_rerun()
                        
                        st.markdown("---")
            else:
                st.info("您還沒有申請任何任務")

# AI 推薦頁面
elif st.session_state.page == 'ai_recommend':
    st.markdown("## 🤖 AI 智慧推薦")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        st.markdown(f"### 為 **{st.session_state.current_user['name']}** 推薦的任務")
        st.info("🛡️ **安全保障**：所有推薦任務已通過多重安全審查")
        
        all_tasks = get_all_tasks(
            status='open',
            exclude_user_id=st.session_state.current_user['id']
        )
        
        if all_tasks:
            with st.spinner("🛡️ AI 正在計算最佳媒合並進行安全檢查..."):
                matcher = MatchingEngine()
                recommendations = []
                
                for task in all_tasks:
                    score_data = matcher.calculate_match_score(st.session_state.current_user, task)
                    recommendations.append({'task': task, 'score': score_data['total_score'], 'scores': score_data})
                
                recommendations.sort(key=lambda x: x['score'], reverse=True)
                
                st.markdown("### 🏆 Top 5 推薦任務")
                
                for i, rec in enumerate(recommendations[:5], 1):
                    task = rec['task']
                    score = rec['score']
                    scores = rec['scores']
                    
                    # 🔧 改用普通 container
                    with st.container():
                        # 重點資訊橫列顯示（外露）
                        col_main1, col_main2, col_main3, col_main4 = st.columns([3, 1, 1, 1])
                        
                        with col_main1:
                            st.markdown(f"### #{i} {task['title']}")
                        with col_main2:
                            st.markdown(f"**🎯 媒合度: {score:.0%}**")
                        with col_main3:
                            st.markdown(f"**💰 {task['points_offered']} 點**")
                        with col_main4:
                            st.markdown(f"**👤 {task['publisher_name']}**")
                        
                        # 基本資訊（外露）
                        info_cols = st.columns(5)
                        with info_cols[0]:
                            st.markdown(f"📍 {task['campus']} - {task['location']}")
                        with info_cols[1]:
                            st.markdown(f"🕒 發布: {task['created_at']}")
                        with info_cols[2]:
                            if task.get('accept_deadline'):
                                st.markdown(f"📅 預定: {task['accept_deadline']}")    
                        with info_cols[3]:
                            if task.get('task_start_time'):
                                st.markdown(f"🕐 開始: {task['task_start_time']}")
                        with info_cols[4]:
                            if task.get('task_duration'):
                                st.markdown(f"⏱️ 時長: {task['task_duration']}")
                        
                        # 🔧 任務描述移到外面（不用展開就能看到）
                        st.markdown("**任務描述**:")
                        st.markdown(task['description'])

                        # 🔧 修改：推薦理由收進展開區，任務描述放推薦理由上方
                        with st.expander("📊 查看詳細推薦理由與權重分析", expanded=False):
                            detail_col1, detail_col2 = st.columns([2, 1])
                            
                            with detail_col1:                                                                
                                st.markdown("**🎯 推薦理由**:")
                                reasons = []
                                if scores['skill_score'] > 0.7:
                                    reasons.append(f"✅ 技能高度匹配 ({scores['skill_score']:.0%})")
                                if scores['location_score'] == 1.0:
                                    reasons.append(f"✅ 地點完全相符 (同校區)")
                                if scores['rating_score'] > 0.8:
                                    reasons.append(f"✅ 發布者信譽優良 ({scores['rating_score']:.0%})")
                                
                                for reason in reasons:
                                    st.markdown(reason)
                          
                            with detail_col2:
                                fig = go.Figure(data=[go.Pie(
                                    labels=['技能匹配', '時間相符', '評價信任', '地點相符'],
                                    values=[
                                        scores['skill_score'] * 100,
                                        scores['time_score'] * 100,
                                        scores['rating_score'] * 100,
                                        scores['location_score'] * 100
                                    ],
                                    hole=0.4,
                                    marker_colors=['#9333ea', '#3b82f6', '#10b981', '#f59e0b']
                                )])
                                fig.update_layout(title=f"總分: {score:.0%}", height=250, margin=dict(l=0, r=0, t=40, b=0), showlegend=True)
                                st.plotly_chart(fig, use_container_width=True, key=f"ai_rec_chart_{i}_{task['id']}")
                        
                        # 申請按鈕
                        if st.button(f"✅ 申請這個任務", key=f"rec_apply_main_{i}_{task['id']}", use_container_width=True):
                            result = apply_for_task(task['id'], st.session_state.current_user['id'])
                            if result:
                                show_notification("申請成功！")
                                st.success("✅ 申請成功！")
                                scroll_to_top_and_rerun()
                            else:
                                show_notification("申請失敗", "❌")
                                st.error("❌ 申請失敗（可能已申請過或這是您自己的任務）")
                    
                    st.markdown("---")
        else:
            st.info("目前沒有可推薦的任務")

# 我的評價頁面
elif st.session_state.page == 'reviews':
    st.markdown("## ⭐ 我的評價")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("平均評分", f"⭐ {st.session_state.current_user['avg_rating']:.1f}")
        with col2:
            st.metric("完成任務", f"{st.session_state.current_user['completed_tasks']} 個")
        with col3:
            st.metric("信任值", f"{st.session_state.current_user['trust_score']:.0%}")
        
        st.markdown("---")
        
        reviews = get_reviews_for_user(st.session_state.current_user['id'])
        
        if reviews:
            st.markdown(f"### 收到的評價 ({len(reviews)} 則)")
            
            for review in reviews:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**任務**: {review['task_title']}")
                        st.markdown(f"**評價者**: {review['reviewer_name']}")
                        if review['comment']:
                            st.markdown(f"💬 {review['comment']}")
                        st.markdown(f"📅 {review['created_at']}")
                    
                    with col2:
                        stars = "⭐" * int(review['rating'])
                        st.markdown(f"### {stars}")
                        st.markdown(f"**{review['rating']:.1f}** / 5.0")
                    
                    st.markdown("---")
        else:
            st.info("您還沒有收到任何評價")

# 技能管理頁面
elif st.session_state.page == 'skills':
    st.markdown("## 🛠️ 技能管理")
    
    if not st.session_state.current_user:
        st.warning("⚠️ 請先在側邊欄選擇使用者")
    else:
        st.markdown(f"### 管理 **{st.session_state.current_user['name']}** 的技能")
        
        current_skills = st.session_state.current_user.get('skills', [])
        
        st.markdown("#### 📝 當前技能")
        if current_skills:
            skills_html = " ".join([f"<span style='background:#e0e7ff;color:#4338ca;padding:0.5rem 1rem;border-radius:0.5rem;margin:0.5rem;display:inline-block;font-size:1rem'>{skill}</span>" 
                                   for skill in current_skills])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.info("您還沒有設定任何技能")
        
        st.markdown("---")
        st.markdown("#### ➕ 新增技能")
        
        st.markdown("**快速選擇常用技能：**")
        common_skills = [
            "攝影", "影片剪輯", "平面設計", "Photoshop", "Illustrator",
            "搬運", "組裝家具", "修理電腦", "跑腿", "代購",
            "英文教學", "日文教學", "簡報製作", "文書處理", "翻譯",
            "數學教學", "程式設計", "Python", "Java", "資料分析",
            "活動企劃", "主持", "表演", "音樂", "吉他"
        ]
        
        col1, col2, col3, col4 = st.columns(4)
        selected_common = []
        
        for i, skill in enumerate(common_skills):
            col = [col1, col2, col3, col4][i % 4]
            with col:
                if st.checkbox(skill, key=f"common_{skill}", value=skill in current_skills):
                    if skill not in current_skills:
                        selected_common.append(skill)
        
        st.markdown("**或輸入自訂技能：**")
        custom_skill = st.text_input("新技能名稱", placeholder="例：烹飪、繪畫...")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("➕ 新增自訂技能", use_container_width=True):
                if custom_skill and custom_skill not in current_skills:
                    new_skills = current_skills + [custom_skill]
                    if update_user_skills(st.session_state.current_user['id'], new_skills):
                        show_notification(f"成功新增技能：{custom_skill}", "✅")
                        st.success(f"✅ 已新增技能：{custom_skill}")
                        st.session_state.current_user = get_user_by_name(st.session_state.current_user['name'])
                        scroll_to_top_and_rerun()
        
        with col_b:
            if st.button("💾 儲存快速選擇", use_container_width=True):
                all_selected = []
                for skill in common_skills:
                    if st.session_state.get(f"common_{skill}", False):
                        all_selected.append(skill)
                
                if update_user_skills(st.session_state.current_user['id'], all_selected):
                    show_notification("技能已更新！", "✅")
                    st.success("✅ 技能已更新！")
                    st.session_state.current_user = get_user_by_name(st.session_state.current_user['name'])
                    scroll_to_top_and_rerun()
        
        if current_skills:
            st.markdown("---")
            st.markdown("#### ❌ 移除技能")
            skill_to_remove = st.selectbox("選擇要移除的技能", current_skills)
            
            if st.button("🗑️ 移除選中的技能", use_container_width=True):
                new_skills = [s for s in current_skills if s != skill_to_remove]
                if update_user_skills(st.session_state.current_user['id'], new_skills):
                    show_notification(f"已移除技能：{skill_to_remove}", "✅")
                    st.success(f"✅ 已移除技能：{skill_to_remove}")
                    st.session_state.current_user = get_user_by_name(st.session_state.current_user['name'])
                    scroll_to_top_and_rerun()

# 統計儀表板頁面
elif st.session_state.page == 'statistics':
    st.markdown("## 📊 平台統計儀表板")
    st.info("🛡️ 展示 Campus Help 的運營數據與活躍度")
    
    stats = get_platform_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-label'>總使用者數</div>"
            f"<div class='stat-number'>{stats['total_users']}</div>"
            f"<div class='stat-label'>🛡️ 已驗證帳號</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-label'>總任務數</div>"
            f"<div class='stat-number'>{stats['total_tasks']}</div>"
            f"<div class='stat-label'>📋 累計發布</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-label'>完成率</div>"
            f"<div class='stat-number'>{stats['completion_rate']:.1f}%</div>"
            f"<div class='stat-label'>✅ 任務完成度</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"<div class='stat-card'>"
            f"<div class='stat-label'>點數流通</div>"
            f"<div class='stat-number'>{stats['total_points']}</div>"
            f"<div class='stat-label'>💰 平台經濟</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 任務狀態分布")
        status_data = pd.DataFrame({
            '狀態': ['開放中', '進行中', '已完成'],
            '數量': [stats['open_tasks'], stats['in_progress_tasks'], stats['completed_tasks']]
        })
        
        fig1 = px.pie(
            status_data, 
            values='數量', 
            names='狀態',
            color='狀態',
            color_discrete_map={'開放中':'#3b82f6', '進行中':'#f59e0b', '已完成':'#10b981'},
            hole=0.4
        )
        fig1.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("### 🏷️ 任務分類分布")
        if stats['category_counts']:
            category_data = pd.DataFrame(
                list(stats['category_counts'].items()),
                columns=['分類', '數量']
            )
            
            fig2 = px.bar(
                category_data,
                x='分類',
                y='數量',
                color='數量',
                color_continuous_scale='Purples'
            )
            fig2.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏫 校區活躍度")
        if stats['campus_counts']:
            campus_data = pd.DataFrame(
                list(stats['campus_counts'].items()),
                columns=['校區', '任務數']
            )
            
            fig3 = px.bar(
                campus_data,
                x='校區',
                y='任務數',
                color='校區',
                color_discrete_map={
                    '外雙溪校區': '#9333ea',
                    '城中校區': '#3b82f6',
                    '校外': '#f59e0b',
                    '線上': '#10b981'
                }
            )
            fig3.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.markdown("### 🏆 Top 3 活躍使用者")
        for i, user in enumerate(stats['top_users'], 1):
            medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, '🏅')
            
            with st.container():
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_a:
                    st.markdown(f"### {medal}")
                with col_b:
                    st.markdown(f"**{user['name']}**")
                    st.markdown(f"⭐ {user['avg_rating']:.1f} | 💪 信任值 {user['trust_score']:.0%}")
                with col_c:
                    st.metric("完成", f"{user['completed_tasks']} 個")
                
                st.markdown("---")

# 底部資訊
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280;'>"
    "💜 校園共享幫幫平台 Campus Help | "
    "🛡️ 安全保護 · 信任認證 · AI 審查<br>"
    "Powered by Streamlit + Google Gemini AI | SDGs 3, 8, 11<br>"
    "有空幫一下，校園時間銀行<br>"
    "<strong>東吳共享 Soochow Share 團隊</strong>"
    "</div>",
    unsafe_allow_html=True
)