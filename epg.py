import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import urllib.parse
import re

def format_start_time(base_date_str, time_str):
    base_date = datetime.strptime(base_date_str, "%m/%d/%Y %H:%M:%S")
    hour, minute = map(int, time_str.split(":"))
    base_date = base_date.replace(hour=hour, minute=minute, second=0)
    return base_date

def make_tvg_id(name):
    # Kanal adını tvg-id uyumlu yap
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

base_date_str = datetime.now().strftime("%m/%d/%Y") + " 00:00:00"
encoded_date = urllib.parse.quote(base_date_str)
url = f"https://www.digiturk.com.tr/Ajax/GetTvGuideFromDigiturk?Day={encoded_date}"

headers = {
    "accept": "*/*",
    "referer": "https://www.digiturk.com.tr/yayin-akisi",
    "user-agent": "Mozilla/5.0",
    "x-requested-with": "XMLHttpRequest"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
channels = soup.select("div.swiper-slide.channelContent")

tv = ET.Element("tv")
channel_counter = 1
program_counter = 1

for channel in channels:
    h3 = channel.select_one("h3.tvguide-channel-name")
    channel_name = h3.get_text(strip=True) if h3 else "Bilinmeyen Kanal"
    channel_id = str(channel_counter)
    tvg_id = make_tvg_id(channel_name)
    channel_counter += 1

    # Kanal bilgisi
    channel_elem = ET.SubElement(tv, "channel", id=channel_id)
    ET.SubElement(channel_elem, "display-name").text = channel_name
    ET.SubElement(channel_elem, "tvg-id").text = tvg_id

    programs = channel.select("div.tvGuideResult-box-wholeDates.channelDetail")
    for prog in programs:
        time_span = prog.select_one("span.tvGuideResult-box-wholeDates-time-hour")
        duration_span = prog.select_one("span.tvGuideResult-box-wholeDates-time-totalMinute")
        title_span = prog.select_one("span.tvGuideResult-box-wholeDates-title")

        if not time_span:
            continue

        start_time_str = time_span.get_text(strip=True)
        duration_str = duration_span.get_text(strip=True) if duration_span else "30"
        title = title_span.get("title") or title_span.get_text(strip=True) if title_span else "Bilinmeyen Program"

        start_dt = format_start_time(base_date_str, start_time_str)
        duration_minutes = int("".join(filter(str.isdigit, duration_str))) or 30
        stop_dt = start_dt + timedelta(minutes=duration_minutes)

        # Programme etiketi tvg-id ile
        programme = ET.SubElement(tv, "programme", {
            "start": start_dt.strftime("%Y%m%d%H%M%S +0300"),
            "stop": stop_dt.strftime("%Y%m%d%H%M%S +0300"),
            "channel": channel_id,
            "tvg-id": tvg_id
        })
        program_counter += 1

        ET.SubElement(programme, "title").text = title

tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print("epg.xml başarıyla oluşturuldu.")
