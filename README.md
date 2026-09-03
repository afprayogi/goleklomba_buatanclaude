<p align="center">
  <img src="assets/banner.svg" alt="Cari Lomba — banner" width="100%">
</p>

<h1 align="center">🏆 Cari Lomba</h1>
<p align="center">
  Cari otomatis info <b>lomba renewable energy, teknik elektro, otomasi &amp; inovasi teknologi</b><br>
  dari banyak sumber sekaligus — lengkap dengan <b>deadline pendaftaran</b> dan <b>tanggal pelaksanaan</b>.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/license-MIT-22c55e" alt="License MIT">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-6b7280" alt="Platform">
  <img src="https://img.shields.io/badge/UI-HTML%20%2B%20browser%20scan-7c3aed" alt="HTML viewer with in-browser scan">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
  <img src="https://img.shields.io/badge/Maintained%3F-yes-success" alt="Maintained">
</p>

<p align="center">
  <a href="#-fitur">Fitur</a> ·
  <a href="#%EF%B8%8F-tampilan-viewerhtml">Tampilan</a> ·
  <a href="#-instalasi">Instalasi</a> ·
  <a href="#-cara-pakai">Cara Pakai</a> ·
  <a href="#-privasi--keamanan-data">Privasi</a> ·
  <a href="#-kontribusi">Kontribusi</a> ·
  <a href="#-lisensi">Lisensi</a>
</p>

---

## ✨ Fitur

- 🔎 **Multi-sumber** — mengambil dari beberapa situs Blogger (KabarLomba, AjangLomba,
  BiruLangit, InfoLombaIT, dll), channel Telegram publik, dan (opsional) Instagram.
- 🧠 **Filter relevansi 2 tingkat** (`strong` / `weak` keyword) supaya tidak kebanjiran
  lomba esai/menulis umum yang cuma menyinggung "teknologi" sekali secara basa-basi.
- 📅 **Parsing tanggal otomatis** — mengerti format "Deadline: 26 Juli 2026", rentang
  "26 Juli–9 Agustus 2026", singkatan bulan Indonesia, sampai format numerik `DD/MM/YYYY`.
- 🔁 **Deduplikasi otomatis** — lomba yang sama dari beberapa sumber digabung jadi satu.
- 🖥️ **Viewer HTML offline** — hasil pencarian bisa dibuka sebagai dashboard yang rapi,
  jalan 100% di browser, **data di-cache di `localStorage`** (tidak perlu server).
- 🌐 **Scan langsung dari browser** — `viewer.html` bisa scraping sumber Blogger
  (KabarLomba, AjangLomba, BiruLangit, InfoLombaIT, Infolomba) sendiri tanpa
  menjalankan Python sama sekali, langsung dari tombol di halaman.
- 📲 **Notifikasi WhatsApp opsional** — kirim lomba baru ke WhatsApp lewat gateway lokal,
  dengan dedup supaya tidak spam lomba yang sama dua kali.
- 🤖 **Terintegrasi Claude Code** — bisa dijalankan lewat skill `/cari-lomba` untuk
  dirangkum otomatis dalam bahasa biasa.
- 🔒 **Sadar privasi** — tidak ada data pribadi (nomor WhatsApp, kredensial) yang
  tersimpan di file contoh/template; semua data sensitif diisi lokal oleh kamu sendiri
  dan sudah di-`.gitignore`.

---

## 🖥️ Tampilan (`viewer.html`)

<p align="center">
  <img src="assets/preview-mockup.svg" alt="Ilustrasi tampilan viewer.html" width="85%">
</p>

`viewer.html` adalah dashboard statis (tanpa build step, tanpa dependency) untuk
menampilkan hasil `cari_lomba.py --format json` dalam bentuk kartu yang enak dibaca —
dan sekarang juga bisa mencari sendiri lomba barunya:

- 🌐 **"Scan Blogger Sekarang"** — mengambil data langsung dari situs Blogger sumber
  lomba (lewat endpoint JSONP resmi Blogger, tanpa proxy pihak ketiga), memfilter,
  memberi skor, mem-parsing tanggal, dan mem-dedup-nya — semua logikanya sama persis
  dengan `cari_lomba.py`, dijalankan ulang dalam JavaScript.
- 📂 Atau muat file `hasil.json` langsung dari file picker / tempel JSON manual —
  berguna untuk hasil dari sumber yang **tidak bisa** di-scan browser (Telegram,
  Instagram) karena diblokir CORS.
- 🔍 Cari, filter per kategori (Business Plan, Poster, Hackathon/PKM, dst.), dan
  filter per status (masih dibuka / segera tutup ≤7 hari / sudah tutup / deadline tidak diketahui).
- 📊 Ringkasan statistik instan (total, dibuka, segera tutup, tutup, deadline tidak diketahui).
- 💾 **Otomatis tersimpan ke cache browser (`localStorage`)** — tutup dan buka lagi
  filenya, hasil scan/data terakhir tetap ada tanpa perlu muat ulang.
- 🌗 Tema terang/gelap (ikut preferensi sistem, bisa di-toggle manual).
- 🔒 **Tidak ada server perantara** — kalau kamu tidak menekan "Scan", halaman ini
  tidak melakukan request apa pun. Saat kamu menekan "Scan", request hanya pergi ke
  situs sumber lomba itu sendiri (bukan ke server pihak ketiga manapun).

Coba langsung tanpa perlu jalankan Python — buka [`viewer.html`](viewer.html) di
browser, lalu klik **"🌐 Scan Blogger Sekarang"**. Atau, untuk melihat contoh
tampilannya secara instan tanpa koneksi internet sama sekali, klik **"Tempel JSON"**
dan tempel isi [`demo/hasil-contoh.json`](demo/hasil-contoh.json).

> **Keterbatasan scan browser:** hanya mencakup sumber Blogger. Telegram & Instagram
> tetap wajib lewat `python cari_lomba.py` karena server mereka memblokir permintaan
> lintas-origin dari browser (CORS) — tidak ada cara mengakalinya tanpa proxy pihak
> ketiga, yang sengaja tidak dipakai proyek ini. Kalau salah satu situs Blogger lambat
> atau tidak merespon, scan otomatis melewati sisa keyword situs itu (mirip mekanisme
> `DeadHost` di `cari_lomba.py`) supaya tidak menggantung lama.

---

## 📦 Instalasi

**Requirement:**

| Kebutuhan | Versi |
|---|---|
| Python | 3.9 atau lebih baru |
| pip | terbaru |
| Browser modern | untuk `viewer.html` (Chrome, Edge, Firefox, Safari) |
| WhatsApp gateway lokal *(opsional)* | untuk fitur kirim notifikasi WA |

```bash
git clone <url-repo-ini>
cd cari-lomba
pip install -r requirements.txt
```

Dependensi utama ([`requirements.txt`](requirements.txt)): `requests`, `beautifulsoup4`,
`PyYAML`, `instaloader` (Instagram bersifat opsional).

---

## 🚀 Cara Pakai

### 1. Jalankan pencarian (CLI)

```bash
python cari_lomba.py                                    # tampilkan sebagai tabel di terminal
python cari_lomba.py --days 30                           # hanya deadline 30 hari ke depan
python cari_lomba.py --keyword "hidrogen"                 # tambah keyword filter sekali pakai
python cari_lomba.py --format json --output output/hasil.json
python cari_lomba.py --format csv  --output output/hasil.csv
python cari_lomba.py --include-closed                     # ikut tampilkan yang deadline-nya lewat
```

### 2. Lihat hasilnya di dashboard HTML

**Opsi A — tanpa Python sama sekali:** buka [`viewer.html`](viewer.html) langsung di
browser, klik **"🌐 Scan Blogger Sekarang"**. Hasilnya otomatis tersimpan di cache
browser untuk kunjungan berikutnya.

**Opsi B — hasil lengkap (termasuk Telegram/Instagram):**

```bash
python cari_lomba.py --format json --output output/hasil.json
```

Lalu buka [`viewer.html`](viewer.html) → klik **"📂 Muat file hasil.json"** → pilih
`output/hasil.json`.

### 3. Lewat Claude Code

Ketik `/cari-lomba` di Claude Code (lihat
[`.claude/skills/cari-lomba/SKILL.md`](.claude/skills/cari-lomba/SKILL.md)). Claude
akan menjalankan script yang sama, merangkum hasilnya dalam bahasa biasa, dan bisa
bantu tweak keyword/sumber secara interaktif.

### 4. Kirim otomatis ke WhatsApp *(opsional)*

```bash
python kirim_info_lomba.py --dry-run   # WAJIB dicoba dulu — preview, tidak mengirim apa pun
python kirim_info_lomba.py             # kirim beneran
```

Atau double-click [`preview_info_lomba.bat`](preview_info_lomba.bat) /
[`kirim_info_lomba.bat`](kirim_info_lomba.bat) di Windows. Detail setup gateway &
dedup ada di bagian [Konfigurasi](#%EF%B8%8F-konfigurasi).

---

## 🔐 Privasi & Keamanan Data

Proyek ini didesain supaya **tidak ada data pribadi yang ikut ter-share**:

- `wa_config.yaml` (nomor WhatsApp & kredensial gateway asli kamu) **sudah masuk
  `.gitignore`** — tidak akan pernah ter-commit ke git secara tidak sengaja.
- Yang di-commit ke repo hanyalah [`wa_config.example.yaml`](wa_config.example.yaml),
  template kosong berisi placeholder (`628xxxxxxxxxx@s.whatsapp.net`), bukan nomor asli.
- WhatsApp gateway yang dipakai **berjalan lokal di komputer kamu sendiri**
  (`http://localhost:3000`), bukan layanan pihak ketiga — kredensialnya tidak pernah
  keluar dari komputer kamu.
- `wa_sent_history.json` (riwayat kirim, berisi tautan lomba) dan folder `output/`
  juga di-`.gitignore` karena isinya data hasil run pribadi kamu.
- Instagram **tidak pernah** menangani password kamu — login dilakukan manual lewat
  `instaloader --login=...` di terminal kamu sendiri.
- `viewer.html` tidak melakukan request apa pun secara default. Saat kamu menekan
  **"Scan Blogger Sekarang"**, permintaan hanya pergi langsung ke situs sumber lomba
  (KabarLomba, AjangLomba, dll) — **tidak lewat server/proxy pihak ketiga manapun**.
  Data hasilnya cuma tersimpan di `localStorage` perangkat kamu, tidak dikirim ke mana pun.

**Sebelum push ke repo publik**, cek dulu:

```bash
git status   # pastikan wa_config.yaml TIDAK muncul di daftar file yang akan di-commit
```

---

## ⚙️ Konfigurasi

Semua sumber & keyword diatur di [`config.yaml`](config.yaml) — edit file itu, bukan
`cari_lomba.py`, untuk menambah situs/channel/keyword baru.

| Sumber | Cara ambil | Keterangan |
|---|---|---|
| [kabarlomba.com](https://www.kabarlomba.com), [ajanglomba.com](https://www.ajanglomba.com), [birulangit.id](https://www.birulangit.id), [infolombait.com](https://www.infolombait.com), dll | API JSON bawaan Blogger (`/feeds/posts/default?q=...`) | Tidak perlu scraping HTML rapuh — resmi disediakan platform Blogger |
| Telegram publik: `@informasilomba`, `@edulantern`, `@infolomba_ofc`, dll | `t.me/s/<channel>` (halaman preview publik, tanpa login) | Tambah channel lain lewat `config.yaml` |
| Instagram *(opsional)* | [instaloader](https://github.com/instaloader/instaloader) | Butuh login manual, berisiko kena rate-limit dari Meta |

### Notifikasi WhatsApp

1. Salin template: `cp wa_config.example.yaml wa_config.yaml` (sudah ada secara default).
2. Isi `recipients.personal` / `recipients.groups` dengan nomor/grup tujuan **kamu sendiri**.
3. Jalankan WhatsApp gateway lokal di `http://localhost:3000` (atau sesuaikan `gateway.base_url`).
4. Selalu coba `--dry-run` dulu sebelum kirim beneran.

Jadwalkan otomatis (mis. tiap pagi) lewat Task Scheduler Windows / `cron`:
`python cari_lomba.py` lalu `python kirim_info_lomba.py`.

---

## 🧠 Cara Kerja Filter Relevansi

Supaya tidak kebanjiran lomba esai/menulis umum yang cuma menyebut "teknologi" atau
"inovasi" sekali secara basa-basi, filternya dua tingkat:

- **strong** — kalau salah satu muncul (mis. "elektro", "energi terbarukan", "IoT",
  "smart grid"), lomba langsung dianggap relevan.
- **weak** — kata umum (mis. "teknologi", "inovasi") baru dianggap sinyal relevan kalau
  ada **≥2 kata weak berbeda** DAN **minimal satu di antaranya muncul di judul** (bukan
  cuma di isi artikel).

Hasil dari beberapa sumber yang sebenarnya lomba yang sama otomatis digabung
(deduplikasi berdasarkan kemiripan judul & link).

---

## 📁 Struktur Proyek

```
cari-lomba/
├── cari_lomba.py             # Script utama: cari, filter, parse tanggal, dedup
├── kirim_info_lomba.py       # Kirim lomba baru ke WhatsApp (opsional)
├── config.yaml               # Sumber & keyword — edit di sini, bukan di .py
├── wa_config.example.yaml    # Template config WhatsApp (aman di-commit)
├── wa_config.yaml            # Config WhatsApp asli kamu (di-gitignore)
├── viewer.html                # Dashboard HTML offline + cache browser
├── demo/hasil-contoh.json    # Data contoh untuk coba viewer.html tanpa run Python
├── output/                   # Hasil export CSV/JSON (di-gitignore)
├── .claude/skills/cari-lomba/ # Skill Claude Code (/cari-lomba)
├── assets/                   # Aset gambar README
├── requirements.txt
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

---

## ⚠️ Keterbatasan

- **Deadline tidak selalu ketemu.** Kalau tanggalnya cuma ada di gambar/infografis
  (bukan teks), kolom deadline akan kosong — cek langsung ke link yang diberikan.
- **Hasil antar-run bisa sedikit berbeda.** Endpoint pencarian Blogger tidak selalu
  mengembalikan hasil identik untuk keyword umum — jalankan beberapa kali untuk
  cakupan lebih lengkap.
- **Instagram/X** di luar akun yang dikonfigurasi belum bisa diotomatisasi stabil
  tanpa API berbayar.
- **Scan langsung di `viewer.html`** adalah port JavaScript dari logika Python, tapi
  disederhanakan: tanpa retry otomatis, timeout lebih pendek, dan deduplikasi memakai
  perhitungan kemiripan judul yang lebih ringan (bukan `difflib` Python persis). Untuk
  hasil paling lengkap & akurat, tetap gunakan `python cari_lomba.py`.

---

## 🤝 Kontribusi

Kontribusi apa pun — laporan bug, ide sumber/keyword baru, sampai pull request —
sangat diterima. Baca [`CONTRIBUTING.md`](CONTRIBUTING.md) untuk panduan lengkapnya,
termasuk area yang paling butuh bantuan.

Langkah singkat:

1. Fork repo ini & buat branch baru.
2. Untuk menambah sumber/keyword, biasanya cukup edit [`config.yaml`](config.yaml) —
   tidak perlu sentuh kode Python sama sekali.
3. Buka Pull Request dengan penjelasan singkat kenapa perubahan itu diperlukan.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE) — bebas dipakai, dimodifikasi,
dan didistribusikan ulang, termasuk untuk keperluan komersial, selama menyertakan
notice lisensi aslinya.

---

## 🙏 Disclaimer

Tool ini melakukan scraping ringan terhadap situs publik (Blogger, Telegram) yang
memang menyediakan info lomba secara terbuka. Gunakan secara wajar (jangan jalankan
berulang kali dalam waktu sangat singkat) supaya tidak membebani server sumbernya.
Fitur Instagram bersifat opsional dan sepenuhnya menjadi tanggung jawab pengguna
terkait Ketentuan Layanan Meta.

<p align="center">Dibuat untuk membantu sesama pelajar &amp; mahasiswa menemukan info lomba lebih cepat. Selamat berkompetisi! 🚀</p>
