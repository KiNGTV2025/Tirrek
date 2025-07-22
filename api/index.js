const fetch = require('node-fetch');

let cache = {
  data: null,
  timestamp: 0
};
const CACHE_DURATION = 300000; // 5 dakika

async function parseM3U(content) {
  const lines = content.split('\n');
  const channels = [];
  let current = {};
  let headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.selcuksportshd1829.xyz/'
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line.startsWith('#EXTVLCOPT:http-user-agent=')) {
      headers['User-Agent'] = line.split('=')[1].trim();
    }
    else if (line.startsWith('#EXTVLCOPT:http-referrer=')) {
      headers['Referer'] = line.split('=')[1].trim();
    }
    else if (line.startsWith('#EXTINF:-1')) {
      const name = line.split(/,(.+)/)[1]?.trim() || 'Unknown';
      current = {
        id: name.toLowerCase()
          .replace(/\s+/g, '')
          .replace('beinsports', 'bein')
          .replace('beinsport', 'bein'),
        name,
        headers: { ...headers }
      };
    }
    else if (line && !line.startsWith('#') && current.id) {
      current.url = line;
      channels.push(current);
      current = {};
    }
  }

  return { channels };
}

module.exports = async (req, res) => {
  // CORS ayarları
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();

  try {
    // Cache kontrolü
    const now = Date.now();
    if (!cache.data || now - cache.timestamp > CACHE_DURATION) {
      const response = await fetch("https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u");
      if (!response.ok) throw new Error(`GitHub error: ${response.status}`);
      
      const text = await response.text();
      cache = {
        data: await parseM3U(text),
        timestamp: now
      };
    }

    const { id } = req.query;
    const { channels } = cache.data;

    if (!id) {
      return res.status(200).json({
        channels: channels.map(ch => ({
          id: ch.id,
          name: ch.name,
          url: `/stream?id=${ch.id}`
        }))
      });
    }

    const channel = channels.find(ch => 
      [ch.id, ch.name.toLowerCase()].some(v => 
        v.includes(id.toLowerCase())
      )
    );

    if (!channel) {
      return res.status(404).json({
        error: "Kanal bulunamadı",
        available: channels.map(c => c.id)
      });
    }

    return res.status(200).json({
      id: channel.id,
      name: channel.name,
      url: channel.url,
      headers: channel.headers
    });

  } catch (error) {
    console.error("Error:", error);
    return res.status(500).json({
      error: "Server error",
      details: error.message
    });
  }
};
