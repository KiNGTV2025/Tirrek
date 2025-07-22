import fetch from 'node-fetch';

export default async function handler(req, res) {
  try {
    const response = await fetch("https://umittvspor.vercel.app/channels");
    const { channels } = await response.json();

    let m3uContent = "#EXTM3U\n";
    
    for (const ch of channels) {
      const channelRes = await fetch(`https://umittvspor.vercel.app/stream?id=${ch.id}`);
      const channel = await channelRes.json();
      
      m3uContent += `#EXTINF:-1 tvg-id="${ch.id}" tvg-name="${ch.name}",${ch.name}\n`;
      m3uContent += `#EXTVLCOPT:http-user-agent=${channel.headers['User-Agent']}\n`;
      m3uContent += `#EXTVLCOPT:http-referrer=${channel.headers['Referer']}\n`;
      m3uContent += `${channel.url}\n\n`;
    }

    res.setHeader('Content-Type', 'application/x-mpegURL');
    res.setHeader('Cache-Control', 'public, max-age=600');
    return res.send(m3uContent);

  } catch (error) {
    console.error("M3U Error:", error);
    return res.status(500).send("#EXTM3U\n# Error generating playlist");
  }
}
