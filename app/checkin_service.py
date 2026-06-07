"""
打卡和成就服务模块
"""
import math
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Set, Tuple, Any
from sqlalchemy.orm import Session
from .extended_schemas import (
    CheckinResult, CheckinRecord,
    Achievement, AchievementType, UserAchievement,
    Location
)
from .auth_service import SessionLocal, DBCheckin, DBAchievement, DBActivityCount


class CheckinActivity:
    """打卡活动"""
    def __init__(
        self,
        id: str,
        name: str,
        icon: str,
        time_slots: List[str],
        description: str,
        rarity: str = "common",
        required_count: int = 20
    ):
        self.id = id
        self.name = name
        self.icon = icon
        self.time_slots = time_slots
        self.description = description
        self.rarity = rarity
        self.required_count = required_count


class CheckinService:
    """打卡服务"""
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        
        self._init_activities()
        self._init_achievements()
    
    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def _load_user_data_from_db(self, user_id: str) -> Dict[str, Any]:
        """从数据库加载用户数据"""
        db = next(self.get_db())
        try:
            user_id_str = user_id
            
            db_checkins = db.query(DBCheckin).filter(DBCheckin.user_id == user_id_str).all()
            checkins = []
            for db_checkin in db_checkins:
                checkins.append(CheckinRecord(
                    id=db_checkin.id,
                    user_id=db_checkin.user_id,
                    place_id=0,
                    place_name=db_checkin.place_name,
                    checkin_time=db_checkin.checkin_time,
                    latitude=db_checkin.latitude,
                    longitude=db_checkin.longitude
                ))
            
            db_achievements = db.query(DBAchievement).filter(DBAchievement.user_id == user_id_str).all()
            achievement_ids = set(a.achievement_id for a in db_achievements)
            
            db_counts = db.query(DBActivityCount).filter(DBActivityCount.user_id == user_id_str).all()
            activity_counts = {}
            for count in db_counts:
                activity_counts[count.activity_id] = count.count
            
            return {
                'checkins': checkins,
                'achievements': achievement_ids,
                'activity_counts': activity_counts
            }
        finally:
            db.close()
    
    def _save_checkin_to_db(self, user_id: str, place_name: str, checkin_time: datetime, 
                         latitude: float = 0.0, longitude: float = 0.0, activity_id: str = ""):
        """保存打卡记录到数据库"""
        db = next(self.get_db())
        try:
            db_checkin = DBCheckin(
                user_id=user_id,
                place_name=place_name,
                checkin_time=checkin_time,
                latitude=latitude,
                longitude=longitude,
                activity_id=activity_id
            )
            db.add(db_checkin)
            db.commit()
            db.refresh(db_checkin)
            return db_checkin.id
        finally:
            db.close()
    
    def _save_achievement_to_db(self, user_id: str, achievement_id: str, unlocked_at: datetime):
        """保存成就到数据库"""
        db = next(self.get_db())
        try:
            existing = db.query(DBAchievement).filter(
                DBAchievement.user_id == user_id,
                DBAchievement.achievement_id == achievement_id
            ).first()
            if not existing:
                db_achievement = DBAchievement(
                    user_id=user_id,
                    achievement_id=achievement_id,
                    unlocked_at=unlocked_at
                )
                db.add(db_achievement)
                db.commit()
        finally:
            db.close()
    
    def _update_activity_count_to_db(self, user_id: str, activity_id: str, count: int):
        """更新活动计数到数据库"""
        db = next(self.get_db())
        try:
            existing = db.query(DBActivityCount).filter(
                DBActivityCount.user_id == user_id,
                DBActivityCount.activity_id == activity_id
            ).first()
            if existing:
                existing.count = count
            else:
                db_count = DBActivityCount(
                    user_id=user_id,
                    activity_id=activity_id,
                    count=count
                )
                db.add(db_count)
            db.commit()
        finally:
            db.close()
    
    def _init_activities(self):
        """初始化打卡活动"""
        self.activities = [
            CheckinActivity(
                id="morning_class",
                name="我上早八",
                icon="📚",
                time_slots=["07:30-08:30"],
                description="既然决定起床，已经很有毅力了！",
                rarity="common",
                required_count=21
            ),
            CheckinActivity(
                id="night_study",
                name="谁说晚自习一定要在教室上",
                icon="📖",
                time_slots=["19:00-22:00"],
                description="看得出你仍有高中生般的自律！",
                rarity="common",
                required_count=21
            ),
            CheckinActivity(
                id="midnight_run",
                name="运动一下",
                icon="🏃",
                time_slots=["15:00-17:00"],
                description="我私下跑步打球游泳都来的",
                rarity="common",
                required_count=15
            ),
            CheckinActivity(
                id="early_bird",
                name="Early Bird",
                icon="🌅",
                time_slots=["06:00-07:00"],
                description="能打到这个卡的人，牛逼！",
                rarity="rare",
                required_count=1
            ),
            CheckinActivity(
                id="lunch_time",
                name="人是铁饭是钢",
                icon="🍜",
                time_slots=["11:30-13:00"],
                description="是啊吃什么",
                rarity="common",
                required_count=25
            ),
            CheckinActivity(
                id="weekend_exercise",
                name="周末啦，放松一下~",
                icon="⚽",
                time_slots=["08:00-10:00", "15:00-18:00"],
                description="祝你这个周末无实验无讲座无周会无考试无ddl^^",
                rarity="rare",
                required_count=8
            ),
        ]
        
        self.activities_dict = {a.id: a for a in self.activities}
    
    def _get_current_activity(self) -> Optional[CheckinActivity]:
        """获取当前时间段匹配的活动"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        current_time = current_hour * 60 + current_minute
        
        for activity in self.activities:
            for slot in activity.time_slots:
                try:
                    start_str, end_str = slot.split('-')
                    start_hour, start_minute = map(int, start_str.split(':'))
                    end_hour, end_minute = map(int, end_str.split(':'))
                    
                    start_time = start_hour * 60 + start_minute
                    end_time = end_hour * 60 + end_minute
                    
                    if start_time <= current_time <= end_time:
                        return activity
                except:
                    continue
        
        return None
    
    def _init_achievements(self):
        """初始化成就系统"""
        achievement_list = [
            Achievement(
                id="first_checkin",
                name="初来乍到",
                description="完成第一次打卡",
                icon="🎯",
                type=AchievementType.CHECKIN,
                required_count=1,
                rarity="common",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="checkin_10",
                name="打卡达人",
                description="累计打卡10次",
                icon="🏆",
                type=AchievementType.CHECKIN,
                required_count=10,
                rarity="common",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="checkin_50",
                name="打卡大师",
                description="累计打卡50次",
                icon="👑",
                type=AchievementType.CHECKIN,
                required_count=50,
                rarity="rare",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="checkin_100",
                name="打卡传奇",
                description="累计打卡100次",
                icon="🌟",
                type=AchievementType.CHECKIN,
                required_count=100,
                rarity="epic",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="streak_7",
                name="坚持一周",
                description="连续打卡7天",
                icon="📅",
                type=AchievementType.STREAK,
                required_count=7,
                rarity="common",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="streak_30",
                name="月度之星",
                description="连续打卡30天",
                icon="🌙",
                type=AchievementType.STREAK,
                required_count=30,
                rarity="rare",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="streak_100",
                name="百日坚持",
                description="连续打卡100天",
                icon="☀️",
                type=AchievementType.STREAK,
                required_count=100,
                rarity="epic",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="explore_5",
                name="校园探索者",
                description="在5个不同地点打卡",
                icon="🗺️",
                type=AchievementType.EXPLORE,
                required_count=5,
                rarity="common",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="explore_10",
                name="校园旅行家",
                description="在10个不同地点打卡",
                icon="🚀",
                type=AchievementType.EXPLORE,
                required_count=10,
                rarity="rare",
                hidden=False,
                created_at=datetime.now()
            ),
            Achievement(
                id="hidden_three_campus",
                name="神秘探索者",
                description="在南湖、马房山、余家头三个校区都完成打卡",
                icon="🔮",
                type=AchievementType.HIDDEN,
                required_count=1,
                rarity="legendary",
                hidden=True,
                display_name="???",
                display_desc="???",
                created_at=datetime.now()
            ),
            Achievement(
                id="hidden_night",
                name="夜行者",
                description="在晚上22:00-06:00之间完成打卡",
                icon="🌙",
                type=AchievementType.HIDDEN,
                required_count=1,
                rarity="legendary",
                hidden=True,
                display_name="???",
                display_desc="???",
                created_at=datetime.now()
            ),
            Achievement(
                id="hidden_morning",
                name="早起达人",
                description="在早上06:00-08:00之间完成打卡",
                icon="🌅",
                type=AchievementType.HIDDEN,
                required_count=1,
                rarity="epic",
                hidden=True,
                display_name="???",
                display_desc="???",
                created_at=datetime.now()
            ),
        ]
        
        for achievement in achievement_list:
            self.achievements[achievement.id] = achievement
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Haversine公式计算两点间距离（米）
        """
        R = 6371000
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def check_if_in_geofence(
        self,
        user_location: Location,
        place_location: Location,
        radius: int
    ) -> bool:
        """
        检查是否在电子围栏内
        """
        distance = self._haversine_distance(
            user_location.latitude,
            user_location.longitude,
            place_location.latitude,
            place_location.longitude
        )
        return distance <= radius
    
    async def checkin(
        self,
        user_id: str,
        user_location: Location = None,
        place_id: int = 0,
        place_name: str = "通用打卡",
        place_location: Location = None,
        geofence_radius: int = 20
    ) -> CheckinResult:
        """
        打卡（基于时间段自动匹配活动）
        """
        now = datetime.now()
        
        current_activity = self._get_current_activity()
        
        user_data = self._load_user_data_from_db(user_id)
        user_checkins = user_data['checkins']
        user_achievements = user_data['achievements']
        user_activity_counts = user_data['activity_counts']
        
        today = datetime.now().date()
        today_checkins = [r for r in user_checkins if r.checkin_time.date() == today]
        
        if current_activity:
            activity_checkins_today = [r for r in today_checkins if r.place_name == current_activity.name]
            if len(activity_checkins_today) > 0:
                return CheckinResult(
                    success=False,
                    message=f"您今天已经在【{current_activity.name}】活动中打过卡了！",
                    new_achievements=[]
                )
            
            if current_activity.id not in user_activity_counts:
                user_activity_counts[current_activity.id] = 0
            
            user_activity_counts[current_activity.id] += 1
        else:
            normal_checkins_today = [r for r in today_checkins if r.place_name.startswith("通用打卡")]
            if len(normal_checkins_today) > 0:
                return CheckinResult(
                    success=False,
                    message="您今天已经打过卡了，明天再来吧！",
                    new_achievements=[]
                )
        
        final_place_name = ""
        if current_activity:
            final_place_name = current_activity.name
        elif place_name:
            final_place_name = place_name
        else:
            final_place_name = f"通用打卡 ({now.strftime('%H:%M')})"
        
        record_id = self._save_checkin_to_db(
            user_id=user_id,
            place_name=final_place_name,
            checkin_time=now,
            latitude=user_location.latitude if user_location else 0.0,
            longitude=user_location.longitude if user_location else 0.0,
            activity_id=current_activity.id if current_activity else ""
        )
        
        if current_activity:
            self._update_activity_count_to_db(user_id, current_activity.id, user_activity_counts[current_activity.id])
        
        user_checkins.append(CheckinRecord(
            id=record_id,
            user_id=str(user_id),
            place_id=place_id or 0,
            place_name=final_place_name,
            checkin_time=now,
            latitude=user_location.latitude if user_location else 0.0,
            longitude=user_location.longitude if user_location else 0.0
        ))
        
        new_achievements = await self._check_and_grant_achievements(
            user_id, 
            user_checkins, 
            user_achievements, 
            now
        )
        
        for achievement in new_achievements:
            self._save_achievement_to_db(user_id, achievement.id, now)
        
        current_consecutive_days = self._get_consecutive_days(user_checkins)
        
        if current_activity:
            message = f"✅ 打卡成功！{current_activity.icon} 计入【{current_activity.name}】进度 ({user_activity_counts.get(current_activity.id, 1)}/{current_activity.required_count})"
        else:
            message = f"✅ 打卡成功！不在任何活动时间段，普通打卡一次"
        
        return CheckinResult(
            success=True,
            message=message,
            place_name=final_place_name,
            new_achievements=new_achievements,
            consecutive_days=current_consecutive_days
        )
    
    async def _check_and_grant_achievements(
        self,
        user_id: str,
        user_checkins: List[CheckinRecord],
        user_achievements: Set[str],
        checkin_time: datetime = None
    ) -> List[Achievement]:
        """
        检查并授予成就
        """
        new_achievements = []
        
        checkin_count = len(user_checkins)
        consecutive_days = self._get_consecutive_days(user_checkins)
        unique_places = len({r.place_name for r in user_checkins})
        
        for achievement in self.achievements.values():
            if achievement.id in user_achievements:
                continue
            
            if achievement.type == AchievementType.CHECKIN:
                if checkin_count >= achievement.required_count:
                    new_achievements.append(achievement)
            
            elif achievement.type == AchievementType.STREAK:
                if consecutive_days >= achievement.required_count:
                    new_achievements.append(achievement)
            
            elif achievement.type == AchievementType.EXPLORE:
                if unique_places >= achievement.required_count:
                    new_achievements.append(achievement)
            
            elif achievement.type == AchievementType.HIDDEN:
                if self._check_hidden_achievement(achievement, user_checkins, checkin_time):
                    new_achievements.append(achievement)
        
        return new_achievements
    
    def _check_hidden_achievement(
        self,
        achievement: Achievement,
        user_checkins: List[CheckinRecord],
        checkin_time: datetime = None
    ) -> bool:
        """
        检查隐藏成就
        """
        if achievement.id == "hidden_three_campus":
            campus_keywords = ['南湖', '马房山', '余家头']
            visited_campuses = set()
            for record in user_checkins:
                for keyword in campus_keywords:
                    if keyword in record.place_name:
                        visited_campuses.add(keyword)
            return len(visited_campuses) >= 3
        
        elif achievement.id == "hidden_night":
            if checkin_time:
                hour = checkin_time.hour
                return hour >= 22 or hour < 6
            return False
        
        elif achievement.id == "hidden_morning":
            if checkin_time:
                hour = checkin_time.hour
                return 6 <= hour < 8
            return False
        
        return False
    
    def _get_consecutive_days(self, checkins: List[CheckinRecord]) -> int:
        """
        获取连续打卡天数
        """
        if not checkins:
            return 0
        
        checkin_dates = {record.checkin_time.date() for record in checkins}
        today = datetime.now().date()
        
        today_checked_in = today in checkin_dates
        yesterday = today - timedelta(days=1)
        yesterday_checked_in = yesterday in checkin_dates
        
        if not today_checked_in and not yesterday_checked_in:
            return 0
        
        if today_checked_in:
            dates_to_check = sorted([today + timedelta(days=i) for i in range(len(checkin_dates))], reverse=True)
        else:
            dates_to_check = sorted([yesterday + timedelta(days=i) for i in range(len(checkin_dates))], reverse=True)
        
        consecutive = 0
        for i, date in enumerate(dates_to_check):
            if date in checkin_dates:
                consecutive += 1
            else:
                break
        
        return consecutive
    
    def _check_consecutive_days(
        self,
        checkins: List[CheckinRecord],
        required_days: int
    ) -> bool:
        """
        检查连续打卡天数
        """
        if not checkins:
            return False
        
        dates = sorted({record.checkin_time.date() for record in checkins}, reverse=True)
        
        if len(dates) < required_days:
            return False
        
        consecutive = True
        for i in range(1, required_days):
            expected_date = dates[0] - timedelta(days=i)
            if dates[i] != expected_date:
                consecutive = False
                break
        
        return consecutive
    
    async def get_checkin_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[CheckinRecord]:
        """
        获取打卡历史
        """
        db = next(self.get_db())
        db_checkins = db.query(DBCheckin).filter(
            DBCheckin.user_id == str(user_id)
        ).order_by(DBCheckin.checkin_time.desc()).limit(limit).all()
        
        records = []
        for db_checkin in db_checkins:
            records.append(CheckinRecord(
                id=db_checkin.id,
                user_id=db_checkin.user_id,
                place_id=0,
                place_name=db_checkin.place_name,
                checkin_time=db_checkin.checkin_time,
                latitude=db_checkin.latitude,
                longitude=db_checkin.longitude
            ))
        
        return records
    
    async def get_user_achievements(
        self,
        user_id: str
    ) -> List[UserAchievement]:
        """
        获取用户已获得的成就
        """
        db = next(self.get_db())
        db_achievements = db.query(DBAchievement).filter(
            DBAchievement.user_id == str(user_id)
        ).all()
        
        achievements = []
        for db_achievement in db_achievements:
            achievement = self.achievements.get(db_achievement.achievement_id)
            if achievement:
                achievements.append(UserAchievement(
                    achievement=achievement,
                    earned_at=db_achievement.unlocked_at,
                    is_new=False
                ))
        
        return achievements
    
    async def get_all_achievements(
        self,
        user_id: Optional[str] = None
    ) -> Tuple[List[UserAchievement], List[Achievement]]:
        """
        获取所有成就（包含未获得的）
        """
        earned: List[UserAchievement] = []
        not_earned: List[Achievement] = []
        
        earned_ids = set()
        if user_id:
            db = next(self.get_db())
            db_achievements = db.query(DBAchievement).filter(
                DBAchievement.user_id == str(user_id)
            ).all()
            earned_ids = {a.achievement_id for a in db_achievements}
            
            for db_achievement in db_achievements:
                achievement = self.achievements.get(db_achievement.achievement_id)
                if achievement:
                    earned.append(UserAchievement(
                        achievement=achievement,
                        earned_at=db_achievement.unlocked_at,
                        is_new=False
                    ))
        
        for achievement in self.achievements.values():
            if achievement.id not in earned_ids:
                not_earned.append(achievement)
        
        return earned, not_earned
    
    async def get_checkin_statistics(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        获取打卡统计
        """
        user_data = self._load_user_data_from_db(user_id)
        records = user_data['checkins']
        total_checkins = len(records)
        earned_ids = user_data['achievements']
        user_activity_counts = user_data['activity_counts']
        
        consecutive_days = self._get_consecutive_days(records)
        
        place_counts: Dict[str, int] = {}
        for record in records:
            place_counts[record.place_name] = place_counts.get(record.place_name, 0) + 1
        
        unique_places = len(place_counts)
        
        achievements_progress = {}
        
        db = next(self.get_db())
        db_achievements = db.query(DBAchievement).filter(
            DBAchievement.user_id == str(user_id)
        ).all()
        achievement_unlock_times = {a.achievement_id: a.unlocked_at for a in db_achievements}
        
        for achievement in self.achievements.values():
            is_unlocked = achievement.id in earned_ids
            unlock_time = None
            
            if is_unlocked:
                unlock_time = achievement_unlock_times.get(achievement.id)
            
            achievements_progress[achievement.id] = {
                'id': achievement.id,
                'unlocked': is_unlocked,
                'unlock_time': unlock_time.isoformat() if unlock_time else None,
                'progress': 0
            }
            
            if not is_unlocked and achievement.type != AchievementType.HIDDEN:
                if achievement.type == AchievementType.CHECKIN:
                    progress = min(100, int((total_checkins / achievement.required_count) * 100))
                elif achievement.type == AchievementType.STREAK:
                    progress = min(100, int((consecutive_days / achievement.required_count) * 100))
                elif achievement.type == AchievementType.EXPLORE:
                    progress = min(100, int((unique_places / achievement.required_count) * 100))
                else:
                    progress = 0
                
                achievements_progress[achievement.id]['progress'] = progress
        
        activities_progress = []
        current_activity = self._get_current_activity()
        
        for activity in self.activities:
            count = user_activity_counts.get(activity.id, 0)
            progress = min(100, int((count / activity.required_count) * 100))
            activities_progress.append({
                'id': activity.id,
                'name': activity.name,
                'icon': activity.icon,
                'description': activity.description,
                'rarity': activity.rarity,
                'count': count,
                'required': activity.required_count,
                'progress': progress,
                'is_active': current_activity.id == activity.id if current_activity else False
            })
        
        return {
            "total_checkins": total_checkins,
            "consecutive_days": consecutive_days,
            "unique_places": unique_places,
            "place_stats": place_counts,
            "earned_achievements": len(earned_ids),
            "achievements": achievements_progress,
            "unique_places_count": unique_places,
            "activities": activities_progress,
            "current_activity": {
                'id': current_activity.id,
                'name': current_activity.name,
                'icon': current_activity.icon,
                'time_slots': current_activity.time_slots
            } if current_activity else None
        }
