import fetch from 'node-fetch';

export default async function handler(req, res) {
  try {
    const response = await fetch("https://umittvspor.vercel.app/api/index");
    const { channels } = await response.json();
    
    let m3uOutput = "#EXTM3U\n";
    
    channels.forEach(channel => {
      m3uOutput += `#EXTINF:-1 tvg-id="${channel.id}" tvg-name="${channel.name}",${channel.name}\n`;
      m3uOutput += `#EXTVLCOPT:http-user-agent=Mozilla/5.0\n`;
      m3uOutput += `#EXTVLCOPT:http-referrer=https://www.selcuksportshd1829.xyz/\n`;
      m3uOutput += `${channel.url}\n\n`;
    });

    res.setHeader('Content-Type', 'application/x-mpegURL');
    res.setHeader('Content-Disposition', 'attachment; filename="umittv.m3u"');
    return res.send(m3uOutput);
    
  } catch (error) {
    console.error("M3U Oluşturma Hatası:", error);
    return res.status(500).send("#EXTM3U\n# Hata oluştu");
  }
}
