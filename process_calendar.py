import os
import requests
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import logging
import sys

# 设置详细的日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# 直接硬编码 Toggl 日历 URL
CALENDAR_URL = 'https://api.plan.toggl.com/api/v4/sharing/7JSUutAmDsvlToJ/icalendar'

def download_calendar():
    try:
        logger.info("Downloading calendar from Toggl")
        response = requests.get(CALENDAR_URL)
        response.raise_for_status()
        content = response.text
        logger.info(f"Successfully downloaded calendar data, size: {len(content)} bytes")
        return content
    except Exception as e:
        logger.error(f"Failed to download calendar: {str(e)}", exc_info=True)
        raise

def process_calendar(ical_data):
    try:
        logger.info("Starting calendar processing")
        # 解析原始日历
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
                summary = component.get('summary')
                logger.debug(f"Processing event: {summary}")

                if dtstart and hasattr(dtstart.dt, 'hour'):
                    new_cal.add_component(component)
                    included_count += 1
                    logger.info(f"Including event: {summary} at {dtstart.dt}")
                else:
                    logger.debug(f"Skipping all-day event: {summary}")

        logger.info(f"Processed {events_count} total events, included {included_count} non-all-day events")
        return new_cal

    except Exception as e:
        logger.error(f"Error processing calendar: {str(e)}", exc_info=True)
        raise

def main():
    try:
        logger.info("Starting calendar sync process")

        # 确保输出目录存在
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")

        # 下载和处理日历
        ical_data = download_calendar()
        processed_calendar = process_calendar(ical_data)

        # 保存处理后的日历
        calendar_path = os.path.join(output_dir, 'calendar.ics')
        with open(calendar_path, 'wb') as f:
            calendar_content = processed_calendar.to_ical()
            f.write(calendar_content)
        logger.info(f"Saved processed calendar to {calendar_path}")

        # 创建美观的 index.html
        index_path = os.path.join(output_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Toggl Calendar</title>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 40px auto;
                        padding: 0 20px;
                        color: #333;
                    }}
                    .container {{
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
                <div class="container">
                    <h2>Calendar Status</h2>
                    <p>Last updated: {datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    <a href="calendar.ics" class="calendar-link">Download Calendar</a>
                </div>
                <div class="container">
                    <h2>How to Use</h2>
                    <ol>
                        <li>Copy this URL: <code>{CALENDAR_URL}</code></li>
                        <li>In your calendar app, add a new subscription calendar</li>
                        <li>The calendar will update automatically every 5 minutes</li>
                    </ol>
                </div>
            </body>
            </html>
            """)
        logger.info(f"Created index.html at {index_path}")

    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
