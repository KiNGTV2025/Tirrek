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

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const match = line.match(/tvg-id="([^"]+)"[^,]*,(.*)/);

      if (match) {
        const id = match[1];
        const name = match[2];

        output += `#EXTINF:-1 tvg-id="${id}",${name}\n`;
        output += `https://umittvspor.vercel.app/api/index?id=${id}\n`;
      }
    }

    res.setHeader("Content-Type", "application/x-mpegURL");
    res.setHeader("Content-Disposition", "attachment; filename=Kablonet.m3u");
    return res.status(200).send(output);

  } catch (err) {
    return res.status(500).send("#EXTM3U\n# Hata oluştu: " + err.message);
  }
}
