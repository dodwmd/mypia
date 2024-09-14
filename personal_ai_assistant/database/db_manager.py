from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from .models import init_db, User, Task, UserPreference, EmailLog, TaskStatus
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from personal_ai_assistant.utils.exceptions import DatabaseError
from personal_ai_assistant.config import encryption_manager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_url):
        try:
            self.engine = init_db(db_url)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise DatabaseError("Failed to initialize database")

    # User operations
    def create_user(self, username, email, password):
        try:
            with self.Session() as session:
                hashed_password = encryption_manager.hash_password(password)
                user = User(username=username, email=encryption_manager.encrypt(email), password=hashed_password)
                session.add(user)
                session.commit()
                logger.info(f"Created user: {username}")
                return user.id
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise DatabaseError("Failed to create user")

    def get_user(self, user_id):
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.email = encryption_manager.decrypt(user.email)
            return user

    def update_user(self, user_id, username=None, email=None, password=None):
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                if username:
                    user.username = username
                if email:
                    user.email = encryption_manager.encrypt(email)
                if password:
                    user.password = encryption_manager.hash_password(password)
                session.commit()
                return True
            return False

    def delete_user(self, user_id):
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False

    # Task operations
    def create_task(self, user_id, title, description):
        with self.Session() as session:
            task = Task(user_id=user_id, title=title, description=description)
            session.add(task)
            session.commit()
            return task.id

    def get_task(self, task_id):
        with self.Session() as session:
            return session.query(Task).filter(Task.id == task_id).first()

    def update_task(self, task_id, title=None, description=None, status=None):
        with self.Session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                if title:
                    task.title = title
                if description:
                    task.description = description
                if status:
                    task.status = TaskStatus(status)
                    if status == TaskStatus.COMPLETED:
                        task.completed_at = datetime.utcnow()
                session.commit()
                return True
            return False

    def delete_task(self, task_id):
        with self.Session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                session.delete(task)
                session.commit()
                return True
            return False

    def get_user_tasks(self, user_id, status=None):
        with self.Session() as session:
            query = session.query(Task).filter(Task.user_id == user_id)
            if status:
                query = query.filter(Task.status == TaskStatus(status))
            return query.all()

    # Enhanced User Preference operations
    def set_user_preference(self, user_id: int, key: str, value: str) -> bool:
        with self.Session() as session:
            pref = session.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.key == key
            ).first()
            encrypted_value = encryption_manager.encrypt(value)
            if pref:
                pref.value = encrypted_value
            else:
                pref = UserPreference(user_id=user_id, key=key, value=encrypted_value)
                session.add(pref)
            session.commit()
            return True

    def get_user_preference(self, user_id: int, key: str) -> Optional[str]:
        with self.Session() as session:
            pref = session.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.key == key
            ).first()
            return encryption_manager.decrypt(pref.value) if pref else None

    def get_all_user_preferences(self, user_id: int) -> List[Dict[str, Any]]:
        with self.Session() as session:
            prefs = session.query(UserPreference).filter(UserPreference.user_id == user_id).all()
            return [{"key": pref.key, "value": pref.value} for pref in prefs]

    def delete_user_preference(self, user_id: int, key: str) -> bool:
        with self.Session() as session:
            pref = session.query(UserPreference).filter(
                UserPreference.user_id == user_id,
                UserPreference.key == key
            ).first()
            if pref:
                session.delete(pref)
                session.commit()
                return True
            return False

    def delete_all_user_preferences(self, user_id: int) -> bool:
        with self.Session() as session:
            session.query(UserPreference).filter(UserPreference.user_id == user_id).delete()
            session.commit()
            return True

    # Email Log operations
    def log_email(self, user_id, subject, sender, recipient, is_sent):
        with self.Session() as session:
            log = EmailLog(user_id=user_id, subject=subject, sender=sender, recipient=recipient, is_sent=is_sent)
            session.add(log)
            session.commit()
            return log.id

    def get_email_logs(self, user_id, limit=10):
        with self.Session() as session:
            return session.query(EmailLog).filter(EmailLog.user_id == user_id).order_by(desc(EmailLog.timestamp)).limit(limit).all()
