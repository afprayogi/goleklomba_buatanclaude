# Berkontribusi ke Cari Lomba

Makasih sudah tertarik bantu proyek ini — kontribusi sekecil apa pun (laporan bug,
saran sumber baru, sampai pull request) sangat dihargai. 🙌

## Cara paling mudah berkontribusi (tanpa nulis kode)

Sebagian besar kebutuhan sudah bisa dipenuhi cukup dengan **edit `config.yaml`**,
tanpa sentuh `cari_lomba.py` sama sekali:

- **Tambah situs Blogger baru** → tambahkan entri di `sources.blogger_sites`
  (perlu situs berbasis Blogger dengan endpoint `/feeds/posts/default`).
- **Tambah channel Telegram publik** → tambahkan nama channel (tanpa `@`) di
  `sources.telegram_channels`.
- **Tambah/ubah keyword filter** → edit `keywords.strong` / `keywords.weak` /
  `keywords.exclude`. Baca komentar di `config.yaml` untuk memahami bedanya
  strong vs weak sebelum menambah, supaya filter tidak jadi kebanjiran hasil
  yang tidak relevan.

Kalau kamu menemukan sumber baru atau keyword yang perlu ditambah tapi tidak
yakin cara editnya, buka **issue** saja dan jelaskan sumbernya — biar dibantu.

## Melaporkan bug

Sertakan sebisa mungkin:

1. Perintah yang dijalankan (mis. `python cari_lomba.py --days 30`).
2. Pesan error lengkap dari terminal (`stdout`/`stderr`).
3. Versi Python (`python --version`) dan OS yang dipakai.

Jangan lampirkan isi `wa_config.yaml` kamu apa adanya di issue publik — nomor
WhatsApp adalah data pribadi. Sensor dulu nomornya kalau memang perlu ditunjukkan.

## Mengajukan Pull Request

1. Fork & buat branch baru dari `main`.
2. Jalankan script secara lokal dan pastikan tidak ada error sebelum membuka PR:
   ```bash
   pip install -r requirements.txt
   python cari_lomba.py --skip-check --format table
   ```
3. Ikuti gaya kode yang sudah ada (type hint, docstring singkat, komentar hanya
   untuk hal yang tidak jelas dari kodenya sendiri).
4. Jelaskan di deskripsi PR: masalah apa yang diperbaiki / fitur apa yang
   ditambah, dan kenapa.
5. Untuk perubahan pada logika parsing tanggal (`find_deadline`/`find_start_date`)
   atau filter relevansi (`is_relevant`), tambahkan contoh teks yang jadi alasan
   perubahan itu di deskripsi PR — bagian ini sensitif terhadap regresi diam-diam.

## Area yang paling butuh bantuan

- Menambah dukungan sumber non-Blogger (situs dengan HTML statis, butuh parser
  khusus per situs).
- Memperbaiki pola tanggal Bahasa Indonesia yang belum terbaca (`BULAN_PATTERN`,
  `DATE_RANGE_TAIL_RE`, dll di `cari_lomba.py`).
- Menambah fitur kecil di [`index.html`](index.html) — semuanya vanilla
  HTML/CSS/JS tanpa build step, jadi cukup edit filenya langsung dan refresh
  browser untuk lihat hasilnya.
- Memperbaiki/menambah logika di [`lib/lomba-core.js`](lib/lomba-core.js) —
  dipakai oleh endpoint server [`api/scan.js`](api/scan.js). Kalau kamu ubah
  logika filter/parsing tanggal, cek juga apakah salinannya di dalam
  `index.html` (bagian scan Blogger browser) perlu diselaraskan.

## Kode etik

Bersikap sopan dan konstruktif. Proyek ini dibuat untuk membantu sesama pelajar/
mahasiswa menemukan info lomba lebih cepat — jaga semangat itu di setiap diskusi.
