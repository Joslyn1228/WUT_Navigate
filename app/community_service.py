"""
社区服务模块
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import func
from .extended_schemas import (
    Post, PostCreate,
    Comment, CommentCreate,
    Location
)
from .auth_service import SessionLocal, DBPost, DBPostImage, DBPostLike, DBPostComment, DBPostFavorite, DBUser


class CommunityService:
    """社区服务"""
    
    def __init__(self):
        pass
    
    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def _get_user_info(self, db, user_id: str):
        """获取用户信息"""
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user:
            return {
                'nickname': user.nickname,
                'avatar': user.avatar
            }
        return {
            'nickname': f"用户{user_id}",
            'avatar': None
        }
    
    def _load_post_from_db(self, db, post_id: int, current_user_id: Optional[str] = None) -> Optional[Post]:
        """从数据库加载帖子"""
        db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
        if not db_post:
            return None
        
        user_info = self._get_user_info(db, db_post.user_id)
        
        likes_count = db.query(DBPostLike).filter(DBPostLike.post_id == post_id).count()
        comments_count = db.query(DBPostComment).filter(DBPostComment.post_id == post_id).count()
        
        is_liked = False
        if current_user_id:
            existing_like = db.query(DBPostLike).filter(
                DBPostLike.post_id == post_id,
                DBPostLike.user_id == current_user_id
            ).first()
            is_liked = existing_like is not None
        
        db_images = db.query(DBPostImage).filter(
            DBPostImage.post_id == post_id
        ).order_by(DBPostImage.sort_order).all()
        images = [{'url': img.image_url} for img in db_images]
        
        # 构建位置信息
        location = None
        if db_post.location_name:
            location = db_post.location_name
            if db_post.campus:
                location = f"{db_post.campus} · {location}"
        
        post = Post(
            id=db_post.id,
            user_id=db_post.user_id,
            content=db_post.content,
            images=images,
            user_nickname=user_info['nickname'],
            user_avatar=user_info['avatar'],
            likes_count=likes_count,
            comments_count=comments_count,
            created_at=db_post.created_at,
            is_liked=is_liked,
            location=location
        )
        
        return post
    
    def _save_post_to_db(self, user_id: str, content: str, images: List[str] = None, 
                        location_name: Optional[str] = None, campus: Optional[str] = None) -> int:
        """保存帖子到数据库"""
        db = next(self.get_db())
        try:
            now = datetime.now()
            
            db_post = DBPost(
                user_id=user_id,
                content=content or "",
                location_name=location_name or "",
                latitude=0.0,
                longitude=0.0,
                campus=campus or "",
                created_at=now,
                updated_at=now
            )
            
            db.add(db_post)
            db.commit()
            db.refresh(db_post)
            
            if images:
                for idx, image_url in enumerate(images):
                    db_image = DBPostImage(
                        post_id=db_post.id,
                        image_url=image_url,
                        thumbnail_url=image_url,
                        sort_order=idx
                    )
                    db.add(db_image)
            db.commit()
        
            return db_post.id
        finally:
            db.close()
    
    async def create_post(
        self,
        user_id: str,
        content: Optional[str],
        images: Optional[List[str]] = None,
        location_name: Optional[str] = None,
        campus: Optional[str] = None
    ) -> Post:
        """
        创建帖子
        
        Args:
            user_id: 用户ID (UUID字符串)
            content: 内容
            images: 图片URL列表
            location_name: 位置名称
            campus: 校区信息
            
        Returns:
            创建的帖子
        """
        post_id = self._save_post_to_db(user_id, content, images or [], location_name, campus)
        return await self.get_post(post_id, user_id)
    
    async def get_post(
        self,
        post_id: int,
        current_user_id: Optional[str] = None
    ) -> Optional[Post]:
        """
        获取帖子详情
        
        Args:
            post_id: 帖子ID
            current_user_id: 当前用户ID (UUID字符串)
            
        Returns:
            帖子或None
        """
        db = next(self.get_db())
        post = self._load_post_from_db(db, post_id, current_user_id)
        
        if post:
            post.comments = await self._get_post_comments(db, post_id, current_user_id)
        
        return post
    
    async def _get_post_comments(self, db, post_id: int, current_user_id: Optional[str] = None) -> List[Comment]:
        """获取帖子评论（支持二级评论）"""
        db_comments = db.query(DBPostComment).filter(
            DBPostComment.post_id == post_id
        ).order_by(DBPostComment.created_at).all()
        
        comments_map = {}
        root_comments = []
        
        for db_comment in db_comments:
            user_info = self._get_user_info(db, db_comment.user_id)
            comment = Comment(
                id=db_comment.id,
                post_id=db_comment.post_id,
                user_id=db_comment.user_id,
                user_nickname=user_info['nickname'],
                content=db_comment.content,
                created_at=db_comment.created_at
            )
            comments_map[db_comment.id] = comment
            
            if db_comment.parent_comment_id == 0:
                root_comments.append(comment)
            else:
                parent = comments_map.get(db_comment.parent_comment_id)
                if parent:
                    if not hasattr(parent, 'replies'):
                        parent.replies = []
                    parent.replies.append(comment)
        
        return root_comments
    
    async def get_feed(
        self,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Post]:
        """
        获取动态列表
        
        Args:
            user_id: 用户ID (UUID字符串)
            page: 页码
            page_size: 每页数量
            
        Returns:
            帖子列表
        """
        db = next(self.get_db())
        
        query = db.query(DBPost).order_by(DBPost.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * page_size
        
        db_posts = query.offset(offset).limit(page_size).all()
        
        posts = []
        for db_post in db_posts:
            post = self._load_post_from_db(db, db_post.id, user_id)
            if post:
                posts.append(post)
        
        return posts
    
    async def like_post(
        self,
        user_id: str,
        post_id: int
    ) -> bool:
        """
        点赞/取消点赞
        
        Args:
            user_id: 用户ID (UUID字符串)
            post_id: 帖子ID
            
        Returns:
            是否成功
        """
        db = next(self.get_db())
        
        db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
        if not db_post:
            return False
        
        existing_like = db.query(DBPostLike).filter(
            DBPostLike.post_id == post_id,
            DBPostLike.user_id == user_id
        ).first()
        
        if existing_like:
            db.delete(existing_like)
        else:
            db_like = DBPostLike(
                post_id=post_id,
                user_id=user_id,
                created_at=datetime.now()
            )
            db.add(db_like)
        
        db.commit()
        return True
    
    async def comment_post(
        self,
        user_id: str,
        post_id: int,
        content: str,
        parent_comment_id: Optional[int] = None
    ) -> Optional[Comment]:
        """
        评论帖子（支持二级评论）
        
        Args:
            user_id: 用户ID (UUID字符串)
            post_id: 帖子ID
            content: 评论内容
            parent_comment_id: 父评论ID（二级评论时使用）
            
        Returns:
            评论或None
        """
        db = next(self.get_db())
        
        db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
        if not db_post:
            return None
        
        parent_id = parent_comment_id or 0
        
        if parent_id > 0:
            parent_comment = db.query(DBPostComment).filter(
                DBPostComment.id == parent_id,
                DBPostComment.post_id == post_id
            ).first()
            if not parent_comment:
                return None
        
        user_info = self._get_user_info(db, user_id)
        
        db_comment = DBPostComment(
            post_id=post_id,
            user_id=user_id,
            parent_comment_id=parent_id,
            content=content,
            created_at=datetime.now()
        )
        
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        
        return Comment(
            id=db_comment.id,
            post_id=db_comment.post_id,
            user_id=db_comment.user_id,
            user_nickname=user_info['nickname'],
            content=db_comment.content,
            created_at=db_comment.created_at
        )
    
    async def delete_post(
        self,
        user_id: str,
        post_id: int
    ) -> bool:
        """
        删除帖子
        
        Args:
            user_id: 用户ID (UUID字符串)
            post_id: 帖子ID
            
        Returns:
            是否成功
        """
        db = next(self.get_db())
        
        db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
        if not db_post:
            return False
        
        if db_post.user_id != user_id:
            return False
        
        db.query(DBPostImage).filter(DBPostImage.post_id == post_id).delete()
        db.query(DBPostLike).filter(DBPostLike.post_id == post_id).delete()
        db.query(DBPostComment).filter(DBPostComment.post_id == post_id).delete()
        db.query(DBPostFavorite).filter(DBPostFavorite.post_id == post_id).delete()
        
        db.delete(db_post)
        db.commit()
        
        return True
    
    async def delete_comment(
        self,
        user_id: str,
        comment_id: int
    ) -> bool:
        """
        删除评论
        
        Args:
            user_id: 用户ID (UUID字符串)
            comment_id: 评论ID
            
        Returns:
            是否成功
        """
        db = next(self.get_db())
        
        db_comment = db.query(DBPostComment).filter(DBPostComment.id == comment_id).first()
        if not db_comment:
            return False
        
        if db_comment.user_id != user_id:
            return False
        
        post_id = db_comment.post_id
        
        db.query(DBPostComment).filter(
            DBPostComment.parent_comment_id == comment_id
        ).delete()
        
        db.delete(db_comment)
        db.commit()
        
        return True
    
    async def get_user_posts(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[Post]:
        """
        获取用户的帖子
        
        Args:
            user_id: 用户ID (UUID字符串)
            page: 页码
            page_size: 每页数量
            
        Returns:
            帖子列表
        """
        db = next(self.get_db())
        
        query = db.query(DBPost).filter(
            DBPost.user_id == user_id
        ).order_by(DBPost.created_at.desc())
        
        offset = (page - 1) * page_size
        db_posts = query.offset(offset).limit(page_size).all()
        
        posts = []
        for db_post in db_posts:
            post = self._load_post_from_db(db, db_post.id, user_id)
            if post:
                posts.append(post)
        
        return posts
    
    async def get_user_post_count(self, user_id: str) -> int:
        """
        获取用户帖子数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            帖子数量
        """
        db = next(self.get_db())
        count = db.query(DBPost).filter(DBPost.user_id == user_id).count()
        return count
    
    async def search_posts(
        self,
        keyword: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[Post]:
        """
        搜索帖子
        
        Args:
            keyword: 关键词
            page: 页码
            page_size: 每页数量
            
        Returns:
            帖子列表
        """
        db = next(self.get_db())
        
        keyword = keyword.lower()
        
        query = db.query(DBPost).filter(
            DBPost.content.ilike(f"%{keyword}%")
        ).order_by(DBPost.created_at.desc())
        
        offset = (page - 1) * page_size
        db_posts = query.offset(offset).limit(page_size).all()
        
        posts = []
        for db_post in db_posts:
            post = self._load_post_from_db(db, db_post.id)
            if post:
                posts.append(post)
        
        return posts
    
    async def favorite_post(
        self,
        user_id: str,
        post_id: int
    ) -> bool:
        """
        收藏/取消收藏帖子
        
        Args:
            user_id: 用户ID (UUID字符串)
            post_id: 帖子ID
            
        Returns:
            是否成功
        """
        db = next(self.get_db())
        
        db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
        if not db_post:
            return False
        
        existing_favorite = db.query(DBPostFavorite).filter(
            DBPostFavorite.post_id == post_id,
            DBPostFavorite.user_id == user_id
        ).first()
        
        if existing_favorite:
            db.delete(existing_favorite)
        else:
            db_favorite = DBPostFavorite(
                post_id=post_id,
                user_id=user_id,
                created_at=datetime.now()
            )
            db.add(db_favorite)
        
        db.commit()
        return True
    
    async def get_favorite_posts(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[Post]:
        """
        获取用户收藏的帖子
        
        Args:
            user_id: 用户ID (UUID字符串)
            page: 页码
            page_size: 每页数量
            
        Returns:
            帖子列表
        """
        db = next(self.get_db())
        
        query = db.query(DBPost).join(DBPostFavorite, DBPost.id == DBPostFavorite.post_id).filter(
            DBPostFavorite.user_id == user_id
        ).order_by(DBPostFavorite.created_at.desc())
        
        offset = (page - 1) * page_size
        db_posts = query.offset(offset).limit(page_size).all()
        
        posts = []
        for db_post in db_posts:
            post = self._load_post_from_db(db, db_post.id, user_id)
            if post:
                posts.append(post)
        
        return posts
    
    async def get_post_likes_count(self, post_id: int) -> int:
        """
        获取帖子点赞数
        
        Args:
            post_id: 帖子ID
            
        Returns:
            点赞数
        """
        db = next(self.get_db())
        return db.query(DBPostLike).filter(DBPostLike.post_id == post_id).count()
    
    async def get_post_comments_count(self, post_id: int) -> int:
        """
        获取帖子评论数
        
        Args:
            post_id: 帖子ID
            
        Returns:
            评论数
        """
        db = next(self.get_db())
        return db.query(DBPostComment).filter(DBPostComment.post_id == post_id).count()