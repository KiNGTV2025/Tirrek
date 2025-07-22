import path from 'path';
import fs from 'fs/promises';

export default async function handler(req, res) {
  const { channel } = req.query;

  try {
    const filePath = path.join(process.cwd(), 'public', 'links.json');
    const fileContents = await fs.readFile(filePath, 'utf8');
    const links = JSON.parse(fileContents);

    const link = links[channel];
    if (!link) {
      return res.status(404).json({ error: 'Kanal bulunamadı' });
    }

    const response = await fetch(link.url, {
      headers: {
        'Referer': link.ref,
        'User-Agent': link.user_agent
      }
    });

    if (!response.ok) {
      return res.status(502).json({ error: 'Yayın alınamadı', status: response.status });
    }

    const contentType = response.headers.get('content-type');
    res.setHeader('Content-Type', contentType || 'application/vnd.apple.mpegurl');

    const stream = await response.text();
    res.status(200).send(stream);
  } catch (err) {
    res.status(500).json({ error: 'Sunucu hatası', details: err.message });
  }
}
