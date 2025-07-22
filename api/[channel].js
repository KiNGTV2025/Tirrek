import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  const { channel } = req.query;

  try {
    const filePath = path.join(process.cwd(), 'api', 'links.json');
    const fileContents = fs.readFileSync(filePath, 'utf8');
    const links = JSON.parse(fileContents);

    const data = links[channel];
    if (!data?.url) {
      return res.status(404).json({ error: "Kanal bulunamadı" });
    }

    const stream = `${data.url}|referer=${data.ref}&|user-agent=${data.user_agent}`;
    return res.status(200).json({ stream });

  } catch (err) {
    return res.status(500).json({ error: "Sunucu hatası", details: err.message });
  }
}
