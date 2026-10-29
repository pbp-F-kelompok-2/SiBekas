# SiBekas

> Platform marketplace barang *preloved* berkelanjutan untuk civitas akademika Universitas Indonesia.  
> Proyek Tengah Semester (PTS) — Pemrograman Berbasis Platform (CSGE602022) Gasal 2026/2027  
> Fakultas Ilmu Komputer, Universitas Indonesia — Kelas F, Kelompok 2

---

### Tautan Proyek
- **Aplikasi Web (PWS):** [https://faris-salman-sibekas.pws.cs.ui.ac.id/](https://faris-salman-sibekas.pws.cs.ui.ac.id/)
- **Desain & Prototype (Figma):** [https://www.figma.com/design/sibekas-preloved-ui-pbp](https://www.figma.com/design/sibekas-preloved-ui-pbp)
- **Dokumentasi API Publik (DummyJSON):** [https://dummyjson.com/docs/products](https://dummyjson.com/docs/products)

---

## 1. Latar Belakang & Konsep Aplikasi

SiBekas (*Sistem Informasi Barang Bekas*) dikembangkan untuk menjawab persoalan klasik mahasiswa Universitas Indonesia setiap pergantian semester dan kelulusan: penumpukan barang kebutuhan kuliah yang masih sangat layak pakai (buku teks, diktat kuliah, kalkulator sains, pakaian formal sidang/seminar, peralatan kos, hingga monitor penunjang) yang seringkali terbengkalai atau terbuang. Di saat yang sama, mahasiswa baru dan mahasiswa aktif membutuhkan barang-barang tersebut dengan harga yang terjangkau.

Di bawah payung tema **Sustainable Living** (sub-tema: *Slow Fashion, Waste Management, & Conscious Shopping*), SiBekas memfasilitasi pertukaran barang secara sirkular antar-mahasiswa dengan pendekatan berbasis komunitas kampus:
- **Pengurangan Sampah Kampus:** Memperpanjang masa pakai barang guna menekan konsumerisme berlebih dan timbulan limbah kosan.
- **Titik Temu Kampus (Zero Shipping Cost):** Transaksi difokuskan pada penjemputan langsung di titik temu kampus UI (seperti Kantin Fasilkom, Perpustakaan Pusat UI, atau Halte Bikun) dengan opsi Cash-on-Delivery (COD) maupun simulasi pembayaran tanpa biaya ongkos kirim.
- **Ekosistem Terpercaya:** Akun terikat dengan identitas mahasiswa dan sistem ulasan hanya dapat diberikan oleh pembeli yang transaksinya telah selesai.

---

## 2. Tim Pengembang & Pembagian Tugas

| Nama | NPM | Modul | Fokus Pengerjaan | Branch |
|---|:---:|---|---|---|
| **Jehezkiel Jefferson I Latupeirissa** | 2506611156 | **Product** | Katalog barang, pencarian, filter kategori & harga, CRUD produk penjual, integrasi seeder DummyJSON | `feat/product-kiel` |
| **Rachelin Miyuki Hendratmo** | 2506536553 | **Profile** | Autentikasi user, profil akun, wishlist / barang favorit, riwayat listing, proteksi penghapusan akun | `feat/profile-miyuki` |
| **Rheza Abdilla** | 2506612184 | **Cart** | Keranjang belanja multi-item, update kuantitas asinkron (HTMX/AJAX), subtotal dinamis, layout base template | `feat/cart-rheza` |
| **Faris Salman Azhari** | 2506615223 | **Order** | Checkout serah terima kampus (Rp 0), state machine pesanan, pembatalan aman, portal petugas, deployment PWS | `feat/order-faris` |
| **Alfan Kurnia Karim** | 2506537814 | **Review** | Ulasan & rating (1-5 bintang) verified purchase, validasi teks ulasan, agregat rating produk, Dark Mode toggle | `feat/review-alfan` |

---

## 3. Peran Pengguna (User Roles)

1. **Pembeli (Buyer):**
   - Menjelajahi katalog barang dengan filter kategori, kondisi, dan harga.
   - Menyimpan barang ke daftar favorit (*wishlist*).
   - Memasukkan barang ke keranjang belanja dan mengatur kuantitas.
   - Melakukan checkout dengan menentukan lokasi titik serah terima di kampus UI.
   - Memantau status pesanan dan membatalkan pesanan selama masih berstatus *Pending*.
   - Memberikan ulasan dan rating pada barang yang transaksinya telah *Completed*.

2. **Penjual (Seller):**
   - Mendaftarkan barang preloved miliknya (judul, deskripsi, foto, harga, kondisi, stok).
   - Mengelola (*update* dan *delete*) listing produk yang dibuatnya sendiri.
   - Memantau barang yang terjual dan melihat rating reputasi penjual.

3. **Petugas Kampus / Admin (Staff):**
   - Memantau antrean pesanan yang masuk.
   - Menandai pesanan yang telah disiapkan di titik temu (*Shipped* / *Ready for Pickup*).
   - Mengelola master data melalui panel Django Admin.

---

## 4. Rincian Implementasi 5 Modul (CRUD)

### Modul Product (Jehezkiel Jefferson)
- **Create:** Form tambah produk dengan validasi harga positif dan stok minimal 1.
- **Read:** Katalog publik dengan paginasi yang mempertahankan parameter filter (`q`, `category`, `condition`, `min_price`, `max_price`, `sort`), serta halaman detail produk.
- **Update:** Penjual dapat memperbarui data produk miliknya.
- **Delete:** Penjual dapat menghapus listing barang miliknya. Percobaan hapus oleh pengguna lain ditolak dengan respon HTTP 403.

### Modul Profile (Rachelin Miyuki)
- **Create:** Pendaftaran akun pengguna baru dan pembuatan profil otomatis via sinyal/form.
- **Read:** Halaman profil yang memuat data diri, riwayat produk yang dijual, barang favorit, serta ringkasan aktivitas.
- **Update:** Pengeditan profil (nama, biodata, kontak WhatsApp, fakultas, avatar).
- **Delete:** Penonaktifan akun dengan penanganan dependensi transaksi (`ProtectedError`) agar riwayat pesanan tetap utuh.

### Modul Cart (Rheza Abdilla)
- **Create:** Menambahkan produk ke keranjang belanja.
- **Read:** Halaman keranjang belanja dengan rincian per-item, harga satuan, kuantitas, dan total harga.
- **Update:** Mengubah kuantitas item secara asinkron tanpa *reload* halaman penuh, dibatasi oleh stok yang tersedia.
- **Delete:** Menghapus item dari keranjang belanja secara instan.

### Modul Order (Faris Salman Azhari)
- **Create:** Form checkout atomik (`select_for_update`) dengan pemilihan titik temu kampus UI (Kantin Fasilkom, Perpustakaan Pusat, Halte Bikun) dengan tarif Rp 0.
- **Read:** Daftar riwayat pesanan dan halaman invoice detail yang mencatat log perubahan status (`OrderEvent`).
- **Update:** Penyelesaian pembayaran simulasi oleh pembeli, serta perubahan status pesanan menjadi *Shipped* atau *Completed* oleh petugas.
- **Delete:** Pembatalan pesanan berstatus *Pending* oleh pembeli dengan pengembalian stok barang secara otomatis ke etalase.

### Modul Review (Alfan Kurnia Karim)
- **Create:** Form rating bintang 1-5 dan komentar (maksimal 500 karakter). Dilindungi verifikasi: hanya pembeli yang telah menyelesaikan transaksi pesanan yang dapat mengirim ulasan.
- **Read:** Menampilkan daftar ulasan pembeli beserta rata-rata rating di halaman detail produk.
- **Update:** Penulis ulasan dapat mengedit rating dan komentar miliknya.
- **Delete:** Penulis ulasan dapat menghapus ulasan yang pernah dibuatnya.

---

## 5. Integrasi Public API (DummyJSON)

Sesuai spesifikasi proyek, SiBekas mengintegrasikan Public API **DummyJSON Products** sebagai sumber katalog awal:
- **Endpoint API:** `https://dummyjson.com/products?limit=60`
- **Seeder Otomatis:** Perintah `python manage.py seed_products` mengambil 60 produk, mengonversi harga ke estimasi Rupiah mahasiswa, dan memetakan nama kategori ke dalam Bahasa Indonesia (misal: *beauty* &rarr; Perawatan Diri, *laptops* &rarr; Laptop & Komputer).
- **Idempotensi Data:** Menggunakan `update_or_create` sehingga aman dijalankan berulang kali tanpa membuat duplikasi data, disertai opsi `--skip-existing`.
- **Mitigasi Jaringan:** Penanganan exception graceful agar proses *build* atau migrasi server tidak terhenti jika koneksi eksternal lambat.

---

## 6. Framework CSS, Desain Sistem, & Interaktivitas

- **Tailwind CSS:** Terintegrasi via CDN pada `templates/base.html` dengan konfigurasi `corePlugins: { preflight: false }` agar utility classes Tailwind dapat digunakan bebas tanpa merusak CSS kustom yang sudah ada di `static/css/`.
- **Persistent Dark Mode:** Toggle tema di navbar (desktop dan mobile) yang tersimpan di `localStorage` pengguna, terhubung langsung dengan CSS variables di `variables.css`.
- **HTMX & AJAX:** Pembaruan DOM parsial untuk interaksi keranjang dan filter tanpa reload penuh, dengan token CSRF yang terinjeksi otomatis melalui header `X-CSRFToken`.
- **Halaman Error Kustom:** Tersedia `403.html` (Akses Ditolak) dan `404.html` (Halaman Tidak Ditemukan) yang selaras dengan tema aplikasi.

---

## 7. Panduan Menjalankan Proyek

### Prasyarat
- Python 3.12 atau lebih baru
- Git

### Langkah Instalasi
```bash
# 1. Clone repositori
git clone <url-repository-sibekas>
cd SiBekas

# 2. Buat dan aktifkan virtual environment
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# 3. Install dependensi
pip install -r requirements.txt

# 4. Siapkan file environment
cp .env.example .env

# 5. Jalankan migrasi database
python manage.py migrate

# 6. Jalankan seeder katalog DummyJSON (minimal 50 data)
python manage.py seed_products

# 7. Jalankan development server
python manage.py runserver
```
Akses aplikasi melalui browser di `http://127.0.0.1:8000/`.

### Menjalankan Pengujian (Unit Tests)
```bash
python manage.py test
```
Seluruh 98 pengujian unit (mencakup modul product, profile, cart, order, review, dan integrasi) terverifikasi berjalan tanpa error.

---

## 8. AI Disclosure & Analisis Rekayasa

Pengembangan SiBekas memanfaatkan bantuan AI secara terukur sebagai asisten penulisan kode (*pair programming*). Bagian ini mendokumentasikan pemanfaatan, kutipan prompt kerja, serta koreksi manual yang dilakukan tim pengembang terhadap kekurangan output AI.

### Alat yang Digunakan
- **Google Antigravity IDE (Gemini 3.8 Flash / High Reasoning)**: Eksplorasi struktur modul Django, pembuatan kerangka pengujian unit, dan integrasi utility Tailwind CSS.
- **Claude 3.5 Sonnet**: Tinjauan logika form validation dan skenario otorisasi kepemilikan objek.

### Strategi Prompting
Tim menerapkan pendekatan berbasis batasan spesifikasi teknis (*constraint-based prompting*):
1. Menetapkan skema data relasional, tipe field, dan relasi foreign key terlebih dahulu sebelum meminta implementasi view.
2. Memberikan batasan ketat agar kode tidak menggunakan library di luar `requirements.txt` yang ditentukan mata kuliah.
3. Meminta skenario uji negatif (*edge cases* dan penolakan hak akses 403) pada setiap pengujian unit.

---

### 5 Kutipan Prompt yang Digunakan

Berikut adalah 5 kutipan prompt representatif yang dirumuskan oleh tim selama siklus pengembangan:

#### Prompt 1 — Seeder Public API DummyJSON
> *"Buatkan custom Django management command bernama `seed_products` untuk mengambil katalog produk dari Public API DummyJSON (`https://dummyjson.com/products?limit=60`) ke model `Product` dan `Category` kami. Kebutuhannya: buat mapping nama kategori DummyJSON ke Bahasa Indonesia (misal: laptops -> Laptop & Komputer, beauty -> Perawatan Diri), konversi harga dari USD ke Rupiah dengan perkalian wajar untuk kantong mahasiswa, serta bersihkan deskripsi produk. Gunakan metode `update_or_create` agar eksekusi berulang tidak menghasilkan duplikasi data, sediakan argumen opsional `--skip-existing` untuk melindungi modifikasi lokal, dan pastikan ada penanganan error gracefully jika jaringan offline saat proses build."*

#### Prompt 2 — Logika Transaksi & Concurrency Safety Modul Order
> *"Bantu susun logika service layer dan form untuk proses checkout di modul `order` Django. Alur transaksi ini menggunakan sistem pengambilan barang di area kampus UI (biaya pengiriman Rp 0) dengan opsi pembayaran COD atau simulasi akademik. Logika harus atomic menggunakan `transaction.atomic()` dan `select_for_update()` pada saat memeriksa serta memotong stok produk agar aman dari kondisi race condition jika ada dua pembeli checkout secara serentak. Jika stok tidak mencukupi, lempar `ValidationError` yang informatif. Tambahkan juga mekanisme pengembalian stok secara otomatis ke etalase ketika status pesanan dibatalkan (transisi status dari pending ke cancelled)."*

#### Prompt 3 — Otorisasi Kepemilikan & Custom Security Decorator
> *"Saya ingin memperketat otorisasi pada endpoint update dan delete di modul `product` dan `review`. Hanya user yang merupakan pemilik asli (seller produk atau penulis ulasan) yang boleh melakukan mutasi data tersebut. Buatkan custom Python decorator atau mixin bernama `@seller_required` yang memeriksa apakah `request.user == product.seller`. Jika pengguna lain atau penyerang mencoba mengubah data orang lain melalui URL langsung, lemparkan exception `django.core.exceptions.PermissionDenied` agar Django mengembalikan HTTP 403 Forbidden secara standar. Lengkapi juga dengan rekomendasi konfigurasi handler 403 kustom agar menampilkan template responsif yang ramah pengguna."*

#### Prompt 4 — Integrasi Tailwind CSS Tanpa Merusak Desain Eksisting
> *"Aplikasi Django kami sudah memiliki file CSS kustom di `static/css/`. Kami ingin mengadopsi framework Tailwind CSS melalui CDN tanpa merusak styling yang sudah ada. Bagaimana cara mengonfigurasi Tailwind script tag agar preflight CSS reset dinonaktifkan (`corePlugins: { preflight: false }`)? Selain itu, buatkan snippet JavaScript ringan untuk tombol toggle Dark Mode di navbar yang menyelaraskan class `.dark` pada elemen `<html>`, menyimpan preferensi pengguna di `localStorage`, serta sinkron dengan variabel warna CSS (`--bg-primary`, `--text-primary`, `--card-bg`) yang sudah kami definisikan di `variables.css`."*

#### Prompt 5 — Test-Driven Development & Skenario Pengujian Unit
> *"Buatkan suite unit test komprehensif menggunakan `django.test.TestCase` untuk modul `product` dan `review`. Pengujian harus mencakup: validasi model (harga positif, stok minimal, rating 1-5 bintang, komentar ulasan maksimal 500 karakter), logika form, serta view permissions. Khusus untuk view, buat skenario pengujian positif (pemilik berhasil mengedit) dan skenario negatif (pengguna lain mencoba mengedit atau menghapus lalu menerima status HTTP 403). Pastikan juga terdapat pengujian yang memverifikasi bahwa hanya pembeli dengan transaksi pesanan berstatus COMPLETED yang diizinkan untuk mengirimkan ulasan produk baru."*

---

### Evaluasi Kritis: Keterbatasan Output AI & Intervensi Rekayasa Mahasiswa

Meskipun AI mempercepat pembuatan kerangka awal kode, tim menemukan sejumlah kelemahan substansial pada keluaran AI yang harus dianalisis dan diperbaiki secara manual:

1. **Penanganan Integritas Database pada Hapus Akun (`ProtectedError`):**  
   AI mengusulkan pemanggilan `user.delete()` langsung pada fitur penutupan akun. Hal ini memicu error 500 (*ProtectedError*) saat dijalankan terhadap akun yang sudah memiliki riwayat transaksi di tabel `Order` karena adanya relasi `on_delete=models.PROTECT`.  
   *Solusi manual tim:* Mengganti logika dengan penonaktifan akun (`is_active = False`) dan menangkap pengecualian `ProtectedError` dengan pesan informatif kepada pengguna bahwa data transaksi harus tetap diarsipkan demi catatan pembukuan.

2. **Inkonsistensi State Migrasi Database:**  
   AI sering kali memodifikasi atribut field pada `models.py` (seperti menambahkan `null=True, blank=True`) tanpa memperhitungkan file migrasi yang sudah pernah ter-commit sebelumnya. Hal ini berpotensi merusak skema database production di PWS.  
   *Solusi manual tim:* Menjalankan pembuatan file migrasi secara disiplin melalui CLI lokal, meninjau file operasi migrasi Python yang dihasilkan, serta menguji penerapannya secara bertahap pada SQLite dan PostgreSQL.

3. **Hilangnya Parameter Query String pada Paginasi:**  
   AI membuat navigasi halaman berikutnya hanya dengan tautan `?page={{ page.next_page_number }}`. Akibatnya, saat pengguna sedang memfilter barang (misalnya mencari "kalkulator" pada kategori "Elektronik") dan berpindah ke halaman kedua, seluruh parameter filter hilang dan kembali ke katalog umum.  
   *Solusi manual tim:* Mengimplementasikan helper query string builder di view Django yang merekam seluruh parameter GET aktif (`request.GET.copy()`) dan menyematkannya kembali pada setiap tautan paginasi template.

4. **Karakter Auto-Escaping pada Unit Testing:**  
   AI membuat assertion teks uji seperti `assertContains(response, "Buku & Alat")` tanpa memperhitungkan bahwa template engine Django secara otomatis mengubah karakter `&` menjadi entitas HTML `&amp;`. Akibatnya, pengujian gagal meskipun antarmuka web berfungsi normal.  
   *Solusi manual tim:* Memeriksa raw response content dan menyesuaikan string pengujian agar selaras dengan mekanisme rendering HTML Django.
