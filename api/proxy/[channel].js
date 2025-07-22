import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  const { channel } = req.query;
  const channelName = channel.replace('.m3u8', '');

  const filePath = path.join(process.cwd(), 'public', 'links.json');
  let links;

  try {
    const jsonData = fs.readFileSync(filePath, 'utf8');
    links = JSON.parse(jsonData);
  } catch (err) {
    return res.status(500).json({ error: 'Sunucu hatası', details: err.message });
  }

  const link = links[channelName];

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

    const contentType = response.headers.get('content-type');
    res.setHeader('Content-Type', contentType || 'application/vnd.apple.mpegurl');
    const body = await response.text();
    res.status(200).send(body);
  } catch (err) {
    res.status(500).json({ error: 'Proxy hatası', details: err.message });
  }
}
