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
        # MET值（代谢当量）
        met_values = {
            WorkoutType.WALKING: 3.5,
            WorkoutType.RUNNING: 8.0,
            WorkoutType.CYCLING: 6.0
        }
        
        met = met_values.get(workout_type, 5.0)
        
        # 公式：卡路里 = MET × 体重(kg) × 时间(h)
        # 如果没有体重，使用默认值
        weight = weight_kg or 70.0
        hours = duration_minutes / 60.0
        
        calories = met * weight * hours
        return round(calories, 2)
    
    def calculate_distance(
        self,
        route_points: List[Location]
    ) -> float:
        """
        计算路线距离（米）
        
        Args:
            route_points: 路线坐标点列表
            
        Returns:
            总距离（米）
        """
        if len(route_points) < 2:
            return 0.0
        
        total_distance = 0.0
        
        for i in range(1, len(route_points)):
            total_distance += self._haversine_distance(
                route_points[i-1].latitude,
                route_points[i-1].longitude,
                route_points[i].latitude,
                route_points[i].longitude
            )
        
        return round(total_distance, 2)
    
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
        R = 6371000  # 地球半径（米）
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
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
            now = datetime.now()
            
            # 创建运动记录
            db_workout = DBWorkout(
                user_id=user_id,
                workout_type=workout_type.value,
                start_time=now,
                created_at=now
            )
            db.add(db_workout)
            db.commit()
            db.refresh(db_workout)
            
            # 如果有起始位置，添加路线点
            if start_location:
                db_route = DBWorkoutRoute(
                    workout_id=db_workout.id,
                    latitude=start_location.latitude,
                    longitude=start_location.longitude,
                    recorded_at=now
                )
                db.add(db_route)
                db.commit()
            
            return db_workout.id
        finally:
            db.close()
    
    async def update_workout(
        self,
        user_id: str,
        workout_id: int,
        location: Location
    ) -> Dict[str, Any]:
        """
        更新运动（添加路线点）
        
        Args:
            user_id: 用户ID
            workout_id: 运动ID
            location: 当前位置
            
        Returns:
            更新信息
        """
        db = SessionLocal()
        try:
            # 查询运动记录
            workout = db.query(DBWorkout).filter(
                DBWorkout.id == workout_id,
                DBWorkout.user_id == user_id,
                DBWorkout.end_time.is_(None)
            ).first()
            
            if not workout:
                raise ValueError("No active workout found")
            
            # 添加路线点
            db_route = DBWorkoutRoute(
                workout_id=workout_id,
                latitude=location.latitude,
                longitude=location.longitude,
                recorded_at=datetime.now()
            )
            db.add(db_route)
            db.commit()
            
            # 查询所有路线点计算距离
            routes = db.query(DBWorkoutRoute).filter(
                DBWorkoutRoute.workout_id == workout_id
            ).order_by(DBWorkoutRoute.recorded_at).all()
            
            route_points = [
                Location(latitude=r.latitude, longitude=r.longitude)
                for r in routes
            ]
            
            # 计算当前距离
            current_distance = self.calculate_distance(route_points)
            
            # 计算当前持续时间
            duration = int((datetime.now() - workout.start_time).total_seconds())
            
            return {
                "workout_id": workout_id,
                "current_distance": current_distance,
                "current_duration": duration,
                "location": location
            }
        finally:
            db.close()
    
    async def end_workout(
        self,
        user_id: str,
        workout_id: int,
        user_weight: Optional[float] = None
    ) -> WorkoutSummary:
        """
        结束运动
        
        Args:
            user_id: 用户ID
            workout_id: 运动ID
            user_weight: 用户体重
            
        Returns:
            运动总结
        """
        db = SessionLocal()
        try:
            # 查询运动记录
            workout = db.query(DBWorkout).filter(
                DBWorkout.id == workout_id,
                DBWorkout.user_id == user_id,
                DBWorkout.end_time.is_(None)
            ).first()
            
            if not workout:
                raise ValueError("No active workout found")
            
            # 更新结束时间
            workout.end_time = datetime.now()
            
            # 查询所有路线点
            routes = db.query(DBWorkoutRoute).filter(
                DBWorkoutRoute.workout_id == workout_id
            ).order_by(DBWorkoutRoute.recorded_at).all()
            
            route_points = [
                Location(latitude=r.latitude, longitude=r.longitude)
                for r in routes
            ]
            
            # 计算总距离
            total_distance = self.calculate_distance(route_points) if route_points else 0.0
            workout.total_distance = total_distance
            
            # 计算总时长
            total_duration = int(
                (workout.end_time - workout.start_time).total_seconds()
            )
            workout.total_duration = total_duration
            
            # 计算卡路里
            duration_minutes = total_duration // 60
            workout_type = WorkoutType(workout.workout_type)
            calories_burned = self.calculate_calories(
                workout_type,
                duration_minutes,
                user_weight
            )
            workout.calories_burned = calories_burned
            
            # 计算平均速度
            avg_speed = 0.0
            if total_distance and total_duration > 0:
                # 转换为公里/小时
                avg_speed = (total_distance / 1000.0) / (total_duration / 3600.0)
                avg_speed = round(avg_speed, 2)
            workout.avg_speed = avg_speed
            
            db.commit()
            
            return WorkoutSummary(
                id=workout.id,
                total_distance=total_distance,
                total_duration=total_duration,
                calories_burned=calories_burned,
                avg_speed=avg_speed,
                route_points=route_points
            )
        finally:
            db.close()
    
    async def get_workout_history(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Workout]:
        """
        获取运动历史
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            
        Returns:
            运动列表
        """
        db = SessionLocal()
        try:
            # 查询用户的运动记录
            db_workouts = db.query(DBWorkout).filter(
                DBWorkout.user_id == user_id
            ).order_by(DBWorkout.created_at.desc()).limit(limit).all()
            
            workouts = []
            for db_workout in db_workouts:
                # 查询路线点
                routes = db.query(DBWorkoutRoute).filter(
                    DBWorkoutRoute.workout_id == db_workout.id
                ).order_by(DBWorkoutRoute.recorded_at).all()
                
                route_points = [
                    Location(latitude=r.latitude, longitude=r.longitude)
                    for r in routes
                ]
                
                workout = Workout(
                    id=db_workout.id,
                    user_id=db_workout.user_id,
                    workout_type=WorkoutType(db_workout.workout_type),
                    start_time=db_workout.start_time,
                    end_time=db_workout.end_time,
                    total_distance=db_workout.total_distance,
                    total_duration=db_workout.total_duration,
                    calories_burned=db_workout.calories_burned,
                    route_points=route_points,
                    created_at=db_workout.created_at
                )
                workouts.append(workout)
            
            return workouts
        finally:
            db.close()
    
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
            统计数据
        """
        db = SessionLocal()
        try:
            # 查询用户的运动记录
            query = db.query(DBWorkout).filter(
                DBWorkout.user_id == user_id,
                DBWorkout.end_time.isnot(None)
            )
            
            # 根据周期筛选
            if period != FitnessStatsPeriod.ALL:
                now = datetime.now()
                if period == FitnessStatsPeriod.DAY:
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif period == FitnessStatsPeriod.WEEK:
                    start_date = now - timedelta(days=now.weekday())
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                else:  # MONTH
                    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(DBWorkout.created_at >= start_date)
            
            period_workouts = query.all()
            
            # 计算统计
            total_distance = sum(w.total_distance or 0 for w in period_workouts)
            total_duration = sum(w.total_duration or 0 for w in period_workouts)
            total_calories = sum(w.calories_burned or 0 for w in period_workouts)
            workout_count = len(period_workouts)
            
            avg_distance = total_distance / workout_count if workout_count > 0 else 0
            avg_duration = total_duration // workout_count if workout_count > 0 else 0
            
            return FitnessStats(
                period=period,
                total_distance=round(total_distance, 2),
                total_duration=total_duration,
                total_calories=round(total_calories, 2),
                workout_count=workout_count,
                avg_distance=round(avg_distance, 2),
                avg_duration=avg_duration
            )
        finally:
            db.close()
    
    async def get_active_workout(
        self,
        user_id: str
    ) -> Optional[Workout]:
        """
        获取当前进行中的运动
        
        Args:
            user_id: 用户ID
            
        Returns:
            当前运动或None
        """
        db = SessionLocal()
        try:
            # 查询进行中的运动（end_time为空）
            db_workout = db.query(DBWorkout).filter(
                DBWorkout.user_id == user_id,
                DBWorkout.end_time.is_(None)
            ).first()
            
            if not db_workout:
                return None
            
            # 查询路线点
            routes = db.query(DBWorkoutRoute).filter(
                DBWorkoutRoute.workout_id == db_workout.id
            ).order_by(DBWorkoutRoute.recorded_at).all()
            
            route_points = [
                Location(latitude=r.latitude, longitude=r.longitude)
                for r in routes
            ]
            
            return Workout(
                id=db_workout.id,
                user_id=db_workout.user_id,
                workout_type=WorkoutType(db_workout.workout_type),
                start_time=db_workout.start_time,
                end_time=db_workout.end_time,
                total_distance=db_workout.total_distance,
                total_duration=db_workout.total_duration,
                calories_burned=db_workout.calories_burned,
                route_points=route_points,
                created_at=db_workout.created_at
            )
        finally:
            db.close()