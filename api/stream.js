const axios = require('axios');
const { parse } = require('url');

async function parseM3UFromGitHub() {
  const m3uUrl = 'https://raw.githubusercontent.com/KiNGTV2025/Tirrek/main/1UmitTV.m3u';
  try {
    const response = await axios.get(m3uUrl);
    const lines = response.data.split('\n');
    const channels = {};
    let currentChannel = null;
    let currentHeaders = {
      'User-Agent': 'Mozilla/5.0',
      'Referer': 'https://www.selcuksportshd1829.xyz/'
    };

    for (const line of lines) {
      if (line.startsWith('#EXTINF:-1')) {
        const idMatch = line.match(/tvg-id="([^"]+)"/) || line.match(/group-title="[^"]*",([^,]+)/);
        currentChannel = {
          id: idMatch ? idMatch[1].toLowerCase().replace(/\s+/g, '') : null,
          name: line.split(/,(.+)/)[1] || 'Unknown',
          url: null,
          headers: { ...currentHeaders } // Mevcut header'ları kopyala
        };
      }
      else if (line.startsWith('#EXTVLCOPT:http-user-agent=')) {
        currentHeaders['User-Agent'] = line.split('=')[1];
      }
      else if (line.startsWith('#EXTVLCOPT:http-referrer=') || line.startsWith('#EXTVLCOPT:http-referer=')) {
        currentHeaders['Referer'] = line.split('=')[1];
      }
      else if (line.trim() && !line.startsWith('#') && currentChannel) {
        currentChannel.url = line.trim();
        if (currentChannel.id) {
          channels[currentChannel.id] = currentChannel;
        }
        currentChannel = null;
      }
    }
    return channels;
  } catch (error) {
    console.error('M3U parse hatası:', error);
    throw new Error('M3U dosyası alınamadı veya parse edilemedi');
  }
}

module.exports = async (req, res) => {
  try {
    const { pathname, query } = parse(req.url, true);
    
    // Tüm kanalları getir
    if (pathname === '/api/umittv.m3u') {
      const channels = await parseM3UFromGitHub();
      let m3uContent = "#EXTM3U\n";
      
      for (const [id, channel] of Object.entries(channels)) {
        m3uContent += `#EXTINF:-1 tvg-id="${id}" tvg-name="${channel.name}" group-title="Selcuksports",${channel.name}\n`;
        m3uContent += `#EXTVLCOPT:http-user-agent=${channel.headers['User-Agent']}\n`;
        m3uContent += `#EXTVLCOPT:http-referer=${channel.headers['Referer']}\n`;
        m3uContent += `${channel.url}\n`;
      }
      
      res.setHeader('Content-Type', 'application/x-mpegURL');
      res.setHeader('Content-Disposition', 'attachment; filename="umittv.m3u"');
      return res.status(200).send(m3uContent);
    }
    
    // Tek kanal getir
    if (pathname === '/api/stream') {
      const channelId = query.id?.toLowerCase();
      if (!channelId) {
        return res.status(400).json({ error: 'Kanal ID parametresi gereklidir (?id=kanaladi)' });
      }
      
      const channels = await parseM3UFromGitHub();
      const channel = channels[channelId];
      
      if (!channel) {
        return res.status(404).json({ 
          error: 'Kanal bulunamadı', 
          available_channels: Object.keys(channels),
          suggestion: channelId.includes('bein') ? 'beinmax1 veya beinmax2 deneyin' : null
        });
      }
      
      return res.status(200).json({
        id: channelId,
        name: channel.name,
        url: channel.url,
        headers: channel.headers
      });
    }
    
    return res.status(404).json({ error: 'Endpoint bulunamadı' });
    
  } catch (error) {
    console.error('Hata:', error);
    return res.status(500).json({ 
      error: 'Sunucu hatası',
      details: error.message 
    });
  }
};
