# API untuk SiBekas Mobile - Checkpoint 1

API Django REST Framework tersedia di `/api/v1/`, menggunakan model dan database web yang sama. Dokumentasi kontrak serta setup Flutter berada di [SiBekas-mobile/docs/api.md](https://github.com/pbp-F-kelompok-2/SiBekas-mobile/blob/main/docs/api.md).

| Modul | Endpoint dasar | Akses |
| --- | --- | --- |
| Product - Jehezkiel | GET `products/`, `products/<int:pk>/`, `categories/` | Publik |
| Profile - Rachelin | GET/PATCH `profile/`, GET `profile/favorites/` | Akun sendiri |
| Cart - Rheza | GET `cart/` | Akun sendiri |
| Order - Faris | GET `orders/`, `orders/<uuid:pk>/` | Pembeli sendiri; daftar `role=seller` untuk penjual, `role=staff` hanya staff |
| Review - Alfan | GET `reviews/` | Publik; filter `mine=true` hanya untuk akun login |

Semua path di atas relatif terhadap `/api/v1/`. List DRF memakai `count`, `next`, `previous`, `results` dan paginasi 20 baris. Keranjang memakai `items`, `subtotal`, `total_items` berdasarkan `cart_summary` web.

POST `auth/login/` menerima JSON username/password akun website, menghasilkan token dan profil. Kirim `Authorization: Token <token>` melalui HTTPS pada request privat. POST `auth/logout/` mencabut token dengan respons 204. Token mobile ditambahkan tanpa menonaktifkan SessionAuthentication/CSRF website. Akun nonaktif ditolak; login dibatasi 10 request/menit per IP.

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test tests.test_mobile_api
python manage.py runserver
```

Migrasi memasang tabel token DRF; tidak mengubah model bisnis. Endpoint tulis produk, keranjang, pesanan dan ulasan belum termasuk CP1 dan dilanjutkan oleh pemilik modul masing-masing. API baca menolak method tulis dengan 405. Seluruh validasi/filter/otorisasi server diuji di `tests/test_mobile_api.py`.
