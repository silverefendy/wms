# ADR-0008: Lokasi Jumbo Bag Memakai ERPNext Warehouse

## Status

Proposed (draft 2026-09-29). Menggantikan ADR-0005 dan ADR-0006.
Mengubah Addendum 2026-09-28 pada ADR-0007 (ADR-0007 belum diedit). ADR-0001 dan ADR-0003 tetap berlaku.

## Konteks

Kebutuhan operasional (dinyatakan Efendy, 2026-09-29): melacak perpindahan Jumbo Bag antar tahap Kosong, Isi, Retur, Rusak, Hilang, dan Jual; tahap awal tanpa Purchase, Sales, atau Delivery Note ERPNext; satu dokumen memuat banyak bag; setiap transfer wajib konfirmasi terima; wajib ada audit trail, remark, dan attachment.

Implementasi sebelumnya (ADR-0006) memakai WMS Location bertipe State sebagai Inventory Dimension dalam satu ERPNext Warehouse, dengan satu dokumen Bag Fill Log per bag per siklus.

Kondisi terverifikasi per 2026-09-29 (site `erp.ciptamebel.co.id`):

- 5 WMS Location bertipe State; 0 Serial No, 0 Stock Entry, 0 Bag Fill Log, 0 Stock Ledger Entry, 0 Bin.
- Tipe Zone, Aisle, Rack, Shelf, dan Bin tidak dipakai oleh kode maupun data.
- Inventory Dimension `WMS Location` membuat 29 Custom Field di DocType inti ERPNext.
- Validasi runtime dimensi baru sebagian (lihat ADR-0006).
- Company memakai perpetual inventory, tanpa item-wise inventory account; Warehouse yang ada tidak punya akun khusus (memakai akun persediaan default Company).
- DocType Serial No memiliki field `warehouse`.

## Keputusan

1. Setiap tahap Jumbo Bag adalah ERPNext Warehouse (leaf) di bawah satu Warehouse grup. Tahap awal: Kosong, Isi, Retur, Rusak, Hilang, Jual. Nama dapat diganti; pemetaan tahap ke Warehouse disimpan sebagai konfigurasi, bukan konstanta di kode.
2. Bag tetap ERPNext Item + Serial No (RFID/QR di Serial No), sesuai ADR-0007. Lokasi bag adalah Warehouse tempat Serial No berada.
3. Perpindahan adalah Stock Entry Material Transfer antar Warehouse. Bag tetap di Warehouse asal sampai penerima mengonfirmasi; stok diposting saat konfirmasi. Fitur transit bawaan ERPNext tidak dipakai pada tahap awal.
4. Dokumen baru `WMS Bag Transfer` (nama sementara): satu dokumen = satu transaksi, berisi banyak bag; Warehouse asal dan tujuan; pengirim dan penerima; status (Draft, Dikirim, Diterima, Diterima dengan Selisih, Dibatalkan); per bag: hasil (Diterima/Selisih), metode (Scan/Manual), remark. Manual hanya untuk role `WMS Warehouse Manager` dengan alasan wajib. Bag yang tidak terscan ditandai Selisih. Attachment/foto didukung.
5. Rusak bersifat final. Hilang dapat kembali ke siklus dengan catatan. Retur menanyakan kembali ke Kosong atau selesai. Approval Rusak/Hilang bersifat opsional.
6. Stok pellet ERPNext tidak dikurangi pada tahap awal. Rata-rata pellet per bag (netto container dibagi jumlah bag, bag yang ikut container diberi penanda) menjadi informasi tambahan di Weighbridge Ticket (fase terpisah).
7. Dihentikan dan dihapus (setelah ADR ini diterima): WMS Location (semua tipe), WMS Location State, Inventory Dimension `WMS Location`, WMS Bag Fill Log beserta dashboard-nya, dan patch `setup_inventory_dimension`. Kebutuhan rack/bin di masa depan dikonfigurasi di ERPNext.

## Alternatif

- Mempertahankan State + Inventory Dimension: ditolak. Laporan stok standar tidak memisahkan bag per tahap tanpa filter dimensi, 29 Custom Field masuk ke DocType inti, dan validasi runtime baru sebagian.
- Mengubah Bag Fill Log ke Warehouse: ditolak. Model satu bag per dokumen tidak cocok dengan kebutuhan satu dokumen banyak bag.
- Transit bawaan ERPNext: tidak dipilih untuk tahap awal; dapat dinilai ulang.

## Konsekuensi

### Positif

- Laporan stok standar per Warehouse langsung memisahkan bag per tahap.
- Tidak ada ketergantungan pada Inventory Dimension.
- Repo lebih ramping.

### Negatif

- Bag yang sedang dikirim masih tampak di Warehouse asal sampai dikonfirmasi.
- Stock Entry manual di ERPNext dapat melewati konfirmasi WMS (perlu kontrol izin).
- Warehouse grup tidak dapat dipakai dalam transaksi.

## Harus Diverifikasi di Site Uji Sebelum Diterima

- Material Transfer Serial No antar Warehouse (perilaku field `warehouse` pada Serial No).
- Dampak valuasi/GL dengan perpetual inventory. Hipotesis: karena semua Warehouse memakai akun persediaan default yang sama, perpindahan antar Warehouse tidak menimbulkan selisih GL. Belum diuji.
- Material Receipt bag dengan valuation rate nol.

## Urutan Penghapusan (Setelah Diterima)

1. Kode pengganti siap atau Bag Fill Log dipensiunkan.
2. Hapus Inventory Dimension `WMS Location`, lalu verifikasi Custom Field `wms_location` hilang (kecuali 3 field Item/Serial No milik WMS).
3. Hapus record WMS Location dan WMS Location State.
4. Patch untuk menghapus DocType terkait.
5. `git rm` file terkait; bersihkan `hooks.py`, `patches.txt`, dan menu workspace.

Setiap langkah destruktif memerlukan konfirmasi eksplisit dari Efendy.

## Related Decisions

- [ADR-0001: ERPNext Stock as System of Record](ADR-0001-erpnext-stock-as-system-of-record.md)
- [ADR-0003: ERPNext Item and Variant Master](ADR-0003-erpnext-item-and-variant-master.md)
- [ADR-0005: WMS Physical Location Model](ADR-0005-wms-physical-location-model.md) (superseded)
- [ADR-0006: Physical Stock Location Strategy](ADR-0006-physical-stock-location-strategy.md) (superseded)
- [ADR-0007: Wood Pellet Bagging and Weighbridge Boundary](ADR-0007-wood-pellet-bagging-and-weighbridge.md)
