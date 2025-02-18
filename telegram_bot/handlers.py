from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
from telegram_bot.scheduler import TaskScheduler

# 定义对话状态
SET_USER, SET_COUNT, SET_TIME = range(3)

# 创建全局scheduler实例
scheduler = None

def init_scheduler(scheduler_instance):
    """初始化全局scheduler"""
    global scheduler
    scheduler = scheduler_instance

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "欢迎使用Twitter监控机器人！\n"
        "可用命令：\n"
        "/get_tweets [用户名] [数量] - 立即获取推文\n"
        "/schedule - 设置定时任务\n"
        "/list_tasks - 查看所有任务"
    )

async def get_tweets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("参数错误，请使用格式：/get_tweets [用户名] [数量]")
        return
    
    username = args[0]
    count = int(args[1])
    
    await update.message.reply_text(f"正在获取 @{username} 的最新 {count} 条推文...")
    
    try:
        # 获取推文
        tweets = scheduler.twitter_client.get_recent_tweets(username, count)
        if tweets:
            # 发送简要信息
            brief_info = f"✅ 已获取 @{username} 的 {len(tweets)} 条推文\n"
            brief_info += f"📅 时间范围：{tweets[-1]['time']} 至 {tweets[0]['time']}\n"
            brief_info += f"📊 总体数据：\n"
            
            total_likes = sum(int(t['stats'].get('likes', 0)) for t in tweets)
            total_retweets = sum(int(t['stats'].get('retweets', 0)) for t in tweets)
            brief_info += f"❤️ 总点赞：{total_likes}\n"
            brief_info += f"🔄 总转发：{total_retweets}\n"
            
            await update.message.reply_text(brief_info)
            
            # AI总结
            await update.message.reply_text("🤖 正在生成AI总结...")
            summary = scheduler.ai_summarizer.summarize_tweets(tweets)
            
            # 发送总结
            summary_message = "📋 AI总结要点：\n\n" + summary
            
            # 如果总结太长，分段发送
            if len(summary_message) > 4000:
                # 按段落分割
                paragraphs = summary_message.split('\n\n')
                current_summary = paragraphs[0]  # 保留标题
                
                for paragraph in paragraphs[1:]:
                    if len(current_summary + "\n\n" + paragraph) > 4000:
                        await update.message.reply_text(current_summary)
                        current_summary = paragraph
                    else:
                        current_summary += "\n\n" + paragraph
                
                if current_summary:
                    await update.message.reply_text(current_summary)
            else:
                await update.message.reply_text(summary_message)
            
            # 提供查看完整内容的选项
            await update.message.reply_text(
                "💡 提示：如需查看完整推文内容，请访问：\n"
                f"https://twitter.com/{username}"
            )
        else:
            await update.message.reply_text(f"❌ 未能找到 @{username} 的推文，请检查用户名是否正确或稍后重试")
    except Exception as e:
        await update.message.reply_text(f"❌ 获取推文时发生错误：{str(e)}")

async def schedule_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("请输入要监控的Twitter用户名：")
    return SET_USER

async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("请输入要获取的推文数量：")
    return SET_COUNT

async def receive_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['count'] = update.message.text
    await update.message.reply_text("请输入执行时间（HH:MM）：")
    return SET_TIME

async def receive_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time = update.message.text
        # 验证时间格式
        hour, minute = map(int, time.split(':'))
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError("Invalid time format")
            
        # 获取之前保存的数据
        username = context.user_data['username']
        count = int(context.user_data['count'])
        chat_id = update.effective_chat.id
        
        # 添加定时任务
        if scheduler.add_task(chat_id, username, count, time):
            await update.message.reply_text(
                f"定时任务已设置！\n"
                f"将在每天 {time} 获取 @{username} 的 {count} 条推文"
            )
        else:
            await update.message.reply_text("设置任务失败，请重试")
            
    except ValueError as e:
        await update.message.reply_text("时间格式错误，请使用HH:MM格式（如：09:00）")
        return SET_TIME
    except Exception as e:
        await update.message.reply_text(f"发生错误：{str(e)}")
        return ConversationHandler.END
    
    return ConversationHandler.END

async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出所有定时任务"""
    chat_id = update.effective_chat.id
    tasks = scheduler.get_tasks(chat_id)
    
    if not tasks:
        await update.message.reply_text("当前没有定时任务")
        return
    
    message = "当前的定时任务：\n\n"
    for task in tasks:
        message += f"ID: {task.id}\n"
        message += f"用户: @{task.twitter_username}\n"
        message += f"数量: {task.tweet_count}\n"
        message += f"时间: {task.schedule_time}\n"
        message += "-------------------\n"
    
    await update.message.reply_text(message) 