"""
資料庫模組 - Campus Help (修復版)
修復內容:
1. 確保發布任務時扣除點數
2. 防止自己申請自己的任務
3. 只能接受一個申請者
4. 新增任務取消功能
5. 新增校外選項
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import json

# 建立引擎
engine = create_engine('sqlite:///campus_help.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# ========== 資料模型 ==========

class User(Base):
    """使用者模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    grade = Column(String(20))
    campus = Column(String(50))
    skills = Column(Text)
    
    points = Column(Integer, default=100)
    avg_rating = Column(Float, default=5.0)
    completed_tasks = Column(Integer, default=0)
    trust_score = Column(Float, default=1.0)
    
    willing_cross_campus = Column(Boolean, default=False)
    status = Column(String(20), default='active')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'department': self.department,
            'grade': self.grade,
            'campus': self.campus,
            'skills': json.loads(self.skills) if self.skills else [],
            'points': self.points,
            'avg_rating': self.avg_rating,
            'completed_tasks': self.completed_tasks,
            'trust_score': self.trust_score,
            'willing_cross_campus': self.willing_cross_campus,
            'status': self.status
        }


class Task(Base):
    """任務模型"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    publisher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    accepted_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    location = Column(String(200))
    campus = Column(String(50))
    
    points_offered = Column(Integer, nullable=False)
    is_urgent = Column(Boolean, default=False)
    status = Column(String(20), default='open')
    
    # 🔧 新增：時間相關欄位
    accept_deadline = Column(String(50), nullable=True)  # 任務預定日期
    task_start_time = Column(String(50), nullable=True) # 接取起始時點
    task_duration = Column(String(50), nullable=True)  # 預估時長
    accepted_at = Column(DateTime, nullable=True)  # 接受時間（用於計算自動完成）
    helper_notified_completion = Column(Boolean, default=False)  # 幫助者是否已通知完成
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    publisher = relationship('User', foreign_keys=[publisher_id])
    accepted_user = relationship('User', foreign_keys=[accepted_user_id])
    
    def to_dict(self):
        session = Session()
        publisher = session.query(User).filter_by(id=self.publisher_id).first()
        accepted_user = session.query(User).filter_by(id=self.accepted_user_id).first() if self.accepted_user_id else None
        
        application_count = session.query(TaskApplication).filter_by(task_id=self.id).count()
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'location': self.location,
            'campus': self.campus,
            'points_offered': self.points_offered,
            'is_urgent': self.is_urgent,
            'status': self.status,
            'publisher_id': self.publisher_id,
            'publisher_name': publisher.name if publisher else '未知',
            'publisher_rating': publisher.avg_rating if publisher else 0,
            'publisher_department': publisher.department if publisher else '未知',
            'accepted_user_id': self.accepted_user_id,
            'accepted_user_name': accepted_user.name if accepted_user else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None,
            'accept_deadline': self.accept_deadline,
            'task_start_time': self.task_start_time,
            'task_duration': self.task_duration,
            'accepted_at': self.accepted_at.strftime('%Y-%m-%d %H:%M') if self.accepted_at else None,
            'helper_notified_completion': self.helper_notified_completion,
            'days_until_auto_complete': self._calculate_days_until_auto_complete(),
            'application_count': application_count
        }
    
    def _calculate_days_until_auto_complete(self):
        """計算距離自動完成還有幾天"""
        if self.status == 'in_progress' and self.accepted_at:
            auto_complete_date = self.accepted_at + timedelta(days=5)
            remaining = auto_complete_date - datetime.utcnow()
            days = remaining.days
            return max(0, days)
        return None


class TaskApplication(Base):
    """任務申請記錄"""
    __tablename__ = 'task_applications'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    applicant_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    status = Column(String(20), default='pending')
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship('Task', foreign_keys=[task_id])
    applicant = relationship('User', foreign_keys=[applicant_id])
    
    def to_dict(self):
        session = Session()
        applicant = session.query(User).filter_by(id=self.applicant_id).first()
        
        return {
            'id': self.id,
            'task_id': self.task_id,
            'applicant_id': self.applicant_id,
            'applicant_name': applicant.name if applicant else '未知',
            'applicant_rating': applicant.avg_rating if applicant else 0,
            'applicant_department': applicant.department if applicant else '未知',
            'applicant_campus': applicant.campus if applicant else '未知',
            'applicant_skills': json.loads(applicant.skills) if applicant and applicant.skills else [],
            'status': self.status,
            'applied_at': self.applied_at.strftime('%Y-%m-%d %H:%M') if self.applied_at else None
        }


class Review(Base):
    """評價記錄"""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    rating = Column(Float, nullable=False)
    comment = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship('Task', foreign_keys=[task_id])
    reviewer = relationship('User', foreign_keys=[reviewer_id])
    reviewee = relationship('User', foreign_keys=[reviewee_id])
    
    def to_dict(self):
        session = Session()
        reviewer = session.query(User).filter_by(id=self.reviewer_id).first()
        reviewee = session.query(User).filter_by(id=self.reviewee_id).first()
        task = session.query(Task).filter_by(id=self.task_id).first()
        
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_title': task.title if task else '未知',
            'reviewer_id': self.reviewer_id,
            'reviewer_name': reviewer.name if reviewer else '未知',
            'reviewee_id': self.reviewee_id,
            'reviewee_name': reviewee.name if reviewee else '未知',
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


# ========== 資料庫操作函數 ==========

def init_db():
    """初始化資料庫"""
    Base.metadata.create_all(engine)


def get_all_users():
    """取得所有使用者"""
    session = Session()
    users = session.query(User).filter_by(status='active').all()
    return [u.to_dict() for u in users]


def get_user_by_name(name):
    """根據名字取得使用者"""
    session = Session()
    user = session.query(User).filter_by(name=name, status='active').first()
    return user.to_dict() if user else None


def get_user_by_id(user_id):
    """根據 ID 取得使用者"""
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    return user.to_dict() if user else None


def update_user_skills(user_id, skills_list):
    """更新使用者技能"""
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.skills = json.dumps(skills_list)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"更新技能失敗: {e}")
        return False
    finally:
        session.close()


def get_all_tasks(status=None, exclude_user_id=None):
    """取得所有任務"""
    session = Session()
    query = session.query(Task)
    
    if status:
        query = query.filter_by(status=status)
    
    if exclude_user_id:
        query = query.filter(Task.publisher_id != exclude_user_id)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return [t.to_dict() for t in tasks]


def create_task(task_data):
    """建立任務（會扣除發起者點數）"""
    session = Session()
    
    try:
        publisher = session.query(User).filter_by(id=task_data['publisher_id']).first()
        
        if publisher.points < task_data['points_offered']:
            print(f"❌ 點數不足: 需要 {task_data['points_offered']}，但只有 {publisher.points}")
            return None
        
        publisher.points -= task_data['points_offered']
        print(f"✅ 已扣除 {task_data['points_offered']} 點，剩餘 {publisher.points} 點")
        
        task = Task(
            title=task_data['title'],
            description=task_data['description'],
            category=task_data['category'],
            location=task_data['location'],
            campus=task_data['campus'],
            points_offered=task_data['points_offered'],
            publisher_id=task_data['publisher_id'],
            is_urgent=task_data.get('is_urgent', False),
            accept_deadline=task_data.get('accept_deadline'),
            task_start_time=task_data.get('task_start_time'),
            task_duration=task_data.get('task_duration')
        )
        
        session.add(task)
        session.commit()
        
        print(f"✅ 任務建立成功，ID: {task.id}")
        return task.id
    except Exception as e:
        session.rollback()
        print(f"❌ 建立任務失敗: {e}")
        return None
    finally:
        session.close()


def cancel_task(task_id, publisher_id):
    """取消任務（返還點數）"""
    session = Session()
    
    try:
        task = session.query(Task).filter_by(id=task_id, publisher_id=publisher_id).first()
        if not task:
            return False
        
        if task.status != 'open':
            return False
        
        publisher = session.query(User).filter_by(id=publisher_id).first()
        publisher.points += task.points_offered
        
        task.status = 'cancelled'
        
        applications = session.query(TaskApplication).filter_by(task_id=task_id).all()
        for app in applications:
            app.status = 'rejected'
        
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"取消任務失敗: {e}")
        return False
    finally:
        session.close()


def get_user_tasks(user_id, task_type='published'):
    """取得使用者的任務"""
    session = Session()
    
    if task_type == 'published':
        tasks = session.query(Task).filter_by(publisher_id=user_id).order_by(Task.created_at.desc()).all()
        return [t.to_dict() for t in tasks]
    
    elif task_type == 'applied':
        applications = session.query(TaskApplication).filter_by(applicant_id=user_id).all()
        result = []
        
        for app in applications:
            task = session.query(Task).filter_by(id=app.task_id).first()
            if task:
                task_dict = task.to_dict()
                task_dict['application_status'] = app.status
                task_dict['applied_at'] = app.applied_at.strftime('%Y-%m-%d %H:%M')
                result.append(task_dict)
        
        return result
    
    return []


def apply_for_task(task_id, applicant_id):
    """申請任務"""
    session = Session()
    
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        if not task:
            print("❌ 任務不存在")
            return False
        
        if task.publisher_id == applicant_id:
            print("❌ 不能申請自己發布的任務")
            return False
        
        existing = session.query(TaskApplication).filter_by(
            task_id=task_id,
            applicant_id=applicant_id
        ).first()
        
        if existing:
            print("❌ 已經申請過此任務")
            return False
        
        application = TaskApplication(
            task_id=task_id,
            applicant_id=applicant_id
        )
        
        session.add(application)
        session.commit()
        
        print("✅ 申請成功")
        return True
    except Exception as e:
        session.rollback()
        print(f"❌ 申請任務失敗: {e}")
        return False
    finally:
        session.close()


def get_task_applications(task_id):
    """取得任務的所有申請"""
    session = Session()
    applications = session.query(TaskApplication).filter_by(task_id=task_id).all()
    return [a.to_dict() for a in applications]


def accept_application(task_id, applicant_id, publisher_id):
    """接受申請（發起者操作）"""
    session = Session()
    
    try:
        task = session.query(Task).filter_by(id=task_id, publisher_id=publisher_id).first()
        if not task:
            return False
        
        if task.status != 'open':
            return False
        
        if task.accepted_user_id is not None:
            print("❌ 已經接受過申請者")
            return False
        
        task.status = 'in_progress'
        task.accepted_user_id = applicant_id
        task.accepted_at = datetime.utcnow()  # 🔧 記錄接受時間
        
        applications = session.query(TaskApplication).filter_by(task_id=task_id).all()
        for app in applications:
            if app.applicant_id == applicant_id:
                app.status = 'accepted'
            else:
                app.status = 'rejected'
        
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"接受申請失敗: {e}")
        return False
    finally:
        session.close()


def helper_notify_completion(task_id, helper_id):
    """幫助者通知已完成（不轉移點數，只是通知）"""
    session = Session()
    
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False
        
        if task.status != 'in_progress':
            return False
        
        if task.accepted_user_id != helper_id:
            return False
        
        task.helper_notified_completion = True
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"通知完成失敗: {e}")
        return False
    finally:
        session.close()


def complete_task(task_id, user_id):
    """完成任務（只有發布者可以確認完成）"""
    session = Session()
    
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False
        
        if task.status != 'in_progress':
            return False
        
        # 🔧 只有發布者可以確認完成
        if user_id != task.publisher_id:
            return False
        
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        
        publisher = session.query(User).filter_by(id=task.publisher_id).first()
        helper = session.query(User).filter_by(id=task.accepted_user_id).first()
        
        if helper:
            helper.points += task.points_offered
            helper.completed_tasks += 1
            publisher.completed_tasks += 1
        
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"完成任務失敗: {e}")
        return False
    finally:
        session.close()


def auto_complete_expired_tasks():
    """自動完成超過5天的進行中任務"""
    session = Session()
    
    try:
        # 找出所有超過5天的進行中任務
        five_days_ago = datetime.utcnow() - timedelta(days=5)
        expired_tasks = session.query(Task).filter(
            Task.status == 'in_progress',
            Task.accepted_at < five_days_ago
        ).all()
        
        for task in expired_tasks:
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            
            helper = session.query(User).filter_by(id=task.accepted_user_id).first()
            publisher = session.query(User).filter_by(id=task.publisher_id).first()
            
            if helper and publisher:
                helper.points += task.points_offered
                helper.completed_tasks += 1
                publisher.completed_tasks += 1
        
        session.commit()
        return len(expired_tasks)
    
    except Exception as e:
        session.rollback()
        print(f"自動完成任務失敗: {e}")
        return 0
    finally:
        session.close()


def submit_review(task_id, reviewer_id, reviewee_id, rating, comment=''):
    """提交評價"""
    session = Session()
    
    try:
        task = session.query(Task).filter_by(id=task_id, status='completed').first()
        if not task:
            return False
        
        if not ((reviewer_id == task.publisher_id and reviewee_id == task.accepted_user_id) or
                (reviewer_id == task.accepted_user_id and reviewee_id == task.publisher_id)):
            return False
        
        existing = session.query(Review).filter_by(
            task_id=task_id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id
        ).first()
        
        if existing:
            return False
        
        review = Review(
            task_id=task_id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            rating=rating,
            comment=comment
        )
        
        session.add(review)
        
        update_user_rating(session, reviewee_id)
        
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"提交評價失敗: {e}")
        return False
    finally:
        session.close()


def update_user_rating(session, user_id):
    """更新使用者的平均評分和信任值"""
    reviews = session.query(Review).filter_by(reviewee_id=user_id).all()
    
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.avg_rating = round(avg_rating, 2)
            completion_rate = min(1.0, user.completed_tasks / 50)
            user.trust_score = round((avg_rating / 5.0 * 0.7) + (completion_rate * 0.3), 2)


def get_reviews_for_user(user_id):
    """取得使用者收到的評價"""
    session = Session()
    reviews = session.query(Review).filter_by(reviewee_id=user_id).order_by(Review.created_at.desc()).all()
    return [r.to_dict() for r in reviews]


def check_review_status(task_id, user_id):
    """檢查用戶是否已對任務進行評價"""
    session = Session()
    
    task = session.query(Task).filter_by(id=task_id, status='completed').first()
    if not task:
        return {'can_review': False, 'reviewee_id': None, 'has_reviewed': False}
    
    if user_id == task.publisher_id:
        reviewee_id = task.accepted_user_id
    elif user_id == task.accepted_user_id:
        reviewee_id = task.publisher_id
    else:
        return {'can_review': False, 'reviewee_id': None, 'has_reviewed': False}
    
    existing = session.query(Review).filter_by(
        task_id=task_id,
        reviewer_id=user_id,
        reviewee_id=reviewee_id
    ).first()
    
    return {
        'can_review': True,
        'reviewee_id': reviewee_id,
        'has_reviewed': existing is not None
    }


def seed_test_data():
    """填充測試資料 - 保持原有資料不變"""
    session = Session()
    
    session.query(Review).delete()
    session.query(TaskApplication).delete()
    session.query(Task).delete()
    session.query(User).delete()
    session.commit()
    
    users_data = [
        {
            'email': 'alice@scu.edu.tw',
            'name': '王小美',
            'department': '資訊管理學系',
            'grade': '大二',
            'campus': '外雙溪校區',
            'skills': json.dumps(['攝影', '影片剪輯', '平面設計', 'Photoshop']),
            'points': 200,
            'avg_rating': 4.8,
            'completed_tasks': 15,
            'trust_score': 0.95
        },
        {
            'email': 'bob@scu.edu.tw',
            'name': '李大明',
            'department': '企業管理學系',
            'grade': '大三',
            'campus': '城中校區',
            'skills': json.dumps(['搬運', '組裝家具', '修理電腦', '跑腿']),
            'points': 350,
            'avg_rating': 4.5,
            'completed_tasks': 28,
            'trust_score': 0.92,
            'willing_cross_campus': True
        },
        {
            'email': 'carol@scu.edu.tw',
            'name': '陳小華',
            'department': '英文學系',
            'grade': '大一',
            'campus': '外雙溪校區',
            'skills': json.dumps(['英文教學', '簡報製作', '文書處理', '翻譯']),
            'points': 150,
            'avg_rating': 4.9,
            'completed_tasks': 10,
            'trust_score': 0.98
        },
        {
            'email': 'david@scu.edu.tw',
            'name': '張志明',
            'department': '數學系',
            'grade': '大四',
            'campus': '外雙溪校區',
            'skills': json.dumps(['數學教學', '程式設計', '資料分析', 'Python']),
            'points': 500,
            'avg_rating': 4.7,
            'completed_tasks': 45,
            'trust_score': 0.94
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
        users.append(user)
    
    session.commit()
    
    tasks_data = [
    {
        'publisher_id': users[0].id,
        'title': '幫忙搬宿舍行李',
        'description': '需要幫忙搬一些行李箱和紙箱，從柚芳樓到楓雅樓，大約20分鐘內可完成。東西不多，主要是幾個紙箱和一個行李箱。',
        'category': '日常支援',
        'location': '柚芳樓 → 楓雅樓',
        'campus': '外雙溪校區',
        'points_offered': 50,
        'is_urgent': True,
        'accept_deadline': (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        'task_start_time': '14:00',
        'task_duration': '30分鐘'
    },
    {
        'publisher_id': users[1].id,
        'title': '協助活動攝影',
        'description': '系學會舉辦迎新晚會，需要攝影記錄約2小時。希望有攝影經驗，能拍出活動氣氛。晚會在望星廣場舉行。',
        'category': '校園協助',
        'location': '望星廣場',
        'campus': '外雙溪校區',
        'points_offered': 80,
        'accept_deadline': (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        'task_start_time': '18:30', 
        'task_duration': '2小時'
    },
    {
        'publisher_id': users[2].id,
        'title': '教微積分解題',
        'description': '期中考前想請教幾題微積分題目，約1小時。主要是導數和積分的應用題，希望能夠耐心講解解題技巧。',
        'category': '學習互助',
        'location': '圖書館 7F會議室',
        'campus': '城中校區',
        'points_offered': 60,
        'accept_deadline': (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        'task_start_time': '15:00',
        'task_duration': '1小時'
    },
    {
        'publisher_id': users[3].id,
        'title': '幫忙修電腦',
        'description': '電腦無法開機，需要懂電腦的人幫忙檢查。可能是硬體或軟體問題，希望能診斷並修復。',
        'category': '日常支援',
        'location': '松勁樓',
        'campus': '外雙溪校區',
        'points_offered': 70,
        'accept_deadline': (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
        'task_start_time': '10:30', 
        'task_duration': '1小時' 
    },
    {
        'publisher_id': users[0].id,
        'title': '代購午餐',
        'description': '課太多走不開，幫忙在商學院附近買便當。可以用 LINE Pay 或現金付款，會多給跑腿費。',
        'category': '日常支援',
        'location': '商學院',
        'campus': '城中校區',
        'points_offered': 30,
        'is_urgent': True,
        'accept_deadline': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), 
        'task_start_time': '12:00', 
        'task_duration': '30分鐘'
    },
    {
        'publisher_id': users[1].id,
        'title': '英文簡報修改',
        'description': '需要英文母語者或英文很好的人幫忙修改英文簡報，約10頁，主要是文法和用詞優化。',
        'category': '學習互助',
        'location': '線上',
        'campus': '線上',
        'points_offered': 100,
        'accept_deadline': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),  
        'task_start_time': '19:00', 
        'task_duration': '2小時' 
    }
]
    
    for task_data in tasks_data:
        task = Task(**task_data)
        session.add(task)
    
    session.commit()
    session.close()
    
    print("✅ 測試資料建立完成！")
    print(f"   - 使用者: {len(users_data)} 位")
    print(f"   - 任務: {len(tasks_data)} 個")


if __name__ == '__main__':
    init_db()
    seed_test_data()