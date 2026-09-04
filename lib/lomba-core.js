// lib/lomba-core.js
//
// Logika inti pencarian & filter lomba, dipakai oleh api/scan.js (serverless,
// jalan di Node — jadi TIDAK kena batasan CORS seperti di browser, sehingga bisa
// scan Blogger *dan* Telegram sekaligus). Ini adalah port dari cari_lomba.py,
// disederhanakan untuk cocok dengan batas waktu fungsi serverless:
//   - Blogger: satu request per situs (feed terbaru, tanpa loop per-keyword)
//     lalu difilter di sisi ini — jauh lebih sedikit request daripada
//     "1 request x tiap keyword x tiap situs" ala CLI.
//   - Telegram: satu request per channel (halaman preview publik /s/<channel>),
//     di-parse dengan regex ringan (sengaja tanpa dependency HTML parser
//     supaya npm install tetap instan & repo tetap kecil).
//
// Kalau kamu mengubah config.yaml, perbarui juga DEFAULT_CONFIG di bawah ini
// secara manual — file ini bukan pembaca config.yaml (menghindari dependency
// parser YAML tambahan demi ukuran paket yang minimal).
//
// Tanpa dependency npm sama sekali — hanya pakai fetch/regex bawaan Node 18+.

"use strict";

const DEFAULT_CONFIG = {
  bloggerSites: [
    { name: "KabarLomba", baseUrl: "https://www.kabarlomba.com" },
    { name: "AjangLomba", baseUrl: "https://www.ajanglomba.com" },
    { name: "BiruLangit", baseUrl: "https://www.birulangit.id" },
    { name: "InfoLombaIT", baseUrl: "https://www.infolombait.com" },
    { name: "Infolomba", baseUrl: "https://www.infolomba.com" },
  ],
  telegramChannels: [
    "informasilomba",
    "edulantern",
    "infolomba_ofc",
    "infolombamahasiswa",
    "lombamahasiswa",
    "infolombanational",
    "eventmahasiswa",
    "id_scholarship",
  ],
  strong: [
    "renewable energy", "energi terbarukan", "energi bersih", "energi baru", "elektro",
    "electrical engineering", "kelistrikan", "internet of things", "robotika",
    "kendaraan listrik", "electric vehicle", "smart grid", "embedded system",
    "mikrokontroler", "PLTS", "PLTB", "PLTA", "solar cell", "panel surya",
    "sustainable energy", "green energy", "inovasi teknologi", "PLC",
    "programmable logic controller", "otomasi", "automation", "sistem kendali",
    "kontrol otomatis", "scada", "hmi", "telemetry", "IoT",
    "pertamuda", "gemastik", "hackathon",
  ],
  weak: [
    "teknologi", "inovasi", "robot", "EV", "AI", "artificial intelligence",
    "kecerdasan buatan", "machine learning", "deep learning", "pemrograman",
    "pemograman", "sensor", "data science", "oee",
  ],
  exclude: ["lomba mewarnai", "tingkat SD", "tingkat SMP", "lomba menari", "lomba menyanyi"],
  freshnessDays: 240,
};

// ---------- tanggal Bahasa Indonesia ----------

const BULAN = {
  januari: 1, jan: 1, februari: 2, feb: 2, maret: 3, mar: 3, april: 4, apr: 4, mei: 5,
  juni: 6, jun: 6, juli: 7, jul: 7, agustus: 8, agt: 8, ags: 8, september: 9, sept: 9,
  sep: 9, oktober: 10, okt: 10, november: 11, nov: 11, desember: 12, des: 12,
};
const BULAN_PATTERN = Object.keys(BULAN).sort((a, b) => b.length - a.length).join("|");
const RANGE_SEP = "(?:[-–—]|s\\.?\\s*/?\\s*d\\.?|sampai(?:\\s+dengan)?)";
const DATE_RANGE_TAIL_RE = new RegExp("(\\d{1,2})\\s+(?:" + BULAN_PATTERN + ")?\\s*" + RANGE_SEP + "\\s*(\\d{1,2})\\s+(" + BULAN_PATTERN + ")\\s+(\\d{4})", "i");
const SINGLE_DATE_RE = new RegExp("(\\d{1,2})\\s+(" + BULAN_PATTERN + ")\\s+(\\d{4})", "i");
const NUMERIC_DATE_RE = /\b(\d{1,2})[/.](\d{1,2})[/.](\d{4})\b/;
const DEADLINE_TRIGGER_RE = /(?:deadline|batas\s+akhir|batas\s+waktu|paling\s+lambat|ditutup|berakhir|terakhir\s+pendaftaran|penutupan\s+pendaftaran|early\s+bird|gelombang\s+terakhir|close\s+registration)/gi;
const PENDAFTARAN_TRIGGER_RE = /pendaftaran/gi;
const START_TRIGGER_RE = /(?:pelaksanaan|dilaksanakan|digelar|berlangsung|acara\s+puncak|grand\s+final|final\s+akan|\bfinal\b|puncak\s+acara|\bawarding\b|pengumuman\s+pemenang)/gi;

function parseIdDate(day, monthName, year) {
  const month = BULAN[monthName.toLowerCase()];
  if (!month) return null;
  const d = new Date(Date.UTC(Number(year), month - 1, Number(day)));
  return (d.getUTCFullYear() === Number(year) && d.getUTCMonth() === month - 1 && d.getUTCDate() === Number(day)) ? d : null;
}
function parseNumericDate(day, month, year) {
  const m = Number(month);
  if (!(m >= 1 && m <= 12)) return null;
  const d = new Date(Date.UTC(Number(year), m - 1, Number(day)));
  return (d.getUTCFullYear() === Number(year) && d.getUTCMonth() === m - 1 && d.getUTCDate() === Number(day)) ? d : null;
}
function findDateNear(text, triggerRe, window) {
  triggerRe.lastIndex = 0;
  let m;
  while ((m = triggerRe.exec(text))) {
    const raw = text.slice(m.index + m[0].length, m.index + m[0].length + window);
    const sentenceEnd = raw.search(/\.(?:\s|$)/);
    const newlineEnd = raw.indexOf("\n");
    const stops = [sentenceEnd, newlineEnd].filter((i) => i !== -1);
    const chunk = stops.length ? raw.slice(0, Math.min(...stops)) : raw;

    const rm = DATE_RANGE_TAIL_RE.exec(chunk);
    if (rm) { const d1 = parseIdDate(rm[2], rm[3], rm[4]); if (d1) return d1; }
    const sm = SINGLE_DATE_RE.exec(chunk);
    if (sm) { const d2 = parseIdDate(sm[1], sm[2], sm[3]); if (d2) return d2; }
    const nm = NUMERIC_DATE_RE.exec(chunk);
    if (nm) { const d3 = parseNumericDate(nm[1], nm[2], nm[3]); if (d3) return d3; }
  }
  return null;
}
function findDeadline(text) {
  return findDateNear(text, DEADLINE_TRIGGER_RE, 45) || findDateNear(text, PENDAFTARAN_TRIGGER_RE, 80);
}
function findStartDate(text) {
  return findDateNear(text, START_TRIGGER_RE, 60);
}
function toIsoDate(d) {
  if (!d) return "";
  const y = d.getUTCFullYear(), m = String(d.getUTCMonth() + 1).padStart(2, "0"), day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

// ---------- keyword & relevansi ----------

const COMPETITION_HINT_RE = /\b(lomba|competition|kompetisi|kontes|lkti|lktin|essay|esai|olimpiade|challenge|business\s*plan|bisnis\s*plan|\bbmc\b|infografis|infographic|paper|poster|debat|pkm|hackathon|inovasi|business\s*case)\b/i;
const CATEGORY_PATTERNS = [
  ["Business Plan", /\b(business\s*plan|bisnis\s*plan|\bbmc\b|business\s*case)\b/i],
  ["Infografis", /\b(infografis|infographic)\b/i],
  ["Paper/LKTI", /\b(lkti|lktin|paper|karya\s+tulis)\b/i],
  ["Esai", /\b(esai|essay)\b/i],
  ["Poster", /\bposter\b/i],
  ["Video", /\bvideo\b/i],
  ["Hackathon/PKM", /\b(hackathon|pkm)\b/i],
  ["Debat", /\bdebat\b/i],
];

function escapeRegExp(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
const _kwPatternCache = new Map();
function keywordPattern(kw) {
  kw = kw.trim();
  if (!_kwPatternCache.has(kw)) _kwPatternCache.set(kw, new RegExp("\\b" + escapeRegExp(kw) + "\\b", "i"));
  return _kwPatternCache.get(kw);
}
function keywordMatches(text, keywords) {
  return keywords.filter((kw) => keywordPattern(kw).test(text));
}
function isRelevant(matched, matchedInTitle, strongSet, weakSet) {
  const matchedLower = matched.map((m) => m.trim().toLowerCase());
  if (matchedLower.some((m) => strongSet.has(m))) return true;
  const titleLower = matchedInTitle.map((m) => m.trim().toLowerCase());
  const weakHits = new Set(matchedLower.filter((m) => weakSet.has(m)));
  const weakTitleHits = new Set(titleLower.filter((m) => weakSet.has(m)));
  return weakHits.size >= 2 && weakTitleHits.size >= 1;
}
function isCompetitionPost(title, categories) {
  if (categories.some((c) => COMPETITION_HINT_RE.test(c))) return true;
  return COMPETITION_HINT_RE.test(title);
}
function detectCategory(title) {
  for (const [label, re] of CATEGORY_PATTERNS) if (re.test(title)) return label;
  return "Lainnya";
}
function relevanceScore(matched, matchedInTitle, strongSet) {
  const matchedLower = new Set(matched.map((m) => m.trim().toLowerCase()));
  const titleLower = new Set(matchedInTitle.map((m) => m.trim().toLowerCase()));
  let score = 0;
  matchedLower.forEach((m) => { if (strongSet.has(m)) score += 3; });
  score += 2 * titleLower.size;
  score += matchedLower.size;
  return score;
}

// ---------- HTML → teks (regex ringan, tanpa dependency) ----------

const HTML_ENTITIES = { amp: "&", quot: '"', apos: "'", lt: "<", gt: ">", nbsp: " " };
function decodeHtmlEntities(s) {
  return s.replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, (whole, ent) => {
    if (ent[0] === "#") {
      const isHex = ent[1] === "x" || ent[1] === "X";
      const code = isHex ? parseInt(ent.slice(2), 16) : parseInt(ent.slice(1), 10);
      return Number.isNaN(code) ? whole : String.fromCodePoint(code);
    }
    const key = ent.toLowerCase();
    return HTML_ENTITIES[key] || whole;
  });
}
function stripHtml(html) {
  if (!html) return "";
  const text = html.replace(/<[^>]+>/g, " ");
  return decodeHtmlEntities(text).replace(/\s+/g, " ").trim();
}

// ---------- deduplikasi (kemiripan judul, pengganti ringan difflib) ----------

function normTitle(t) { return (t || "").toLowerCase().replace(/[^a-z0-9 ]/g, "").trim(); }
function bigrams(s) { const arr = []; for (let i = 0; i < s.length - 1; i++) arr.push(s.slice(i, i + 2)); return arr; }
function diceCoefficient(a, b) {
  if (!a || !b) return 0;
  const bgA = bigrams(a), bgB = bigrams(b);
  if (!bgA.length || !bgB.length) return a === b ? 1 : 0;
  const mapB = new Map();
  bgB.forEach((bg) => mapB.set(bg, (mapB.get(bg) || 0) + 1));
  let matches = 0;
  bgA.forEach((bg) => { const c = mapB.get(bg); if (c > 0) { matches++; mapB.set(bg, c - 1); } });
  return (2 * matches) / (bgA.length + bgB.length);
}
function dedupItems(items) {
  const unique = [];
  items.forEach((item) => {
    const itemNorm = normTitle(item.title);
    let match = null;
    for (const existing of unique) {
      const ratio = diceCoefficient(itemNorm, normTitle(existing.title));
      if (ratio >= 0.6 || (item.link && item.link === existing.link)) { match = existing; break; }
    }
    if (match) {
      if (item.source !== match.source && !match.also_seen_on.includes(item.source)) match.also_seen_on.push(item.source);
      match.deadline = match.deadline || item.deadline;
      match.start_date = match.start_date || item.start_date;
      match.score = Math.max(match.score, item.score);
    } else {
      unique.push(item);
    }
  });
  return unique;
}

// ---------- fetch dengan timeout ----------

async function fetchWithTimeout(url, opts, timeoutMs) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs || 8000);
  try {
    return await fetch(url, { ...opts, signal: ctrl.signal });
  } finally {
    clearTimeout(timer);
  }
}

const UA = "Mozilla/5.0 (compatible; CariLombaBot/1.0; +https://github.com/afprayogi/goleklomba_buatanclaude)";

// ---------- sumber: Blogger ----------

async function fetchBloggerSite(site, maxResults, timeoutMs) {
  const url = `${site.baseUrl.replace(/\/$/, "")}/feeds/posts/default?alt=json&max-results=${maxResults}`;
  const resp = await fetchWithTimeout(url, { headers: { "User-Agent": UA } }, timeoutMs);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const data = await resp.json();
  const entries = (data && data.feed && data.feed.entry) || [];
  return entries.map((entry) => {
    const title = ((entry.title && entry.title.$t) || "").trim();
    const contentHtml = (entry.content && entry.content.$t) || (entry.summary && entry.summary.$t) || "";
    const contentText = stripHtml(contentHtml);
    const published = (entry.published && entry.published.$t) || "";
    const categories = (entry.category || []).map((c) => c.term || "");
    let link = "";
    for (const l of entry.link || []) { if (l.rel === "alternate") { link = l.href || ""; break; } }
    return {
      id: link || title,
      title, link, source: site.name,
      published: published ? published.slice(0, 10) : null,
      publishedMs: published ? Date.parse(published) : NaN,
      titleText: title,
      fullText: `${title} ${contentText}`,
      snippet: contentText.slice(0, 280),
      categories,
    };
  });
}

// ---------- sumber: Telegram ----------

function parseTelegramHtml(html, channel) {
  const parts = html.split('<div class="tgme_widget_message_wrap js-widget_message_wrap">');
  const out = [];
  for (let i = 1; i < parts.length; i++) {
    const chunk = parts[i];
    const postMatch = chunk.match(/data-post="([^"]+)"/);
    const textMatch = chunk.match(/<div class="tgme_widget_message_text[^"]*"[^>]*>([\s\S]*?)<\/div>/);
    const timeMatch = chunk.match(/<time datetime="([^"]+)"/);
    if (!postMatch || !textMatch) continue;
    const text = stripHtml(textMatch[1]);
    if (!text) continue;
    const link = `https://t.me/${postMatch[1]}`;
    const published = timeMatch ? timeMatch[1].slice(0, 10) : null;
    const title = text.slice(0, 120);
    out.push({
      id: link,
      title, link, source: `Telegram @${channel}`,
      published,
      publishedMs: timeMatch ? Date.parse(timeMatch[1]) : NaN,
      titleText: title,
      fullText: text,
      snippet: text.slice(0, 280),
      categories: [],
    });
  }
  return out;
}
async function fetchTelegramChannel(channel, timeoutMs) {
  const url = `https://t.me/s/${channel}`;
  const resp = await fetchWithTimeout(url, { headers: { "User-Agent": UA } }, timeoutMs);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  const html = await resp.text();
  return parseTelegramHtml(html, channel);
}

// ---------- orkestrasi utama ----------

async function scan(options) {
  const cfg = DEFAULT_CONFIG;
  const opts = options || {};
  const timeoutMs = opts.timeoutMs || 8000;
  const maxResultsPerSite = opts.maxResultsPerSite || 150;
  const extraKeywords = opts.extraKeywords || [];
  const includeTelegram = opts.includeTelegram !== false;
  const includeClosed = opts.includeClosed === true;
  const maxDays = Number.isFinite(opts.days) ? opts.days : null;

  const strong = cfg.strong.concat(extraKeywords);
  const weak = cfg.weak;
  const keywords = strong.concat(weak);
  const strongSet = new Set(strong.map((k) => k.trim().toLowerCase()));
  const weakSet = new Set(weak.map((k) => k.trim().toLowerCase()));
  const excludeList = cfg.exclude.map((e) => e.toLowerCase());
  const freshnessCutoff = Date.now() - cfg.freshnessDays * 86400000;

  const sourcesOk = [];
  const sourcesFailed = [];
  const rawResults = [];

  const bloggerJobs = cfg.bloggerSites.map(async (site) => {
    try {
      const entries = await fetchBloggerSite(site, maxResultsPerSite, timeoutMs);
      sourcesOk.push(site.name);
      return entries;
    } catch (e) {
      sourcesFailed.push({ source: site.name, error: e.message });
      return [];
    }
  });

  const telegramJobs = includeTelegram
    ? cfg.telegramChannels.map(async (channel) => {
        const label = `Telegram @${channel}`;
        try {
          const entries = await fetchTelegramChannel(channel, timeoutMs);
          sourcesOk.push(label);
          return entries;
        } catch (e) {
          sourcesFailed.push({ source: label, error: e.message });
          return [];
        }
      })
    : [];

  const allEntryLists = await Promise.all([...bloggerJobs, ...telegramJobs]);
  const allEntries = allEntryLists.flat();

  allEntries.forEach((e) => {
    if (!Number.isNaN(e.publishedMs) && e.publishedMs < freshnessCutoff) return;
    if (!isCompetitionPost(e.titleText, e.categories)) return;
    const matched = keywordMatches(e.fullText, keywords);
    if (!matched.length) return;
    rawResults.push({
      title: e.title, link: e.link, source: e.source, published: e.published,
      snippet: e.snippet,
      matched,
      matchedInTitle: keywordMatches(e.titleText, keywords),
      fullText: e.fullText,
    });
  });

  const relevant = rawResults.filter((r) => isRelevant(r.matched, r.matchedInTitle, strongSet, weakSet));

  let items = relevant.map((r) => {
    const deadline = findDeadline(r.fullText);
    const startDate = findStartDate(r.fullText);
    return {
      title: r.title, link: r.link, source: r.source, published: r.published,
      deadline: toIsoDate(deadline), start_date: toIsoDate(startDate),
      snippet: r.snippet,
      matched_keywords: r.matched.join(", "),
      matched_in_title: r.matchedInTitle.join(", "),
      also_seen_on: [],
      category: detectCategory(r.title),
      score: relevanceScore(r.matched, r.matchedInTitle, strongSet),
    };
  });

  if (excludeList.length) {
    items = items.filter((i) => {
      const hay = `${i.title} ${i.snippet}`.toLowerCase();
      return !excludeList.some((ex) => hay.includes(ex));
    });
  }

  let deduped = dedupItems(items);
  deduped.forEach((i) => { i.also_seen_on = i.also_seen_on.join(", "); });

  // Default-nya samakan dengan CLI: sembunyikan yang deadline-nya sudah lewat,
  // dan (opsional) batasi hanya yang deadline-nya dalam N hari ke depan.
  if (!includeClosed || maxDays !== null) {
    const todayUtc = Date.UTC(new Date().getUTCFullYear(), new Date().getUTCMonth(), new Date().getUTCDate());
    deduped = deduped.filter((i) => {
      if (!i.deadline) return true;
      const dMs = Date.parse(i.deadline + "T00:00:00Z");
      if (Number.isNaN(dMs)) return true;
      if (!includeClosed && dMs < todayUtc) return false;
      if (maxDays !== null && Math.round((dMs - todayUtc) / 86400000) > maxDays) return false;
      return true;
    });
  }

  deduped.sort((a, b) => {
    const da = a.deadline ? Date.parse(a.deadline) : NaN;
    const db = b.deadline ? Date.parse(b.deadline) : NaN;
    if (Number.isNaN(da) && Number.isNaN(db)) return b.score - a.score;
    if (Number.isNaN(da)) return 1;
    if (Number.isNaN(db)) return -1;
    return da - db;
  });

  return {
    items: deduped,
    sourcesOk,
    sourcesFailed,
    generatedAt: new Date().toISOString(),
  };
}

module.exports = {
  DEFAULT_CONFIG,
  scan,
  findDeadline,
  findStartDate,
  toIsoDate,
  keywordMatches,
  isRelevant,
  isCompetitionPost,
  detectCategory,
  relevanceScore,
  stripHtml,
  dedupItems,
  parseTelegramHtml,
};
