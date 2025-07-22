import fetch from 'node-fetch';

const M3U_URL = "https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u";

export default async function handler(req, res) {
  try {
    const response = await fetch(M3U_URL);
    const text = await response.text();
    
    const channels = parseM3U(text).map(ch => ({
      id: ch.id,
      name: ch.name,
      url: `/stream?id=${ch.id}`
    }));

    return res.json({ channels });
    
  } catch (error) {
    console.error("Error:", error);
    return res.status(500).json({ error: error.message });
  }
}

function parseM3U(content) {
  const result = [];
  const lines = content.split('\n');
  let current = {};

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line.startsWith('#EXTINF:-1')) {
      const name = line.split(/,(.+)/)[1]?.trim() || 'Unknown';
      current = {
        id: createChannelId(name),
        name: name,
        url: ''
      };
    } 
    else if (line && !line.startsWith('#') && current.id) {
      current.url = line;
      result.push(current);
    }
  }

  return result;
}

function createChannelId(name) {
  return name.toLowerCase()
    .replace(/\s+/g, '')
    .replace('beinsports', 'bein')
    .replace('beinsport', 'bein');
}
