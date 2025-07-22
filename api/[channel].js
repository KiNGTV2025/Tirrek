export default async function handler(req, res) {
  const { channel } = req.query;

  try {
    const response = await fetch(`${process.env.VERCEL_URL ? "https://" + process.env.VERCEL_URL : "http://localhost:3000"}/links.json`);
    const links = await response.json();

    const data = links[channel];
    if (!data || !data.url) {
      return res.status(404).json({ error: "Kanal bulunamadı" });
    }

    const stream = `${data.url}|referer=${data.ref}&|user-agent=${data.user_agent}`;
    return res.status(200).json({ stream });
  } catch (err) {
    return res.status(500).json({ error: "Sunucu hatası", details: err.message });
  }
}
