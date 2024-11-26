import os
import requests
from icalendar import Calendar, Event
from datetime import datetime
import pytz

def download_calendar(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def process_calendar(ical_data):
    # 解析原始日历
    cal = Calendar.from_ical(ical_data)

    # 创建新的日历
    new_cal = Calendar()
    new_cal.add('prodid', '-//My Calendar Processor//EN')
    new_cal.add('version', '2.0')

    # 筛选事件
    for component in cal.walk():
        if component.name == "VEVENT":
            # 检查是否有具体时间
            dtstart = component.get('dtstart')
            if dtstart and hasattr(dtstart.dt, 'hour'):  # 如果有hour属性，说明不是全天事件
                new_cal.add_component(component)

    return new_cal

def main():
    # 创建输出目录
    os.makedirs('output', exist_ok=True)

    # 下载和处理日历
    calendar_url = os.environ['CALENDAR_URL']
    ical_data = download_calendar(calendar_url)
    new_cal = process_calendar(ical_data)

    # 保存处理后的日历
    with open('output/calendar.ics', 'wb') as f:
        f.write(new_cal.to_ical())

    # 创建index.html文件以便于访问
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Calendar</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>Calendar</h1>
        <p>Last updated: {}</p>
        <p><a href="calendar.ics">Download Calendar</a></p>
    </body>
    </html>
    """.format(datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S UTC'))

    with open('output/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    main()
