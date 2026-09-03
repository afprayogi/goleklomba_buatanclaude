#!/usr/bin/env python3
"""
cari_lomba.py — Cari info lomba (renewable energy / elektro / inovasi teknologi)
dari beberapa sumber, filter by keyword, dedup, dan tampilkan deadline pendaftaran
+ tanggal pelaksanaan (kalau tersedia).

Jalan mandiri (non-Claude):
    python cari_lomba.py
    python cari_lomba.py --format json --output output/hasil.json
    python cari_lomba.py --keyword "hidrogen" --keyword "baterai"
    python cari_lomba.py --include-closed
    python cari_lomba.py --days 30

Semua sumber & keyword diatur lewat config.yaml — tidak perlu ubah script ini
untuk menambah situs Blogger baru, channel Telegram baru, atau keyword baru.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
import yaml
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
TIMEOUT = 15


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    # Retry otomatis untuk blip jaringan sesaat (DNS/koneksi putus-nyambung),
    # supaya satu hiccup tidak langsung dianggap sumber itu mati total.
    retry = Retry(
        total=2, connect=2, read=2, backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = _make_session()
_dead_hosts: set[str] = set()


class DeadHost(Exception):
    """Host ini sudah gagal koneksi sebelumnya di run yang sama — jangan diulang lagi."""


def guarded_get(url: str, **kwargs) -> requests.Response:
    host = urlparse(url).netloc
    if host in _dead_hosts:
        raise DeadHost(host)
    try:
        return SESSION.get(url, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        _dead_hosts.add(host)
        raise

BULAN = {
    "januari": 1, "jan": 1,
    "februari": 2, "feb": 2,
    "maret": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mei": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "agustus": 8, "agt": 8, "ags": 8,
    "september": 9, "sept": 9, "sep": 9,
    "oktober": 10, "okt": 10,
    "november": 11, "nov": 11,
    "desember": 12, "des": 12,
}
# Nama bulan lebih panjang duluan supaya "September" tidak keburu ke-cut jadi "Sep".
BULAN_PATTERN = "|".join(sorted(BULAN.keys(), key=len, reverse=True))


@dataclass
class Lomba:
    title: str
    link: str
    source: str
    published: Optional[str] = None
    deadline: Optional[date] = None
    start_date: Optional[date] = None
    snippet: str = ""
    matched_keywords: list = field(default_factory=list)
    matched_in_title: list = field(default_factory=list)
    also_seen_on: list = field(default_factory=list)
    category: str = "Lainnya"
    score: int = 0

    def to_row(self) -> dict:
        d = asdict(self)
        d["deadline"] = self.deadline.isoformat() if self.deadline else ""
        d["start_date"] = self.start_date.isoformat() if self.start_date else ""
        d["matched_keywords"] = ", ".join(self.matched_keywords)
        d["matched_in_title"] = ", ".join(self.matched_in_title)
        d["also_seen_on"] = ", ".join(self.also_seen_on)
        return d


def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def strip_html(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)


def parse_id_date(day: str, month_name: str, year: str) -> Optional[date]:
    month = BULAN.get(month_name.lower())
    if not month:
        return None
    try:
        return date(int(year), month, int(day))
    except ValueError:
        return None


# Banyak blog (mis. AjangLomba/BiruLangit) menulis tanggal sebagai daftar "Timeline:"
# berisi rentang, misal "Pendaftaran & Abstrak: 26 Juli-9 Agustus 2026" — bukan kalimat
# "Deadline: ...". Fallback ini mencari label lalu ambil tanggal terakhir dalam rentang.
# Separator rentang: dash biasa, "s.d", "s/d", atau "sampai (dengan)".
RANGE_SEP = r"(?:[-–—]|s\.?\s*/?\s*d\.?|sampai(?:\s+dengan)?)"
DATE_RANGE_TAIL_RE = re.compile(
    rf"(\d{{1,2}})\s+(?:{BULAN_PATTERN})?\s*{RANGE_SEP}\s*(\d{{1,2}})\s+({BULAN_PATTERN})\s+(\d{{4}})",
    re.IGNORECASE,
)
SINGLE_DATE_RE = re.compile(rf"(\d{{1,2}})\s+({BULAN_PATTERN})\s+(\d{{4}})", re.IGNORECASE)
# Format numerik DD/MM/YYYY atau DD-MM-YYYY (gaya Indonesia: tanggal duluan).
NUMERIC_DATE_RE = re.compile(r"\b(\d{1,2})[/.](\d{1,2})[/.](\d{4})\b")

DEADLINE_TRIGGER_RE = re.compile(
    r"(?:deadline|batas\s+akhir|batas\s+waktu|paling\s+lambat|ditutup|"
    r"berakhir|terakhir\s+pendaftaran|penutupan\s+pendaftaran|early\s+bird|"
    r"gelombang\s+terakhir|close\s+registration)",
    re.IGNORECASE,
)
PENDAFTARAN_TRIGGER_RE = re.compile(r"pendaftaran", re.IGNORECASE)
START_TRIGGER_RE = re.compile(
    r"(?:pelaksanaan|dilaksanakan|digelar|berlangsung|acara\s+puncak|"
    r"grand\s+final|final\s+akan|\bfinal\b|puncak\s+acara|\bawarding\b|pengumuman\s+pemenang)",
    re.IGNORECASE,
)


def parse_numeric_date(day: str, month: str, year: str) -> Optional[date]:
    try:
        d, m, y = int(day), int(month), int(year)
    except ValueError:
        return None
    if not (1 <= m <= 12):
        return None
    try:
        return date(y, m, d)
    except ValueError:
        return None


def _find_date_near(text: str, trigger_re: re.Pattern, window: int = 60) -> Optional[date]:
    for m in trigger_re.finditer(text):
        raw = text[m.end():m.end() + window]
        # Jangan lewat batas kalimat/baris biar tidak "nyangkut" ke info lain yang
        # kebetulan ada tanggalnya juga. Titik di singkatan (mis. "s.d", "No.5")
        # bukan akhir kalimat, jadi cuma hitung titik yang diikuti spasi/akhir teks.
        sentence_end = re.search(r"\.(?:\s|$)", raw)
        newline_end = raw.find("\n")
        stops = [i for i in (sentence_end.start() if sentence_end else -1, newline_end) if i != -1]
        chunk = raw[:min(stops)] if stops else raw

        rm = DATE_RANGE_TAIL_RE.search(chunk)
        if rm:
            d = parse_id_date(rm.group(2), rm.group(3), rm.group(4))
            if d:
                return d
        sm = SINGLE_DATE_RE.search(chunk)
        if sm:
            d = parse_id_date(*sm.groups())
            if d:
                return d
        nm = NUMERIC_DATE_RE.search(chunk)
        if nm:
            d = parse_numeric_date(*nm.groups())
            if d:
                return d
    return None


def find_deadline(text: str) -> Optional[date]:
    d = _find_date_near(text, DEADLINE_TRIGGER_RE, window=45)
    if d:
        return d
    return _find_date_near(text, PENDAFTARAN_TRIGGER_RE, window=80)


def find_start_date(text: str) -> Optional[date]:
    return _find_date_near(text, START_TRIGGER_RE, window=60)


_KEYWORD_PATTERN_CACHE: dict[str, re.Pattern] = {}


def _keyword_pattern(kw: str) -> re.Pattern:
    kw = kw.strip()
    if kw not in _KEYWORD_PATTERN_CACHE:
        # \b di kedua ujung supaya keyword pendek (mis. "EV", "AI") tidak
        # menangkap potongan kata lain seperti "reLEVan" atau "developAI-ent".
        _KEYWORD_PATTERN_CACHE[kw] = re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
    return _KEYWORD_PATTERN_CACHE[kw]


def keyword_matches(text: str, keywords: list[str]) -> list[str]:
    return [kw for kw in keywords if _keyword_pattern(kw).search(text)]


def is_relevant(matched: list[str], matched_in_title: list[str], strong: set[str], weak: set[str]) -> bool:
    matched_lower = {m.strip().lower() for m in matched}
    if matched_lower & strong:
        return True
    # Kata umum (weak) sangat sering muncul sebagai basa-basi di isi artikel,
    # jadi minimal salah satu match weak harus ada di JUDUL, plus total >=2 match weak.
    title_lower = {m.strip().lower() for m in matched_in_title}
    weak_hits = matched_lower & weak
    weak_title_hits = title_lower & weak
    return len(weak_hits) >= 2 and len(weak_title_hits) >= 1


COMPETITION_HINT_RE = re.compile(
    r"\b(lomba|competition|kompetisi|kontes|lkti|lktin|essay|esai|olimpiade|challenge|"
    r"business\s*plan|bisnis\s*plan|\bbmc\b|infografis|infographic|paper|poster|"
    r"debat|pkm|hackathon|inovasi|business\s*case)\b",
    re.IGNORECASE,
)


def is_competition_post(title: str, categories: list[str]) -> bool:
    if any(COMPETITION_HINT_RE.search(c) for c in categories):
        return True
    return bool(COMPETITION_HINT_RE.search(title))


# Label tipe lomba yang ditampilkan ke user, supaya business plan/infografis/dll
# gampang dikenali sekilas tanpa buka link satu-satu. Urutan menentukan prioritas
# kalau judul cocok lebih dari satu (mis. "Esai & Poster" -> ambil yang pertama).
CATEGORY_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("Business Plan", re.compile(r"\b(business\s*plan|bisnis\s*plan|\bbmc\b|business\s*case)\b", re.IGNORECASE)),
    ("Infografis", re.compile(r"\b(infografis|infographic)\b", re.IGNORECASE)),
    ("Paper/LKTI", re.compile(r"\b(lkti|lktin|paper|karya\s+tulis)\b", re.IGNORECASE)),
    ("Esai", re.compile(r"\b(esai|essay)\b", re.IGNORECASE)),
    ("Poster", re.compile(r"\bposter\b", re.IGNORECASE)),
    ("Video", re.compile(r"\bvideo\b", re.IGNORECASE)),
    ("Hackathon/PKM", re.compile(r"\b(hackathon|pkm)\b", re.IGNORECASE)),
    ("Debat", re.compile(r"\bdebat\b", re.IGNORECASE)),
]


def detect_category(title: str) -> str:
    for label, pattern in CATEGORY_PATTERNS:
        if pattern.search(title):
            return label
    return "Lainnya"


def relevance_score(matched: list[str], matched_in_title: list[str], strong: set[str]) -> int:
    matched_lower = {m.strip().lower() for m in matched}
    title_lower = {m.strip().lower() for m in matched_in_title}
    score = 0
    score += 3 * len(matched_lower & strong)
    score += 2 * len(title_lower)  # keyword apa pun yang nongol di judul lebih meyakinkan
    score += len(matched_lower)
    return score


def fetch_blogger_source(name: str, base_url: str, keywords: list[str], freshness_days: int) -> list[Lomba]:
    results: list[Lomba] = []
    seen_ids = set()
    cutoff = datetime.now().astimezone() - timedelta(days=freshness_days)
    for kw in keywords:
        url = f"{base_url.rstrip('/')}/feeds/posts/default"
        # Catatan: published-min TIDAK dihormati oleh endpoint ini saat dipakai
        # bareng q= (sudah diverifikasi manual), jadi filter freshness dilakukan
        # di sisi client dari field published tiap entry.
        params = {"q": kw, "alt": "json", "max-results": 25}
        try:
            resp = guarded_get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except DeadHost:
            # Sudah gagal koneksi ke host ini sebelumnya di run ini — jangan
            # diulang untuk tiap keyword, cukup lewati sisa keyword untuk sumber ini.
            break
        except Exception as e:
            print(f"  [!] {name}: gagal ambil keyword '{kw}' ({e})", file=sys.stderr)
            continue

        entries = data.get("feed", {}).get("entry", [])
        for entry in entries:
            entry_id = entry.get("id", {}).get("$t", "")
            if entry_id in seen_ids:
                continue
            seen_ids.add(entry_id)

            title = entry.get("title", {}).get("$t", "").strip()
            content_html = entry.get("content", {}).get("$t", "") or \
                entry.get("summary", {}).get("$t", "")
            content_text = strip_html(content_html)
            published = entry.get("published", {}).get("$t", "")
            categories = [c.get("term", "") for c in entry.get("category", [])]

            if published:
                try:
                    published_dt = datetime.fromisoformat(published)
                except ValueError:
                    published_dt = None
                if published_dt and published_dt < cutoff:
                    continue

            if not is_competition_post(title, categories):
                continue

            link = ""
            for l in entry.get("link", []):
                if l.get("rel") == "alternate":
                    link = l.get("href", "")
                    break

            full_text = f"{title} {content_text}"
            matched = keyword_matches(full_text, keywords)
            if not matched:
                continue

            results.append(Lomba(
                title=title,
                link=link,
                source=name,
                published=published[:10] if published else None,
                deadline=find_deadline(full_text),
                start_date=find_start_date(full_text),
                snippet=content_text[:280],
                matched_keywords=matched,
                matched_in_title=keyword_matches(title, keywords),
            ))
    return results


def fetch_telegram_channel(channel: str, keywords: list[str]) -> list[Lomba]:
    results: list[Lomba] = []
    url = f"https://t.me/s/{channel}"
    try:
        resp = guarded_get(url)
        resp.raise_for_status()
    except DeadHost:
        print(f"  [!] Telegram @{channel}: dilewati, t.me sedang tidak bisa diakses", file=sys.stderr)
        return results
    except Exception as e:
        print(f"  [!] Telegram @{channel}: gagal diambil ({e})", file=sys.stderr)
        return results

    soup = BeautifulSoup(resp.text, "html.parser")
    for wrap in soup.select("div.tgme_widget_message"):
        text_el = wrap.select_one(".tgme_widget_message_text")
        if not text_el:
            continue
        text = text_el.get_text(" ", strip=True)
        matched = keyword_matches(text, keywords)
        if not matched:
            continue

        date_link = wrap.select_one("a.tgme_widget_message_date")
        link = date_link.get("href", "") if date_link else ""
        time_el = wrap.select_one("time")
        published = None
        if time_el and time_el.get("datetime"):
            published = time_el["datetime"][:10]

        title = text.split("\n")[0][:120] or text[:120]

        results.append(Lomba(
            title=title,
            link=link,
            source=f"Telegram @{channel}",
            published=published,
            deadline=find_deadline(text),
            start_date=find_start_date(text),
            snippet=text[:280],
            matched_keywords=matched,
            matched_in_title=keyword_matches(title, keywords),
        ))
    return results


def fetch_instagram(accounts: list[str], session_username: str, keywords: list[str]) -> list[Lomba]:
    """Baca postingan akun IG publik lewat instaloader (github.com/instaloader/instaloader).

    Butuh session login yang dibuat MANUAL oleh user lewat terminal:
        instaloader --login=<username>
    Script ini tidak pernah meminta atau menyimpan password. Kalau belum login,
    sumber ini di-skip dengan pesan, bukan error fatal.
    """
    results: list[Lomba] = []
    if not accounts or not session_username:
        return results
    try:
        import instaloader
    except ImportError:
        print("  [!] Instagram: 'pip install instaloader' dulu untuk mengaktifkan sumber ini", file=sys.stderr)
        return results

    L = instaloader.Instaloader(
        download_pictures=False, download_videos=False,
        download_video_thumbnails=False, save_metadata=False,
        compress_json=False, quiet=True,
    )
    try:
        L.load_session_from_file(session_username)
    except Exception as e:
        print(
            f"  [!] Instagram: belum login. Jalankan 'instaloader --login={session_username}' "
            f"sendiri di terminal (masukkan password kamu di sana), lalu ulangi. ({e})",
            file=sys.stderr,
        )
        return results

    for account in accounts:
        try:
            profile = instaloader.Profile.from_username(L.context, account)
        except Exception as e:
            print(f"  [!] Instagram @{account}: gagal diakses ({e})", file=sys.stderr)
            continue
        try:
            for count, post in enumerate(profile.get_posts(), start=1):
                if count > 40:  # batasi biar tidak memicu rate-limit Instagram
                    break
                caption = post.caption or ""
                matched = keyword_matches(caption, keywords)
                if not matched:
                    continue
                title = caption.split("\n")[0][:120] or caption[:120]
                results.append(Lomba(
                    title=title,
                    link=f"https://www.instagram.com/p/{post.shortcode}/",
                    source=f"Instagram @{account}",
                    published=post.date.strftime("%Y-%m-%d"),
                    deadline=find_deadline(caption),
                    start_date=find_start_date(caption),
                    snippet=caption[:280],
                    matched_keywords=matched,
                    matched_in_title=keyword_matches(title, keywords),
                ))
        except Exception as e:
            print(f"  [!] Instagram @{account}: error saat scraping ({e})", file=sys.stderr)
    return results


def dedup(items: list[Lomba]) -> list[Lomba]:
    def norm(t: str) -> str:
        return re.sub(r"[^a-z0-9 ]", "", t.lower()).strip()

    unique: list[Lomba] = []
    for item in items:
        item_norm = norm(item.title)
        match = None
        for existing in unique:
            ratio = difflib.SequenceMatcher(None, item_norm, norm(existing.title)).ratio()
            if ratio >= 0.72 or (item.link and item.link == existing.link):
                match = existing
                break
        if match:
            if item.source not in match.also_seen_on and item.source != match.source:
                match.also_seen_on.append(item.source)
            match.deadline = match.deadline or item.deadline
            match.start_date = match.start_date or item.start_date
            match.score = max(match.score, item.score)
        else:
            unique.append(item)
    return unique


def collect(config: dict, extra_keywords: list[str]) -> list[Lomba]:
    kw_cfg = config.get("keywords", {})
    strong = list(kw_cfg.get("strong", []))
    weak = list(kw_cfg.get("weak", []))
    # extra keyword dari CLI diperlakukan sebagai strong (user eksplisit minta ini)
    strong = strong + extra_keywords
    keywords = strong + weak
    strong_set = {k.strip().lower() for k in strong}
    weak_set = {k.strip().lower() for k in weak}
    exclude = [e.lower() for e in kw_cfg.get("exclude", []) or []]

    all_items: list[Lomba] = []

    freshness_days = config.get("output", {}).get("freshness_days", 240)
    for site in config.get("sources", {}).get("blogger_sites", []) or []:
        print(f"[*] Mengambil dari {site['name']} ({site['base_url']}) ...")
        all_items.extend(fetch_blogger_source(site["name"], site["base_url"], keywords, freshness_days))

    for channel in config.get("sources", {}).get("telegram_channels", []) or []:
        print(f"[*] Mengambil dari Telegram @{channel} ...")
        all_items.extend(fetch_telegram_channel(channel, keywords))

    ig_cfg = config.get("sources", {}).get("instagram", {}) or {}
    ig_accounts = ig_cfg.get("accounts", []) or []
    ig_user = ig_cfg.get("session_username", "") or ""
    if ig_accounts and ig_user:
        print(f"[*] Mengambil dari Instagram ({', '.join(ig_accounts)}) ...")
        all_items.extend(fetch_instagram(ig_accounts, ig_user, keywords))
    else:
        print("[*] Instagram: dilewati (isi session_username di config.yaml setelah login manual)")

    all_items = [
        i for i in all_items
        if is_relevant(i.matched_keywords, i.matched_in_title, strong_set, weak_set)
    ]

    for i in all_items:
        i.category = detect_category(i.title)
        i.score = relevance_score(i.matched_keywords, i.matched_in_title, strong_set)

    if exclude:
        all_items = [
            i for i in all_items
            if not any(ex in f"{i.title} {i.snippet}".lower() for ex in exclude)
        ]

    return dedup(all_items)


def filter_by_days(items: list[Lomba], days: Optional[int], include_closed: bool) -> list[Lomba]:
    today = date.today()
    out = []
    for i in items:
        if i.deadline and not include_closed and i.deadline < today:
            continue
        if i.deadline and days is not None and (i.deadline - today).days > days:
            continue
        out.append(i)
    return out


def sort_items(items: list[Lomba]) -> list[Lomba]:
    # Utama: deadline paling dekat dulu (yang tidak ketahuan deadline-nya di akhir).
    # Kalau deadline sama/sama-sama tidak ketahuan: skor relevansi tertinggi dulu,
    # supaya yang paling jelas nyambung ke kriteria kamu naik ke atas.
    return sorted(items, key=lambda i: (i.deadline is None, i.deadline or date.max, -i.score))


def print_table(items: list[Lomba]) -> None:
    if not items:
        print("Tidak ada lomba yang cocok dengan kriteria.")
        return
    print(f"\nDitemukan {len(items)} lomba:\n")
    for i, item in enumerate(items, 1):
        deadline_s = item.deadline.strftime("%d %b %Y") if item.deadline else "tidak diketahui"
        start_s = item.start_date.strftime("%d %b %Y") if item.start_date else "tidak diketahui"
        sources = item.source + (f" (juga di: {', '.join(item.also_seen_on)})" if item.also_seen_on else "")
        print(f"{i}. [{item.category}] {item.title}")
        print(f"   Deadline pendaftaran : {deadline_s}")
        print(f"   Awal pelaksanaan     : {start_s}")
        print(f"   Sumber               : {sources}")
        print(f"   Link                 : {item.link}")
        print(f"   Skor relevansi       : {item.score}")
        print(f"   Keyword cocok        : {', '.join(item.matched_keywords)}")
        print()


def write_csv(items: list[Lomba], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["title", "category", "link", "source", "published", "deadline", "start_date",
              "score", "snippet", "matched_keywords", "also_seen_on"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in items:
            writer.writerow(item.to_row())
    print(f"Tersimpan ke {path}")


def write_json(items: list[Lomba], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([i.to_row() for i in items], f, ensure_ascii=False, indent=2)
    print(f"Tersimpan ke {path}")


def cek_sinyal() -> bool:
    """Cek cepat: internet nyala atau tidak, sebelum mulai proses yang panjang."""
    print("[*] Cek sinyal internet dulu...")
    try:
        SESSION.get("https://www.google.com", timeout=5)
        print("[*] Sinyal aman, lanjut cari lomba...\n")
        return True
    except requests.exceptions.RequestException:
        return False


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Cari info lomba renewable energy / elektro / inovasi teknologi")
    parser.add_argument("--config", default="config.yaml", help="Path ke config.yaml")
    parser.add_argument("--keyword", action="append", default=[], help="Tambah keyword filter (bisa diulang)")
    parser.add_argument("--format", choices=["table", "csv", "json"], help="Format output")
    parser.add_argument("--output", help="Path file output (untuk csv/json)")
    parser.add_argument("--days", type=int, default=None, help="Hanya tampilkan deadline dalam N hari ke depan")
    parser.add_argument("--include-closed", action="store_true", help="Ikut tampilkan lomba yang deadline-nya sudah lewat")
    parser.add_argument("--skip-check", action="store_true", help="Lewati cek sinyal awal, langsung jalan")
    args = parser.parse_args()

    if not args.skip_check and not cek_sinyal():
        print(
            "\n[!] Internet kamu kelihatannya belum konek (atau lagi bermasalah).\n"
            "    Coba buka situs apa saja dulu di browser, atau restart WiFi/data kamu,\n"
            "    baru jalankan lagi 'python cari_lomba.py'.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = Path(__file__).parent / config_path
    config = load_config(config_path)

    items = collect(config, args.keyword)
    items = filter_by_days(items, args.days, args.include_closed)
    items = sort_items(items)

    if _dead_hosts:
        hosts_list = ", ".join(sorted(_dead_hosts))
        print(
            f"\n[!] Beberapa situs gagal diakses di tengah proses: {hosts_list}\n"
            f"    Kemungkinan koneksi internet kamu putus-nyambung pas proses jalan.\n"
            f"    Hasil di bawah ini kemungkinan tidak lengkap — jalankan ulang kalau\n"
            f"    koneksi sudah stabil.\n",
            file=sys.stderr,
        )

    fmt = args.format or config.get("output", {}).get("default_format", "table")

    if fmt == "table":
        print_table(items)
    elif fmt == "csv":
        out = Path(args.output) if args.output else Path(__file__).parent / config["output"]["default_dir"] / "hasil.csv"
        write_csv(items, out)
    elif fmt == "json":
        out = Path(args.output) if args.output else Path(__file__).parent / config["output"]["default_dir"] / "hasil.json"
        write_json(items, out)


if __name__ == "__main__":
    main()
