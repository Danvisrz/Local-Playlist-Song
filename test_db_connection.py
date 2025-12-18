from data_manager import get_all_available_songs, create_new_playlist

# 1. Uji READ (Mengambil data master lagu)
available_songs = get_all_available_songs()
print("Daftar Lagu Tersedia (Main Page):")
for song in available_songs:
    print(f"- ID {song['song_id']}: {song['title']} oleh {song['artist']}")

# 2. Uji CREATE (Simulasi user memilih lagu dan menekan 'Finish')
# Kita asumsikan user memilih lagu ID 1, 4, dan 3 dalam urutan tersebut.
selected_ids = [1, 4, 3] 
playlist_name = "Playlist Uji Coba Baru"

if create_new_playlist(playlist_name, selected_ids):
    print(f"\nSUCCESS: Playlist '{playlist_name}' berhasil dibuat dan disimpan ke DB.")
else:
    print("\nFAILED: Gagal membuat playlist.")