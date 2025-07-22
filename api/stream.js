import fetch from 'node-fetch';

const M3U_URL = "https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u";

export default async function handler(req, res) {
  try {
    const { id } = req.query;
    if (!id) return res.status(400).json({ error: "id parameter required" });

    const response = await fetch(M3U_URL);
    const text = await response.text();
    
    const channel = findChannel(text, id);
    if (!channel) return res.status(404).json({ error: "Channel not found" });

    return res.json(channel);

  } catch (error) {
    console.error("Error:", error);
    return res.status(500).json({ error: error.message });
  }
}

function findChannel(content, searchId) {
  const lines = content.split('\n');
  let current = {};
  let headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.selcuksportshd1829.xyz/'
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line.startsWith('#EXTVLCOPT:http-user-agent=')) {
      headers['User-Agent'] = line.split('=')[1].trim();
    }
    else if (line.startsWith('#EXTVLCOPT:http-referrer=')) {
      headers['Referer'] = line.split('=')[1].trim();
    }
    else if (line.startsWith('#EXTINF:-1')) {
      const name = line.split(/,(.+)/)[1]?.trim() || 'Unknown';
      const id = createChannelId(name);
      
      if (id === searchId.toLowerCase()) {
        current = { id, name, headers: { ...headers } };
      }
    }
    else if (line && !line.startsWith('#') && current.id) {
      return {
        ...current,
        url: line
      };
    }
  }

  return null;
}

function createChannelId(name) {
  return name.toLowerCase()
    .replace(/\s+/g, '')
    .replace('beinsports', 'bein')
    .replace('beinsport', 'bein');
}
