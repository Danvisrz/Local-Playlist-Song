# gui_audio.py - KODE FINAL TANPA FITUR SEEK

import tkinter as tk
from tkinter import messagebox
import os
import pygame 
import random 

# --- Import semua fungsi DB dan Kelas DLL ---
from data_manager import (
    get_all_available_songs, 
    create_new_playlist, 
    get_all_playlists, 
    load_songs_for_playlist,
    delete_playlist,          
    remove_song_from_playlist,
    add_song_to_existing_playlist
)
from playlist_dll import DoubleLinkedListPlaylist

# --- Pengaturan Warna Dark Mode ---
COLOR_BG_DARK = "#121212"    
COLOR_BG_MEDIUM = "#1E1E1E"  
COLOR_HIGHLIGHT = "#1DB954"  
COLOR_TEXT_LIGHT = "#FFFFFF" 

# --- Variabel Global Logika ---
current_playlist_dll = None
selected_song_ids = []
available_songs = get_all_available_songs() 

# --- INISIALISASI PYGAME MIXER ---
try:
    pygame.mixer.init()
    print("Pygame Mixer berhasil diinisialisasi.")
except pygame.error as e:
    print(f"Gagal inisialisasi Pygame Mixer: {e}")

class PlaylistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Playlist App")
        self.root.geometry("800x600")
        self.root.configure(bg=COLOR_BG_DARK)

        self.current_song_label = None 
        self.btn_play = None 
        self.is_playing = False
        self.loop_mode = False

        self.root.after(100, self.check_song_end)

        self.main_frame = tk.Frame(root, bg=COLOR_BG_DARK)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.content_frame = tk.Frame(self.main_frame, bg=COLOR_BG_DARK)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.player_frame = tk.Frame(self.main_frame, bg=COLOR_BG_MEDIUM, relief=tk.RAISED, borderwidth=1)
        self.player_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        self.setup_player_bar()
        
        self.show_main_page() 

    # ----------------------------------------------------
    # FUNGSI PEMUTARAN AUDIO
    # ----------------------------------------------------
    def play_song(self, file_path):
        """Memutar file audio menggunakan pygame.mixer."""
        
        if not pygame.mixer.get_init():
             messagebox.showerror("Audio Error", "Pygame Mixer gagal diinisialisasi.")
             return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error File", f"File tidak ditemukan di path: {file_path}")
            return
            
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(file_path)
            
            # Memutar lagu HANYA SEKALI. Logika loop playlist ditangani oleh check_song_end.
            pygame.mixer.music.play(loops=0) 
            
            self.is_playing = True
            self.btn_play.config(text="|| PAUSE")
            
        except pygame.error as e:
            messagebox.showerror("Audio Error", f"Gagal memutar lagu: {e}")

    def handle_play_pause(self):
        """Mengontrol Play, Pause, dan Unpause."""
        global current_playlist_dll
        if not current_playlist_dll or not current_playlist_dll.current:
            messagebox.showwarning("Warning", "Tidak ada lagu yang dimuat untuk dimainkan.")
            return
        if not pygame.mixer.get_init():
             messagebox.showerror("Audio Error", "Pygame Mixer gagal diinisialisasi.")
             return

        if self.is_playing:
            # 1. Jika sedang Play, lakukan Pause
            pygame.mixer.music.pause()
            self.is_playing = False
            self.btn_play.config(text="▶ PLAY")
            
        else:
            # 2. Jika sedang Pause atau Stop
            current_song = current_playlist_dll.current.data
            
            # Cek apakah lagu sedang di-pause (musik sudah dimuat tapi tidak aktif)
            # Pygame tidak memiliki fungsi is_paused(), jadi kita bergantung pada get_busy()
            
            # Jika mixer tidak sedang 'busy' (tidak memutar), dan lagu sudah di-load sebelumnya, 
            # maka panggil unpause.
            if pygame.mixer.music.get_busy() == 0 and pygame.mixer.music.get_pos() > 0:
                 # Jika tidak sedang busy TAPI get_pos > 0 (berarti sudah diputar sebelumnya/di-pause)
                 pygame.mixer.music.unpause()
            elif pygame.mixer.music.get_busy() == 0:
                 # Jika tidak sedang busy DAN get_pos = 0 (baru di-load atau stop total)
                 self.play_song(current_song['file_path'])
            else:
                 # Jika statusnya adalah stop (0 pos), kita play ulang
                 self.play_song(current_song['file_path'])
                
            self.is_playing = True
            self.btn_play.config(text="|| PAUSE")

    # ----------------------------------------------------
    # SETUP PLAYER BAR (VERSI SIMPLE TANPA SEEK)
    # ----------------------------------------------------
    def setup_player_bar(self):
        # Label Current Song
        self.current_song_label = tk.Label(self.player_frame, text="Current Song: None (No Playlist Loaded)", anchor="w", 
                                           bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT)
        self.current_song_label.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        
        self.seek_frame = tk.Frame(self.player_frame, bg=COLOR_BG_MEDIUM)
        self.seek_frame.pack(side=tk.RIGHT, padx=5, pady=5)

        # Tombol Next
        tk.Button(self.player_frame, text="Next >>", bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK, 
                  activebackground=COLOR_HIGHLIGHT, command=self.handle_next).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Tombol Previous
        tk.Button(self.player_frame, text="<< Previous", bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK, 
                  activebackground=COLOR_HIGHLIGHT, command=self.handle_previous).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Tombol Play/Pause
        self.btn_play = tk.Button(self.player_frame, text="▶ PLAY", bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK, command=self.handle_play_pause)
        self.btn_play.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # --- TOMBOL SHUFFLE ---
        # Karena shuffle memerlukan info playlist_id, kita harus membuat logika yang berbeda.
        # Kita akan membuat tombol ini memanggil fungsi shuffle TANPA parameter ID, 
        # dan fungsi shuffle akan mengambil ID dari playlist yang sedang dimuat (DLL).
        
        tk.Button(self.seek_frame, text="🔀 SHUFFLE", 
                  bg='#008CBA', fg=COLOR_TEXT_LIGHT, 
                  command=self.handle_shuffle_from_bar).pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.btn_loop = tk.Button(self.seek_frame, text="🔁 Loop OFF", 
                                  bg='#444444', fg=COLOR_TEXT_LIGHT, # Warna abu-abu default
                                  command=self.toggle_loop_mode)
        self.btn_loop.pack(side=tk.RIGHT, padx=5, pady=5)

    # ----------------------------------------------------
    # HANDLE NEXT/PREVIOUS (INTI DLL)
    # ----------------------------------------------------
    def update_current_song_display(self, song_data=None):
        if song_data:
            text = f"Playing: {song_data['title']} - {song_data['artist']}"
        else:
            text = "Current Song: None (No Playlist Loaded)"
        self.current_song_label.config(text=text)

    def handle_next(self):
        global current_playlist_dll
        if current_playlist_dll:
            next_song = current_playlist_dll.play_next()
            if next_song:
                self.update_current_song_display(next_song)
                self.play_song(next_song['file_path']) 
            else:
                messagebox.showinfo("Akhir Playlist", "Sudah lagu terakhir.")

    def handle_previous(self):
        global current_playlist_dll
        if current_playlist_dll:
            prev_song = current_playlist_dll.play_previous()
            if prev_song:
                self.update_current_song_display(prev_song)
                self.play_song(prev_song['file_path']) 
            else:
                messagebox.showinfo("Awal Playlist", "Sudah lagu pertama.")


    # ----------------------------------------------------
    # FUNGSI SHUFFLE (DIJAGA)
    # ----------------------------------------------------

    def handle_shuffle_from_bar(self):
        """
        Fungsi yang dipanggil dari Player Bar. 
        Memerlukan playlist yang sedang dimuat (current_playlist_dll).
        """
        global current_playlist_dll
        
        if not current_playlist_dll or not current_playlist_dll.head:
            messagebox.showwarning("Shuffle Gagal", "Belum ada playlist yang dimuat ke Player Bar. Muat playlist terlebih dahulu.")
            return

        # Kita memerlukan ID playlist dan nama. Karena DLL hanya menyimpan data lagu, 
        # kita asumsikan jika DLL dimuat, kita bisa melakukan shuffle langsung pada Node DLL.
        # Namun, untuk shuffle yang benar (mengambil dari DB dan mengacaknya), 
        # kita butuh ID.
        
        # Solusi Cepat: Lakukan shuffle pada DLL yang ada di memori.
        # Kelemahan: Jika DLL dimuat dari DB, kita harus tahu ID-nya. 
        # Solusi Terbaik: Ketika playlist dimuat, simpan ID-nya di variabel instance.
        
        # Untuk menyederhanakan, kita akan membuat logika shuffle langsung bekerja pada Nodes DLL yang ada di memori.

        songs_data_list = []
        current_node = current_playlist_dll.head
        
        # 1. Ekstrak data dari DLL ke list Python
        while current_node:
            songs_data_list.append(current_node.data)
            current_node = current_node.next
            
        if not songs_data_list:
             messagebox.showwarning("Shuffle Gagal", "Playlist kosong.")
             return

        # 2. Acak list data
        random.shuffle(songs_data_list)
        
        # 3. Buat DLL baru dari urutan yang sudah diacak
        new_dll = DoubleLinkedListPlaylist()
        for song_data in songs_data_list:
            new_dll.add_song(song_data)
            
        # 4. Ganti DLL global
        current_playlist_dll = new_dll
        
        # 5. Atur current ke head dan mulai putar
        current_playlist_dll.current = current_playlist_dll.head
        self.update_current_song_display(current_playlist_dll.current.data)
        self.play_song(current_playlist_dll.current.data['file_path']) 
        
        messagebox.showinfo("Shuffle Berhasil", "Urutan pemutaran telah diacak! Gunakan tombol Next/Previous.")
        
    def handle_shuffle(self, playlist_id, playlist_name):
        """
        Mengambil semua lagu dari playlist, mengacak urutannya,
        dan memuat ulang current_playlist_dll dengan urutan acak tersebut.
        """
        global current_playlist_dll
        
        songs_in_order = load_songs_for_playlist(playlist_id)
        
        if not songs_in_order:
            messagebox.showwarning("Shuffle Gagal", "Playlist kosong, tidak ada yang bisa diacak.")
            return

        shuffled_songs = songs_in_order[:] 
        random.shuffle(shuffled_songs)
        
        new_dll = DoubleLinkedListPlaylist()
        for song_data in shuffled_songs:
            new_dll.add_song(song_data)
            
        current_playlist_dll = new_dll
        
        if current_playlist_dll.head:
            current_playlist_dll.current = current_playlist_dll.head
            self.update_current_song_display(current_playlist_dll.current.data)
            self.play_song(current_playlist_dll.current.data['file_path']) 
            
            messagebox.showinfo("Shuffle Berhasil", 
                                f"Playlist '{playlist_name}' telah diacak! Urutan pemutaran baru telah dimuat ke Player Bar.")

    # ----------------------------------------------------
    # LOGIKA LOOP PLAYLIST
    # ----------------------------------------------------

    def toggle_loop_mode(self):
        """Mengaktifkan atau menonaktifkan mode loop playlist."""
        
        self.loop_mode = not self.loop_mode # Toggle status

        if self.loop_mode:
            self.btn_loop.config(text="🔁 Loop Playlist ON", bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK)
            messagebox.showinfo("Loop Status", "Mode Loop Playlist ON. Setelah lagu terakhir, playlist akan diulang dari awal.")
        else:
            self.btn_loop.config(text="🔁 Loop Playlist OFF", bg='#444444', fg=COLOR_TEXT_LIGHT)
            messagebox.showinfo("Loop Status", "Mode Loop Playlist OFF. Playlist akan berhenti setelah lagu terakhir.")

    def check_song_end(self):
        """Memeriksa apakah lagu yang sedang diputar telah selesai."""
        global current_playlist_dll
        
        # Pastikan mixer diinisialisasi dan ada DLL yang dimuat
        if current_playlist_dll and pygame.mixer.get_init():
            # Jika self.is_playing TRUE (kita tahu kita harus memutar) 
            # DAN pygame.mixer.music.get_busy() FALSE (lagu sudah selesai atau dihentikan)
            if self.is_playing and not pygame.mixer.music.get_busy():
                
                # Cek tambahan: Jika posisi lagu di mixer mendekati nol, 
                # ini berarti lagu baru saja selesai (bukan di-pause atau stop manual)
                if pygame.mixer.music.get_pos() == -1: 
                    # Pygame mengembalikan -1 setelah lagu selesai diputar
                    self.handle_playlist_skip()
                # Jika get_pos() > 0 dan get_busy() = 0, kemungkinan besar itu manual stop/pause.
                
                # Kita akan menggunakan logika sederhana: jika tidak busy, maka panggil skip.
                # Ini akan memaksa lagu berikutnya dimuat secara otomatis.
                else:
                    self.handle_playlist_skip()
            
        # Jadwalkan pengecekan ini lagi dalam 100ms
        self.root.after(100, self.check_song_end)

    def handle_playlist_skip(self):
        """Menentukan lagu berikutnya atau mengulang playlist (loop) jika lagu selesai."""
        global current_playlist_dll

        if not current_playlist_dll or not current_playlist_dll.current:
            self.is_playing = False
            self.btn_play.config(text="▶ PLAY")
            return

        next_song_data = current_playlist_dll.current.next
        
        if next_song_data:
            # 1. Jika ada lagu berikutnya, pindah dan putar
            self.handle_next() 
            
        elif self.loop_mode:
            # 2. Jika sudah lagu terakhir DAN Loop Mode ON
            if current_playlist_dll.head:
                current_playlist_dll.current = current_playlist_dll.head
                new_song = current_playlist_dll.current.data
                self.update_current_song_display(new_song)
                self.play_song(new_song['file_path'])
            else:
                self.is_playing = False
                self.btn_play.config(text="▶ PLAY")
                
        else:
            # 3. Jika sudah lagu terakhir DAN Loop Mode OFF, hentikan.
            pygame.mixer.music.stop()
            self.is_playing = False
            self.btn_play.config(text="▶ PLAY")
            messagebox.showinfo("Playback Selesai", "Playlist telah selesai diputar.")

    # ----------------------------------------------------
    # HALAMAN UTAMA & CRUD PLAYLIST (KODE LAMA TETAP SAMA)
    # ----------------------------------------------------
    
    def show_main_page(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Pilih Lagu untuk Playlist Baru", 
                 font=('Arial', 14, 'bold'), bg=COLOR_BG_DARK, fg=COLOR_TEXT_LIGHT).pack(pady=10)
        
        tk.Button(self.content_frame, text="<< Go to My Playlists", 
                  bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT, 
                  command=self.show_playlist_list_page).pack(pady=5)
        
        list_frame = tk.Frame(self.content_frame, bg=COLOR_BG_DARK)
        list_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(list_frame, text="Daftar Lagu:", 
                 bg=COLOR_BG_DARK, fg=COLOR_HIGHLIGHT).pack(padx=5, pady=5, anchor='w')

        self.song_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, 
                                      bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT, 
                                      selectbackground=COLOR_HIGHLIGHT, selectforeground=COLOR_BG_DARK)
        self.song_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        global available_songs
        for song in available_songs:
            self.song_listbox.insert(tk.END, f"ID {song['song_id']}: {song['title']} - {song['artist']}")
        
        btn_add = tk.Button(self.content_frame, text="+ Buat Playlist Baru", 
                            bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK, activebackground=COLOR_HIGHLIGHT,
                            command=self.open_naming_popup)
        btn_add.pack(pady=10)
        
    def open_naming_popup(self):
        global selected_song_ids
        selected_indices = self.song_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Peringatan", "Pilih minimal satu lagu!")
            return

        selected_song_ids = [available_songs[i]['song_id'] for i in selected_indices]
        
        self.popup = tk.Toplevel(self.root, bg=COLOR_BG_DARK)
        self.popup.title("Nama Playlist Baru")
        
        tk.Label(self.popup, text="Masukkan Nama Playlist:", bg=COLOR_BG_DARK, fg=COLOR_TEXT_LIGHT).pack(padx=10, pady=5)
        self.playlist_name_entry = tk.Entry(self.popup, width=40, bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT)
        self.playlist_name_entry.pack(padx=10, pady=5)
        
        btn_finish = tk.Button(self.popup, text="Finish & Simpan", bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK, 
                               activebackground=COLOR_HIGHLIGHT, command=self.save_new_playlist)
        btn_finish.pack(pady=10)

    def save_new_playlist(self):
        playlist_name = self.playlist_name_entry.get().strip()
        
        if not playlist_name:
            messagebox.showwarning("Peringatan", "Nama playlist tidak boleh kosong.")
            return

        global selected_song_ids
        
        if create_new_playlist(playlist_name, selected_song_ids):
            messagebox.showinfo("Berhasil", f"Playlist '{playlist_name}' berhasil dibuat dan lagu diurutkan (Queue) di database!")
            self.popup.destroy()
            self.show_playlist_list_page() 
        else:
            messagebox.showerror("Gagal", "Gagal menyimpan playlist ke database.")
            self.popup.destroy()
            
    def show_playlist_list_page(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="DAFTAR PLAYLIST ANDA", 
                 font=('Arial', 14, 'bold'), bg=COLOR_BG_DARK, fg=COLOR_TEXT_LIGHT).pack(pady=10)
        
        playlists = get_all_playlists()

        if not playlists:
            tk.Label(self.content_frame, text="Belum ada playlist yang dibuat. Kembali ke halaman utama untuk membuat.", 
                     bg=COLOR_BG_DARK, fg=COLOR_TEXT_LIGHT).pack(pady=20)
        else:
            tk.Label(self.content_frame, text="Pilih Playlist:", 
                     bg=COLOR_BG_DARK, fg=COLOR_HIGHLIGHT).pack(pady=5)
            
            list_container = tk.Frame(self.content_frame, bg=COLOR_BG_DARK)
            list_container.pack(fill=tk.X, padx=10)

            for p in playlists:
                playlist_id = p['playlist_id']
                playlist_name = p['name']
                
                row_frame = tk.Frame(list_container, bg=COLOR_BG_DARK)
                row_frame.pack(pady=3, fill=tk.X)
                
                btn_load_edit = tk.Button(row_frame, 
                                     text=f"{playlist_name}", 
                                     bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT, 
                                     command=lambda pid=playlist_id, pname=playlist_name: self.show_playlist_detail_page(pid, pname))
                btn_load_edit.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                btn_delete = tk.Button(row_frame, text="HAPUS", 
                                       bg='#E30000', fg=COLOR_TEXT_LIGHT, 
                                       command=lambda pid=playlist_id, pname=playlist_name: self.confirm_delete_playlist(pid, pname))
                btn_delete.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(self.content_frame, text="<< Kembali ke Daftar Lagu (Buat Playlist Baru)", 
                  bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT, 
                  command=self.show_main_page).pack(pady=20)

    def confirm_delete_playlist(self, playlist_id, playlist_name):
        if messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus playlist '{playlist_name}'? Tindakan ini tidak dapat dibatalkan."):
            if delete_playlist(playlist_id):
                messagebox.showinfo("Berhasil", f"Playlist '{playlist_name}' berhasil dihapus.")
                self.show_playlist_list_page()
            else:
                messagebox.showerror("Gagal", "Gagal menghapus playlist dari database.")

    def show_playlist_detail_page(self, playlist_id, playlist_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        global current_playlist_dll
        songs_in_order = load_songs_for_playlist(playlist_id)
        
        current_playlist_dll = DoubleLinkedListPlaylist()
        song_data_list = []
        
        for song_data in songs_in_order:
            current_playlist_dll.add_song(song_data)
            song_data_list.append(song_data)

        
        tk.Label(self.content_frame, text=f"{playlist_name}", 
                 font=('Arial', 14, 'bold'), bg=COLOR_BG_DARK, fg=COLOR_HIGHLIGHT).pack(pady=10)
        
        tk.Label(self.content_frame, text="Daftar Lagu (Urutan Queue):", 
                 bg=COLOR_BG_DARK, fg=COLOR_TEXT_LIGHT).pack(pady=5, anchor='w')

        list_frame = tk.Frame(self.content_frame, bg=COLOR_BG_DARK)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.detail_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, 
                                        bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT, 
                                        selectbackground=COLOR_HIGHLIGHT, selectforeground=COLOR_BG_DARK)
        self.detail_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for i, song in enumerate(song_data_list):
            self.detail_listbox.insert(tk.END, f"{i+1}. {song['title']} - {song['artist']} (ID: {song['song_id']})")
        
        button_frame = tk.Frame(self.content_frame, bg=COLOR_BG_DARK)
        button_frame.pack(pady=10)
        
        # Tombol Muat & Play
        tk.Button(button_frame, text="▶ Muat & Play (Uji DLL)", 
                  bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK, 
                  command=lambda: self.load_and_play_from_detail(playlist_name)).pack(side=tk.LEFT, padx=5)
        
        # Tombol Hapus Lagu
        tk.Button(button_frame, text="- Hapus Lagu Terpilih", 
                  bg='#E30000', fg=COLOR_TEXT_LIGHT, 
                  command=lambda: self.delete_selected_song(playlist_id, playlist_name, song_data_list)).pack(side=tk.LEFT, padx=5)
        
        # Tombol Tambah Lagu
        tk.Button(button_frame, text="+ Tambah Lagu", 
                  bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK, 
                  command=lambda: self.open_add_song_popup(playlist_id, playlist_name)).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="<< Kembali ke Daftar Playlist", 
                  bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT, 
                  command=self.show_playlist_list_page).pack(side=tk.LEFT, padx=5)

    def load_and_play_from_detail(self, playlist_name):
        if current_playlist_dll.head:
            current_playlist_dll.current = current_playlist_dll.head
            self.update_current_song_display(current_playlist_dll.current.data)
            self.play_song(current_playlist_dll.current.data['file_path']) 
            self.btn_play.config(text="|| PAUSE") 
            messagebox.showinfo("Player Bar", f"Playlist '{playlist_name}' dimuat. Gunakan tombol Next/Previous.")
        else:
            messagebox.showwarning("Gagal Muat", "Playlist kosong.")
            
    def delete_selected_song(self, playlist_id, playlist_name, song_data_list):
        selected_indices = self.detail_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Peringatan", "Pilih lagu yang ingin dihapus terlebih dahulu.")
            return

        index_to_remove = selected_indices[0]
        song_to_remove = song_data_list[index_to_remove]
        song_id_to_remove = song_to_remove['song_id']
        song_title = song_to_remove['title']
        
        if messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus '{song_title}' dari playlist ini? Ini akan mengubah urutan Queue."):
            if remove_song_from_playlist(playlist_id, song_id_to_remove):
                messagebox.showinfo("Berhasil", f"Lagu '{song_title}' berhasil dihapus dan urutan Queue di-update di database.")
                self.show_playlist_detail_page(playlist_id, playlist_name)
            else:
                messagebox.showerror("Gagal", "Gagal menghapus lagu dari database.")
                
    def open_add_song_popup(self, current_playlist_id, current_playlist_name):
        self.popup_add = tk.Toplevel(self.root, bg=COLOR_BG_DARK)
        self.popup_add.title(f"Tambah Lagu ke {current_playlist_name}")
        
        tk.Label(self.popup_add, text="Pilih Lagu untuk Ditambahkan ke Akhir Queue:", 
                 bg=COLOR_BG_DARK, fg=COLOR_TEXT_LIGHT).pack(padx=10, pady=5)
        
        list_frame = tk.Frame(self.popup_add, bg=COLOR_BG_DARK)
        list_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.add_song_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, 
                                            bg=COLOR_BG_MEDIUM, fg=COLOR_TEXT_LIGHT, 
                                            selectbackground=COLOR_HIGHLIGHT, selectforeground=COLOR_BG_DARK)
        self.add_song_listbox.pack(fill=tk.BOTH, expand=True)

        global available_songs
        for song in available_songs:
            self.add_song_listbox.insert(tk.END, f"ID {song['song_id']}: {song['title']} - {song['artist']}")
            
        btn_save = tk.Button(self.popup_add, text="Tambahkan (Enqueue)", bg=COLOR_HIGHLIGHT, fg=COLOR_BG_DARK, 
                             command=lambda: self.save_added_song(current_playlist_id, current_playlist_name))
        btn_save.pack(pady=10)

    def save_added_song(self, playlist_id, playlist_name):
        selected_indices = self.add_song_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Peringatan", "Pilih satu lagu yang akan ditambahkan.")
            return
            
        index = selected_indices[0]
        song_id_to_add = available_songs[index]['song_id']
        song_title = available_songs[index]['title']
        
        from data_manager import add_song_to_existing_playlist 

        if add_song_to_existing_playlist(playlist_id, song_id_to_add):
            messagebox.showinfo("Berhasil", f"Lagu '{song_title}' berhasil ditambahkan ke akhir Queue di playlist '{playlist_name}'.")
            self.popup_add.destroy()
            self.show_playlist_detail_page(playlist_id, playlist_name)
        else:
            messagebox.showerror("Gagal", f"Gagal menambahkan lagu. Kemungkinan lagu '{song_title}' sudah ada di playlist.")
            self.popup_add.destroy()

if __name__ == '__main__':
    if available_songs:
        root = tk.Tk()
        app = PlaylistApp(root)
        root.mainloop()
    else:
        print("Gagal memuat lagu dari database. Pastikan MySQL berjalan, kredensial benar, dan tabel 'song' terisi.")