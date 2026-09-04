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
  <img src="https://img.shields.io/badge/node-%3E%3D18-339933?logo=node.js&logoColor=white" alt="Node.js 18+">
  <img src="https://img.shields.io/badge/dependencies-0-success" alt="Zero npm dependencies">
  <img src="https://img.shields.io/badge/deploy-Vercel-000000?logo=vercel&logoColor=white" alt="Deploy on Vercel">
  <img src="https://img.shields.io/badge/license-MIT-22c55e" alt="License MIT">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
</p>

<p align="center">
  <a href="https://vercel.com/new/clone?repository-url=https://github.com/afprayogi/goleklomba_buatanclaude">
    <img src="https://vercel.com/button" alt="Deploy with Vercel">
  </a>
</p>

<p align="center">
  🇮🇩 Bahasa Indonesia · <a href="README.md">🇬🇧 English</a>
</p>

<p align="center">
  <a href="#-fitur">Fitur</a> ·
  <a href="#%EF%B8%8F-tampilan-indexhtml">Tampilan</a> ·
  <a href="#-deploy-ke-vercel">Deploy ke Vercel</a> ·
  <a href="#-instalasi">Instalasi</a> ·
  <a href="#-cara-pakai">Cara Pakai</a> ·
  <a href="#-privasi--keamanan-data">Privasi</a> ·
  <a href="#-kontribusi">Kontribusi</a> ·
  <a href="#-lisensi">Lisensi</a>
</p>

---

## ✨ Fitur

- 🚀 **Web app siap deploy ke Vercel** — satu klik tombol *Deploy* di atas, langsung
  jadi situs sendiri. **Tanpa dependency npm** (`node_modules` kosong), jadi build-nya
  cepat dan gampang dijalankan siapa saja.
- 🔎 **Multi-sumber** — Blogger (KabarLomba, AjangLomba, BiruLangit, InfoLombaIT,
  Infolomba), channel Telegram publik, dan (lewat CLI) Instagram opsional.
- 🌩️ **Scan server-side (Blogger + Telegram sekaligus)** — endpoint `/api/scan` jalan
  di Node, jadi *tidak* kena batasan CORS seperti di browser. Tinggal klik satu tombol
  di halaman web, tanpa install Python sama sekali.
- 🧠 **Filter relevansi 2 tingkat** (`strong` / `weak` keyword) supaya tidak kebanjiran
  lomba esai/menulis umum yang cuma menyinggung "teknologi" sekali secara basa-basi.
- 📅 **Parsing tanggal otomatis** — mengerti format "Deadline: 26 Juli 2026", rentang
  "26 Juli–9 Agustus 2026", singkatan bulan Indonesia, sampai format numerik `DD/MM/YYYY`.
- 🔁 **Deduplikasi otomatis** — lomba yang sama dari beberapa sumber digabung jadi satu.
- 🖥️ **Dashboard HTML modern** — kartu lomba, filter kategori/status, statistik instan,
  tema terang/gelap, skeleton loading, notifikasi toast, dan **cache di `localStorage`**
  browser kamu (bukan di server).
- 📲 **Notifikasi WhatsApp opsional (CLI)** — kirim lomba baru ke WhatsApp lewat gateway
  lokal, dengan dedup supaya tidak spam lomba yang sama dua kali.
- 🤖 **Terintegrasi Claude Code** — bisa dijalankan lewat skill `/cari-lomba` untuk
  dirangkum otomatis dalam bahasa biasa.
- 🔒 **Sadar privasi** — endpoint server tidak menyimpan apa pun (stateless, cuma
  meneruskan hasil scan); tidak ada data pribadi (nomor WhatsApp, kredensial) di file
  contoh/template; semua data sensitif sudah di-`.gitignore` *dan* `.vercelignore`.

---

## 🖥️ Tampilan (`index.html`)

<p align="center">
  <img src="assets/preview-mockup.svg" alt="Ilustrasi tampilan index.html" width="85%">
</p>

`index.html` adalah dashboard satu-file (tanpa framework, tanpa build step) yang jadi
halaman utama saat proyek ini di-deploy ke Vercel — dan tetap bisa dibuka langsung dari
komputer kamu (klik dua kali) tanpa server sama sekali. Ada tiga cara mengisi datanya:

| Tombol | Sumber | Butuh server? |
|---|---|---|
| 🚀 **Scan Semua Sumber** | Blogger *dan* Telegram, lewat `/api/scan` (Node, tanpa batas CORS) | Ya — hanya aktif setelah deploy (atau `vercel dev` lokal) |
| 🌐 **Scan Blogger (di browser)** | Blogger saja, langsung dari JavaScript browser (JSONP resmi Blogger) | Tidak — jalan walau file dibuka langsung |
| 📂 **Muat file / 📋 Tempel JSON** | Hasil `python cari_lomba.py --format json` (termasuk Instagram) | Tidak |

Halaman otomatis mendeteksi mode-nya (lihat badge kecil di header: 🟢 *mode web* atau
🟡 *mode lokal*) dan menonaktifkan tombol yang tidak relevan. Fitur lain:

- 🔍 Cari, filter per kategori (Business Plan, Poster, Hackathon/PKM, dst.), dan filter
  per status (masih dibuka / segera tutup ≤7 hari / sudah tutup / deadline tidak diketahui).
- 📊 Ringkasan statistik instan, kartu lomba dengan indikator sisa hari, dan link "juga
  ditemukan di sumber lain" untuk lomba yang muncul di beberapa situs sekaligus.
- 💀 Skeleton loading + status berjalan saat scan server sedang berlangsung.
- 💾 **Otomatis tersimpan ke cache browser (`localStorage`)** — tutup dan buka lagi,
  hasil scan terakhir tetap ada.
- 🌗 Tema terang/gelap (ikut preferensi sistem, bisa di-toggle manual), responsif di HP.
- 🔔 Notifikasi toast & modal (tidak ada lagi `alert()`/`prompt()` browser yang kaku).

Belum sempat deploy? Klik **"👀 Lihat contoh dulu"** di halaman kosong untuk memuat
[`demo/hasil-contoh.json`](demo/hasil-contoh.json) secara instan, tanpa koneksi internet.

---

## 🚢 Deploy ke Vercel

Proyek ini **tanpa dependency npm** — `npm install` selesai dalam hitungan detik, jadi
build di Vercel juga cepat.

### Opsi 1 — satu klik

Klik tombol **Deploy with Vercel** di bagian atas README ini, lalu ikuti alurnya (import
dari GitHub kamu sendiri, atau fork dulu repo ini). Vercel otomatis mendeteksi
`api/scan.js` sebagai Serverless Function dan `index.html` sebagai halaman utama —
tidak perlu konfigurasi tambahan.

### Opsi 2 — lewat CLI

```bash
npm i -g vercel      # sekali saja, kalau belum pernah pakai Vercel CLI
vercel                # deploy preview
vercel --prod          # deploy ke production
```

### Opsi 3 — coba lokal dulu sebelum deploy

```bash
vercel dev
```

Ini menjalankan `index.html` **dan** `/api/scan` di `http://localhost:3000` persis
seperti di production, jadi tombol **"🚀 Scan Semua Sumber"** ikut aktif (beda dengan
buka `index.html` langsung lewat `file://`, yang otomatis membatasi diri ke mode
browser-only).

**Yang perlu diketahui:**

- `api/scan.js` di-set `maxDuration: 30` detik di [`vercel.json`](vercel.json). Kalau
  plan Vercel kamu tidak mengizinkan durasi itu, turunkan angkanya atau andalkan tombol
  "Scan Blogger (di browser)" sebagai cadangan.
- Respons `/api/scan` di-cache di CDN Vercel selama 30 menit (`stale-while-revalidate`
  1 jam) — supaya pengunjung berikutnya dapat hasil instan dan situs sumber tidak
  dibebani tiap ada yang buka halaman.
- `.vercelignore` sudah disiapkan supaya `wa_config.yaml`, `wa_sent_history.json`,
  `output/`, dan file Python **tidak pernah ikut ter-upload** saat deploy lewat CLI dari
  folder lokal kamu (CLI tidak otomatis membaca `.gitignore`).

---

## 📦 Instalasi

**Requirement:**

| Kebutuhan | Versi | Untuk apa |
|---|---|---|
| Node.js | 18 atau lebih baru | Web app + `/api/scan` (tanpa dependency npm) |
| Python | 3.9 atau lebih baru | CLI (`cari_lomba.py`, Telegram+Instagram lengkap, notifikasi WA) |
| Browser modern | — | Chrome, Edge, Firefox, Safari |
| WhatsApp gateway lokal *(opsional)* | — | Fitur kirim notifikasi WA |

```bash
git clone https://github.com/afprayogi/goleklomba_buatanclaude.git
cd goleklomba_buatanclaude
npm install                    # instan — proyek ini nol dependency
pip install -r requirements.txt   # opsional, hanya kalau mau pakai CLI Python
```

---

## 🚀 Cara Pakai

### 1. Web app (Vercel) — cara paling gampang

Buka situs yang sudah di-deploy (lihat [Deploy ke Vercel](#-deploy-ke-vercel) kalau
belum), klik **"🚀 Scan Semua Sumber"**. Selesai — hasilnya (Blogger + Telegram)
langsung tampil dan tersimpan di cache browser kamu.

### 2. Buka langsung dari komputer (tanpa server)

Klik dua kali [`index.html`](index.html). Tombol **"🌐 Scan Blogger (di browser)"** tetap
aktif (Blogger saja); untuk cakupan penuh, pakai CLI di bawah lalu muat hasilnya lewat
**"📂 Muat file hasil.json"**.

### 3. CLI Python — hasil paling lengkap

```bash
python cari_lomba.py                                    # tampilkan sebagai tabel di terminal
python cari_lomba.py --days 30                           # hanya deadline 30 hari ke depan
python cari_lomba.py --keyword "hidrogen"                 # tambah keyword filter sekali pakai
python cari_lomba.py --format json --output output/hasil.json
python cari_lomba.py --format csv  --output output/hasil.csv
python cari_lomba.py --include-closed                     # ikut tampilkan yang deadline-nya lewat
```

Lalu buka [`index.html`](index.html) → klik **"📂 Muat file hasil.json"** → pilih
`output/hasil.json` (mencakup Instagram juga, kalau sudah dikonfigurasi).

### 4. Lewat Claude Code

Ketik `/cari-lomba` di Claude Code (lihat
[`.claude/skills/cari-lomba/SKILL.md`](.claude/skills/cari-lomba/SKILL.md)). Claude
akan menjalankan script yang sama, merangkum hasilnya dalam bahasa biasa, dan bisa
bantu tweak keyword/sumber secara interaktif.

### 5. Kirim otomatis ke WhatsApp *(opsional, CLI)*

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
  `.gitignore` dan `.vercelignore`** — tidak akan ter-commit ke git atau ter-upload ke
  Vercel secara tidak sengaja.
- Yang di-commit ke repo hanyalah [`wa_config.example.yaml`](wa_config.example.yaml),
  template kosong berisi placeholder (`628xxxxxxxxxx@s.whatsapp.net`), bukan nomor asli.
- WhatsApp gateway yang dipakai **berjalan lokal di komputer kamu sendiri**
  (`http://localhost:3000`), bukan layanan pihak ketiga — kredensialnya tidak pernah
  keluar dari komputer kamu, dan tidak ada hubungannya dengan deployment Vercel.
- `wa_sent_history.json` (riwayat kirim) dan folder `output/` juga di-`.gitignore` +
  `.vercelignore` karena isinya data hasil run pribadi kamu.
- Instagram **tidak pernah** menangani password kamu — login dilakukan manual lewat
  `instaloader --login=...` di terminal kamu sendiri (fitur CLI, bukan bagian dari
  deployment Vercel).
- **`/api/scan` bersifat stateless** — tidak ada database, tidak menyimpan siapa yang
  request atau apa yang dicari. Ia hanya meneruskan (dan meng-cache sebentar di CDN)
  hasil scan situs publik, yang memang datanya sudah publik.
- `index.html` tidak mengirim apa pun ke pihak ketiga di luar (a) `/api/scan` di domain
  Vercel kamu sendiri, atau (b) situs sumber lomba saat tombol "Scan Blogger (di
  browser)" ditekan. Data yang tampil hanya tersimpan di `localStorage` perangkat kamu.

**Sebelum push ke repo publik / deploy dari CLI**, cek dulu:

```bash
git status   # pastikan wa_config.yaml TIDAK muncul di daftar file yang akan di-commit
```

---

## ⚙️ Konfigurasi

Semua sumber & keyword untuk CLI diatur di [`config.yaml`](config.yaml). Untuk web app
(`/api/scan` dan mode "Scan Blogger di browser"), sumber & keyword ada di
[`lib/lomba-core.js`](lib/lomba-core.js) dan di dalam `index.html` — sengaja disalin
manual (bukan membaca `config.yaml` saat runtime) supaya proyek ini tetap **nol
dependency** (tanpa parser YAML tambahan). Kalau mengubah salah satu, selaraskan juga
yang lain.

| Sumber | Cara ambil | Keterangan |
|---|---|---|
| [kabarlomba.com](https://www.kabarlomba.com), [ajanglomba.com](https://www.ajanglomba.com), [birulangit.id](https://www.birulangit.id), [infolombait.com](https://www.infolombait.com), dll | API JSON bawaan Blogger (`/feeds/posts/default`) | Tidak perlu scraping HTML rapuh — resmi disediakan platform Blogger |
| Telegram publik: `@informasilomba`, `@edulantern`, `@infolomba_ofc`, dll | `t.me/s/<channel>` (halaman preview publik, tanpa login) | Di CLI & `/api/scan` (server); tidak bisa dari browser (CORS) |
| Instagram *(opsional, CLI saja)* | [instaloader](https://github.com/instaloader/instaloader) | Butuh login manual, berisiko kena rate-limit dari Meta |

### Notifikasi WhatsApp (CLI)

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
├── index.html                # Web app (dashboard + scan) — halaman utama di Vercel
├── api/scan.js                # Serverless Function: GET /api/scan (Blogger + Telegram)
├── lib/lomba-core.js          # Logika inti (filter, parsing tanggal, dedup) — dipakai api/scan.js
├── vercel.json                 # Konfigurasi Vercel (maxDuration fungsi, dst.)
├── .vercelignore                # Cegah file pribadi ikut ter-upload saat deploy dari CLI
├── package.json                 # Nol dependency npm — install instan
│
├── cari_lomba.py              # CLI Python: cari, filter, parse tanggal, dedup (paling lengkap)
├── kirim_info_lomba.py        # Kirim lomba baru ke WhatsApp (opsional, CLI)
├── config.yaml                 # Sumber & keyword untuk CLI
├── requirements.txt
│
├── wa_config.example.yaml     # Template config WhatsApp (aman di-commit)
├── wa_config.yaml              # Config WhatsApp asli kamu (di-gitignore & di-vercelignore)
├── demo/hasil-contoh.json     # Data contoh untuk coba index.html tanpa run apa pun
├── output/                     # Hasil export CLI (di-gitignore & di-vercelignore)
├── .claude/skills/cari-lomba/  # Skill Claude Code (/cari-lomba)
├── assets/                      # Aset gambar README
├── LICENSE
├── CONTRIBUTING.md
├── README.md                    # Versi Inggris
└── README.id.md                 # Versi Indonesia (file ini)
```

---

## ⚠️ Keterbatasan

- **Deadline tidak selalu ketemu.** Kalau tanggalnya cuma ada di gambar/infografis
  (bukan teks), kolom deadline akan kosong — cek langsung ke link yang diberikan.
- **`/api/scan` mengambil postingan terbaru per situs** (bukan per-keyword seperti CLI)
  supaya tetap cepat dan ringan dalam batas waktu serverless. Untuk cakupan paling
  lengkap (termasuk lomba lama yang jarang muncul di feed terbaru), pakai
  `python cari_lomba.py`.
- **Instagram/X** di luar akun yang dikonfigurasi belum bisa diotomatisasi stabil tanpa
  API berbayar, dan hanya tersedia lewat CLI (bukan bagian dari deployment Vercel).
- **Scan langsung di browser** (mode "Scan Blogger") adalah port JavaScript yang
  disederhanakan: tanpa retry otomatis, dan deduplikasi memakai perhitungan kemiripan
  judul yang lebih ringan (bukan `difflib` Python persis).

---

## 🤝 Kontribusi

Kontribusi apa pun — laporan bug, ide sumber/keyword baru, sampai pull request —
sangat diterima. Baca [`CONTRIBUTING.md`](CONTRIBUTING.md) untuk panduan lengkapnya,
termasuk area yang paling butuh bantuan.

Langkah singkat:

1. Fork repo ini & buat branch baru.
2. Untuk menambah sumber/keyword CLI, cukup edit [`config.yaml`](config.yaml). Untuk
   web app, selaraskan juga [`lib/lomba-core.js`](lib/lomba-core.js) dan `index.html`.
3. Buka Pull Request dengan penjelasan singkat kenapa perubahan itu diperlukan.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE) — bebas dipakai, dimodifikasi,
dan didistribusikan ulang, termasuk untuk keperluan komersial, selama menyertakan
notice lisensi aslinya.

---

## 🙏 Disclaimer

Tool ini melakukan scraping ringan terhadap situs publik (Blogger, Telegram) yang
memang menyediakan info lomba secara terbuka. Gunakan secara wajar supaya tidak
membebani server sumbernya — respons `/api/scan` sudah di-cache di CDN Vercel selama
30 menit untuk tujuan ini. Fitur Instagram bersifat opsional dan sepenuhnya menjadi
tanggung jawab pengguna terkait Ketentuan Layanan Meta.

<p align="center">Dibuat untuk membantu sesama pelajar &amp; mahasiswa menemukan info lomba lebih cepat. Selamat berkompetisi! 🚀</p>
