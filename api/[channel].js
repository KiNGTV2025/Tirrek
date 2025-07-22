import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  let { channel } = req.query; // örn: "trt1.m3u8"

  // ".m3u8" uzantısını temizle
  channel = channel.replace('.m3u8', '');

  const filePath = path.join(process.cwd(), 'public', 'links.json');

  try {
    const jsonData = fs.readFileSync(filePath, 'utf8');
    const links = JSON.parse(jsonData);

    if (!links[channel]) {
      res.status(404).json({ error: "Kanal bulunamadı" });
      return;
    }

    const { url, ref, user_agent } = links[channel];

    // IPTV uygulamaları genelde header info'yu URL içine | işaretleri ile ekler
    const streamUrl = `${url}|referer=${ref}|user-agent=${user_agent}`;

    // M3U8 dosyası gibi yanıt vereceğiz, içerik tipi değiştir
    res.setHeader('Content-Type', 'application/vnd.apple.mpegurl');

    // Basitçe stream URL'yi içeren bir m3u8 dosyası oluşturabiliriz
    // Örnek içerik:
    // #EXTM3U
    // #EXTINF:-1,${channel}
    // ${streamUrl}

    const m3u8Content = `#EXTM3U
#EXTINF:-1,${channel}
${streamUrl}
`;

    res.status(200).send(m3u8Content);

  } catch (error) {
    res.status(500).json({ error: "Sunucu hatası", details: error.message });
  }
}
