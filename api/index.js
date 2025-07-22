import fetch from 'node-fetch';

let cachedData = {
  m3uContent: null,
  channels: [],
  lastUpdated: 0
};
const CACHE_TIME = 5 * 60 * 1000; // 5 dakika

export default async function handler(req, res) {
  // CORS ayarları
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();

  try {
    // Cache kontrolü ve veri güncelleme
    if (!cachedData.m3uContent || Date.now() - cachedData.lastUpdated > CACHE_TIME) {
      const response = await fetch("https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u");
      if (!response.ok) throw new Error(`GitHub'dan veri alınamadı: ${response.status}`);
      
      const m3uText = await response.text();
      const parsed = parseM3U(m3uText);
      
      cachedData = {
        m3uContent: m3uText,
        channels: parsed.channels,
        lastUpdated: Date.now()
      };
    }

    const { id } = req.query;
    
    // Tüm kanalları listeleme
    if (!id) {
      return res.status(200).json({
        channels: cachedData.channels.map(ch => ({
          id: ch.id,
          name: ch.name,
          url: `/api/index?id=${ch.id}`
        }))
      });
    }

    // Kanal arama
    const foundChannel = cachedData.channels.find(ch => 
      ch.id === id.toLowerCase() || 
      ch.name.toLowerCase().includes(id.toLowerCase())
    );

    if (foundChannel) {
      // Doğrudan orijinal M3U8 linkini dön
      return res.status(200).json({
        id: foundChannel.id,
        name: foundChannel.name,
        url: foundChannel.url,
        headers: foundChannel.headers,
        direct: true // Doğrudan orijinal link olduğunu belirt
      });
    }

    return res.status(404).json({
      error: "Kanal bulunamadı",
      available: cachedData.channels.map(c => c.id)
    });

  } catch (error) {
    console.error("Hata:", error);
    return res.status(500).json({
      error: "Sunucu hatası",
      details: error.message
    });
  }
}

// M3U Parser Fonksiyonu
function parseM3U(content) {
  const lines = content.split('\n');
  const channels = [];
  let current = {};

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line.startsWith('#EXTINF:-1')) {
      current = {
        id: '',
        name: '',
        url: '',
        headers: {
          'User-Agent': 'Mozilla/5.0',
          'Referer': 'https://www.selcuksportshd1829.xyz/'
        }
      };
      
      // Kanal adını çıkar
      const nameMatch = line.match(/,(.+)$/);
      if (nameMatch) current.name = nameMatch[1].trim();
      
      // Kanal ID oluştur
      current.id = current.name.toLowerCase()
        .replace(/\s+/g, '')
        .replace('beinsports', 'bein')
        .replace('beinsport', 'bein')
        .replace('tv', '');
      
      // Header bilgilerini çıkar
      const userAgentMatch = line.match(/http-user-agent=([^\s]+)/);
      if (userAgentMatch) current.headers['User-Agent'] = userAgentMatch[1];
      
      const refererMatch = line.match(/http-referrer=([^\s]+)/);
      if (refererMatch) current.headers['Referer'] = refererMatch[1];
      
      // Sonraki satır URL mi kontrol et
      if (i + 1 < lines.length) {
        const urlLine = lines[i + 1].trim();
        if (urlLine && !urlLine.startsWith('#')) {
          current.url = urlLine;
          channels.push(current);
          i++; // URL satırını atla
        }
      }
    }
  }

  return { channels };
}
