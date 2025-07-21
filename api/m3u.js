export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  try {
    const response = await fetch("https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u");
    const text = await response.text();
    const lines = text.split("\n").map(line => line.trim());

    let output = "#EXTM3U\n";
    let currentHeaders = {
      'User-Agent': 'Mozilla/5.0',
      'Referer': 'https://www.selcuksportshd1829.xyz/'
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Header bilgilerini işle
      if (line.startsWith('#EXTVLCOPT:http-user-agent=')) {
        currentHeaders['User-Agent'] = line.split('=')[1];
        continue;
      }
      else if (line.startsWith('#EXTVLCOPT:http-referer=')) {
        currentHeaders['Referer'] = line.split('=')[1];
        continue;
      }
      
      // Kanal bilgilerini işle
      const match = line.match(/tvg-id="([^"]+)"[^,]*,(.*)/);
      if (match) {
        const id = match[1];
        const name = match[2];
        
        output += line + '\n';
        output += `#EXTVLCOPT:http-user-agent=${currentHeaders['User-Agent']}\n`;
        output += `#EXTVLCOPT:http-referer=${currentHeaders['Referer']}\n`;
        
        // Bir sonraki satır URL ise
        if (i + 1 < lines.length && lines[i + 1].trim() && !lines[i + 1].startsWith('#')) {
          output += lines[i + 1] + '\n';
          i++; // Bir sonraki satırı atla
        } else {
          output += `https://umittvspor.vercel.app/api/index?id=${id}\n`;
        }
      }
    }

    res.setHeader("Content-Type", "application/x-mpegURL");
    res.setHeader("Content-Disposition", "attachment; filename=umittv.m3u");
    return res.status(200).send(output);

  } catch (err) {
    return res.status(500).send("#EXTM3U\n# Hata oluştu: " + err.message);
  }
}
