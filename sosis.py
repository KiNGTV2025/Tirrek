from httpx import Client
import re
import json
import os

class SelcuksportsManager:
    def __init__(self):
        self.httpx = Client(timeout=10, verify=False)

        self.channel_ids = [
            "selcukbeinsports1", "selcukbeinsports2", "selcukbeinsports3",
            "selcukbeinsports4", "selcukbeinsports5", "selcukbeinsportsmax1",
            "selcukbeinsportsmax2", "selcukssport", "selcukssport2",
            "selcuksmartspor", "selcuksmartspor2", "selcuktivibuspor1",
            "selcuktivibuspor2", "selcuktivibuspor3", "selcuktivibuspor4",
            "selcukbeinsportshaber", "selcukaspor", "selcukeurosport1",
            "selcukeurosport2", "selcuksf1", "selcuktabiispor", "ssportplus1"
        ]

        self.channel_names = {
            "selcukbeinsports1": "Bein Sports 1",
            "selcukbeinsports2": "Bein Sports 2",
            "selcukbeinsports3": "Bein Sports 3",
            "selcukbeinsports4": "Bein Sports 4",
            "selcukbeinsports5": "Bein Sports 5",
            "selcukbeinsportsmax1": "Bein Max 1",
            "selcukbeinsportsmax2": "Bein Max 2",
            "selcukssport": "S Sport",
            "selcukssport2": "S Sport 2",
            "selcuksmartspor": "Smart Spor",
            "selcuksmartspor2": "Smart Spor 2",
            "selcuktivibuspor1": "Tivibu Spor 1",
            "selcuktivibuspor2": "Tivibu Spor 2",
            "selcuktivibuspor3": "Tivibu Spor 3",
            "selcuktivibuspor4": "Tivibu Spor 4",
            "selcukbeinsportshaber": "Bein Haber",
            "selcukaspor": "A Spor",
            "selcukeurosport1": "Eurosport 1",
            "selcukeurosport2": "Eurosport 2",
            "selcuksf1": "S Sport F1",
            "selcuktabiispor": "Tabii Spor",
            "ssportplus1": "S Sport Plus 1"
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
        for i, channel_id in enumerate(self.channel_ids, start=130):
            full_url = f"{base_url}{channel_id}/playlist.m3u8"
            kanal_adi = self.channel_names.get(channel_id, channel_id.upper())
            links[str(i)] = {
                "baslik": f"{kanal_adi} [HD]",
                "url": full_url,
                "logo": f"https://example.com/logos/{channel_id}.png",  # Logo URL’leri burada özelleştirilebilir
                "grup": "ÜmitVIP~Spor"
            }

        os.makedirs("public", exist_ok=True)
        with open("public/links.json", "w", encoding="utf-8") as f:
            json.dump(links, f, indent=2, ensure_ascii=False)

    def calistir(self):
        html, referer = self.find_working_domain()
        if not html:
            print("❌ Aktif domain bulunamadı")
            return

        stream_domain = self.find_dynamic_player_domain(html)
        if not stream_domain:
            print("❌ Player domain bulunamadı")
            return

        response = self.httpx.get(
            f"{stream_domain}/index.php?id={self.channel_ids[0]}",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": referer
            }
        )

        base_url = self.extract_base_stream_url(response.text)
        if not base_url:
            print("❌ baseStreamUrl bulunamadı")
            return

        self.generate_links_json(base_url, referer)
        print("✅ JSON başarıyla oluşturuldu ve kaydedildi!")


if __name__ == "__main__":
    SelcuksportsManager().calistir()
