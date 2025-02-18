from dotenv import load_dotenv
import os
import asyncio
from telegram import Update
from telegram_bot.handlers import *
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram_bot.scheduler import TaskScheduler

class Config:
    # 加载.env文件
    load_dotenv()
    
    # 从环境变量中获取配置
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
    AZURE_DEPLOYMENT = os.getenv('AZURE_DEPLOYMENT')

# 添加这些常量定义
SET_USER, SET_COUNT, SET_TIME = range(3)

async def cancel(update, context):
    """取消当前的对话"""
    await update.message.reply_text('操作已取消。')
    return ConversationHandler.END

def run_bot():
    """运行机器人的主函数"""
    # 创建应用
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # 注册处理程序
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_tweets", get_tweets))
    application.add_handler(CommandHandler("list_tasks", list_tasks))
    
    # 定时任务对话处理
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('schedule', schedule_task)],
        states={
            SET_USER: [MessageHandler(filters.TEXT, receive_username)],
            SET_COUNT: [MessageHandler(filters.TEXT, receive_count)],
            SET_TIME: [MessageHandler(filters.TEXT, receive_time)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)
    
    # 设置调度器
    scheduler = TaskScheduler()
    scheduler.bot = application.bot
    init_scheduler(scheduler)
    
    # 启动调度器
    application.job_queue.run_once(lambda _: scheduler.start(), 0)
    print("Scheduler started successfully")
    
    # 启动机器人
    print("Bot started. Press Ctrl+C to exit.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\nBot stopped gracefully")
    except Exception as e:
        print(f"Error occurred: {e}") 