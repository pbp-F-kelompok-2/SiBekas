# SiBekas — Marketplace Preloved Mahasiswa UI
> **Platform Marketplace Barang Preloved Berkelanjutan Khusus Mahasiswa Universitas Indonesia**  
> *Pemrograman Berbasis Platform (CSGE602022) — Gasal 2026/2027*  
> *Fakultas Ilmu Komputer, Universitas Indonesia*

[![Deploy PWS](https://img.shields.io/badge/Deploy-PWS%20Fasilkom%20UI-10b981?style=for-the-badge&logo=django)](https://faris-salman-sibekas.pws.cs.ui.ac.id/)
[![Figma Design](https://img.shields.io/badge/Figma-Design%20System-f24e1e?style=for-the-badge&logo=figma)](https://www.figma.com/design/sibekas-preloved-ui-pbp)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776ab?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django 5.x](https://img.shields.io/badge/Django-5.x-092e20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-Responsive-38bdf8?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

---

## 📌 Tautan Penting Proyek
- **Tautan Deployment PWS (Live Web)**: [https://faris-salman-sibekas.pws.cs.ui.ac.id/](https://faris-salman-sibekas.pws.cs.ui.ac.id/)
- **Tautan Desain Figma (UI/UX Prototype & Design System)**: [https://www.figma.com/design/sibekas-preloved-ui-pbp](https://www.figma.com/design/sibekas-preloved-ui-pbp)
- **Dokumentasi Public API (DummyJSON)**: [https://dummyjson.com/docs/products](https://dummyjson.com/docs/products)

---

## 📖 Deskripsi Aplikasi & Latar Belakang

**SiBekas** (*Sistem Informasi Barang Bekas*) adalah platform marketplace sirkular khusus civitas akademika Universitas Indonesia yang hadir di bawah naungan tema **Sustainable Living** (sub-tema: *Slow Fashion, Waste Management, & Conscious Shopping*).

Setiap pergantian tahun ajaran baru dan kelulusan, ribuan mahasiswa UI menghadapi masalah penumpukan barang kebutuhan kuliah (buku teks perkuliahan, perlengkapan kos, kalkulator saintifik, pakaian seminar/sidang, hingga perangkat elektronik pendukung) yang seringkali hanya dibuang atau terbengkalai. Di sisi lain, mahasiswa baru dan mahasiswa aktif senantiasa mencari barang layak pakai dengan harga terjangkau.

SiBekas menyelesaikan persoalan ini dengan menyediakan wadah transaksi yang aman, terpercaya, dan terpusat di lingkungan kampus:
- **Pengurangan Jejak Karbon & Sampah Kampus**: Memperpanjang siklus hidup barang (*reuse & circular economy*) sehingga meminimalkan limbah kosan dan konsumerisme berlebih.
- **Sistem Serah Terima Kampus Terpercaya**: Mendukung metode serah terima langsung di titik temu kampus UI (seperti Kantin Fasilkom, Perpustakaan Pusat UI, atau Halte Bikun) dengan opsi Cash-on-Delivery (COD) maupun pembayaran simulasi akademik tanpa perantara biaya ekspedisi yang mahal.
- **Fondasi Web Service Mobile-Ready**: Dirancang dengan pola Model-View-Template (MVT) Django yang bersih dan endpoint JSON asinkron yang siap dihubungkan dengan aplikasi mobile Flutter pada Proyek Akhir Semester.

---

## 👥 Anggota Kelompok & Pembagian Modul

| No. | Nama Mahasiswa | NPM | Modul Utama | Tanggung Jawab Modul | Branch Git |
|:---:|:---|:---:|:---|:---|:---|
| 1 | **Jehezkiel Jefferson I Latupeirissa** | 2506611156 | **Product** | Katalog produk preloved, kategori dinamis, multi-filter (harga, kondisi, status), live search, CRUD produk penjual, dan seeder 50+ data DummyJSON. | `feat/product-jehezkiel` |
| 2 | **Rachelin Miyuki Hendratmo** | 2506536553 | **Profile / User** | Manajemen profil pengguna, autentikasi lokal akun UI (`@ui.ac.id`), personalisasi data, riwayat aktivitas, bookmark/wishlist favorit, dan perlindungan penghapusan akun. | `feat/profile-rachelin` |
| 3 | **Rheza Abdilla** | 2506612184 | **Cart & Shared Templates** | Keranjang belanja multi-item, pembaruan kuantitas asinkron, perhitungan subtotal otomatis, struktur template bersama (`base.html`, `navbar.html`, `footer.html`), dan styling responsif. | `feat/cart-rheza` |
| 4 | **Faris Salman Azhari** | 2506615223 | **Order / Transaction & Integration** | Alur checkout serah terima kampus, validasi data transaksi, pembayaran COD/simulasi, riwayat pesanan, pembatalan pesanan aman, portal petugas pesanan kampus, integrasi monolit, dan deployment PWS. | `feat/order-faris` |
| 5 | **Alfan Kurnia Karim** | 2506537814 | **Review & Design System** | Ulasan dan rating (1-5 bintang) khusus pembeli terverifikasi (*verified purchase*), CRUD ulasan, rekapitulasi rating pada katalog dan profil, standardisasi warna brand eco-green, dan Dark Mode toggle. | `feat/review-alfan` |

---

## 👤 Peran Pengguna (User Roles)

1. **Mahasiswa Pembeli (Buyer)**:
   - Menjelajahi katalog barang dengan filter kategori, kondisi, dan rentang harga.
   - Menyimpan barang ke daftar favorit (*wishlist*).
   - Memasukkan produk ke keranjang belanja dan mengatur kuantitas.
   - Melakukan checkout dengan penentuan titik temu di kampus UI.
   - Memantau status pesanan hingga barang diterima.
   - Memberikan ulasan dan rating pada barang yang transaksinya telah berstatus *COMPLETED*.
2. **Mahasiswa Penjual (Seller)**:
   - Mendaftarkan barang preloved yang ingin dijual lengkap dengan foto, deskripsi, harga, dan kondisi.
   - Mengelola (*update/delete*) listing barang miliknya sendiri (dilindungi otorisasi kepemilikan ketat).
   - Memantau barang yang laku terjual dan melihat reputasi rating dari para pembeli.
3. **Petugas Kampus / Admin (Staff)**:
   - Memantau seluruh pesanan yang sedang diproses.
   - Menandai pesanan telah disiapkan dan siap diserahterimakan di titik temu kampus (`SHIPPED`).
   - Mengelola data master aplikasi melalui portal Django Admin.

---

## 📦 Rincian 5 Modul SiBekas (CRUD Implementation)

### 1. Modul Product (Jehezkiel Jefferson)
- **Create**: Formulir penambahan produk oleh penjual login dengan validasi harga positif dan stok minimal 1.
- **Read**: Katalog produk publik dengan pagination yang mempertahankan seluruh query filter (`q`, `category`, `condition`, `min_price`, `max_price`, `sort`), serta halaman detail produk lengkap dengan reputasi penjual dan ulasan pembeli.
- **Update**: Penjual dapat mengedit informasi harga, kondisi, deskripsi, dan foto produk miliknya.
- **Delete**: Penjual dapat menghapus listing produk. Akses pengguna lain ditolak dengan pesan HTTP 403 Forbidden.

### 2. Modul Profile / User (Rachelin Miyuki)
- **Create**: Pendaftaran akun mahasiswa menggunakan email berdomain UI (`@ui.ac.id` / `@alumni.ui.ac.id`).
- **Read**: Halaman profil pribadi yang menampilkan ringkasan data diri, riwayat listing, daftar barang favorit, serta agregat statistik total pesanan dan ulasan.
- **Update**: Pembaruan biodata, nomor WhatsApp, fakultas, dan avatar melalui modal profil.
- **Delete**: Penonaktifan akun yang aman dari crash `ProtectedError` pada pesanan tersimpan, menjamin integritas riwayat transaksi pembeli.

### 3. Modul Cart (Rheza Abdilla)
- **Create**: Penambahan barang ke keranjang belanja dengan feedback visual instan.
- **Read**: Tampilan keranjang belanja responsif yang merinci item, harga satuan, subtotal, dan kuantitas.
- **Update**: Penyesuaian kuantitas barang secara asinkron (AJAX) dengan pembatasan stok real-time.
- **Delete**: Penghapusan item individual dari keranjang belanja secara instan.

### 4. Modul Order / Transaction (Faris Salman Azhari)
- **Create**: Formulir checkout cerdas yang memvalidasi ketersediaan stok produk secara atomik (`select_for_update`) dan menetapkan titik temu serah terima di lingkungan kampus UI tanpa biaya ongkos kirim.
- **Read**: Riwayat transaksi pesanan pembeli dan halaman faktur detail (*invoice*) yang mencatat setiap peristiwa status (`OrderEvent`).
- **Update**: Pembeli dapat menyelesaikan pembayaran simulasi; petugas kampus dapat memperbarui status pesanan menjadi `SHIPPED` atau `COMPLETED`.
- **Delete**: Pembatalan pesanan yang masih berstatus `PENDING` oleh pembeli, yang secara otomatis mengembalikan stok barang ke etalase.

### 5. Modul Review (Alfan Kurnia Karim)
- **Create**: Formulir ulasan bintang interaktif (1-5) dan komentar teks (maksimal 500 karakter). Fitur ini memiliki verifikasi ketat: hanya pembeli yang telah menyelesaikan transaksi pesanan (`status=completed`) yang berhak menuliskan ulasan.
- **Read**: Menampilkan daftar ulasan pembeli dan rata-rata rating bintang pada detail produk dan tab profil.
- **Update**: Penulis ulasan dapat merevisi ulasan dan rating miliknya (otomatis ditandai *Diedit*).
- **Delete**: Penulis ulasan dapat menghapus ulasan buatannya sendiri.

---

## 🌐 Public API Integration (DummyJSON Products API)

Sesuai ketentuan silabus penugasan, aplikasi terintegrasi dengan **Public API DummyJSON Products** (`https://dummyjson.com/products?limit=60`) sebagai penyedia data katalog awal:
- **Seeder Otomatis (`seed_products`)**: Perintah manajemen `python manage.py seed_products` mengambil 60 data produk awal dari API publik DummyJSON, mengonversi kurs mata uang menjadi Rupiah yang terjangkau bagi mahasiswa, memetakan kategori ke dalam Bahasa Indonesia baku (*Kecantikan, Laptop, Ponsel, Pakaian, dll.*), dan menyimpannya ke database.
- **Idempotensi & Keamanan Data**: Mekanisme `update_or_create` memastikan seeder aman dijalankan berulang kali tanpa membuat data duplikat, serta opsi `--skip-existing` untuk melindungi modifikasi yang telah dilakukan oleh pengguna.
- **Mitigasi Offline**: Bila koneksi jaringan terhambat saat proses build server, sistem menangani pengecualian secara anggun tanpa menghentikan kesiapan server.

---

## 🎨 Penerapan Framework CSS Tailwind, Dark Mode, & HTMX

1. **Framework CSS Tailwind**:
   - Terintegrasi melalui Play CDN pada `templates/base.html` dengan konfigurasi `corePlugins: { preflight: false }` untuk menjamin keselarasan sempurna antara utility classes Tailwind dan styling kustom SiBekas yang sudah ada.
   - Palet warna bertema kelestarian lingkungan (*Sustainable Living*): `brand-500` (Emerald Green UI), `accent-500` (Amber), dan slate neutrals.
2. **Persistent Dark Mode**:
   - Dilengkapi tombol toggle Dark / Light Mode pada header navbar (desktop dan mobile drawer) dengan ikon bulan/matahari dari Lucide Icons.
   - Preferensi tema tersimpan secara persisten pada `localStorage` pengguna dan mendeteksi preferensi sistem secara otomatis (*WCAG AA compliant contrast*).
3. **Interaktivitas Asinkron (HTMX & AJAX)**:
   - Terintegrasi dengan pustaka HTMX untuk pembaruan DOM parsial tanpa *full-page reload*.
   - Otentikasi token CSRF terinjeksi otomatis pada setiap request asinkron via header `X-CSRFToken`.
   - Notifikasi toast melayang (*floating alert*) yang dapat ditutup secara instan.
4. **Halaman Error Ramah Pengguna**:
   - Menyediakan `templates/403.html` (Akses Ditolak) dan `templates/404.html` (Halaman Tidak Ditemukan) dengan tata letak serasi dan navigasi kembali yang jelas.

---

## 🚀 Panduan Menjalankan Proyek Secara Lokal

### Prasyarat
- Python 3.12+
- Git

### Langkah Instalasi
```powershell
# 1. Kloning repositori proyek
git clone <url-repository-sibekas>
cd SiBekas

# 2. Buat dan aktifkan virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# (Jika menggunakan Linux/macOS: source .venv/bin/activate)

# 3. Perbarui pip dan pasang dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Siapkan environment file
Copy-Item .env.example .env

# 5. Jalankan migrasi database
python manage.py migrate

# 6. Jalankan seeder katalog DummyJSON (minimal 50 produk)
python manage.py seed_products

# 7. Jalankan server lokal
python manage.py runserver
```
Buka browser di `http://127.0.0.1:8000/`.

### Menjalankan Suite Pengujian (Unit Tests)
```powershell
# Jalankan seluruh 98 test suite terverifikasi
python manage.py test
```

---

## 🤖 AI Disclosure & Engineering Analysis

Pengembangan platform **SiBekas** memanfaatkan bantuan teknologi kecerdasan buatan (*Artificial Intelligence*) secara beretika, transparan, dan terukur sebagai akselerator produktivitas rekayasa perangkat lunak (*pair programming assistant*).

### Alat AI yang Digunakan
- **Google Antigravity IDE (Gemini 3.8 Flash / High Reasoning)**: Digunakan untuk perancangan arsitektur MVT, implementasi pola OOP Django, pembuatan test case, dan penataan design system Tailwind.
- **Claude 3.5 Sonnet**: Digunakan untuk validasi silang struktur kode dan perumusan skenario pengujian otorisasi.

---

### Strategi Prompting
Tim menerapkan metode **Iterative Specification Prompting** dan **Test-Driven Prompting**:
1. Menentukan kontrak antarmuka (*interface contract*) dan skema model database terlebih dahulu.
2. Memberikan batasan teknis (*technical constraints*) yang ketat agar kode yang dihasilkan mematuhi kaidah Django idiomatik dan prinsip keamanan OWASP.
3. Meminta AI menghasilkan test case komprehensif yang mencakup skenario kegagalan (*negative testing*), bukan hanya skenario ideal (*happy path*).

---

### 💬 5 Kutipan Prompt Profesional yang Digunakan dalam Pengembangan

Berikut adalah dokumentasi 5 kutipan prompt representatif yang dirumuskan oleh tim pengembang dalam memandu AI selama siklus pengembangan SiBekas:

#### Kutipan Prompt 1 — Arsitektur Monolit MVT & Konfigurasi Multi-Environment
> *"Bertindaklah sebagai Senior Python & Django Architect. Rancang fondasi arsitektur proyek Django 5.x monolitik bernama SiBekas untuk platform marketplace kampus berkelanjutan. Konfigurasikan settings.py dengan pemisahan lingkungan bersih antara development lokal dan production PWS. Terapkan django-environ atau dj-database-url agar secara otomatis mendukung SQLite lokal dan PostgreSQL di server tanpa hardcoded credentials. Pastikan ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, staticfiles WhiteNoise, dan media handler terisolasi secara aman. Sertakan struktur aplikasi modular untuk lima domain: product, profiles, cart, order, dan review, lengkap dengan namespace URL yang konsisten dan base template terpadu yang responsif."*

#### Kutipan Prompt 2 — Integrasi Public API DummyJSON & Seeder Otomatis
> *"Sebagai backend engineer spesialis integrasi data, buat custom Django management command seed_products yang mengonsumsi Public API DummyJSON (https://dummyjson.com/products?limit=60). Petakan data produk eksternal ke dalam schema Product dan Category internal, termasuk konversi kurs harga USD ke IDR yang realistis bagi mahasiswa, sanitasi deskripsi, dan pemetaan nama kategori berbahasa Indonesia menggunakan mapping dictionary. Terapkan mekanisme update_or_create idempotent agar aman dijalankan berulang kali, sertakan flag --skip-existing untuk menjaga modifikasi data lokal, serta rancang graceful error handling jika API eksternal mengalami timeout atau kegagalan jaringan saat deployment."*

#### Kutipan Prompt 3 — State Machine Pesanan & Transaksi Concurrency Safety
> *"Rancang alur transaksi checkout dan manajemen status pesanan berbasis Django ORM dengan concurrency safety tingkat tinggi. Gunakan select_for_update() pada tabel Cart dan Order untuk mencegah race condition serta double submission saat banyak pengguna bertransaksi bersamaan. Terapkan validasi stok bersyarat pada saat pembentukan OrderItem, kalkulasi total yang menjamin subtotal ditambah biaya pengiriman kampus selalu presisi, dan mekanisme atomic transaction rollback bila terjadi kegagalan pembaruan inventaris. Lengkapi dengan state machine transisi status pesanan (pending, processing, shipped, completed, cancelled) yang otomatis mengembalikan stok barang saat pembatalan dilakukan."*

#### Kutipan Prompt 4 — Security Hardening & Object-Level Access Control (OLAC)
> *"Terapkan kontrol otorisasi tingkat lanjut (Object-Level Access Control) dan pengerasan keamanan di seluruh modul Django SiBekas. Buat custom security decorators seperti @seller_required dan @order_participant_required yang memvalidasi kepemilikan objek sebelum mengizinkan aksi mutasi (update/delete). Jika pengguna yang tidak berhak mencoba mengakses atau mengubah resource milik pengguna lain, lemparkan django.core.exceptions.PermissionDenied agar sistem merespons dengan kode HTTP 403 Forbidden yang terhubung ke template 403.html ramah pengguna. Tambahkan pula sanitasi input teks bebas pada form ulasan dan profil guna memitigasi celah Cross-Site Scripting (XSS)."*

#### Kutipan Prompt 5 — Comprehensive Test-Driven Development (Coverage >90%)
> *"Sebagai QA lead pengujian web Django, buat test suite komprehensif berstandar Test-Driven Development (TDD) untuk modul Product dan Review guna mencapai cakupan kode di atas 90%. Susun pengujian terstruktur yang memvalidasi logika Model, batasan Form (seperti rentang rating 1-5 bintang dan batas maksimal 500 karakter komentar), serta skenario View positif dan negatif. Pastikan terdapat pengujian khusus untuk memverifikasi penolakan akses 403 saat non-pemilik mencoba mengubah produk atau ulasan orang lain, serta verifikasi bahwa hanya pembeli dengan transaksi COMPLETED yang diizinkan menuliskan ulasan produk."*

---

### ⚠️ Analisis Kritis: Keterbatasan AI & Perbaikan Rekayasa Manual Mahasiswa

Meskipun AI sangat membantu dalam mempercepat penulisan kode boilerplate, tim menemukan sejumlah **keterbatasan mendasar dan halusinasi AI** yang jika tidak diaudit dan diperbaiki secara manual oleh mahasiswa akan menyebabkan kegagalan sistem fatal:

1. **Halusinasi Penghapusan Akun Pengguna (`ProtectedError`)**:
   - *Kelemahan AI*: AI awalnya menghasilkan kode `user.delete()` sederhana pada fitur hapus akun profil.
   - *Dampak*: Menimbulkan crash server 500 karena tabel `Order` memiliki relasi `buyer = models.ForeignKey(User, on_delete=models.PROTECT)`. Akibatnya, setiap mahasiswa yang sudah memiliki riwayat transaksi akan mengalami crash fatal saat mencoba menutup akunnya.
   - *Solusi Manual Mahasiswa*: Mahasiswa menganalisis dependensi foreign-key database dan mengganti logika penghapusan dengan *soft deactivation* (`user.is_active = False`) serta blok `try...except ProtectedError` yang memberikan pesan edukatif bahwa riwayat pesanan tetap wajib diarsipkan demi integritas transaksi.
2. **Inkonsistensi Migrasi Database vs Definisi Model**:
   - *Kelemahan AI*: AI memodifikasi field `Product.category` menjadi `null=True, blank=True` di model, namun tidak menghasilkan file migrasi yang selaras ke database.
   - *Dampak*: Terjadi `IntegrityError: NOT NULL constraint failed: product_product.category_id` saat pengguna membuat listing produk tanpa kategori.
   - *Solusi Manual Mahasiswa*: Mahasiswa merekonstruksi skema migrasi Django `0002_alter_product_category.py` secara manual dan mengujinya pada database SQLite serta PostgreSQL.
3. **Hilangnya Parameter Filter pada Navigasi Pagination**:
   - *Kelemahan AI*: AI membuat tautan halaman berikutnya hanya dengan `?page={{ page.next_page_number }}`.
   - *Dampak*: Saat pengguna sedang mencari produk "kalkulator" pada kategori "Elektronik" dan berpindah ke halaman 2, seluruh filter pencarian dan kategori mendadak hilang kembali ke halaman depan umum.
   - *Solusi Manual Mahasiswa*: Mahasiswa membangun query string builder dinamis di Python view (`params = request.GET.copy(); params.pop('page'); querystring = params.urlencode()`) dan menyematkannya ke seluruh tautan pagination template.
4. **HTML Entity Auto-escaping pada Unit Testing**:
   - *Kelemahan AI*: AI membuat assertion pengujian string `assertContains(response, "Buku & Alat")` tanpa menyadari bahwa template engine Django secara otomatis meng-escape karakter `&` menjadi `&amp;`.
   - *Dampak*: Seluruh test suite ulasan gagal meskipun tampilan di browser terlihat benar.
   - *Solusi Manual Mahasiswa*: Mahasiswa menelusuri respon biner HTTP dan mengoreksi data uji agar selaras dengan standar parsing HTML entity Django.

---
*SiBekas — Memberi Barang Preloved Kesempatan Kedua demi Kampus UI yang Berkelanjutan.*
