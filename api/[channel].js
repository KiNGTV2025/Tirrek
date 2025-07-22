import fs from 'fs';
import path from 'path';

export default function handler(req, res) {
  const { channel } = req.query;

  try {
    // Public klasördeki links.json dosyasının tam yolu
    const filePath = path.resolve('./public/links.json');
    const fileContents = fs.readFileSync(filePath, 'utf-8');
    const links = JSON.parse(fileContents);

    const data = links[channel];
    if (!data) {
      return res.status(404).json({ error: "Kanal bulunamadı" });
    }

    // İstenen formatta stream linki oluşturuyoruz
    const stream = `${data.url}|referer=${data.ref}&|user-agent=${data.user_agent}`;

    return res.status(200).json({ stream });

  } catch (error) {
    return res.status(500).json({
      error: "Sunucu hatası",
      details: error.message,
    });
  }
}
