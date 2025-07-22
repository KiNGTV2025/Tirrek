const fs = require("fs");
const path = require("path");

module.exports = async (req, res) => {
  const { channel } = req.query;

  // JSON dosyasının yolu
  const filePath = path.join(__dirname, "links.json");

  // Dosya var mı kontrol et
  if (!fs.existsSync(filePath)) {
    return res.status(500).json({ error: "links.json bulunamadı" });
  }

  // JSON'u oku
  let links;
  try {
    const raw = fs.readFileSync(filePath, "utf-8");
    links = JSON.parse(raw);
  } catch (err) {
    return res.status(500).json({ error: "links.json okunamadı", detay: err.message });
  }

  // Kanal var mı kontrol et
  if (!links[channel]) {
    return res.status(404).json({ error: "Kanal bulunamadı", kanal: channel });
  }

  // Kanal linkini döndür
  return res.status(200).json(links[channel]);
};
