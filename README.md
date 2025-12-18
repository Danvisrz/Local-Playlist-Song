playlist_dll.py (struktur data inti/ dll/ pembentukan node dsb) :
Ini adalah "jantung" dari penggunaan struktur data dalam proyek ini.
class SongNode: Menggunakan atribut self.next dan self.prev. Inilah identitas utama Double Linked List (bisa menunjuk ke depan dan ke belakang).
self.head & self.tail: Pointer untuk menandai awal dan akhir antrean (Queue).
self.current: Pointer khusus dalam DLL yang menandai lagu mana yang sedang aktif di memori.
Metode add_song: Ini adalah operasi Enqueue (menambah ke antrean). Logikanya menyambungkan pointer next dan prev secara dua arah.
Metode play_next: Operasi navigasi maju menggunakan self.current.next.
Metode play_previous: Operasi navigasi mundur menggunakan self.current.prev.

data_manager.py & audiogui.py (pembuatan dan penyimpanan file):
Bagian ini mengatur bagaimana Queue (antrean) dibentuk secara permanen.
Pemilihan Lagu di Main Page: Saat Anda memilih lagu, urutan klik Anda disimpan dalam list Python. Ini adalah tahap pembentukan urutan antrean (Queue Formation).
Kolom song_order di Database: Di data_manager.py, urutan antrean disimpan menggunakan angka integer (1, 2, 3...). Ini adalah cara menjaga struktur Queue tetap konsisten meskipun aplikasi ditutup.
Fungsi add_song_to_existing_playlist: Menambahkan lagu ke urutan song_order paling akhir. Ini secara teknis adalah operasi Enqueue pada database.

audiogui.py (logika pemutaran musik) :
Bagian ini adalah tempat DLL bekerja secara real-time di memori komputer.
Fungsi show_playlist_detail_page: Saat playlist dimuat, data dari MySQL dikonversi menjadi objek DoubleLinkedListPlaylist. Ini adalah proses transfer data dari database ke struktur data DLL.
Tombol handle_next: Memanggil fungsi DLL untuk memajukan pointer ke lagu berikutnya.
Tombol handle_previous: Memanggil fungsi DLL untuk memundurkan pointer ke lagu sebelumnya.
Fungsi handle_shuffle_from_bar:
Mengambil semua data dari DLL saat ini ke list.
Diacak menggunakan random.shuffle.
Membangun ulang DLL baru dari hasil acakan tersebut.
Fungsi handle_playlist_skip & check_song_end: Logika yang mendeteksi akhir antrean (End of Queue). Jika mencapai ujung DLL (node.next adalah None), ia akan berhenti atau kembali ke head (Loop).

Loop Logic in audiogui.py:
handle_playlist_skip (Mode Loop ON): Saat mencapai tail (akhir antrean), pointer DLL dipaksa lompat kembali ke head (awal antrean). Ini mengubah perilaku Linear Queue menjadi Circular Queue secara logis.
