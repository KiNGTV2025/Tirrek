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

    for (let i = 0; i < lines.length; i++) {
      const match = lines[i].match(/tvg-id="([^"]+)"[^,]*,(.*)/);
      if (match) {
        kanalListesi.push({ id: match[1], name: match[2] });
      }
    }

    const matchingIndex = lines.findIndex(line => line.includes(`tvg-id="${id}"`));
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

    const streamUrl = lines[matchingIndex + 1]?.trim();
    if (streamUrl) return res.redirect(streamUrl);
    else return res.status(404).send("Yayın linki bulunamadı.");
  } catch (error) {
    return res.status(500).send(`<h1>Sunucu hatası</h1><p>${error.message}</p>`);
  }
}
