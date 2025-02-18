# tweetsToTelegram

A Python-based Twitter content monitoring and Telegram push service that supports scheduled tweet fetching and intelligent summarization through AI.

## 🌟 Key Features

- 📩 Real-time monitoring of specified Twitter users' latest tweets
- 🤖 Intelligent content summarization using Azure OpenAI GPT-4
- ⏰ Flexible scheduled task management system
- 📊 Automated data storage and task logging
- 🛡️ Built-in anti-crawling protection mechanism

## 🚀 Quick Start

### Requirements

- Python 3.9+
- Docker (optional, for containerized deployment)

### Method 1: Local Deployment

1. Clone the project
```bash
git clone <repository-url>
cd tweetsToTelegram
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment variables
```bash
cp .env.sample .env
```

4. Edit the `.env` file with necessary configurations:
```ini
# Telegram Bot Configuration
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_DEPLOYMENT=gpt-4o
```

5. Start the service
```bash
python main.py
```

### Method 2: Docker Deployment

1. Build the image
```bash
docker build -t tweetstobot .
```

2. Run the container
```bash
docker run -d --name tweetstobot tweetstobot
```

View running logs:
```bash
docker logs -f tweetstobot
```

## 💡 Usage Guide

### Telegram Bot Commands

- `/start` - Get usage help
- `/get_tweets <username> <count>` - Immediately fetch tweets from specified user
  Example: `/get_tweets elonmusk 5`
- `/schedule` - Create scheduled fetching task
- `/list_tasks` - View all scheduled tasks

### Scheduled Task Configuration

Use the `/schedule` command to set up scheduled tasks, follow the prompts to input:
- Twitter username
- Number of tweets to fetch
- Execution time (24-hour format, e.g., 09:00)

## 🔧 Configuration Guide

### Telegram Bot Configuration

1. Find [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` to create a new bot
3. Follow prompts to set bot name
4. Get and save the API Token

### Azure OpenAI Configuration

1. Visit [Azure Portal](https://portal.azure.com)
2. Create Azure OpenAI service
3. Get necessary information:
   - API key
   - Endpoint URL
   - API version
   - Deployment name

## 📁 Project Structure

```
tweetsToTelegram/
├── config.py           # Configuration management
├── main.py            # Program entry
├── telegram_bot/      # Telegram bot module
├── twitter/           # Twitter crawler module
├── ai_summarizer/     # AI content processing module
└── database/         # Data storage module
```

## ⚠️ Important Notes

1. **API Key Security**
   - Safely store all API keys
   - Avoid committing configuration files containing keys to the repository

2. **Anti-crawling Protection**
   - System default 1-3 seconds random delay
   - Uses dynamic User-Agent
   - Recommend reasonable request rate control

3. **Data Storage**
   - Uses SQLite database by default
   - Database file: `twitter_monitor.db`
   - Supports custom database configuration

## 🤝 Contribution Guide

Issues and Pull Requests are welcome to help improve the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details