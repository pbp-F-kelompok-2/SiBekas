# Mengaktifkan ongkir RajaOngkir di SiBekas

Kode pencarian tujuan, perhitungan tarif, pilihan layanan, dan validasi ongkir
sudah tersedia. Yang perlu disiapkan pemilik akun adalah API key dan lokasi asal.
DummyJSON tetap menjadi sumber katalog produk dan tidak menghitung ongkir.

1. Daftar atau masuk ke akun [RajaOngkir](https://www.rajaongkir.com/). Selesaikan
   verifikasi akun jika diminta. Pilih produk **Shipping Cost**, dengan akses
   metode **Direct Search** sesuai paket akun. Jangan memakai key dari produk
   pengiriman/produk API lain.
2. Salin API key Shipping Cost ke environment privat lokal `.env` dan ke project
   `faris.salman/sibekas` pada **PWS -> Environs**:

   ```dotenv
   RAJAONGKIR_API_KEY=key-pribadi-anda
   RAJAONGKIR_COURIERS=jne:jnt:sicepat
   ORDER_ENABLE_DEMO_PAYMENT=True
   ```

   Kode kurir harus sesuai akses akun. Jangan commit key ke Git atau menaruhnya
   pada JavaScript/browser. Nama key tidak perlu diubah di kode.
3. Cari ID asal dari titik pengumpulan barang yang benar. Di terminal PWS:

   ```bash
   python manage.py lookup_shipping_destination "Pondok Cina"
   ```

   Untuk PowerShell lokal gunakan:

   ```powershell
   .\.venv\bin\python.exe manage.py lookup_shipping_destination "Pondok Cina"
   ```

   Perintah ini hanya memerlukan API key; ID asal boleh belum diisi. Hasil berisi
   ID dan alamat. Pilih lokasi yang cocok dengan kelurahan/kecamatan/kode pos
   titik pengumpulan kelompok. Jangan memakai ID contoh atau hasil pertama
   tanpa memeriksa alamatnya.
4. Isi `RAJAONGKIR_ORIGIN_ID` dengan ID yang dipilih pada environment lokal/PWS.
   Simpan perubahan dan redeploy/restart aplikasi agar proses server memuatnya.
5. Periksa konfigurasi:

   ```bash
   python manage.py check_order_readiness --require-shipping
   ```

   Ini memeriksa kelengkapan konfigurasi. Validitas key, kuota, dan layanan kurir
   tetap perlu diuji dengan request API sebenarnya.
6. Login sebagai pembeli, tambahkan produk ke keranjang, buka checkout, pilih
   **Kirim dengan kurir**, cari tujuan, pilih tujuan lalu layanan. Periksa
   ongkir, estimasi, total berat, dan total pembayaran. Tarif berlaku 15 menit.
   Jika keranjang berubah atau tarif kedaluwarsa, hitung ulang.
7. Buat pesanan dan gunakan **Simulasikan pembayaran**. Petugas mengisi nomor
   resi ketika menandai pesanan dikirim. Pembeli mengonfirmasi penerimaan setelah
   barang diterima.

Pembayaran simulasi tidak memindahkan uang. API Shipping Cost menghitung tarif;
pemesanan paket dan penyerahan barang ke kurir dilakukan petugas secara terpisah.
COD pada aplikasi tersedia untuk pengambilan di kampus. Jika key belum siap,
alur pickup/COD tetap dapat digunakan.

| Masalah | Pemeriksaan |
| --- | --- |
| Kurir belum tersedia | Periksa API key, ID asal positif dari direct search, daftar kurir, dan flag pembayaran simulasi. |
| Key ditolak | Pastikan key untuk Shipping Cost dan akses akun sudah aktif. Periksa dashboard/kuota akun. |
| Tujuan tidak ditemukan | Coba kelurahan, kecamatan, atau kode pos yang lebih tepat. |
| Tarif kosong | Ganti layanan/kurir yang tersedia untuk rute tersebut; periksa berat produk. |
| Ongkir kedaluwarsa | Cari dan pilih tujuan serta layanan kembali sebelum checkout. |

Kontrak request mengikuti contoh cURL/tabel parameter resmi:
[pencarian tujuan](https://www.rajaongkir.com/docs/shipping-cost/endpoint-rajaongkir-for-search-base/search-destination-rajaongkir)
dan [perhitungan tarif](https://www.rajaongkir.com/docs/shipping-cost/endpoint-rajaongkir-for-search-base/calculate-domestic-cost).
