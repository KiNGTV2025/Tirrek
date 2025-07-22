import fetch from 'node-fetch';

export default async function handler(req, res) {
  try {
    const apiResponse = await fetch("https://umittvspor.vercel.app/api/index");
    const { channels } = await apiResponse.json();

    let m3u = "#EXTM3U\n";
    
    channels.forEach(channel => {
      m3u += `#EXTINF:-1 tvg-id="${channel.id}" tvg-name="${channel.name}",${channel.name}\n`;
      m3u += `#EXTVLCOPT:http-user-agent=Mozilla/5.0\n`;
      m3u += `#EXTVLCOPT:http-referrer=https://www.selcuksportshd1829.xyz/\n`;
      m3u += `${channel.url}\n\n`;
    });

    res.setHeader('Content-Type', 'application/x-mpegURL');
    res.setHeader('Cache-Control', 'public, max-age=1800');
    return res.send(m3u);

  } catch (error) {
    console.error("M3U Error:", error);
    return res.status(500).send("#EXTM3U\n# Error generating playlist");
  }
}
