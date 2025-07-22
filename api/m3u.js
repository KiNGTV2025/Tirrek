export default async function handler(req, res) {
  // CORS ayarları
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  try {
    // GitHub'dan M3U dosyasını çek
    const response = await fetch("https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u");
    
    if (!response.ok) {
      throw new Error(`GitHub'dan dosya çekilemedi: ${response.status}`);
    }
    
    const m3uContent = await response.text();
    
    if (!m3uContent || m3uContent.length < 10) {
      throw new Error("Dosya içeriği boş veya çok kısa");
    }

    // M3U içeriğini satır satır işle
    const lines = m3uContent.split("\n");
    let processedOutput = "#EXTM3U\n";
    let currentHeaders = {
      'User-Agent': 'Mozilla/5.0',
      'Referer': 'https://www.selcuksportshd1829.xyz/'
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Header bilgilerini güncelle
      if (line.startsWith('#EXTVLCOPT:http-user-agent=')) {
        currentHeaders['User-Agent'] = line.split('=')[1].trim();
        continue;
      }
      else if (line.startsWith('#EXTVLCOPT:http-referrer=')) {
        currentHeaders['Referer'] = line.split('=')[1].trim();
        continue;
      }
      
      // Kanal bilgisi satırı
      if (line.startsWith('#EXTINF:-1')) {
        const channelInfo = line;
        let channelUrl = '';
        
        // Sonraki satırın URL olup olmadığını kontrol et
        if (i + 1 < lines.length) {
          const nextLine = lines[i + 1].trim();
          if (nextLine && !nextLine.startsWith('#')) {
            channelUrl = nextLine;
            i++; // URL satırını atla
          }
        }
        
        // Çıktıya ekle
        processedOutput += `${channelInfo}\n`;
        processedOutput += `#EXTVLCOPT:http-user-agent=${currentHeaders['User-Agent']}\n`;
        processedOutput += `#EXTVLCOPT:http-referrer=${currentHeaders['Referer']}\n`;
        
        if (channelUrl) {
          processedOutput += `${channelUrl}\n`;
        } else {
          // URL yoksa proxy linki oluştur
          const channelIdMatch = line.match(/group-title="[^"]*",([^,]+)/);
          if (channelIdMatch) {
            const channelId = channelIdMatch[1].toLowerCase().replace(/\s+/g, '');
            processedOutput += `https://umittvspor.vercel.app/api/stream?id=${channelId}\n`;
          }
        }
      }
    }

    // Çıktıyı gönder
    res.setHeader("Content-Type", "application/x-mpegURL");
    res.setHeader("Content-Disposition", "attachment; filename=umittv.m3u");
    return res.status(200).send(processedOutput);

  } catch (err) {
    console.error("Hata oluştu:", err);
    // Hata durumunda basit bir M3U çıktısı gönder
    return res.status(200).send(`
#EXTM3U
#EXTINF:-1 tvg-id="error" tvg-name="Error",Hata Oluştu
#EXTVLCOPT:http-user-agent=Mozilla/5.0
#EXTVLCOPT:http-referrer=https://www.selcuksportshd1829.xyz/
https://example.com/error.m3u8
    `);
  }
}
