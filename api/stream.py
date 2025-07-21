from http.server import BaseHTTPRequestHandler
from httpx import Client
import re
import json
from urllib.parse import urlparse, parse_qs

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
        self.cached_links = None
        self.last_update = 0

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

    def get_stream_links(self):
        import time
        # 10 dakika cache'leme
        if self.cached_links and time.time() - self.last_update < 600:
            return self.cached_links

        html, referer = self.find_working_domain()
        if not html:
            return None

        stream_domain = self.find_dynamic_player_domain(html)
        if not stream_domain:
            return None

        response = self.httpx.get(f"{stream_domain}/index.php?id={list(self.kanallar.values())[0]}", headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": referer
        })

        base_url = self.extract_base_stream_url(response.text)
        if not base_url:
            return None

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

def handler(req):
    path = req.path
    query = parse_qs(urlparse(path).query)
    
    manager = SelcuksportsManager()
    links = manager.get_stream_links()
    
    if not links:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Stream links could not be fetched'})
        }
    
    if path == '/api/umittv.m3u':
        m3u_content = "#EXTM3U\n"
        for name, data in links.items():
            m3u_content += f'#EXTINF:-1 tvg-id="{name}" tvg-name="{name}",{name}\n{data["url"]}\n'
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/x-mpegURL',
                'Content-Disposition': 'attachment; filename="umittv.m3u"'
            },
            'body': m3u_content
        }
    
    if path.startswith('/api/stream'):
        channel_id = query.get('id', [None])[0]
        if not channel_id or channel_id not in links:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Channel not found'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'url': links[channel_id]['url'],
                'headers': {
                    'Referer': links[channel_id]['ref'],
                    'User-Agent': links[channel_id]['user_agent']
                }
            })
        }
    
    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Endpoint not found'})
    }
