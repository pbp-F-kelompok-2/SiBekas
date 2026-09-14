# SiBekas

## Deskripsi Aplikasi

**SiBekas** adalah platform marketplace barang *preloved* khusus mahasiswa Universitas Indonesia (UI). Aplikasi ini memungkinkan mahasiswa UI untuk membeli dan menjual barang yang masih layak digunakan dalam lingkungan kampus.

Pengguna dapat melakukan autentikasi menggunakan **SSO UI**, melihat dan mencari produk berdasarkan kategori, mengelola profil, memasukkan barang ke keranjang, melakukan transaksi pembelian, serta memberikan ulasan terhadap barang yang telah dibeli.

SiBekas hadir untuk mendukung penggunaan kembali barang dan mendorong kebiasaan **conscious shopping** di lingkungan mahasiswa UI.

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
`-`

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
`-`

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
`-`

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
`-`

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
`-`

---

## Public API / Mock API

<!-- Akan ditentukan kemudian. -->

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
