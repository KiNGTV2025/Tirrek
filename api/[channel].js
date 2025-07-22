const fs = require("fs");
const path = require("path");

module.exports = async (req, res) => {
  const { channel } = req.query;

  // DEBUG: Kanal ismini logla
  console.log("GELEN KANAL:", channel);

  const filePath = path.join(__dirname, "links.json");

  // Dosya var mı kontrol et
  if (!fs.existsSync(filePath)) {
    return res.status(500).json({ error: "links.json bulunamadı" });
  }

  // JSON oku
  const data = fs.readFileSync(filePath, "utf-8");

  let links;
  try {
    links = JSON.parse(data);
  } catch (err) {
    return res.status(500).json({ error: "links.json bozuk", detay: err.message });
  }

  // Kanal mevcut mi?
  if (!links[channel]) {
    return res.status(404).json({ error: "Kanal bulunamadı", kanal: channel });
  }

  // Kanal bilgilerini döndür
  res.status(200).json(links[channel]);
};
