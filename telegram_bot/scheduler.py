from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database.models import Session, ScheduledTask
from twitter.client import TwitterClient
from ai_summarizer.processor import AISummarizer

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")  # 设置时区
        self.twitter_client = TwitterClient()
        self.ai_summarizer = AISummarizer()
        self.bot = None
        
    async def execute_task(self, chat_id: int, username: str, count: int):
        """执行单个任务"""
        try:
            # 获取推文
            tweets = self.twitter_client.get_recent_tweets(username, count)
            if tweets:
                # AI总结
                summary = self.ai_summarizer.summarize_tweets(tweets)
                # 发送结果（需要通过bot发送）
                await self.bot.send_message(chat_id, summary)
        except Exception as e:
            print(f"Task execution failed: {str(e)}")
    
    def add_task(self, chat_id: int, username: str, count: int, time: str):
        """添加新任务"""
        try:
            # 保存到数据库
            session = Session()
            task = ScheduledTask(
                chat_id=chat_id,
                twitter_username=username,
                tweet_count=count,
                schedule_time=time
            )
            session.add(task)
            session.commit()
            
            # 添加到调度器
            hour, minute = map(int, time.split(':'))
            self.scheduler.add_job(
                self.execute_task,
                CronTrigger(hour=hour, minute=minute),
                args=[chat_id, username, count],
                id=f"task_{task.id}"
            )
            return True
        except Exception as e:
            print(f"Failed to add task: {str(e)}")
            return False
        finally:
            session.close()
    
    def remove_task(self, task_id: int):
        """删除任务"""
        try:
            session = Session()
            task = session.query(ScheduledTask).filter_by(id=task_id).first()
            if task:
                # 从调度器中移除
                self.scheduler.remove_job(f"task_{task.id}")
                # 从数据库中删除
                session.delete(task)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_tasks(self, chat_id: int):
        """获取用户的所有任务"""
        session = Session()
        try:
            tasks = session.query(ScheduledTask).filter_by(chat_id=chat_id).all()
            return tasks
        finally:
            session.close()
    
    def start(self):
        """启动调度器并加载现有任务"""
        session = Session()
        try:
            # 加载所有任务
            tasks = session.query(ScheduledTask).all()
            for task in tasks:
                hour, minute = map(int, task.schedule_time.split(':'))
                self.scheduler.add_job(
                    self.execute_task,
                    CronTrigger(hour=hour, minute=minute),
                    args=[task.chat_id, task.twitter_username, task.tweet_count],
                    id=f"task_{task.id}"
                )
            
            # 启动调度器
            if not self.scheduler.running:
                self.scheduler.start()
            print("Scheduler started successfully")
        except Exception as e:
            print(f"Failed to start scheduler: {e}")
            raise
        finally:
            session.close() 