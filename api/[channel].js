import fetch from "node-fetch";

const channels = {
  "trt1": "https://alpha.cf-worker-9c77973d29ec8a.workers.dev/live/selcukbeinsports1/playlist.m3u8",
  "trt2": "https://alpha.cf-worker-9c77973d29ec8a.workers.dev/live/selcukbeinsports2/playlist.m3u8",
  "beinmax1": "https://alpha.cf-worker-9c77973d29ec8a.workers.dev/live/selcukbeinsportsmax1/playlist.m3u8",
  // ... diğer kanallar
};

export default async function handler(req, res) {
  const { channel } = req.query;

  if (!channel || !channels[channel]) {
    res.status(404).json({ error: "Kanal bulunamadı" });
    return;
  }

  const streamUrl = channels[channel];

  try {
    const response = await fetch(streamUrl, {
      headers: {
        "Referer": "https://www.selcuksportshd1829.xyz/",
        "User-Agent": "Mozilla/5.0"
      }
    });

    if (!response.ok) {
      res.status(response.status).json({ error: `Stream erişim hatası: ${response.status}` });
      return;
    }

    const contentType = response.headers.get("content-type") || "application/vnd.apple.mpegurl";
    res.setHeader("Content-Type", contentType);

    const body = await response.text();
    res.status(200).send(body);

  } catch (error) {
    res.status(500).json({ error: "Sunucu hatası", details: error.message });
  }
}
