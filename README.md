# SiBekas

## Deskripsi Aplikasi

**SiBekas** adalah platform marketplace barang *preloved* khusus mahasiswa Universitas Indonesia (UI). Aplikasi ini memungkinkan mahasiswa UI untuk membeli dan menjual barang yang masih layak digunakan dalam lingkungan kampus.

Pengguna dapat melakukan autentikasi menggunakan **SSO UI**, melihat dan mencari produk berdasarkan kategori, mengelola profil, memasukkan barang ke keranjang, melakukan transaksi pembelian, serta memberikan ulasan terhadap barang yang telah dibeli.

SiBekas hadir untuk mendukung penggunaan kembali barang dan mendorong kebiasaan **conscious shopping** di lingkungan mahasiswa UI.

---

## Menjalankan Project

### Prasyarat

- Python 3.12
- Git

### Setup pertama kali

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

Jika Python Windows Anda berasal dari MSYS/UCRT dan virtual environment membuat
folder `.venv/bin` (bukan `.venv/Scripts`), aktifkan dengan:

```powershell
.\.venv\bin\Activate.ps1
```

Untuk macOS atau Linux, aktifkan virtual environment dengan:

```bash
source .venv/bin/activate
```

Buka `http://127.0.0.1:8000/`. Endpoint `http://127.0.0.1:8000/health/`
digunakan untuk memastikan aplikasi dan database siap.

> Jangan commit `.env`, database lokal, atau virtual environment. Ketiganya sudah
> dilindungi oleh `.gitignore`; bagikan perubahan konfigurasi melalui
> `.env.example`.

### Pemeriksaan sebelum push

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

## Struktur Project

```text
SiBekas/
├── sibekas/          # settings, URL utama, ASGI, dan WSGI
├── product/          # katalog, kategori, filter, dan detail produk
├── profiles/         # data dan personalisasi pengguna
├── cart/             # keranjang belanja
├── order/            # checkout, pembayaran, dan transaksi
├── review/           # rating dan ulasan
├── static/           # aset CSS/JS/gambar sumber
├── templates/        # template global
├── tests/            # tes integrasi fondasi project
├── .env.example      # contoh konfigurasi tanpa secret
├── manage.py
└── requirements.txt
```

Semua app utama telah didaftarkan di `INSTALLED_APPS` dan memiliki namespace URL
sendiri:

| App | URL awal | Namespace |
|---|---|---|
| Product | `/products/` | `product` |
| Profile / User | `/profile/` | `profile` |
| Cart | `/cart/` | `cart` |
| Order / Transaction | `/orders/` | `order` |
| Review | `/reviews/` | `review` |

### Environment dan database

Pengembangan lokal menggunakan SQLite secara default. Deployment dapat memakai
PostgreSQL cukup dengan mengubah `DATABASE_URL`, tanpa mengubah `settings.py`.
Server PostgreSQL perlu menyediakan library client `libpq` untuk driver `psycopg`.

| Variabel | Kegunaan | Nilai lokal |
|---|---|---|
| `DJANGO_SECRET_KEY` | Kunci kriptografi Django | kunci development dari `.env.example` |
| `DJANGO_DEBUG` | Mode debug | `True` |
| `DJANGO_ALLOWED_HOSTS` | Host yang diizinkan, dipisahkan koma | `localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origin HTTPS tepercaya, dipisahkan koma | kosong |
| `DATABASE_URL` | Koneksi database | `sqlite:///db.sqlite3` |

Saat deployment, gunakan `DJANGO_DEBUG=False`, secret key yang kuat, host/origin
produksi, dan `DATABASE_URL` PostgreSQL dari penyedia hosting.

---

## Anggota Kelompok

| No. | Nama | NPM |
|---|---|---|
| 1 | Alfan Kurnia Karim | 2506537814 |
| 2 | Faris Salman Azhari | 2506615223 |
| 3 | Jehezkiel Jefferson I Latupeirissa | 2506611156 |
| 4 | Rachelin Miyuki Hendratmo | 2506536553 |
| 5 | Rheza Abdilla | 2506612184 |

---

## Peran Pengguna

Mahasiswa UI menjadi pengguna utama aplikasi dan melakukan autentikasi menggunakan **SSO UI**. Setiap pengguna dapat berperan sebagai **Penjual** maupun **Pembeli**.

### Penjual

Penjual adalah mahasiswa UI yang menjual barang *preloved* melalui aplikasi. Penjual dapat:

- Menambahkan listing barang.
- Melihat barang yang telah dipublikasikan.
- Mengubah informasi barang.
- Menghapus listing barang.
- Mengelola barang yang ditawarkan kepada pengguna lain.

### Pembeli

Pembeli adalah mahasiswa UI yang mencari dan membeli barang *preloved*. Pembeli dapat:

- Mencari dan melihat barang.
- Melihat detail produk.
- Menggunakan filter dan kategori produk.
- Menambahkan produk ke keranjang.
- Melakukan pembelian.
- Melihat riwayat transaksi.
- Memberikan ulasan dan rating setelah transaksi.

---

## Daftar Modul

### 1. Product

Modul **Product** digunakan untuk mengelola data barang yang dijual di dalam aplikasi.

**Cakupan fitur:**

- Kategori produk.
- Detail barang.
- Filter produk.

**Operasi CRUD:**

| Operasi | Deskripsi |
|---|---|
| Create | Menambahkan data produk |
| Read | Melihat daftar produk, kategori, filter, dan detail produk |
| Update | Mengubah data produk |
| Delete | Menghapus data produk |

**Penanggung Jawab:**  
`Jehezkiel Jefferson I`

---

### 2. Profile / User

Modul **Profile / User** digunakan untuk mengelola data dan personalisasi pengguna.

**Cakupan fitur:**

- Detail pengguna.
- Personalisasi profil.

**Operasi CRUD:**

| Operasi | Deskripsi |
|---|---|
| Create | Membuat data profil pengguna |
| Read | Melihat data profil pengguna |
| Update | Mengubah data profil dan personalisasi |
| Delete | Menghapus data pengguna |

**Penanggung Jawab:**  
`Rachelin Miyuki`

---

### 3. Cart

Modul **Cart** digunakan untuk mengelola barang yang ingin dibeli sebelum proses transaksi dilakukan.

**Cakupan fitur:**

- Menambahkan produk ke keranjang.
- Melihat isi keranjang.
- Mengubah jumlah barang.
- Menghapus produk dari keranjang.

**Operasi CRUD:**

| Operasi | Deskripsi |
|---|---|
| Create | Menambahkan produk ke keranjang |
| Read | Melihat isi keranjang |
| Update | Mengubah jumlah barang dalam keranjang |
| Delete | Menghapus produk dari keranjang |

**Penanggung Jawab:**  
`Rheza Abdilla`

---

### 4. Order / Transaction

Modul **Order / Transaction** digunakan untuk menangani proses pembelian dan transaksi pengguna.

**Cakupan fitur:**

- Checkout.
- Lokasi pengiriman.
- Pembayaran.
- Riwayat transaksi.

**Operasi CRUD:**

| Operasi | Deskripsi |
|---|---|
| Create | Membuat order atau transaksi |
| Read | Melihat detail dan riwayat order atau transaksi |
| Update | Mengubah status order atau transaksi |
| Delete | Membatalkan order atau transaksi |

**Penanggung Jawab:**  
`Faris Salman Azhari`

---

### 5. Review

Modul **Review** digunakan untuk memberikan ulasan dan rating terhadap barang yang telah dibeli. Fitur ini bertujuan membantu meningkatkan kredibilitas penjual.

Ulasan akan tersedia pada **menu profil** serta dapat diakses melalui **bar navigasi**.

**Operasi CRUD:**

| Operasi | Deskripsi |
|---|---|
| Create | Menambahkan ulasan dan rating |
| Read | Melihat ulasan dan rating |
| Update | Mengubah ulasan dan rating |
| Delete | Menghapus ulasan dan rating |

**Penanggung Jawab:**  
`Alfan Kurnia Karim`

---

## Public API / Mock API

### RajaOngkir API

SiBekas menggunakan **RajaOngkir API** untuk mendukung proses pengiriman barang antara penjual dan pembeli. API ini menyediakan data lokasi serta informasi ongkos kirim dari berbagai layanan ekspedisi di Indonesia.

**Kegunaan:**

- Mencari dan memvalidasi lokasi asal serta tujuan pengiriman.
- Menghitung ongkos kirim berdasarkan lokasi, berat barang, dan kurir yang dipilih.
- Menampilkan pilihan layanan kurir, biaya, dan estimasi waktu pengiriman pada proses checkout.
- Membantu pembeli membandingkan opsi pengiriman sebelum membuat pesanan.

Dokumentasi resmi: [RajaOngkir API](https://www.rajaongkir.com/docs/shipping-cost)

### DummyJSON API

SiBekas menggunakan **DummyJSON API** sebagai sumber data awal (*placeholder*) untuk katalog produk. Sebanyak minimal 50 data produk akan diambil dari endpoint produk DummyJSON, disesuaikan dengan skema data SiBekas, lalu di-*seed* dan disimpan ke database aplikasi sebelum situs web di-*deploy*.

**Kegunaan:**

- Menyediakan minimal 50 produk awal agar katalog tidak kosong saat aplikasi pertama kali dijalankan.
- Menyediakan data contoh berupa nama, deskripsi, kategori, harga, rating, serta gambar produk.
- Membantu pengembangan dan pengujian fitur katalog, pencarian, filter, pagination, dan detail produk.
- Menjadi data *placeholder* sebelum tersedia cukup banyak listing asli dari mahasiswa UI.

Endpoint yang digunakan: [`https://dummyjson.com/products?limit=50`](https://dummyjson.com/products?limit=50)

Data dari DummyJSON hanya digunakan sebagai data awal. Operasi CRUD untuk listing produk, keranjang, transaksi, dan ulasan tetap dilakukan dan disimpan melalui database internal SiBekas.

Dokumentasi resmi: [DummyJSON Products API](https://dummyjson.com/docs/products)

---

## Ringkasan Fitur Utama

- Autentikasi mahasiswa menggunakan SSO UI.
- Marketplace barang *preloved* khusus mahasiswa UI.
- Pencarian, kategori, filter, dan detail produk.
- Pengelolaan profil pengguna.
- Keranjang belanja.
- Checkout dan transaksi pembelian.
- Riwayat transaksi.
- Rating dan review setelah pembelian.
- Dukungan bagi pengguna untuk berperan sebagai penjual maupun pembeli.

---

## Tujuan Proyek

Proyek ini bertujuan membangun platform yang memudahkan mahasiswa Universitas Indonesia untuk memperjualbelikan barang *preloved* secara lebih terpusat sekaligus mendukung penggunaan kembali barang dan kebiasaan **conscious shopping** di lingkungan kampus.
