import re
import requests
import urllib3
import json
from typing import Dict, Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_content(url: str) -> Optional[str]:
    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)'},
            verify=False,
            timeout=15
        )
        return response.text
    except Exception as e:
        print(f"Hata: {url} - {str(e)}")
        return None

def get_dynamic_urls() -> Dict[str, str]:
    redirect_content = fetch_content('https://eniyiyayinci.github.io/redirect/index.html')
    domain_match = re.search(r'URL=(https:\/\/[^"]+)', redirect_content or '')
    dynamic_domain = (domain_match.group(1) if domain_match else 'https://trgoals896.xyz').rstrip('/') + '/'

    channel_content = fetch_content(f"{dynamic_domain}channel.html")
    base_match = re.search(r'const\s+baseurl\s*=\s*["\']([^"\']+)["\']', channel_content or '', re.IGNORECASE)
    base_url = (base_match.group(1) if base_match else 'https://iss.trgoalshls1.shop').rstrip('/') + '/'

    return {
        'dynamic_domain': dynamic_domain,
        'base_url': base_url
    }

def generate_links() -> dict:
    urls = get_dynamic_urls()

    channels = {
        1: "BEIN SPORTS 1 (ZIRVE)",
        2: "BEIN SPORTS 1 (1)",
        3: "BEIN SPORTS 1 (INAT)",
        4: "BEIN SPORTS 2",
        5: "BEIN SPORTS 3",
        6: "BEIN SPORTS 4",
        7: "BEIN SPORTS 5",
        8: "BEIN SPORTS MAX 1",
        9: "BEIN SPORTS MAX 2",
        10: "S SPORT 1",
        11: "S SPORT 2",
        13: "TIVIBU SPOR 1",
        14: "TIVIBU SPOR 2",
        15: "TIVIBU SPOR 3",
        16: "SPOR SMART 1",
        17: "SPOR SMART 2",
        18: "TRT SPOR 1",
        19: "TRT SPOR 2",
        20: "TRT 1",
        21: "A SPOR",
        22: "ATV",
        23: "TV 8",
        24: "TV 8.5",
        25: "FORMULA 1",
        26: "NBA TV",
        27: "EURO SPORT 1",
        28: "EURO SPORT 2",
        29: "S SPORT PLUS 2",
        30: "S SPORT PLUS 1",
        31: "EXXEN SPOR 3",
        32: "EXXEN SPOR 4",
        33: "EXXEN SPOR 5",
        34: "EXXEN SPOR 6",
        35: "EXXEN SPOR 7",
        36: "EXXEN SPOR 8"
    }

    stream_paths = {
        1: "yayinzirve.m3u8",
        2: "yayin1.m3u8",
        3: "yayininat.m3u8",
        4: "yayinb2.m3u8",
        5: "yayinb3.m3u8",
        6: "yayinb4.m3u8",
        7: "yayinb5.m3u8",
        8: "yayinbm1.m3u8",
        9: "yayinbm2.m3u8",
        10: "yayinss.m3u8",
        11: "yayinss2.m3u8",
        13: "yayint1.m3u8",
        14: "yayint2.m3u8",
        15: "yayint3.m3u8",
        16: "yayinsmarts.m3u8",
        17: "yayinsms2.m3u8",
        18: "yayintrtspor.m3u8",
        19: "yayintrtspor2.m3u8",
        20: "yayintrt1.m3u8",
        21: "yayinas.m3u8",
        22: "yayinatv.m3u8",
        23: "yayintv8.m3u8",
        24: "yayintv85.m3u8",
        25: "yayinf1.m3u8",
        26: "yayinnbatv.m3u8",
        27: "yayineu1.m3u8",
        28: "yayineu2.m3u8",
        29: "yayinex1.m3u8",
        30: "yayinex2.m3u8",
        31: "yayinex3.m3u8",
        32: "yayinex4.m3u8",
        33: "yayinex5.m3u8",
        34: "yayinex6.m3u8",
        35: "yayinex7.m3u8",
        36: "yayinex8.m3u8"
    }

    result = {}
    index = 130  # Başlangıç ID

    for cid, cname in channels.items():
        if cid in stream_paths:
            full_url = f"{urls['base_url']}{stream_paths[cid]}|referer={urls['dynamic_domain']}"
            result[str(index)] = {
                "baslik": cname,
                "url": full_url,
                "logo": f"https://example.com/logo/{cid}.png",
                "grup": "ÜmitVIP~Spor"
            }
            index += 1

    return result

if __name__ == "__main__":
    json_output = generate_links()
    with open("public/links2.json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print("✅ Yeni formatta JSON 'public/links2.json' dosyasına yazıldı.")
