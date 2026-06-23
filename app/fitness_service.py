"""
运动健康服务模块
"""
import math
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .extended_schemas import (
    Workout, WorkoutType, WorkoutSummary,
    FitnessStats, FitnessStatsPeriod,
    Location
)
from .auth_service import SessionLocal, DBWorkout, DBWorkoutRoute


class FitnessService:
    """运动健康服务"""
    
    def __init__(self):
        self.current_workouts: Dict[str, Workout] = {}
    
    def calculate_calories(
        self,
        workout_type: WorkoutType,
        duration_minutes: int,
        weight_kg: Optional[float] = None
    ) -> float:
        """
        计算卡路里消耗
        
        Args:
            workout_type: 运动类型
            duration_minutes: 持续时间（分钟）
            weight_kg: 体重（公斤）
            
        Returns:
            消耗的卡路里
        """
        met_values = {
            WorkoutType.WALKING: 3.5,
            WorkoutType.RUNNING: 8.0,
            WorkoutType.CYCLING: 6.0
        }
        
        met = met_values.get(workout_type, 5.0)
        weight = weight_kg if weight_kg else 65.0
        
        calories = met * weight * (duration_minutes / 60)
        return round(calories, 2)
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        计算两点之间的距离（米）
        
        Args:
            loc1: 位置1
            loc2: 位置2
            
        Returns:
            距离（米）
        """
        lat1, lon1 = loc1.latitude, loc1.longitude
        lat2, lon2 = loc2.latitude, loc2.longitude
        
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2) ** 2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    async def start_workout(
        self,
        user_id: str,
        workout_type: WorkoutType,
        start_location: Optional[Location] = None
    ) -> int:
        """
        开始运动
        
        Args:
            user_id: 用户ID
            workout_type: 运动类型
            start_location: 起始位置
            
        Returns:
            运动ID
        """
        db = SessionLocal()
        try:
            new_workout = DBWorkout(
                user_id=user_id,
                workout_type=workout_type.value,
                start_time=datetime.now()
            )
            
            db.add(new_workout)
            db.commit()
            db.refresh(new_workout)
            
            workout = Workout(
                workout_id=new_workout.id,
                user_id=user_id,
                workout_type=workout_type,
                start_time=new_workout.start_time,
                start_location=start_location,
                end_time=None,
                end_location=None,
                duration=0,
                distance=0.0,
                calories=0.0,
                route=[]
            )
            
            self.current_workouts[user_id] = workout
            return new_workout.id
        finally:
            db.close()
    
    async def update_workout(
        self,
        user_id: str,
        workout_id: int,
        location: Optional[Location] = None
    ) -> bool:
        """
        更新运动位置
        
        Args:
            user_id: 用户ID
            workout_id: 运动ID
            location: 当前位置
            
        Returns:
            是否更新成功
        """
        if user_id not in self.current_workouts:
            return False
        
        workout = self.current_workouts[user_id]
        
        if location and workout.start_location:
            distance_added = self.calculate_distance(workout.start_location, location)
            workout.distance += distance_added
        
        if location:
            workout.route.append({
                'latitude': location.latitude,
                'longitude': location.longitude,
                'timestamp': datetime.now()
            })
            
            db = SessionLocal()
            try:
                route_point = DBWorkoutRoute(
                    workout_id=workout_id,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    timestamp=datetime.now(),
                    sequence=len(workout.route)
                )
                db.add(route_point)
                db.commit()
            finally:
                db.close()
        
        return True
    
    async def end_workout(
        self,
        user_id: str,
        workout_id: int,
        weight: Optional[float] = None,
        distance: Optional[float] = None,
        duration: Optional[int] = None,
        calories: Optional[float] = None
    ) -> WorkoutSummary:
        """
        结束运动
        
        Args:
            user_id: 用户ID
            workout_id: 运动ID
            weight: 体重（用于计算卡路里）
            distance: 前端发送的运动距离（米）
            duration: 前端发送的运动时长（秒）
            calories: 前端发送的卡路里消耗
            
        Returns:
            运动总结
        """
        end_time = datetime.now()
        
        # 使用前端发送的数据，如果没有则从内存中获取或计算
        if user_id in self.current_workouts:
            workout = self.current_workouts[user_id]
            start_time = workout.start_time
            workout_type = workout.workout_type
            
            # 如果前端没有发送数据，从后端计算
            if duration is None:
                duration = int((end_time - workout.start_time).total_seconds())
            if distance is None:
                distance = getattr(workout, 'distance', 0.0)
            if calories is None:
                calories = self.calculate_calories(workout.workout_type, duration // 60, weight)
            
            del self.current_workouts[user_id]
        else:
            # 如果内存中没有记录，从数据库获取
            db = SessionLocal()
            try:
                db_workout = db.query(DBWorkout).filter(DBWorkout.id == workout_id).first()
                if db_workout:
                    start_time = db_workout.start_time
                    workout_type = db_workout.workout_type
                else:
                    start_time = end_time
                    workout_type = WorkoutType.WALKING
            finally:
                db.close()
            
            # 如果没有任何数据，使用默认值
            if duration is None:
                duration = 0
            if distance is None:
                distance = 0.0
            if calories is None:
                calories = 0.0
        
        # 更新数据库
        db = SessionLocal()
        try:
            db_workout = db.query(DBWorkout).filter(DBWorkout.id == workout_id).first()
            if db_workout:
                db_workout.end_time = end_time
                db_workout.total_duration = duration
                db_workout.total_distance = distance
                db_workout.calories_burned = calories
                if duration > 0:
                    db_workout.avg_speed = (distance / 1000) / (duration / 3600)
                db.commit()
        finally:
            db.close()
        
        return WorkoutSummary(
            workout_id=workout_id,
            user_id=user_id,
            workout_type=workout_type,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            distance=round(distance, 2),
            calories=calories
        )
    
    async def get_fitness_stats(
        self,
        user_id: str,
        period: FitnessStatsPeriod
    ) -> FitnessStats:
        """
        获取运动统计
        
        Args:
            user_id: 用户ID
            period: 统计周期
            
        Returns:
            运动统计数据
        """
        db = SessionLocal()
        try:
            now = datetime.now()
            
            if period == FitnessStatsPeriod.WEEK:
                start_date = now - timedelta(weeks=1)
            elif period == FitnessStatsPeriod.MONTH:
                start_date = now - timedelta(days=30)
            elif period == FitnessStatsPeriod.YEAR:
                start_date = now - timedelta(days=365)
            else:
                start_date = None
            
            query = db.query(DBWorkout).filter(DBWorkout.user_id == user_id)
            
            if start_date:
                query = query.filter(DBWorkout.start_time >= start_date)
            
            workouts = query.all()
            
            total_distance = sum(w.total_distance or 0 for w in workouts)
            total_calories = sum(w.calories_burned or 0 for w in workouts)
            total_duration = sum(w.total_duration or 0 for w in workouts)
            count = len(workouts)
            
            avg_distance = round(total_distance / count, 2) if count > 0 else 0.0
            avg_duration = round(total_duration / count) if count > 0 else 0
            
            return FitnessStats(
                total_distance=round(total_distance, 2),
                total_calories=round(total_calories, 2),
                total_duration=total_duration,
                workout_count=count,
                avg_distance=avg_distance,
                avg_duration=avg_duration,
                period=period
            )
        finally:
            db.close()
    
    async def get_workout_history(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取运动历史记录
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            运动历史记录列表
        """
        db = SessionLocal()
        try:
            workouts = db.query(DBWorkout)\
                .filter(DBWorkout.user_id == user_id)\
                .order_by(DBWorkout.start_time.desc())\
                .limit(limit)\
                .all()
            
            history = []
            for w in workouts:
                history.append({
                    'id': w.id,
                    'workout_type': w.workout_type,
                    'start_time': w.start_time.isoformat(),
                    'total_duration': w.total_duration or 0,
                    'total_distance': round(w.total_distance or 0, 2),
                    'calories_burned': round(w.calories_burned or 0, 2),
                    'created_at': w.created_at.isoformat() if w.created_at else w.start_time.isoformat()
                })
            
            return history
        finally:
            db.close()
    
    async def get_current_workout(self, user_id: str) -> Optional[Workout]:
        """
        获取当前进行中的运动
        
        Args:
            user_id: 用户ID
            
        Returns:
            当前运动对象，如果没有则返回None
        """
        return self.current_workouts.get(user_id)
