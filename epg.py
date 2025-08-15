import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import urllib.parse
import unicodedata
import re
import time
import random
from tqdm import tqdm  # İlerleme çubuğu

def normalize_tvg_id(name):
    name = name.lower()
    name = unicodedata.normalize("NFD", name)
    name = name.encode("ascii", "ignore").decode("utf-8")
    name = re.sub(r"[^a-z0-9]+", "", name)
    return name

def format_start_time(base_date_str, time_str):
    base_date = datetime.strptime(base_date_str, "%m/%d/%Y %H:%M:%S")
    hour, minute = map(int, time_str.split(":"))
    base_date = base_date.replace(hour=hour, minute=minute, second=0)
    return base_date

def fetch_with_retry(scraper, url, headers, max_retries=5):
    delay = 2
    for attempt in range(1, max_retries + 1):
        try:
            response = scraper.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(delay)
            delay *= 2
    return None

def process_day(scraper, tarih, gun, kanallar_dict, kayma_uyarilari, tv):
    base_date_str = tarih.strftime("%m/%d/%Y") + " 00:00:00"
    encoded_date = urllib.parse.quote(base_date_str, safe='')
    url = f"https://www.digiturk.com.tr/Ajax/GetTvGuideFromDigiturk?Day={encoded_date}"
    headers = {
        "accept": "*/*",
        "referer": "https://www.digiturk.com.tr/yayin-akisi",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

    try:
        response = fetch_with_retry(scraper, url, headers)
    except Exception:
        return False

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

            if gun == 0:
                fark = abs((start_dt - datetime.now()).total_seconds()) / 60
                if fark > 180:
                    kayma_uyarilari.append(
                        f"{channel_name} - '{title}' saati uyumsuz! EPG: {start_dt}, Şimdi: {datetime.now()}"
                    )

            programme = ET.SubElement(tv, "programme", {
                "start": start_dt.strftime("%Y%m%d%H%M%S +0300"),
                "stop": stop_dt.strftime("%Y%m%d%H%M%S +0300"),
                "channel": tvg_id,
                "tvg-id": tvg_id
            })
            ET.SubElement(programme, "title").text = title

    time.sleep(random.uniform(1, 3))
    return True

KANALLAR_DOSYA = "kanallar.txt"
KAYMA_DOSYA = "kayma_uyarilari.txt"
kanallar_dict = {}
kayma_uyarilari = []
basarisiz_gunler = []
tv = ET.Element("tv")
today = datetime.now()
scraper = cloudscraper.create_scraper()

# İlk tur
for gun in tqdm(range(0, 7), desc="EPG Verisi Çekiliyor", unit="gün"):
    tarih = today + timedelta(days=gun)
    success = process_day(scraper, tarih, gun, kanallar_dict, kayma_uyarilari, tv)
    if not success:
        basarisiz_gunler.append((tarih, gun))

# İkinci tur
if basarisiz_gunler:
    yeniden_basarisizlar = []
    for tarih, gun in tqdm(basarisiz_gunler, desc="Başarısız Günler Tekrar Deneniyor", unit="gün"):
        success = process_day(scraper, tarih, gun, kanallar_dict, kayma_uyarilari, tv)
        if not success:
            yeniden_basarisizlar.append((tarih, gun))
    basarisiz_gunler = yeniden_basarisizlar

# Kaydetme işlemleri
tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
with open(KANALLAR_DOSYA, "w", encoding="utf-8") as f:
    for ad, tid in sorted(kanallar_dict.items()):
        f.write(f"{ad} => {tid}\n")
if kayma_uyarilari or basarisiz_gunler:
    with open(KAYMA_DOSYA, "w", encoding="utf-8") as f:
        if kayma_uyarilari:
            f.write("Kayma Uyarıları:\n" + "\n".join(kayma_uyarilari) + "\n\n")
        if basarisiz_gunler:
            f.write("Verisi Alınamayan Günler:\n" + "\n".join([t.strftime("%Y-%m-%d") for t, _ in basarisiz_gunler]))

print("\n✅ epg.xml, kanallar.txt ve kayma_uyarilari.txt oluşturuldu.")
