import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import urllib.parse
import unicodedata
import re

# -------------------------
# TVG-ID OLUŞTURUCU FONKSİYON
# -------------------------
def kanal_adi_to_tvgid(name):
    # Türkçe karakterleri ASCII'ye çevir
    name = unicodedata.normalize('NFD', name)
    name = name.encode('ascii', 'ignore').decode('utf-8')
    # Harf ve rakam dışındaki her şeyi kaldır
    name = re.sub(r'[^A-Za-z0-9]', '', name)
    # Küçük harfe çevir
    return name.lower()

# -------------------------
# BAŞLANGIÇ
# -------------------------
BASE_URL = "https://www.digiturk.com.tr/Ajax/GetTvGuideFromDigiturk"
headers = {
    "accept": "*/*",
    "referer": "https://www.digiturk.com.tr/yayin-akisi",
    "user-agent": "Mozilla/5.0",
    "x-requested-with": "XMLHttpRequest"
}

tv = ET.Element("tv")
eklenen_kanallar = set()
kanal_listesi = []

# -------------------------
# 7 GÜNLÜK EPG ÇEKME
# -------------------------
for gun_offset in range(7):
    tarih = datetime.now() + timedelta(days=gun_offset)
    base_date_str = tarih.strftime("%m/%d/%Y") + " 00:00:00"
    encoded_date = urllib.parse.quote(base_date_str)
    url = f"{BASE_URL}?Day={encoded_date}"

    print(f"[+] {tarih.strftime('%Y-%m-%d')} EPG çekiliyor...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    channels = soup.select("div.swiper-slide.channelContent")

    program_counter = 1

    for channel in channels:
        h3 = channel.select_one("h3.tvguide-channel-name")
        channel_name = h3.get_text(strip=True) if h3 else "Bilinmeyen Kanal"
        tvg_id = kanal_adi_to_tvgid(channel_name)

        # Kanal bilgisi bir kez eklenir
        if channel_name not in eklenen_kanallar:
            channel_elem = ET.SubElement(tv, "channel", id=tvg_id)
            ET.SubElement(channel_elem, "display-name").text = channel_name
            kanal_listesi.append(f"{channel_name} => {tvg_id}")
            eklenen_kanallar.add(channel_name)

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

            start_dt = tarih.replace(
                hour=int(start_time_str.split(":")[0]),
                minute=int(start_time_str.split(":")[1]),
                second=0
            )
            duration_minutes = int("".join(filter(str.isdigit, duration_str))) or 30
            stop_dt = start_dt + timedelta(minutes=duration_minutes)

            programme = ET.SubElement(tv, "programme", {
                "start": start_dt.strftime("%Y%m%d%H%M%S +0300"),
                "stop": stop_dt.strftime("%Y%m%d%H%M%S +0300"),
                "channel": tvg_id
            })
            ET.SubElement(programme, "title").text = title

# -------------------------
# XML ve Kanal Listesi Kaydetme
# -------------------------
tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

with open("kanallar.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(kanal_listesi)))

print("[✓] epg.xml oluşturuldu.")
print("[✓] kanallar.txt oluşturuldu.")
