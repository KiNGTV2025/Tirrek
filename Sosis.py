from httpx import Client
import re
import json
import os

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

        self.kanal_adlari = {
            "trt1": "TRT 1",
            "trt2": "TRT 2",
            "beinmax1": "Bein Sports Max 1",
            "beinmax2": "Bein Sports Max 2",
            "smartspor": "Smart Spor",
            "smartspor2": "Smart Spor 2",
            "ssport": "S Sport",
            "ssport2": "S Sport 2",
            "eurosport1": "Eurosport 1",
            "eurosport2": "Eurosport 2",
            "sf1": "S Sport F1",
            "tabiispor": "Tabii Spor",
            "aspor": "A Spor"
        }

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
        for i, (name, cid) in enumerate(self.kanallar.items(), start=130):
            full_url = f"{base_url}{cid}/playlist.m3u8"
            guzel_isim = self.kanal_adlari.get(name, name.upper())
            links[str(i)] = {
                "baslik": f"{guzel_isim} [HD]",
                "url": full_url,
                "logo": f"https://example.com/logos/{name}.png",  # İstersen CDN logosuyla değiştir
                "grup": "ÜmitVIP~Spor2"
            }
        return links

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

        links = self.generate_links_json(base_url, referer)

        # JSON dosyasına yaz
        os.makedirs("public", exist_ok=True)
        with open("public/links.json", "w", encoding="utf-8") as f:
            json.dump(links, f, indent=2, ensure_ascii=False)

        print("✅ links.json dosyası oluşturuldu ve güncellendi.")

if __name__ == "__main__":
    SelcuksportsManager().calistir()
