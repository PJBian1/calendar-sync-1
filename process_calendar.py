import os
import requests
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # 确保输出目录存在
        output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Output directory: {output_dir}")

        # 创建一个基本的日历文件（测试用）
        test_cal = Calendar()
        test_cal.add('prodid', '-//Test Calendar//EN')
        test_cal.add('version', '2.0')

        # 添加测试事件
        event = Event()
        event.add('summary', 'Test Event')
        now = datetime.now(pytz.UTC)
        event.add('dtstart', now)
        event.add('dtend', now)
        event.add('dtstamp', now)
        test_cal.add_component(event)

        # 保存测试日历
        calendar_path = os.path.join(output_dir, 'calendar.ics')
        with open(calendar_path, 'wb') as f:
            f.write(test_cal.to_ical())
        logger.info(f"Created test calendar at {calendar_path}")

        # 列出所有创建的文件
        logger.info("Files in output directory:")
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            logger.info(f"- {file}: {os.path.getsize(file_path)} bytes")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
