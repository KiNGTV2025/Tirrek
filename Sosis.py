from httpx import Client
import re
import os
import json

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
        self.output_file = "1UmitTV.m3u"
        self.links_json_file = "api/links.json"

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

    def build_m3u8_and_json(self, base_url, referer_url):
        m3u = ["#EXTM3U"]
        links = {}
        for cid in self.channel_ids:
            full_url = f"{base_url}{cid}/playlist.m3u8"
            name = cid.replace("selcuk", "").capitalize()

            m3u.append(f'#EXTINF:-1 group-title="Selcuksports",{name}')
            m3u.append('#EXTVLCOPT:http-user-agent=Mozilla/5.0')
            m3u.append(f'#EXTVLCOPT:http-referrer={referer_url}')
            m3u.append(full_url)

            links[cid] = full_url

        # M3U dosyasını yaz
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u))

        # JSON dosyasını yaz
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

        response = self.httpx.get(f"{stream_domain}/index.php?id={self.channel_ids[0]}", headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": referer
        })

        base_url = self.extract_base_stream_url(response.text)
        if not base_url:
            print("❌ Base stream URL bulunamadı")
            return

        self.build_m3u8_and_json(base_url, referer)
        print("✅ Başarıyla güncellendi!")

if __name__ == "__main__":
    SelcuksportsManager().calistir()
