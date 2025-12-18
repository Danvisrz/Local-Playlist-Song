import mysql.connector

# --- PENTING: GANTI DENGAN KREDENSIAL MYSQL ANDA ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "", 
    "database": "playlist" 
}
# ----------------------------------------------------

def get_db_connection():
    """Membuat objek koneksi database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error koneksi database: {err}")
        return None

# --- READ: Mengambil semua lagu master ---
def get_all_available_songs():
    """Mengambil semua lagu dari tabel 'song' (untuk Main Page)."""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True) 
    query = "SELECT song_id, title, artist, duration, file_path FROM song ORDER BY title ASC"
    
    try:
        cursor.execute(query)
        songs = cursor.fetchall()
        return songs
    except mysql.connector.Error as err:
        print(f"Error saat mengambil lagu: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- CREATE: Membuat Playlist Baru dan Isi Queue ---
def create_new_playlist(playlist_name, selected_song_ids):
    """
    Membuat playlist baru dan menambahkan lagu-lagu yang dipilih ke dalamnya.
    Urutan list selected_song_ids adalah urutan Queue (song_order).
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()

    try:
        # 1. INSERT ke tabel playlist
        insert_playlist_query = "INSERT INTO playlist (name) VALUES (%s)"
        cursor.execute(insert_playlist_query, (playlist_name,))
        playlist_id = cursor.lastrowid # Ambil ID playlist yang baru dibuat

        # 2. INSERT ke tabel playlist_song (Mengimplementasikan Queue/Urutan)
        insert_playlist_song_query = "INSERT INTO playlist_song (playlist_id, song_id, song_order) VALUES (%s, %s, %s)"
        
        for index, song_id in enumerate(selected_song_ids):
            song_order = index + 1 
            cursor.execute(insert_playlist_song_query, (playlist_id, song_id, song_order))
        
        conn.commit()
        return True
    
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error saat membuat playlist: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- READ: Mengambil Daftar Semua Playlist ---
def get_all_playlists():
    """Mengambil semua playlist (ID dan Nama) dari tabel 'playlist'."""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True) 
    query = "SELECT playlist_id, name FROM playlist ORDER BY name ASC"
    
    try:
        cursor.execute(query)
        playlists = cursor.fetchall()
        return playlists
    except mysql.connector.Error as err:
        print(f"Error saat mengambil daftar playlist: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- READ: Mengambil Lagu Playlist TERTENTU (untuk DLL) ---
def load_songs_for_playlist(playlist_id):
    """
    Mengambil semua lagu dalam playlist tertentu, diurutkan berdasarkan song_order (ASC).
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT 
            s.song_id, s.title, s.artist, s.duration, s.file_path
        FROM 
            playlist_song ps
        JOIN 
            song s ON ps.song_id = s.song_id
        WHERE 
            ps.playlist_id = %s
        ORDER BY 
            ps.song_order ASC;
    """
    
    try:
        cursor.execute(query, (playlist_id,))
        songs = cursor.fetchall()
        return songs
    except mysql.connector.Error as err:
        print(f"Error saat memuat lagu playlist: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

        # data_manager.py (Tambahkan fungsi ini)

# --- DELETE: Menghapus Playlist ---
def delete_playlist(playlist_id):
    """Menghapus playlist dari tabel 'playlist'."""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    # Karena kita menggunakan ON DELETE CASCADE pada tabel playlist_song, 
    # menghapus dari tabel playlist akan otomatis menghapus entri di playlist_song.
    query = "DELETE FROM playlist WHERE playlist_id = %s"
    
    try:
        cursor.execute(query, (playlist_id,))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error saat menghapus playlist: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- DELETE: Menghapus Lagu dari Playlist (Delete Node dari Linked List di DB) ---
def remove_song_from_playlist(playlist_id, song_id_to_remove):
    """
    Menghapus lagu dari playlist dan mengurutkan ulang sisa lagu.
    Ini adalah operasi DELETE pada tabel playlist_song, diikuti UPDATE song_order.
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 1. Hapus lagu dari playlist_song
        delete_query = "DELETE FROM playlist_song WHERE playlist_id = %s AND song_id = %s"
        cursor.execute(delete_query, (playlist_id, song_id_to_remove))
        
        # 2. UPDATE: Urutkan ulang sisa lagu
        # Query untuk mengambil sisa lagu dalam urutan yang benar
        reorder_select_query = "SELECT playlist_song_id FROM playlist_song WHERE playlist_id = %s ORDER BY song_order ASC"
        cursor.execute(reorder_select_query, (playlist_id,))
        songs_to_reorder = cursor.fetchall()
        
        # 3. Looping untuk mengupdate song_order
        update_query = "UPDATE playlist_song SET song_order = %s WHERE playlist_song_id = %s"
        for index, row in enumerate(songs_to_reorder):
            new_order = index + 1
            cursor.execute(update_query, (new_order, row[0])) # row[0] adalah playlist_song_id
            
        conn.commit()
        return True
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error saat menghapus lagu dan re-order: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- CREATE/UPDATE: Menambah Lagu ke Playlist yang Sudah Ada (Enqueue) ---
def add_song_to_existing_playlist(playlist_id, song_id_to_add):
    """
    Menambahkan satu lagu ke akhir (tail) playlist yang sudah ada.
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 1. Cari song_order tertinggi saat ini (atau 0 jika playlist kosong)
        max_order_query = "SELECT MAX(song_order) FROM playlist_song WHERE playlist_id = %s"
        cursor.execute(max_order_query, (playlist_id,))
        result = cursor.fetchone()
        
        current_max_order = result[0] if result[0] is not None else 0
        new_order = current_max_order + 1
        
        # 2. INSERT lagu baru dengan urutan berikutnya (Enqueue)
        insert_query = "INSERT INTO playlist_song (playlist_id, song_id, song_order) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (playlist_id, song_id_to_add, new_order))
        
        conn.commit()
        return True
    
    except mysql.connector.Error as err:
        conn.rollback()
        # Kasus umum: Lagu yang sama sudah ada di playlist (UNIQUE constraint)
        if err.errno == 1062: # Error code for Duplicate entry
            print("Error: Lagu sudah ada di playlist.")
            return False
        
        print(f"Error saat menambahkan lagu ke playlist: {err}")
        return False
    finally:
        cursor.close()
        conn.close()