const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
  const { channel } = req.query;

  const filePath = path.join(__dirname, 'links.json');

  if (!fs.existsSync(filePath)) {
    return res.status(500).json({ error: "links.json bulunamadı" });
  }

  const data = fs.readFileSync(filePath, 'utf-8');
  const links = JSON.parse(data);

  if (!links[channel]) {
    return res.status(404).json({ error: "Kanal bulunamadı" });
  }

  return res.status(200).json(links[channel]);
};
