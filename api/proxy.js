import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  let { channel } = req.query;

  // ".m3u8" varsa temizle
  if (channel.endsWith('.m3u8')) {
    channel = channel.replace('.m3u8', '');
  }

  const filePath = path.join(process.cwd(), 'public', 'links.json');

  let links;
  try {
    const fileContents = fs.readFileSync(filePath, 'utf8');
    links = JSON.parse(fileContents);
  } catch (err) {
    return res.status(500).json({ error: 'links.json okunamadı', details: err.message });
  }

  const link = links[channel];

  if (!link) {
    return res.status(404).json({ error: 'Kanal bulunamadı' });
  }

  try {
    const response = await fetch(link.url, {
      headers: {
        'Referer': link.ref,
        'User-Agent': link.user_agent
      }
    });

    if (!response.ok) {
      throw new Error(`Hata: ${response.status}`);
    }

    const contentType = response.headers.get('content-type') || 'application/vnd.apple.mpegurl';
    res.setHeader('Content-Type', contentType);
    const body = await response.text();
    res.status(200).send(body);
  } catch (err) {
    res.status(500).json({ error: 'Proxy hatası', details: err.message });
  }
}
