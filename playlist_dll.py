# playlist_dll.py

# Representasi Node
class SongNode:
    """Representasi Node Lagu dalam Double Linked List."""
    def __init__(self, data):
        self.data = data    # Berisi data lagu (dictionary dari DB)
        self.prev = None    
        self.next = None    
# Representasi Double Linked List
class DoubleLinkedListPlaylist:
    """Kelas yang mengelola urutan lagu (Queue) menggunakan Double Linked List."""
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None  # Pointer ke lagu yang sedang dimainkan
        self.size = 0
    
    # --- OPERASI ADD ---
    def add_song(self, song_data):
        """Menambahkan lagu baru ke akhir playlist."""
        new_node = SongNode(song_data)

        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.current = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        
        self.size += 1
        return new_node
    
    # --- OPERASI PLAYBACK (NEXT/DEQUEUE) ---
    def play_next(self):
        """Pindah ke lagu berikutnya."""
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current.data
        return None # Sudah lagu terakhir
    
    # --- OPERASI PLAYBACK (PREVIOUS) ---
    def play_previous(self):
        """Pindah ke lagu sebelumnya (Fitur kunci DLL)."""
        if self.current and self.current.prev:
            self.current = self.current.prev
            return self.current.data
        return None # Sudah lagu pertama