from httpx import Client
import re
import os
import json

class SelcuksportsManager:
    def __init__(self):
        self.httpx = Client(timeout=10, verify=False)
        self.kanallar = {
            "trt1": "selcukbeinsports1",
            "trt2": "selcukbeinsports2",
            "beinmax1": "selcukbeinsportsmax1",
            "beinmax2": "selcukbeinsportsmax2",
            "smartspor": "selcuksmartspor",
            "smartspor2": "selcuksmartspor2",
            "ssport": "selcukssport",
            "ssport2": "selcukssport2",
            "eurosport1": "selcukeurosport1",
            "eurosport2": "selcukeurosport2",
            "sf1": "selcuksf1",
            "tabiispor": "selcuktabiispor",
            "aspor": "selcukaspor"
        }
        self.links_json_file = "public/links.json"

    def find_working_domain(self):
        for i in range(1825, 1850):
            url = f"https://www.selcuksportshd{i}.xyz/"
            try:
                r = self.httpx.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200 and "uxsyplayer" in r.text:
                    return r.text, url
            except:
                continue
        return None, None

    def find_dynamic_player_domain(self, html):
        match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', html)
        return f"https://{match.group(1)}" if match else None

    def extract_base_stream_url(self, html):
        match = re.search(r'this\.baseStreamUrl\s*=\s*[\'"]([^\'"]+)', html)
        return match.group(1) if match else None

    def generate_links_json(self, base_url, referer_url):
        links = {}
        for name, cid in self.kanallar.items():
            full_url = f"{base_url}{cid}/playlist.m3u8"
            links[name] = {
                "url": full_url,
                "ref": referer_url,
                "user_agent": "Mozilla/5.0"
            }

        os.makedirs(os.path.dirname(self.links_json_file), exist_ok=True)

        with open(self.links_json_file, "w", encoding="utf-8") as f:
            json.dump(links, f, indent=2)

    def calistir(self):
        html, referer = self.find_working_domain()
        if not html:
            print("❌ Aktif domain bulunamadı")
            return

        stream_domain = self.find_dynamic_player_domain(html)
        if not stream_domain:
            print("❌ Player domain bulunamadı")
            return

        response = self.httpx.get(f"{stream_domain}/index.php?id={list(self.kanallar.values())[0]}", headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": referer
        })

        base_url = self.extract_base_stream_url(response.text)
        if not base_url:
            print("❌ baseStreamUrl bulunamadı")
            return

        self.generate_links_json(base_url, referer)
        print("✅ JSON başarıyla güncellendi!")

if __name__ == "__main__":
    SelcuksportsManager().calistir()
