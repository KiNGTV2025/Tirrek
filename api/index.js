let cachedM3U = null;
let lastFetched = 0;
const CACHE_DURATION = 10 * 60 * 1000; // 10 dakika

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") return res.status(200).end();

  const { id } = req.query;

  try {
    const now = Date.now();
    if (!cachedM3U || now - lastFetched > CACHE_DURATION) {
      const response = await fetch("https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u");
      const text = await response.text();
      cachedM3U = text.split("\n").map(line => line.trim());
      lastFetched = now;
    }

    const lines = cachedM3U;
    const kanalListesi = [];
    let currentHeaders = {
      'User-Agent': 'Mozilla/5.0',
      'Referer': 'https://www.selcuksportshd1829.xyz/'
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Kanal bilgilerini işle
      const match = line.match(/tvg-id="([^"]+)"[^,]*,(.*)/);
      if (match) {
        kanalListesi.push({ id: match[1], name: match[2] });
      }
      
      // Header bilgilerini işle
      if (line.startsWith('#EXTVLCOPT:http-user-agent=')) {
        currentHeaders['User-Agent'] = line.split('=')[1];
      }
      else if (line.startsWith('#EXTVLCOPT:http-referer=')) {
        currentHeaders['Referer'] = line.split('=')[1];
      }
      
      // ID eşleşmesi ve yayın URL'si
      if (id && line.includes(`tvg-id="${id}"`)) {
        const streamUrl = lines[i + 1]?.trim();
        if (streamUrl && !streamUrl.startsWith('#')) {
          // Yayın URL'sini doğrudan yönlendirme yerine header'ları ekleyerek dön
          return res.status(200).json({
            url: streamUrl,
            headers: currentHeaders
          });
        }
      }
    }

    // ID belirtilmemiş veya bulunamamışsa
    if (!id || matchingIndex === -1) {
      const html = `
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Mevcut Kanallar</title></head><body>
        <h1>${id ? "ID bulunamadı!" : "Geçersiz ID"}</h1>
        <table><tr><th>ID</th><th>Kanal</th></tr>
        ${kanalListesi.map(k => `<tr><td>${k.id}</td><td>${k.name}</td></tr>`).join("")}
        </table></body></html>`;
      res.setHeader("Content-Type", "text/html; charset=utf-8");
      return res.status(200).send(html);
    }

    return res.status(404).send("Yayın linki bulunamadı.");
  } catch (error) {
    return res.status(500).send(`<h1>Sunucu hatası</h1><p>${error.message}</p>`);
  }
}
