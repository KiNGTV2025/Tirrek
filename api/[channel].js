import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  let { channel } = req.query;

  // Eğer kanal ".m3u8" ile geliyorsa onu kırp
  channel = channel.replace('.m3u8', '');

  const filePath = path.join(process.cwd(), 'public', 'links.json');

  try {
    const data = fs.readFileSync(filePath, 'utf8');
    const links = JSON.parse(data);

    if (!links[channel]) {
      res.status(404).json({ error: 'Kanal bulunamadı' });
      return;
    }

    const { url, ref, user_agent } = links[channel];

    // IPTV playerlar referer ve user-agent desteğini bazen url'nin içine | işareti ile koyuyor
    const streamUrl = `${url}|referer=${ref}|user-agent=${user_agent}`;

    // İçerik tipini m3u8 olarak ayarla
    res.setHeader('Content-Type', 'application/vnd.apple.mpegurl');

    // M3U8 içeriğini oluştur
    const m3u8Content = `#EXTM3U
#EXTINF:-1,${channel}
${streamUrl}
`;

    res.status(200).send(m3u8Content);

  } catch (error) {
    res.status(500).json({ error: 'Sunucu hatası', details: error.message });
  }
}
