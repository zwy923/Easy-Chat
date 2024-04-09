import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_message(message):
    """记录普通的日志信息"""
    logging.info(message)

def log_error(message):
    """记录错误日志"""
    logging.error(message)

def format_message(sender, message):
    """格式化聊天消息，例如加上时间戳"""
    return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {sender}: {message}"

def parse_command(input):
    """解析用户输入的命令，返回命令类型和内容"""
    if input.startswith("/"):
        parts = input.split(" ", 1)
        command = parts[0][1:]
        argument = parts[1] if len(parts) > 1 else ""
        return command, argument
    return None, input
