import links from '../../links.json';

export default function handler(req, res) {
  const { channel } = req.query;

  if (!channel || !links[channel]) {
    res.status(404).json({ error: "Kanal bulunamadı" });
    return;
  }

  const { url, ref, user_agent } = links[channel];

  const stream = `${url}|referer=${ref}&|user-agent=${user_agent}`;

  res.status(200).json({ stream });
}
