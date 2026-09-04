// api/scan.js
//
// Endpoint serverless Vercel: GET /api/scan
// Menjalankan pencarian lomba di server (Blogger + Telegram sekaligus — di sisi
// server TIDAK ada batasan CORS seperti di browser, jadi Telegram pun bisa ikut,
// tidak seperti mode "Scan Blogger Sekarang" di browser yang hanya mendukung
// Blogger). Lihat lib/lomba-core.js untuk logikanya.
//
// Query params (semua opsional):
//   keyword=xxx        tambah keyword filter (bisa diulang: ?keyword=a&keyword=b)
//   telegram=0         matikan sumber Telegram (biar lebih cepat)
//   maxResults=150     jumlah post terbaru yang diambil per situs Blogger
//   timeout=8000       timeout per request (ms)
//   days=30            hanya deadline dalam N hari ke depan
//   includeClosed=1    ikut tampilkan lomba yang deadline-nya sudah lewat
//
// Response di-cache di CDN Vercel selama 30 menit (stale-while-revalidate 1 jam)
// supaya pengunjung berikutnya dapat hasil instan & situs sumber tidak dibebani
// setiap ada yang buka halaman.

const { scan } = require("../lib/lomba-core.js");

module.exports = async (req, res) => {
  if (req.method !== "GET") {
    res.status(405).json({ error: "Method not allowed, pakai GET." });
    return;
  }

  const query = req.query || {};
  const extraKeywords = [].concat(query.keyword || []).filter(Boolean);
  const includeTelegram = query.telegram !== "0" && query.telegram !== "false";
  const maxResultsPerSite = Math.min(Math.max(parseInt(query.maxResults, 10) || 150, 20), 250);
  const timeoutMs = Math.min(Math.max(parseInt(query.timeout, 10) || 8000, 2000), 20000);
  const includeClosed = query.includeClosed === "1" || query.includeClosed === "true";
  const daysRaw = parseInt(query.days, 10);
  const days = Number.isFinite(daysRaw) ? daysRaw : null;

  try {
    const result = await scan({ extraKeywords, includeTelegram, maxResultsPerSite, timeoutMs, includeClosed, days });
    res.setHeader("Cache-Control", "public, s-maxage=1800, stale-while-revalidate=3600");
    res.status(200).json(result);
  } catch (e) {
    res.status(500).json({ error: "Scan gagal total: " + e.message });
  }
};
