---
name: cari-lomba
description: Cari info lomba renewable energy / teknik elektro / inovasi teknologi dari kabarlomba.com, ajanglomba.com, birulangit.id, dan channel Telegram info lomba, lengkap dengan deadline pendaftaran dan tanggal pelaksanaan. Gunakan saat user minta dicarikan lomba, dicek deadline lomba, atau update lomba terbaru.
---

# Cari Lomba

Skill ini menjalankan `cari_lomba.py` di root project ini untuk mengambil dan
memfilter info lomba dari beberapa sumber (lihat `README.md` untuk detail sumber
dan cara kerja filter).

## Langkah

1. Jalankan script dari root project ini:
   ```bash
   python cari_lomba.py --format json --output output/hasil.json
   ```
   Kalau user menyebut rentang waktu tertentu (mis. "bulan ini", "30 hari ke depan"),
   tambahkan `--days N` yang sesuai. Kalau user minta keyword tambahan yang tidak ada
   di `config.yaml`, tambahkan `--keyword "..."` (bisa diulang untuk lebih dari satu).

2. Baca `output/hasil.json`, lalu rangkum ke user dalam bahasa biasa (bukan dump JSON
   mentah), urut berdasarkan deadline paling dekat. Untuk tiap lomba tampilkan:
   judul, deadline pendaftaran, tanggal pelaksanaan (kalau ada), sumber, dan link.

3. Kalau `deadline` kosong untuk suatu lomba, bilang terus terang bahwa tanggalnya
   tidak berhasil terbaca otomatis dari sumbernya — jangan menebak-nebak tanggal.

4. Kalau hasil kosong atau terlalu sedikit, cek `stderr` script untuk error koneksi
   dulu sebelum menyimpulkan memang tidak ada lomba yang cocok.

## Menyesuaikan kriteria

Kalau user minta ubah kriteria pencarian secara permanen (tambah/kurang keyword,
tambah sumber Blogger baru, tambah channel Telegram), edit `config.yaml` langsung —
jangan ubah `cari_lomba.py`. Lihat komentar di `config.yaml` untuk struktur `strong`
vs `weak` keyword.

Kalau user minta cek satu link/postingan spesifik (mis. dari Instagram yang belum
diotomatisasi, atau share link manual), baca link itu langsung (WebFetch/browser)
alih-alih lewat script ini.
