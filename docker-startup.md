# Docker 构建和运行说明

## 构建Docker镜像
```bash
# 在项目根目录下执行
docker build -t twitter-monitor-bot .
```

## 运行Docker容器
```bash
# 确保已经配置好.env文件
docker run -d --name twitter-monitor twitter-monitor-bot
```

## 查看容器日志
```bash
docker logs -f twitter-monitor
```

## 停止容器
```bash
docker stop twitter-monitor
```

## 删除容器
```bash
docker rm twitter-monitor
```

## 注意事项
1. 运行容器前请确保已经正确配置了 `.env` 文件
2. 容器会自动加载环境变量并启动机器人服务
3. 使用 `-d` 参数可以让容器在后台运行
4. 可以通过 `docker logs` 命令查看运行日志