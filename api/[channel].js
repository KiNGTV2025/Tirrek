import fs from "fs";
import path from "path";

export default async function handler(req, res) {
  const { channel } = req.query;

  try {
    // public/links.json yolunu belirle
    const jsonPath = path.resolve("./public/links.json");
    const data = fs.readFileSync(jsonPath, "utf-8");
    const links = JSON.parse(data);

    if (!links[channel]) {
      return res.status(404).json({ error: "Kanal bulunamadı" });
    }

    const ch = links[channel];

    // Yayın URL'sine header'larla fetch yap
    const response = await fetch(ch.url, {
      headers: {
        Referer: ch.ref,
        "User-Agent": ch.user_agent,
      },
    });

    if (!response.ok) {
      return res.status(500).json({ error: "Yayın alınamadı", status: response.status });
    }

    const body = await response.text();

    // M3U8 içeriğini döndür
    res.setHeader("Content-Type", "application/vnd.apple.mpegurl");
    res.status(200).send(body);

  } catch (error) {
    res.status(500).json({ error: "Sunucu hatası", details: error.message });
  }
}
