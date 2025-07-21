from http.server import BaseHTTPRequestHandler
from httpx import Client
import re
import json
import time
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def __init__(self):
        self.httpx = Client(timeout=10, verify=False)
        self.kanallar = {
            "trt1": "selcukbeinsports1",
            "trt2": "selcukbeinsports2",
            # Diğer kanallar...
        }
        self.cached_links = None
        self.last_update = 0

    def find_working_domain(self):
        for i in range(1825, 1850):
            url = f"https://www.selcuksportshd{i}.xyz/"
            try:
                r = self.httpx.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200 and "uxsyplayer" in r.text:
                    return r.text, url
            except Exception as e:
                print(f"Domain {url} hatası: {str(e)}")
                continue
        return None, None

    def do_GET(self):
        try:
            path = self.path
            query = parse_qs(urlparse(path).query
            
            links = self.get_stream_links()
            
            if not links:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Stream links could not be fetched'}).encode())
                return
            
            if path == '/api/umittv.m3u':
                self.send_response(200)
                self.send_header('Content-type', 'application/x-mpegURL')
                self.send_header('Content-Disposition', 'attachment; filename="umittv.m3u"')
                self.end_headers()
                
                m3u_content = "#EXTM3U\n"
                for name, data in links.items():
                    m3u_content += f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}",{name}\n{data["url"]}\n'
                
                self.wfile.write(m3u_content.encode())
                return
            
            if path.startswith('/api/stream'):
                channel_id = query.get('id', [None])[0]
                if not channel_id or channel_id not in links:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Channel not found'}).encode())
                    return
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'url': links[channel_id]['url'],
                    'headers': {
                        'Referer': links[channel_id]['ref'],
                        'User-Agent': links[channel_id]['user_agent']
                    }
                }).encode())
                return
            
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Endpoint not found'}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def get_stream_links(self):
        try:
            # 10 dakika cache'leme
            if self.cached_links and time.time() - self.last_update < 600:
                return self.cached_links

            html, referer = self.find_working_domain()
            if not html:
                print("Çalışan domain bulunamadı")
                return None

            stream_domain = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', html)
            if not stream_domain:
                print("Player domain bulunamadı")
                return None

            stream_domain = f"https://{stream_domain.group(1)}"
            response = self.httpx.get(f"{stream_domain}/index.php?id={list(self.kanallar.values())[0]}", headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": referer
            })

            base_url = re.search(r'this\.baseStreamUrl\s*=\s*[\'"]([^\'"]+)', response.text)
            if not base_url:
                print("baseStreamUrl bulunamadı")
                return None

            base_url = base_url.group(1)
            links = {}
            for name, cid in self.kanallar.items():
                full_url = f"{base_url}{cid}/playlist.m3u8"
                links[name] = {
                    "url": full_url,
                    "ref": referer,
                    "user_agent": "Mozilla/5.0"
                }

            self.cached_links = links
            self.last_update = time.time()
            return links
            
        except Exception as e:
            print(f"Link oluşturma hatası: {str(e)}")
            return None
