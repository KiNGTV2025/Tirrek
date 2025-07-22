const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
  const { channel } = req.query;
  const filePath = path.join(__dirname, 'links.json');

  if (!fs.existsSync(filePath)) {
    return res.status(500).json({ error: "links.json bulunamadı" });
  }

  const raw = fs.readFileSync(filePath);
  const links = JSON.parse(raw);

  if (!links[channel]) {
    return res.status(404).json({ error: "Kanal bulunamadı" });
  }

  res.setHeader('Content-Type', 'application/json');
  res.status(200).json(links[channel]);
};
