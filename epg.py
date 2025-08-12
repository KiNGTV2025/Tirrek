import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import urllib.parse

def format_start_time(prev_dt, base_date_str, time_str):
    """Saatleri doğru güne yerleştirir, gece yarısından sonra günü +1 yapar."""
    base_date = datetime.strptime(base_date_str, "%m/%d/%Y %H:%M:%S")
    hour, minute = map(int, time_str.split(":"))
    dt = base_date.replace(hour=hour, minute=minute, second=0)
    if prev_dt and dt < prev_dt:
        dt += timedelta(days=1)
    return dt

# Günün tarihi
base_date_str = datetime.now().strftime("%m/%d/%Y") + " 00:00:00"
encoded_date = urllib.parse.quote(base_date_str)

# Digiturk EPG kaynağı
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

# XML kök
tv = ET.Element("tv")

kanallar_txt = []  # KANAL => tvg-id listesi
program_counter = 1

for channel in channels:
    h3 = channel.select_one("h3.tvguide-channel-name")
    channel_name = h3.get_text(strip=True) if h3 else "Bilinmeyen Kanal"

    # tvg-id basitçe kanalı küçük harf + boşlukları silerek oluşturuyoruz
    tvg_id = channel_name.lower().replace(" ", "").replace("ç", "c").replace("ğ", "g").replace("ş", "s").replace("ö", "o").replace("ü", "u").replace("ı", "i")
    kanallar_txt.append(f"{channel_name} => {tvg_id}")

    channel_elem = ET.SubElement(tv, "channel", id=tvg_id)
    ET.SubElement(channel_elem, "display-name").text = channel_name

    programs = channel.select("div.tvGuideResult-box-wholeDates.channelDetail")
    prev_dt = None
    for prog in programs:
        time_span = prog.select_one("span.tvGuideResult-box-wholeDates-time-hour")
        duration_span = prog.select_one("span.tvGuideResult-box-wholeDates-time-totalMinute")
        title_span = prog.select_one("span.tvGuideResult-box-wholeDates-title")

        if not time_span:
            continue

        start_time_str = time_span.get_text(strip=True)
        duration_str = duration_span.get_text(strip=True) if duration_span else "30"
        title = title_span.get("title") or title_span.get_text(strip=True) if title_span else "Bilinmeyen Program"

        start_dt = format_start_time(prev_dt, base_date_str, start_time_str)
        prev_dt = start_dt
        duration_minutes = int("".join(filter(str.isdigit, duration_str))) or 30
        stop_dt = start_dt + timedelta(minutes=duration_minutes)

        programme = ET.SubElement(tv, "programme", {
            "start": start_dt.strftime("%Y%m%d%H%M%S +0300"),
            "stop": stop_dt.strftime("%Y%m%d%H%M%S +0300"),
            "channel": tvg_id,
            "tvg-id": tvg_id,
            "id": f"program{program_counter}"
        })
        program_counter += 1

        ET.SubElement(programme, "title").text = title

# XML kaydet
tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

# Kanal listesi kaydet
with open("kanallar.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(kanallar_txt))

print("✅ epg.xml ve kanallar.txt oluşturuldu.")
