let cachedM3U = null;
let lastFetchTime = 0;
const CACHE_DURATION = 10 * 60 * 1000; // 10 dakika cache

export default async function handler(req, res) {
  // CORS ayarları
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  const { id } = req.query;

  try {
    // Cache kontrolü
    const now = Date.now();
    if (!cachedM3U || now - lastFetchTime > CACHE_DURATION) {
      console.log("Cache yenileniyor...");
      const response = await fetch("https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u");
      
      if (!response.ok) {
        throw new Error(`GitHub'dan M3U alınamadı: ${response.status}`);
      }
      
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
        const channelNameMatch = line.match(/group-title="[^"]*",([^,]+)/) || 
                               line.match(/tvg-name="([^"]+)"/) || 
                               line.match(/,(.+)$/);
        
        if (channelNameMatch) {
          const channelName = channelNameMatch[1].trim();
          const channelId = channelName.toLowerCase().replace(/\s+/g, '');
          
          // Tüm kanalları listeye ekle
          allChannels.push({ id: channelId, name: channelName });
          
          // Eğer ID parametresi varsa ve eşleşiyorsa
          if (id && channelId === id.toLowerCase()) {
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

    // ID belirtilmemişse tüm kanalları listele
    if (!id) {
      const htmlResponse = `
        <html>
          <head>
            <title>Mevcut Kanallar</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              table { border-collapse: collapse; width: 100%; }
              th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
              th { background-color: #f2f2f2; }
              a { color: #0066cc; text-decoration: none; }
              a:hover { text-decoration: underline; }
            </style>
          </head>
          <body>
            <h1>Mevcut Kanallar</h1>
            <table>
              <tr><th>ID</th><th>Kanal Adı</th><th>Link</th></tr>
              ${allChannels.map(ch => `
                <tr>
                  <td>${ch.id}</td>
                  <td>${ch.name}</td>
                  <td><a href="/api/index?id=${ch.id}">API Linki</a></td>
                </tr>
              `).join('')}
            </table>
          </body>
        </html>
      `;
      res.setHeader('Content-Type', 'text/html');
      return res.status(200).send(htmlResponse);
    }

    // Kanal bulunduysa
    if (foundChannel) {
      return res.status(200).json(foundChannel);
    }
    
    // Kanal bulunamadıysa
    return res.status(404).json({
      error: "Kanal bulunamadı",
      available_channels: allChannels.map(c => c.id),
      suggestion: id.includes('bein') ? 
        'beinmax1, beinmax2, beinsports1 deneyin' : 
        'Geçerli kanal IDleri için /api/index adresini ziyaret edin'
    });

  } catch (err) {
    console.error("Hata oluştu:", err);
    return res.status(500).json({
      error: "Sunucu hatası",
      details: err.message,
      stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
    });
  }
}
