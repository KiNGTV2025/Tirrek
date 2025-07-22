let cachedM3U = null;
let lastFetchTime = 0;
const CACHE_DURATION = 10 * 60 * 1000; // 10 dakika cache

export default async function handler(req, res) {
  // CORS ayarları
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();

  const { id } = req.query;

  try {
    // Cache kontrolü
    const now = Date.now();
    if (!cachedM3U || now - lastFetchTime > CACHE_DURATION) {
      const response = await fetch("https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u");
      if (!response.ok) throw new Error(`GitHub'dan M3U alınamadı: ${response.status}`);
      cachedM3U = await response.text();
      lastFetchTime = now;
    }

    const lines = cachedM3U.split("\n");
    let currentHeaders = {
      'User-Agent': 'Mozilla/5.0',
      'Referer': 'https://www.selcuksportshd1829.xyz/'
    };
    let foundChannel = null;
    let allChannels = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Header bilgilerini güncelle
      if (line.startsWith('#EXTVLCOPT:http-user-agent=')) {
        currentHeaders['User-Agent'] = line.split('=')[1].trim();
      }
      else if (line.startsWith('#EXTVLCOPT:http-referrer=')) {
        currentHeaders['Referer'] = line.split('=')[1].trim();
      }
      
      // Kanal bilgisi satırı
      if (line.startsWith('#EXTINF:-1')) {
        const channelNameMatch = line.match(/group-title="[^"]*",([^,]+)/);
        if (channelNameMatch) {
          const channelName = channelNameMatch[1].trim();
          // Özel ID eşleme mantığı
          let channelId = channelName.toLowerCase()
            .replace(/\s+/g, '')
            .replace('beinsports', 'bein')
            .replace('beinsport', 'bein');
          
          // Tüm kanalları listeye ekle (orijinal isimle)
          allChannels.push({ id: channelId, name: channelName });
          
          // Eğer ID parametresi varsa ve eşleşiyorsa
          if (id && (channelId === id.toLowerCase() || 
                     channelName.toLowerCase().includes(id.toLowerCase()))) {
            // Sonraki satırın URL olup olmadığını kontrol et
            if (i + 1 < lines.length) {
              const nextLine = lines[i + 1].trim();
              if (nextLine && !nextLine.startsWith('#')) {
                foundChannel = {
                  id: channelId,
                  name: channelName,
                  url: nextLine,
                  headers: { ...currentHeaders }
                };
                break;
              }
            }
          }
        }
      }
    }

    // Kanal bulunduysa
    if (foundChannel) {
      return res.status(200).json(foundChannel);
    }
    
    // Kanal bulunamadıysa
    return res.status(404).json({
      error: "Kanal bulunamadı",
      available_channels: allChannels.map(c => c.id),
      suggestion: id.toLowerCase().includes('bein') ? 
        'beinmax1, beinmax2, beinsports1 deneyin' : 
        'Geçerli kanal IDleri için /api/index adresini ziyaret edin',
      debug_info: {
        searched_id: id,
        normalized_id: id?.toLowerCase().replace(/\s+/g, '')
      }
    });

  } catch (err) {
    console.error("Hata oluştu:", err);
    return res.status(500).json({
      error: "Sunucu hatası",
      details: err.message
    });
  }
}
