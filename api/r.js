import { put } from "@vercel/blob";

const OUTLOOK = ["Getting better", "Neither better nor worse", "Getting worse"];

// Store one anonymous quiz completion: randomized arm, outlook answer, score, referrer tag.
export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();
  let b = req.body;
  if (typeof b === "string") { try { b = JSON.parse(b); } catch { return res.status(400).end(); } }
  const { arm, outlook, score } = b || {};
  if (!["pre", "post"].includes(arm) || !OUTLOOK.includes(outlook) ||
      !Number.isInteger(score) || score < 0 || score > 5) {
    return res.status(400).json({ error: "invalid" });
  }
  const ref = String(b.ref || "direct").replace(/[^a-z0-9_-]/gi, "").slice(0, 40) || "direct";
  const lang = String(b.lang || "en").replace(/[^a-z-]/gi, "").slice(0, 8) || "en";
  const rec = { t: new Date().toISOString(), arm, outlook, score, ref, lang };
  const id = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  await put(`r/${id}.json`, JSON.stringify(rec), {
    access: "public", contentType: "application/json", addRandomSuffix: false,
  });
  return res.status(204).end();
}
