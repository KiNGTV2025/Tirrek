import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import urllib.parse
import unicodedata
import re

def normalize_tvg_id(name):
    """Kanal adından tvg-id oluşturur"""
    name = name.lower()
    name = unicodedata.normalize("NFD", name)
    name = name.encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"[^a-z0-9]+", "", name)  # harf ve rakam dışında sil
    return name

def format_start_time(base_date_str, time_str):
    """Tarihi ve saati birleştirir"""
    base_date = datetime.strptime(base_date_str, "%m/%d/%Y %H:%M:%S")
    hour, minute = map(int, time_str.split(":"))
    base_date = base_date.replace(hour=hour, minute=minute, second=0)
    return base_date

KANALLAR_DOSYA = "kanallar.txt"
KAYMA_DOSYA = "kayma_uyarilari.txt"

kanallar_dict = {}
kayma_uyarilari = []

tv = ET.Element("tv")
today = datetime.now()

for gun in range(0, 7):  # 7 günlük çekim
    tarih = today + timedelta(days=gun)
    base_date_str = tarih.strftime("%m/%d/%Y") + " 00:00:00"
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

    for channel in channels:
        h3 = channel.select_one("h3.tvguide-channel-name")
        channel_name = h3.get_text(strip=True) if h3 else "Bilinmeyen Kanal"
        tvg_id = normalize_tvg_id(channel_name)
        kanallar_dict[channel_name] = tvg_id

        channel_elem = tv.find(f"./channel[@id='{tvg_id}']")
        if channel_elem is None:
            channel_elem = ET.SubElement(tv, "channel", id=tvg_id)
            ET.SubElement(channel_elem, "display-name").text = channel_name

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

            # Kayma kontrolü (sadece bugünkü programlarda)
            if gun == 0:
                fark = abs((start_dt - datetime.now()).total_seconds()) / 60
                if fark > 180:  # 3 saatten fazla fark varsa
                    kayma_uyarilari.append(f"{channel_name} - '{title}' saati uyumsuz! EPG: {start_dt}, Şimdi: {datetime.now()}")

            programme = ET.SubElement(tv, "programme", {
                "start": start_dt.strftime("%Y%m%d%H%M%S +0300"),
                "stop": stop_dt.strftime("%Y%m%d%H%M%S +0300"),
                "channel": tvg_id,
                "tvg-id": tvg_id
            })
            ET.SubElement(programme, "title").text = title

# EPG XML kaydet
tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

# Kanal listesi kaydet
with open(KANALLAR_DOSYA, "w", encoding="utf-8") as f:
    for ad, tid in sorted(kanallar_dict.items()):
        f.write(f"{ad} => {tid}\n")

# Kayma uyarıları kaydet
if kayma_uyarilari:
    with open(KAYMA_DOSYA, "w", encoding="utf-8") as f:
        f.write("\n".join(kayma_uyarilari))

print("epg.xml, kanallar.txt ve kayma_uyarilari.txt oluşturuldu.")
