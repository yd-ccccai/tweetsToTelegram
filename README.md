# tweetsToTelegram

一个基于Python的Twitter内容监控和Telegram推送服务，支持定时抓取推文并通过AI进行智能总结。

## 🌟 主要功能

- 📩 实时监控指定Twitter用户的最新推文
- 🤖 使用Azure OpenAI GPT-4进行智能内容总结
- ⏰ 灵活的定时任务管理系统
- 📊 自动化的数据存储和任务记录
- 🛡️ 内置反爬虫保护机制

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Docker（可选，用于容器化部署）

### 方式一：本地部署

1. 克隆项目
```bash
git clone <项目仓库地址>
cd tweetsToTelegram
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.sample .env
```

4. 编辑 `.env` 文件，填入必要配置：
```ini
# Telegram Bot配置
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Azure OpenAI配置
AZURE_OPENAI_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_DEPLOYMENT=gpt-4o
```

5. 启动服务
```bash
python main.py
```

### 方式二：Docker部署

1. 构建镜像
```bash
docker build -t tweetstobot .
```

2. 运行容器
```bash
docker run -d --name tweetstobot tweetstobot
```

查看运行日志：
```bash
docker logs -f tweetstobot
```

## 💡 使用指南

### Telegram机器人命令

- `/start` - 获取使用帮助
- `/get_tweets <用户名> <数量>` - 立即获取指定用户的推文
  示例：`/get_tweets elonmusk 5`
- `/schedule` - 创建定时抓取任务
- `/list_tasks` - 查看所有定时任务

### 定时任务配置

通过 `/schedule` 命令可以设置定时任务，按提示输入：
- Twitter用户名
- 需要获取的推文数量
- 执行时间（24小时制，如：09:00）

## 🔧 配置说明

### Telegram Bot配置

1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 获取并保存API Token

### Azure OpenAI配置

1. 访问 [Azure门户](https://portal.azure.com)
2. 创建Azure OpenAI服务
3. 获取必要信息：
   - API密钥
   - 终结点URL
   - API版本
   - 部署名称

## 📁 项目结构

```
tweetsToTelegram/
├── config.py           # 配置管理
├── main.py            # 程序入口
├── telegram_bot/      # Telegram机器人模块
├── twitter/           # Twitter爬虫模块
├── ai_summarizer/     # AI内容处理模块
└── database/         # 数据存储模块
```

## ⚠️ 注意事项

1. **API密钥安全**
   - 妥善保管所有API密钥
   - 避免将含密钥的配置文件提交到代码库

2. **反爬虫保护**
   - 系统默认配置1-3秒随机延迟
   - 使用动态User-Agent
   - 建议合理控制请求频率

3. **数据存储**
   - 默认使用SQLite数据库
   - 数据库文件：`twitter_monitor.db`
   - 支持自定义数据库配置

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件