import path from 'path';
import fs from 'fs/promises';

export default async function handler(req, res) {
  const { channel } = req.query;

  try {
    const filePath = path.join(process.cwd(), 'public', 'links.json');
    const fileContents = await fs.readFile(filePath, 'utf8');
    const data = JSON.parse(fileContents);

    if (!data[channel]) {
      return res.status(404).json({ error: "Kanal bulunamadı" });
    }

    const { url, ref, user_agent } = data[channel];
    return res.status(200).json({
      stream: `${url}|referer=${ref}|user-agent=${user_agent}`
    });

  } catch (err) {
    res.status(500).json({ error: "Sunucu hatası", details: err.message });
  }
}
