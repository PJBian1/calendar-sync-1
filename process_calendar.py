import os
import requests
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_calendar(url):
    try:
        logger.info(f"Downloading calendar from Toggl")
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Successfully downloaded calendar data ({len(response.text)} bytes)")
        return response.text
    except Exception as e:
        logger.error(f"Error downloading calendar: {str(e)}")
        raise

def process_calendar(ical_data):
    try:
        # 解析原始日历
        logger.info("Parsing calendar data")
        cal = Calendar.from_ical(ical_data)

        # 创建新的日历
        new_cal = Calendar()
        new_cal.add('prodid', '-//Toggl Calendar Processor//EN')
        new_cal.add('version', '2.0')
        new_cal.add('x-wr-calname', 'Toggl Calendar')

        # 筛选事件
        events_count = 0
        included_count = 0

        for component in cal.walk():
            if component.name == "VEVENT":
                events_count += 1
                dtstart = component.get('dtstart')
                if dtstart and hasattr(dtstart.dt, 'hour'):  # 检查是否有具体时间
                    new_cal.add_component(component)
                    included_count += 1
                    # 记录事件信息用于调试
                    logger.info(f"Including event: {component.get('summary')} at {dtstart.dt}")

        logger.info(f"Processed {events_count} events, included {included_count} non-all-day events")
        return new_cal

    except Exception as e:
        logger.error(f"Error processing calendar: {str(e)}")
        raise

def create_html_index(included_events):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Toggl Calendar Sync</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 40px auto;
                padding: 0 20px;
                color: #333;
            }}
            .status-box {{
                background: #f5f5f5;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .calendar-link {{
                display: inline-block;
                background: #0366d6;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px 0;
            }}
            .calendar-link:hover {{
                background: #0256b9;
            }}
        </style>
    </head>
    <body>
        <h1>Toggl Calendar Sync</h1>
        <div class="status-box">
            <h2>Status</h2>
            <p>Last updated: {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>Included events: {included_events}</p>
        </div>
        <div class="status-box">
            <h2>Instructions</h2>
            <p>Subscribe to this calendar using the link below:</p>
            <a href="calendar.ics" class="calendar-link">Download Calendar</a>
            <h3>How to use:</h3>
            <ul>
                <li>iOS/macOS: Add to Calendar app as a subscription calendar</li>
                <li>Google Calendar: Add "From URL" under "Other calendars"</li>
                <li>Calendar updates every 5 minutes</li>
            </ul>
        </div>
    </body>
    </html>
    """

def main():
    try:
        # 确保输出目录存在
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)

        # 下载和处理日历
        calendar_url = os.environ.get('CALENDAR_URL')
        if not calendar_url:
            raise ValueError("CALENDAR_URL environment variable not set")

        ical_data = download_calendar(calendar_url)
        processed_calendar = process_calendar(ical_data)

        # 计算包含的事件数量
        included_events = len([c for c in processed_calendar.walk() if c.name == "VEVENT"])

        # 保存日历文件
        calendar_path = os.path.join(output_dir, 'calendar.ics')
        with open(calendar_path, 'wb') as f:
            f.write(processed_calendar.to_ical())
        logger.info(f"Saved calendar to {calendar_path}")

        # 创建 index.html
        index_path = os.path.join(output_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(create_html_index(included_events))
        logger.info(f"Created index.html at {index_path}")

        # 列出创建的文件
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            logger.info(f"Created {file}: {os.path.getsize(file_path)} bytes")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
