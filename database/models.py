from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)

class ScheduledTask(Base):
    __tablename__ = 'scheduled_tasks'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)  # Telegram聊天ID
    twitter_username = Column(String)
    tweet_count = Column(Integer)
    schedule_time = Column(String)  # 格式：HH:MM
    
    def __repr__(self):
        return f"<Task {self.twitter_username} at {self.schedule_time}>"

# 创建所有表
Base.metadata.create_all(engine) 