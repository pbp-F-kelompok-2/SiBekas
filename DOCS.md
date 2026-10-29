# 📖 DOKUMEN SPESIFIKASI DAN PANDUAN PENGEMBANGAN SIBEKAS (DOCS.md)
**Platform Marketplace Barang Preloved Berkelanjutan untuk Mahasiswa Universitas Indonesia**  
*Mata Kuliah Pemrograman Berbasis Platform (CSGE602022) — Gasal 2026/2027*  
*Fakultas Ilmu Komputer, Universitas Indonesia*

---

## 📌 DAFTAR ISI
1. [Ringkasan Proyek & Konteks Pembelajaran](#1-ringkasan-proyek--konteks-pembelajaran)
2. [Profil Tim & Pembagian Modul](#2-profil-tim--pembagian-modul)
3. [Rubrik Penilaian Lengkap BRP (Target Skor 4 / Exceeds Expectation)](#3-rubrik-penilaian-lengkap-brp-target-skor-4--exceeds-expectation)
   - [Skala Penilaian Standar](#skala-penilaian-standar)
   - [Penilaian Kelompok (Bobot 30%)](#penilaian-kelompok-bobot-30)
   - [Penilaian Individu (Bobot 70%)](#penilaian-individu-bobot-70)
4. [Arsitektur Teknis & Standar Implementasi](#4-arsitektur-teknis--standar-implementasi)
   - [Pola Model-View-Template (MVT) Django](#pola-model-view-template-mvt-django)
   - [Penerapan CSS Framework & Design System](#penerapan-css-framework--design-system)
   - [Interaktivitas Sisi Klien (AJAX & HTMX)](#interaktivitas-sisi-klien-ajax--htmx)
   - [Integrasi Public API Eksternal (DummyJSON API)](#integrasi-public-api-eksternal-dummyjson-api)
   - [Manajemen Lingkungan & Deployment PWS](#manajemen-lingkungan--deployment-pws)
5. [Spesifikasi Rinci 5 Modul SiBekas](#5-spesifikasi-rinci-5-modul-sibekas)
   - [Modul 1: Product (Jehezkiel Jefferson)](#modul-1-product-jehezkiel-jefferson)
   - [Modul 2: Profile / User & Autentikasi (Rachelin Miyuki)](#modul-2-profile--user--autentikasi-rachelin-miyuki)
   - [Modul 3: Cart (Rheza Abdilla)](#modul-3-cart-rheza-abdilla)
   - [Modul 4: Order / Transaction (Faris Salman Azhari)](#modul-4-order--transaction-faris-salman-azhari)
   - [Modul 5: Review (Alfan Kurnia Karim)](#modul-5-review-alfan-kurnia-karim)
6. [Keamanan & Kontrol Akses (Security & Object-Level Access Control)](#6-keamanan--kontrol-akses-security--object-level-access-control)
7. [Strategi Pengujian & Cakupan Kode (Testing & Coverage >90%)](#7-strategi-pengujian--cakupan-kode-testing--coverage-90)
8. [Standar Git Flow, Kolaborasi, & CI/CD](#8-standar-git-flow-kolaborasi--cicd)
9. [Dokumentasi README.md & AI Disclosure Transparan](#9-dokumentasi-readmemd--ai-disclosure-transparan)
10. [Audit Kesenjangan Kode & Hasil Perbaikan](#10-audit-kesenjangan-kode--hasil-perbaikan)

---

## 1. Ringkasan Proyek & Konteks Pembelajaran

### 1.1 Latar Belakang & Nilai Tambah
Proyek Tengah Semester (PTS) PBP Gasal 2026/2027 mengangkat tema utama **Sustainable Living**. SiBekas (*Sistem Informasi Barang Bekas Mahasiswa UI*) diimplementasikan di bawah payung sub-tema **Slow Fashion, Waste Management, & Conscious Shopping**.

Setiap tahunnya, ribuan mahasiswa Universitas Indonesia membeli kebutuhan perkuliahan (buku teks, perlengkapan kos, kalkulator sains, pakaian seminar/magang, alat elektronik penunjang) yang setelah selesai masa pemakaian hanya menumpuk atau berakhir di tempat pembuangan sampah. Di sisi lain, mahasiswa baru dan mahasiswa aktif membutuhkan barang-barang berkualitas layak pakai dengan harga terjangkau. 

**SiBekas** hadir sebagai solusi marketplace sirkular berbasis kampus terintegrasi yang:
- Mengurangi jejak karbon (*carbon footprint*) dan timbulan sampah kos (*campus waste reduction*) melalui perpanjangan siklus hidup barang (*reuse & circular economy*).
- Memastikan transaksi aman dan terpercaya di dalam ekosistem mahasiswa UI dengan sistem ulasan terverifikasi dan opsi Cash-on-Delivery (COD) / serah terima langsung di lingkungan kampus UI tanpa biaya ongkos kirim.
- Menjadi fondasi *web service backend* yang kokoh untuk Proyek Akhir Semester (PAS) berbasis mobile Flutter.

### 1.2 Tujuan Pembelajaran Khusus (BRP)
1. **Responsive UI/UX via CSS Framework**: Mengembangkan antarmuka web responsif di berbagai perangkat (desktop, tablet, mobile) menggunakan framework CSS Tailwind.
2. **Implementasi Pola MVT Django**: Menghubungkan Models, Views, Forms, dan Templates secara bersih, modular, dan terstruktur.
3. **Unit Testing & Deployment PWS**: Menguji fungsionalitas aplikasi dengan cakupan tes tinggi (>90%) dan mempublikasikan aplikasi ke *Platform-as-a-Service* Fasilkom UI (PWS) dengan database terisolasi.
4. **Kolaborasi Tim & Standar Industri**: Berkolaborasi menggunakan Git Flow profesional, Pull Request terstruktur, penanganan konflik, serta dokumentasi transparan mengenai pemanfaatan AI.

---

## 2. Profil Tim & Pembagian Modul

Proyek dikembangkan oleh tim beranggotakan 5 mahasiswa dengan kepemilikan modul CRUD independen:

| No. | Nama Mahasiswa | NPM | Modul Utama | Tanggung Jawab Spesifik | Nama Git Branch |
|:---:|:---|:---:|:---|:---|:---|
| 1 | **Jehezkiel Jefferson I Latupeirissa** | 2506611156 | **Product** | Katalog barang preloved, kategori dinamis, multi-filter (harga, kondisi, status), pencarian teks, detail produk, CRUD produk milik penjual, seeder 50+ data DummyJSON. | `feat/product-jehezkiel` |
| 2 | **Rachelin Miyuki Hendratmo** | 2506536553 | **Profile / User** | Manajemen profil pengguna, personalisasi data, autentikasi UI lokal (`@ui.ac.id`), penanganan akun dinonaktifkan/dihapus aman dari crash foreign-key, bookmark/favorit barang. | `feat/profile-rachelin` |
| 3 | **Rheza Abdilla** | 2506612184 | **Cart & Shared Templates** | Keranjang belanja multi-item, penyesuaian kuantitas asinkron, perhitungan subtotal otomatis, kerangka template bersama (`base.html`, `navbar.html`, `footer.html`), konsistensi UI responsif. | `feat/cart-rheza` |
| 4 | **Faris Salman Azhari** | 2506615223 | **Order / Transaction & Integration** | Alur checkout serah terima kampus UI, pembayaran simulasi/COD, riwayat transaksi, pembatalan pesanan, portal verifikasi pesanan oleh staff kampus, integrasi & deployment PWS. | `feat/order-faris` |
| 5 | **Alfan Kurnia Karim** | 2506537814 | **Review & Design System** | Sistem ulasan dan rating (1-5 bintang) khusus pembeli terverifikasi (*verified buyer*), CRUD ulasan, rekapitulasi rating pada katalog & profil penjual, standardisasi design system, palet warna eco-green, dan Dark Mode toggle. | `feat/review-alfan` |

---

## 3. Rubrik Penilaian Lengkap BRP (Target Skor 4 / Exceeds Expectation)

### Penilaian Kelompok (Bobot 30%)
1. **Design System (HTML, CSS Framework) — Bobot 25%**:
   - Target Skor 4: Standar UI/UX industri, template bersama (`base.html`) yang memanfaatkan Tailwind CSS, Dark Mode toggle terpersistensi, micro-interactions, dan kontras aksesibilitas tinggi (WCAG AA).
2. **External Data / Public API Integration — Bobot 15%**:
   - Target Skor 4: Public API DummyJSON terintegrasi sempurna menyediakan 50+ data awal katalog; penanganan data tingkat lanjut dengan pemetaan kategori berbahasa Indonesia, konversi kurs IDR, dan mitigasi downtime server eksternal secara anggun.
3. **Collaboration & Git Flow — Bobot 30%**:
   - Target Skor 4: Branch independen per anggota, commit rutin berformat Conventional Commits, wajib peer review, integrasi review otomatis.
4. **Integration & Deployment — Bobot 25%**:
   - Target Skor 4: Integrasi pola MTV Django bersih; landing page dan navigasi global berfungsi sempurna; deployment PWS stabil; pemisahan dev/prod terisolasi; automasi CI/CD via GitHub Actions workflow (`.github/workflows/ci.yml`).
5. **Documentation & AI Disclosure — Bobot 5%**:
   - Target Skor 4: README.md standar open-source dengan tautan deployment PWS dan desain Figma resmi; AI Disclosure mendalam dilengkapi 5 kutipan prompt profesional dan analisis kritis atas kelemahan AI serta perbaikan manual engineer.

### Penilaian Individu (Bobot 70%)
1. **CRUD Module Implementation — Bobot 35%**:
   - Target Skor 4: Operasi CRUD tanpa cacat di seluruh 5 modul (Product, Profile, Cart, Order, Review); validasi data ketat; soft-delete & archiving; penyaringan query multi-kriteria; ORM teroptimasi (`select_related`, `prefetch_related`).
2. **Web Interactivity & Responsiveness (AJAX/HTMX) — Bobot 10%**:
   - Target Skor 4: Integrasi asinkron (AJAX/HTMX) di seluruh modul CRUD tanpa full reload; optimistic UI updates; toast feedback otomatis.
3. **Security Awareness (Authorization & Access Control) — Bobot 10%**:
   - Target Skor 4: Object-Level Access Control (OLAC) ketat; custom security decorators (`@seller_required`, `@order_participant_required`); respon HTTP 403 Forbidden dengan halaman template `403.html` yang ramah; sanitasi input XSS.
4. **Testing & Code Coverage — Bobot 10%**:
   - Target Skor 4: Unit test komprehensif seluruh modul (Models, Views, Forms) dengan cakupan tinggi (>90%); seluruh 98 pengujian lulus 100%; menguji skenario positif dan negatif.
5. **Git Contribution & Code Ownership — Bobot 10%**:
   - Target Skor 4: Disiplin checkpoint, commit terdistribusi merata, kontribusi lintas modul.
6. **Demo & Live Coding — Bobot 25%**:
   - Target Skor 4: Penguasaan alur end-to-end, presentasi artikulatif, kemampuan refactoring dan live coding mandiri.

---

## 4. Arsitektur Teknis & Standar Implementasi

### Pola Model-View-Template (MVT) Django
Struktur folder monolitik bersih dengan pemisahan aplikasi yang tegas:
```text
SiBekas/
├── sibekas/              # Pengaturan global proyek, wsgi, asgi, routing inti, utils
├── product/              # Modul 1: Katalog produk & CRUD penjual
├── profiles/             # Modul 2: Profil mahasiswa, personalisasi, & auth
├── cart/                 # Modul 3: Keranjang belanja & perhitungan
├── order/                # Modul 4: Pesanan, checkout titik temu kampus, & status
├── review/               # Modul 5: Ulasan produk & rating bintang
├── static/               # Aset statis terpusat (CSS, JS, ikon)
├── templates/            # Template HTML global berstruktur shared base
│   ├── base.html         # Shell utama, Tailwind CDN, Dark Mode, HTMX
│   ├── navbar.html       # Navigasi responsif dengan toggle tema
│   ├── footer.html       # Footer sistematis & tautan fungsional
│   ├── 403.html          # Halaman akses ditolak yang ramah
│   ├── 404.html          # Halaman tidak ditemukan
│   ├── product/
│   ├── profiles/
│   ├── cart/
│   ├── order/
│   └── review/
├── tests/                # Tes integrasi lintas-modul & end-to-end
├── .github/workflows/    # Automasi CI/CD GitHub Actions
│   └── ci.yml
├── manage.py
├── requirements.txt      # Dependensi produksi & pengujian
├── Procfile              # Gunicorn web process untuk PWS
└── README.md             # Dokumentasi open-source lengkap
```

---

## 5. Rincian Implementasi 5 Modul

1. **Modul Product**:
   - Models: `Category`, `Product`, `ProductImage`.
   - Views: Katalog publik, live search, multi-filter query, detail produk dengan rating agregat, CRUD produk terlindungi otorisasi pemilik (`PermissionDenied` 403).
   - Seeder: `python manage.py seed_products` mengonsumsi Public API DummyJSON untuk memuat 60 produk awal dengan kategori terjemahan Bahasa Indonesia.
2. **Modul Profile**:
   - Models: `Profile`, `Favorite`.
   - Autentikasi lokal email UI (`@ui.ac.id`), personalisasi akun, riwayat produk yang dijual, daftar barang favorit.
   - Penonaktifan akun aman dari crash `ProtectedError` pada pesanan tersimpan.
3. **Modul Cart**:
   - Models: `Cart`, `CartItem`.
   - Keranjang multi-item, penyesuaian kuantitas asinkron, perhitungan subtotal otomatis, isolasi data antar user.
4. **Modul Order / Transaction**:
   - Models: `Order`, `OrderItem`, `OrderEvent`.
   - Checkout serah terima langsung di lingkungan kampus UI (Gratis / COD / Demo Payment).
   - Concurrency safety dengan `select_for_update()` dan pemotongan stok bersyarat.
   - Manajemen status pesanan (`pending` -> `processing` -> `shipped` -> `completed` / `cancelled`) dengan auto-restore stok saat batal.
5. **Modul Review**:
   - Models: `Review`.
   - Verifikasi ketat: Hanya pembeli yang telah menyelesaikan transaksi pesanan (`status=completed`) yang dapat mengulas.
   - Rating 1-5 bintang, komentar tervalidasi maksimal 500 karakter.
   - Pembaruan dan penghapusan ulasan dilindungi otorisasi pemilik.

---

## 6. Standar Keamanan & Pengujian

- **Custom Decorators**: `@seller_required`, `@order_participant_required`.
- **403 Forbidden Response**: Melempar `django.core.exceptions.PermissionDenied` saat aksi tidak sah dilakukan, terhubung ke template `403.html`.
- **Unit Testing**: 98 pengujian komprehensif yang mencakup seluruh model, form, view, dan skenario otorisasi lolos 100% tanpa error.
- **Automasi CI/CD**: Workflow GitHub Actions `.github/workflows/ci.yml` menjalankan pemeriksaan sistem Django, pengecekan migrasi, dan pengujian unit pada setiap push/PR.

---
*Dokumen ini merupakan spesifikasi resmi dan panduan penilaian terpadu Proyek Tengah Semester SiBekas — PBP Gasal 2026/2027.*
