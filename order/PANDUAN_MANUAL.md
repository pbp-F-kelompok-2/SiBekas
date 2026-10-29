# Panduan Faris: Order, Integrasi, dan PWS

Panduan ini mengikuti pembagian tugas Faris pada halaman 11 PDF tugas: checkout,
alamat, ongkir RajaOngkir, pembayaran sesuai lingkup proyek, riwayat/detail/status,
pembatalan, integrasi anggota, dan deployment. SSO tetap menjadi pekerjaan modul
Profile/User. Pembayaran proyek tersedia sebagai COD saat ambil di kampus dan
simulasi akademik; belum ada penagihan atau pemindahan uang melalui payment gateway.

## 1. Jalankan dan periksa project

Di PowerShell, buka folder `SiBekas`, lalu gunakan Python virtual environment:

```powershell
.\.venv\bin\python.exe manage.py migrate
.\.venv\bin\python.exe manage.py check
.\.venv\bin\python.exe manage.py makemigrations --check --dry-run
.\.venv\bin\python.exe manage.py test
.\.venv\bin\python.exe manage.py collectstatic --noinput
.\.venv\bin\python.exe manage.py check_order_readiness
.\.venv\bin\python.exe manage.py runserver
```

Jika venv dibuat oleh Python Windows standar, gunakan `.venv\Scripts\python.exe`.
Jika belum memiliki venv, ikuti setup di README utama. Salin `.env.example` hanya
jika `.env` belum ada; pertahankan konfigurasi lokal yang sudah digunakan.

Migrasi `product/0002_alter_product_category.py` menyelaraskan kategori opsional
di model dan database. Jalankan migrasi baru ini pada database lokal maupun PWS.
Tidak perlu menghapus database atau mengulang migrasi awal.

## 2. Aktifkan ongkir RajaOngkir

Langkah ini memerlukan akun dan API key milik kelompok. Registrasi/aktivasi akun
serta pemilihan titik pengumpulan barang harus dilakukan pemilik akun.

1. Masuk ke dashboard RajaOngkir/Komerce dan ambil API key **Shipping Cost** yang
   mendukung metode **direct search**. Key untuk produk API lain belum tentu cocok.
2. Isi `RAJAONGKIR_API_KEY` di `.env` lokal atau environment PWS. Jangan masukkan
   key ke kode, frontend, README, atau Git.
3. Cari ID asal dengan perintah berikut; `RAJAONGKIR_ORIGIN_ID` boleh masih kosong:

   ```powershell
   .\.venv\bin\python.exe manage.py lookup_shipping_destination "Pondok Cina"
   ```

4. Perintah menampilkan ID dan alamat. Pilih baris yang sesuai lokasi titik
   pengumpulan sebenarnya di UI, bukan sekadar hasil pertama. Ulangi pencarian
   dengan kelurahan/kode pos bila lokasi belum tepat.
5. Masukkan ID tersebut ke `RAJAONGKIR_ORIGIN_ID`, lalu pilih kode kurir yang
   tersedia pada akun kelompok. Contoh konfigurasi tanpa secret:

   ```dotenv
   RAJAONGKIR_API_KEY=isi-key-pribadi-di-environment
   RAJAONGKIR_ORIGIN_ID=isi-id-hasil-pencarian
   RAJAONGKIR_COURIERS=jne:jnt:sicepat
   ORDER_ENABLE_DEMO_PAYMENT=True
   ```

6. Restart server lokal atau rebuild/restart deployment setelah mengganti environment.
7. Jalankan `python manage.py check_order_readiness --require-shipping`, kemudian
   uji checkout: pilih kurir, cari tujuan, pilih tujuan dan layanan. Periksa bahwa
   ongkir, estimasi, dan total berubah sesuai layanan.

Perintah readiness memeriksa kelengkapan konfigurasi, bukan validitas key atau
kuota layanan. Uji checkout live tetap diperlukan. Jika API gagal/tidak dikonfigurasi,
pengguna tetap dapat memilih ambil di kampus dengan COD. Tarif kurir tidak diganti
dengan angka contoh di aplikasi produksi.

API Shipping Cost menghitung tarif dan tidak memesan pengiriman. Kelompok tetap
perlu menyerahkan paket ke kurir serta memasukkan nomor resi sebenarnya. COD via
kurir tidak diaktifkan dalam implementasi ini.

Kontrak request mengikuti contoh cURL dan tabel parameter resmi:
[pencarian tujuan](https://www.rajaongkir.com/docs/shipping-cost/endpoint-rajaongkir-for-search-base/search-destination-rajaongkir)
dan [perhitungan tarif](https://www.rajaongkir.com/docs/shipping-cost/endpoint-rajaongkir-for-search-base/calculate-domestic-cost).

## 3. Siapkan petugas pesanan

Isi `ORDER_STAFF_USERNAME`, `ORDER_STAFF_EMAIL`, dan `ORDER_STAFF_PASSWORD` pada
environment privat. Jalankan `python manage.py bootstrap_order_staff`
di terminal PWS setelah deploy
untuk membuat akun aktif dengan `is_staff=True` dan `is_superuser=False`.
Kredensial yang dibuat untuk project ini disimpan pada file privat
`output/akun-petugas-sibekas.txt` di luar repository, dan konfigurasi lokal
privatnya berada pada `.env.pws` yang diabaikan Git.

Jika akun sudah ada, command tidak mengganti password atau hak akses. Username
yang dipakai pelanggan lain tidak akan dipromosikan menjadi petugas. Untuk
menjalankan perintah secara manual, gunakan terminal project SiBekas pada PWS.
Pada server lokal, isi environment yang sama lalu jalankan:

```powershell
.\.venv\bin\python.exe manage.py bootstrap_order_staff
```

Petugas masuk melalui **email** dan password akun SiBekas pada halaman login
biasa. Identitas email petugas dipakai sebagai login lokal; ini bukan akun SSO
baru atau pembuatan mailbox UI. `createsuperuser` hanya diperlukan jika kelompok
juga membutuhkan administrator Django dengan hak lebih luas.

Petugas membuka `/orders/`, memilih **Kelola semua pesanan**, lalu membuka detail:

- COD pickup: **Diproses** -> petugas **Tandai siap diambil** -> pembeli
  **Pesanan diterima** -> **Selesai**, pembayaran ditandai lunas.
- Kurir/simulasi: pembeli **Simulasikan pembayaran** -> petugas mengisi resi dan
  **Kirim pesanan** -> pembeli **Pesanan diterima**.
- Pembatalan tersedia sebelum dikirim/siap diambil. Stok dikembalikan satu kali;
  pembayaran simulasi yang sudah lunas ditandai dikembalikan.
- Setelah selesai, pembeli dapat menulis ulasan dari detail pesanan. Ulasan
  tampil di detail produk dan jumlahnya tersambung ke halaman profil.

Jangan menjadikan seluruh pengguna sebagai petugas. Gunakan akun petugas terpisah
untuk demonstrasi, agar alur pembeli dan petugas mudah diuji.

## 4. Pastikan data dan integrasi siap

`python manage.py check_order_readiness --strict` memerlukan database termigrasi,
minimal 50 produk, serta setidaknya satu petugas aktif. Tambahkan
`--require-shipping` bila demonstrasi mencakup ongkir live.

Jika katalog belum mencapai 50 produk, koordinasikan data dengan penanggung jawab
Product. Gunakan `python manage.py seed_products --skip-existing` untuk mengambil
data DummyJSON tanpa menimpa stok/perubahan produk yang sudah ada. Tanpa flag
tersebut, seeder tetap memiliki perilaku lama `update_or_create` yang bisa mereset
stok contoh yang sudah bertransaksi.

Set `DJANGO_SEED_INITIAL_PRODUCTS=True` pada environment, lalu jalankan
`python manage.py bootstrap_catalog` melalui tab **Terminal** PWS setelah deploy.
Hanya jika opsi itu aktif dan katalog belum mencapai 50 produk, seeder dipanggil
dengan `--skip-existing`. Set kembali ke `False` setelah data awal terisi bila
tidak diperlukan lagi. Pengisian katalog memerlukan akses internet ke DummyJSON.
PWS yang diperiksa tidak menjalankan tahap `release` dari Procfile; tahap itu
tetap dapat digunakan pada hosting lain yang mendukungnya.

Sebelum merge anggota, jalankan `git fetch origin`, periksa PR/perubahan masing-masing,
dan gabungkan melalui PR sesuai kesepakatan kelompok. Jangan mengganti perubahan
anggota dengan salinan folder lama. Sesudah konflik diselesaikan, ulangi seluruh
pemeriksaan pada langkah 1 dan uji alur pembelian sampai ulasan.

## 5. Konfigurasi dan deployment PWS

Project yang sudah terdaftar menggunakan alamat:
`https://faris-salman-sibekas.pws.cs.ui.ac.id/`.

Buka project yang benar di dashboard PWS, lalu tab **Environment/Environs**.
Gabungkan variabel berikut dengan konfigurasi database hosting yang sudah ada.
Jangan mengosongkan variabel database bawaan atau menyalin nilai contoh sebagai secret.

```dotenv
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=secret-acak-yang-kuat-dan-tetap
DJANGO_ALLOWED_HOSTS=faris-salman-sibekas.pws.cs.ui.ac.id
DJANGO_CSRF_TRUSTED_ORIGINS=https://faris-salman-sibekas.pws.cs.ui.ac.id
DATABASE_URL=URL-PostgreSQL-project-dari-hosting
ORDER_ENABLE_DEMO_PAYMENT=True
RAJAONGKIR_API_KEY=key-Shipping-Cost-kelompok
RAJAONGKIR_ORIGIN_ID=id-lokasi-asal-yang-sudah-dipilih
RAJAONGKIR_COURIERS=jne:jnt:sicepat
DJANGO_SEED_INITIAL_PRODUCTS=True
```

Gunakan secret stabil: menggantinya membatalkan sesi dan token checkout yang ada.
Untuk membuat secret lokal yang baru, gunakan
`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`,
lalu simpan hasilnya langsung di environment privat. Untuk reset password, lengkapi
`MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, dan `MAIL_FROM_EMAIL`.
Gmail memerlukan kredensial SMTP yang sesuai kebijakan akun, misalnya app password.

Setelah kode sudah diverifikasi dan disetujui untuk integrasi, workflow branch-nya:

```powershell
git switch feat/order-faris
git status
git add <file-perubahan-yang-sudah-ditinjau>
git commit -m "Complete order integration and deployment readiness"
git push origin feat/order-faris
```

Jika commit sudah dibuat/dipush, tidak perlu mengulang commit yang sama. Buat PR
ke `main` untuk peninjauan kelompok. PDF melarang push langsung ke `main`.
Deploy commit yang sudah dipilih dengan:

```powershell
git push pws HEAD:master
```

Remote `pws` harus menunjuk project kelompok yang benar. Jika diminta login,
gunakan **Project Credentials PWS**, bukan password SSO. Tidak perlu menyimpan
password di remote URL atau memasukkannya ke commit. Jangan memakai force push
untuk mengatasi riwayat deployment yang berbeda; periksa commit dan integrasinya dahulu.

PWS membuat image Docker dan pada deployment yang diperiksa tidak mengeksekusi
phase `release` dari `Procfile`. Setelah build **Successful** dan status
**Running**, buka tab **Terminal** project lalu jalankan:

```bash
python manage.py migrate --noinput
python manage.py bootstrap_catalog
python manage.py bootstrap_order_staff
python manage.py collectstatic --noinput
```

Perintah dapat dijalankan ulang: bootstrap mempertahankan produk dan akun yang
sudah tersedia. Setelah itu periksa kesiapan database produksi:

```bash
python manage.py check_order_readiness --deployment --require-shipping
```

Panduan platform: [tutorial deployment PWS dari PBP](https://pbp-fasilkom-ui.github.io/ganjil-2026/docs/tutorial-0).
Nama tab/fitur console dapat berbeda menurut versi dashboard.

## 6. Pemeriksaan manual setelah deployment

1. Buka `/health/`; harapkan HTTP 200 dan `{"status":"ok","database":"ok"}`.
   Kegagalan database menghasilkan HTTP 503 tanpa rincian kredensial.
2. Periksa katalog berisi minimal 50 produk dan aset CSS/JS termuat.
3. Login sebagai pembeli, tambah barang milik pengguna lain, cek jumlah serta
   subtotal, lalu checkout. Pastikan stok turun dan keranjang menjadi kosong.
4. Selesaikan satu pesanan pickup/COD memakai akun petugas dan pembeli.
5. Jika API key sudah aktif, selesaikan satu checkout kurir dengan tujuan nyata;
   cocokkan layanan, ongkir, berat, dan total. Simulasi pembayaran tetap tidak
   memindahkan uang nyata.
6. Batalkan pesanan yang belum dikirim dan pastikan stok kembali tanpa bertambah
   lagi saat tombol dikirim ulang.
7. Selesaikan pesanan, tulis ulasan, periksa tampilannya sebagai tamu pada produk,
   lalu periksa statistik pesanan/ulasan di profil.
8. Uji pengguna lain tidak dapat melihat/mengubah pesanan tersebut. Uji pembeli
   tidak dapat menandai kiriman sebagai dikirim.
9. Ulangi halaman checkout, riwayat, dan detail di layar ponsel sekitar 390 px.

Pengujian otomatis memakai database sementara; tes ongkir memakai respons mock.
Aktivasi API key, pemilihan lokasi asal sebenarnya, operasional paket/resi, dan
pemeriksaan tarif live tetap memerlukan pemilik akun/petugas kelompok.
