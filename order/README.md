# Order / Transaction — Faris

Modul ini mengganti placeholder `/orders/` dengan checkout, riwayat, detail,
pembayaran, pembaruan status, pembatalan, dan pencatatan perjalanan pesanan.
Semua halaman memakai `base.html`, navbar/footer bersama, dan design token yang
sudah ada pada `static/css/variables.css`.

Panduan konfigurasi RajaOngkir, akun petugas, pemeriksaan integrasi, dan deployment
PWS tersedia di [PANDUAN_MANUAL.md](PANDUAN_MANUAL.md). Perintah tambahan:
`python manage.py lookup_shipping_destination "Pondok Cina"` dan
`python manage.py check_order_readiness --strict --require-shipping`.

## Menjalankan

```bash
python manage.py migrate
python manage.py runserver
```

Login, buka detail produk, tambahkan barang ke keranjang, lalu pilih **Lanjut ke
Checkout**. Isi penerima, telepon, dan alamat atau titik temu di kampus UI.
Riwayat tersedia di `/orders/` dan mendukung filter status, pencarian nama
produk/penerima, serta pagination.

Integrasi menggunakan `CartItem.product` dari implementasi keranjang Rheza.
Migration keranjang memindahkan referensi ID lama ke foreign key sebelum
menghapus kolom referensi lama. Produk yang hilang,
stok yang tidak mencukupi, dan produk milik pembeli sendiri ditandai tidak
tersedia; keranjang harus diperbaiki sebelum checkout.

## Pembayaran dan status

| Aksi | Pengguna | Syarat | Hasil |
| --- | --- | --- | --- |
| Checkout COD | Pembeli | Pengambilan di kampus | Diproses, belum dibayar |
| Checkout simulasi | Pembeli | Simulasi diaktifkan | Menunggu pembayaran |
| Simulasikan pembayaran | Pembeli pemilik pesanan | Menunggu pembayaran simulasi | Diproses, sudah dibayar |
| Kirim / tandai siap diambil | Petugas (`is_staff`) | Diproses | Dikirim / siap diambil |
| Pesanan diterima | Pembeli pemilik pesanan | Dikirim / siap diambil | Selesai; COD ditandai dibayar |
| Batalkan | Pembeli pemilik pesanan atau petugas | Menunggu pembayaran / diproses | Dibatalkan, stok kembali |

Petugas login melalui halaman login biasa dan memilih **Kelola semua pesanan**
di `/orders/`. Untuk kurir, nomor resi wajib diisi saat menandai pesanan dikirim.
Pemenuhan pesanan dikelola petugas dari titik pengumpulan SiBekas di kampus UI.
Penjual menyerahkan barang ke titik pengumpulan untuk pengiriman gabungan.

Pembayaran simulasi adalah demonstrasi akademik: tidak menagih kartu, membuat
rekening virtual, mentransfer uang, atau melakukan refund uang nyata. Kendalikan
opsi ini melalui `ORDER_ENABLE_DEMO_PAYMENT`; default mengikuti `DJANGO_DEBUG`.
Untuk demo proyek di PWS, aktifkan secara eksplisit dengan `True`. Tanpa simulasi,
checkout tetap bisa dipakai untuk COD saat pengambilan di kampus. COD via kurir
tidak ditawarkan karena API Shipping Cost hanya memberi tarif, bukan pemesanan
pengiriman dengan penagihan COD.

Pembatalan mempertahankan riwayat pesanan dan mengembalikan stok satu kali.
Pembayaran simulasi yang sudah dibayar ditandai dikembalikan. Pesanan yang sudah
dikirim atau selesai tidak dapat dibatalkan. Ulasan hanya dapat dibuat untuk
produk dalam pesanan selesai milik pengguna tersebut.

## RajaOngkir / Komerce

Tambahkan konfigurasi berikut ke `.env` lokal atau environment proyek PWS:

```dotenv
RAJAONGKIR_API_KEY=
RAJAONGKIR_ORIGIN_ID=
RAJAONGKIR_COURIERS=jne:jnt:sicepat
ORDER_ENABLE_DEMO_PAYMENT=True
```

`RAJAONGKIR_ORIGIN_ID` adalah **ID subdistrict** titik pengumpulan kampus dari
metode direct search, bukan ID kecamatan dari endpoint hierarki. Pilih kurir
sesuai paket akun RajaOngkir. Seluruh barang dalam satu checkout dihitung sebagai
satu paket yang berangkat dari titik pengumpulan tersebut; berat merupakan
jumlah `Product.weight_grams × quantity`.

Integrasi mengikuti dokumentasi resmi:

- [Pencarian tujuan](https://www.rajaongkir.com/docs/shipping-cost/endpoint-rajaongkir-for-search-base/search-destination-rajaongkir):
  `GET destination/domestic-destination`.
- [Perhitungan ongkir](https://www.rajaongkir.com/docs/shipping-cost/endpoint-rajaongkir-for-search-base/calculate-domestic-cost):
  `POST calculate/domestic-cost`, form URL-encoded, header `key`, berat dalam gram.

API key hanya dikirim dari server. Browser menerima tujuan dan pilihan tarif
dengan tanda tangan Django. Tarif berlaku 15 menit dan terikat pada pembeli,
tujuan, berat, harga, serta isi keranjang. Ongkir/total dari browser tidak
dipercaya. Jika konfigurasi belum tersedia atau API gagal, pengguna mendapat
pesan yang sesuai dan bisa memilih pengambilan di kampus tanpa ongkir.

## Konsistensi data

- Checkout, pencadangan stok, rincian pesanan, dan pengosongan keranjang berada
  dalam satu transaksi database.
- Cart/order/product dikunci pada database yang mendukung row locking.
  Pengurangan stok juga memakai conditional update agar tidak menjadi negatif.
- Token checkout dan unique checkout key mencegah order ganda saat submit diulang.
- Harga, nama, penjual, kondisi, dan gambar disalin ke `OrderItem`; perubahan atau
  penghapusan listing tidak mengubah rincian pembelian sebelumnya.
- Semua perubahan menggunakan POST dan CSRF. Pembeli hanya bisa mengakses
  pesanannya sendiri; petugas bisa mengelola seluruh pesanan.
- Django Admin menampilkan data order sebagai read-only. Aksi pembatalan admin
  menggunakan service yang sama agar tidak melewati pengembalian stok.

## Pemeriksaan dan deployment

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

Tes mencakup integrasi produk/keranjang, token palsu dan kedaluwarsa, harga
berubah, stok habis, checkout ganda, rollback transaksi, akses lintas pengguna,
CSRF, transisi status, pengembalian stok, pembayaran simulasi, eligibility ulasan,
serta kontrak dan kegagalan API RajaOngkir dengan response mock. Tarif live tetap
perlu diuji memakai akun dan API key RajaOngkir yang valid.

`Procfile` menjalankan migration, bootstrap katalog opsional, dan collectstatic saat release, kemudian
Gunicorn. Gunakan konfigurasi produksi pada `.env.example` dengan secret key
kuat, `DJANGO_DEBUG=False`, HTTPS, dan database PWS. Untuk demo ongkir kurir,
aktifkan simulasi dan isi konfigurasi RajaOngkir di PWS.

Pekerjaan dilakukan pada `feat/order-faris`; jangan push ke `main` secara langsung.
Setelah commit, push branch fitur dan deploy commit yang sudah diuji ke PWS:

```bash
git push origin feat/order-faris
git push pws HEAD:master
```

PWS menjalankan build/release setelah push. Periksa status Running dan
`https://faris-salman-sibekas.pws.cs.ui.ac.id/health/`, lalu ulangi alur pengguna
di deployment. Jangan menjalankan ulang `seed_products` pada setiap release:
command seed tanpa `--skip-existing` memakai `update_or_create` dan akan mengatur ulang stok
contoh dari DummyJSON, termasuk stok yang sudah berkurang karena transaksi.
Untuk data awal pada PWS tanpa console, aktifkan `DJANGO_SEED_INITIAL_PRODUCTS=True`;
bootstrap hanya berjalan jika katalog belum mencapai 50 produk dan mempertahankan
produk yang sudah ada. Nonaktifkan opsi setelah data awal terisi.
