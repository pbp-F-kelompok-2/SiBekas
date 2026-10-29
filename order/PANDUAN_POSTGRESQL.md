# Menyiapkan database persisten untuk PWS

Pada pemeriksaan 29 Oktober 2026, project SiBekas memakai SQLite di
`/app/db.sqlite3`, tanpa volume khusus `/app`/data yang terlihat di container.
Belum ada connection string PostgreSQL. Data SQLite tersebut belum bisa dianggap
aman terhadap penggantian container/redeploy. Jangan menganggap seed katalog
dan pembuatan ulang akun petugas sebagai penyimpanan riwayat transaksi.

Koneksi PostgreSQL harus berasal dari database milik kelompok atau penyedia yang
Anda kelola. Kode Django sudah mendukungnya melalui `DATABASE_URL`.

## Pilihan konektor Neon

Pasang dan hubungkan integrasi Neon ke akun Anda. Sesudah koneksi terkonfirmasi,
agent dapat membantu membuat database khusus SiBekas serta mengatur koneksinya
ke PWS. Saran integrasi saja belum membuat akun, database, atau koneksi aktif.

## Menyiapkan secara manual

1. Masuk/daftar di [Neon Console](https://console.neon.tech/) atau penyedia
   PostgreSQL yang disepakati kelompok. Tinjau ketentuan dan paket akun sendiri.
2. Buat project/database khusus `sibekas`. Pilih region yang sesuai dan simpan
   kredensial database pada penyimpanan privat.
3. Dari menu **Connect**, salin connection string PostgreSQL. Pertahankan opsi
   TLS seperti `sslmode=require` yang diberikan penyedia.
4. Tambahkan ke file lokal privat `SiBekas/.env.pws`:

   ```dotenv
   DATABASE_URL=postgresql://user:password@hostname/database?sslmode=require
   ```

   Gunakan nilai sebenarnya dari provider; baris di atas hanya contoh struktur.
   File `.env.pws` diabaikan Git dan tidak dimuat otomatis sebagai `.env` lokal.
   Jangan menyalin connection string ke README atau mengirim password di chat.
5. Pada PWS project `faris.salman/sibekas`, tambahkan `DATABASE_URL` melalui
   **Environs**. Pertahankan environment lain yang sudah ada. Jangan mengganti
   secret Django hanya untuk mengganti database.
6. Pastikan `DJANGO_SEED_INITIAL_PRODUCTS=True` serta ketiga `ORDER_STAFF_*`
   sudah tersedia di environment privat PWS, kemudian redeploy commit terbaru.
   Release menjalankan migrasi, mengisi katalog dari DummyJSON jika dibutuhkan,
   dan membuat akun petugas bila belum ada.
7. Jalankan di terminal PWS:

   ```bash
   python manage.py check_order_readiness --deployment
   ```

   Engine harus PostgreSQL, migrasi selesai, katalog minimal 50 produk, dan
   petugas aktif tersedia. Tambahkan `--require-shipping` setelah RajaOngkir siap.
8. Verifikasi akun petugas dan katalog tetap ada setelah redeploy berikutnya.
   Jika SQLite sementara sudah memiliki pesanan/pengguna lain, ekspor dan migrasi
   data lebih dahulu; jangan berpindah database dengan mengabaikan data lama.

Dokumentasi resmi: [Neon Console](https://neon.com/docs/get-started/signing-up)
dan [connection string PostgreSQL](https://neon.com/docs/connect/connect-from-any-app).
