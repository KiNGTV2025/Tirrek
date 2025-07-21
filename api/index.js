import links from './links.json';

export default function handler(req, res) {
  const id = parseInt(req.query.id);
  const keys = Object.keys(links);

  if (isNaN(id) || id < 0 || id >= keys.length) {
    return res.status(404).send("Kanal bulunamadı");
  }

  const cid = keys[id];
  const streamUrl = links[cid];
  if (!streamUrl) {
    return res.status(404).send("Link yok");
  }

  res.redirect(streamUrl);
}
