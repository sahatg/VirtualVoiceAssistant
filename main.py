import speech_recognition as sr
import subprocess
import pyautogui
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import webbrowser
import urllib.parse
import pygetwindow as gw
import time
import pystray
from PIL import Image, ImageDraw

# Variabel global untuk menyimpan URL terakhir
last_opened_url = None
# Variabel untuk mode pencarian
search_mode = False
search_type = None  # 'spotify' atau 'youtube'
search_start_time = None
# Variabel untuk system tray dan GUI
tray_icon = None
root = None  # Menyimpan referensi ke jendela utama ### REVISI

# Fungsi untuk membuat ikon default
def create_default_icon():
    image = Image.new("RGB", (64, 64), color="black")
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 54, 54), fill="gray")
    draw.rectangle((28, 20, 36, 44), fill="white")
    return image

# Fungsi buka browser
def open_chrome(url):
    global last_opened_url
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    print(f"🔄 Mencoba membuka {url} dengan Chrome di {chrome_path}")
    try:
        if os.path.exists(chrome_path):
            subprocess.Popen([chrome_path, url])  # Non-blocking
            print(f"✅ Berhasil membuka {url} dengan Chrome")
        else:
            print(f"❌ Chrome tidak ditemukan di {chrome_path}, menggunakan browser default")
            webbrowser.open(url)
            print(f"✅ Berhasil membuka {url} di browser default")
        last_opened_url = url
        print(f"📌 URL terakhir diperbarui: {last_opened_url}")
    except Exception as e:
        print(f"❌ Error saat membuka browser: {e}")

# Fungsi cari lagu di Spotify
def search_spotify(song_name):
    encoded_song = urllib.parse.quote(song_name)
    spotify_url = f"https://open.spotify.com/search/{encoded_song}"
    print(f"🎵 Mencari musik: {song_name} di Spotify")
    open_chrome(spotify_url)

# Fungsi cari lagu atau video di YouTube
def search_youtube(query):
    encoded_query = urllib.parse.quote(query)
    youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    print(f"🎬 Mencari: {query} di YouTube")
    open_chrome(youtube_url)
    time.sleep(5)
    activate_youtube_window()

# Fungsi untuk mengaktifkan jendela YouTube
def activate_youtube_window():
    try:
        windows = gw.getWindowsWithTitle("YouTube")
        if windows:
            youtube_window = windows[0]
            youtube_window.activate()
            time.sleep(0.1)
            print("🟢 Jendela YouTube diaktifkan")
            return True
        else:
            print("❌ Jendela YouTube tidak ditemukan")
            return False
    except Exception as e:
        print(f"❌ Error saat mengaktifkan jendela YouTube: {e}")
        return False

# Fungsi untuk mengaktifkan jendela Chrome
def activate_chrome_window(url):
    try:
        windows = []
        if "youtube" in url.lower():
            windows = gw.getWindowsWithTitle("YouTube")
        elif "spotify" in url.lower():
            windows = gw.getWindowsWithTitle("Spotify")
        elif "facebook" in url.lower():
            windows = gw.getWindowsWithTitle("Facebook")
        elif "google" in url.lower():
            windows = gw.getWindowsWithTitle("Google")
        elif "tik tok" in url.lower():
            windows = gw.getWindowsWithTitle("TikTok")
        elif "shorts" in url.lower():
            windows = gw.getWindowsWithTitle("shorts")
        
        if not windows:
            windows = gw.getWindowsWithTitle("Chrome")
            print(f"🔍 Fallback ke jendela Chrome umum untuk {url}")

        if windows:
            chrome_window = windows[0]
            chrome_window.activate()
            time.sleep(0.5)
            print(f"🟢 Jendela Chrome untuk {url} diaktifkan")
            return True
        else:
            print(f"❌ Jendela Chrome untuk {url} tidak ditemukan")
            return False
    except Exception as e:
        print(f"❌ Error saat mengaktifkan jendela Chrome: {e}")
        return False

# Eksekusi Perintah
def execute_command(command, gui_log, status_label):
    global search_mode, search_type, search_start_time
    command = command.lower()
    print(f"✅ Eksekusi perintah: {command}")
    gui_log.insert(tk.END, f"Perintah: {command}\n")
    gui_log.see(tk.END)

    # Daftar sinonim untuk perintah
    spotify_open_keywords = ["buka spotify", "open spotify", "jalankan spotify", "start spotify"]
    spotify_search_keywords = ["cari lagu", "buka lagu", "mainkan lagu", "putar lagu", "temukan lagu", "search song", "play song"]
    youtube_shorts_keywords = ["buka shorts", "buka video pendek", "shorts youtube"]
    youtube_open_keywords = ["buka youtube", "open youtube", "jalankan youtube", "start youtube"]
    youtube_search_keywords = ["cari video", "buka video", "putar video", "temukan video", "search video", "play video", "tonton video", "lihat video"]
    close_tab_keywords = ["close tab", "tutup tab", "close youtube", "tutup youtube", "close spotify", "tutup spotify", 
                         "close facebook", "tutup facebook", "close google", "tutup google", "close tiktok", "tutup tiktok",
                         "tutup", "keluar tab", "hentikan tab"]

    # Jika dalam mode pencarian
    if search_mode:
        if command:
            if search_type == "spotify":
                gui_log.insert(tk.END, f"Mencari lagu: {command} di Spotify\n")
                search_spotify(command)
            elif search_type == "youtube":
                gui_log.insert(tk.END, f"Mencari video: {command} di YouTube\n")
                search_youtube(command)
            search_mode = False
            search_type = None
            search_start_time = None
            status_label.config(text="Mendengarkan perintah...")
            gui_log.insert(tk.END, "Mode pencarian dimatikan\n")
        else:
            gui_log.insert(tk.END, "Judul tidak dikenali, pencarian dibatalkan\n")
            search_mode = False
            search_type = None
            search_start_time = None
            status_label.config(text="Mendengarkan perintah...")
        gui_log.see(tk.END)
        return False

    # Perintah buka Spotify
    if any(keyword in command for keyword in spotify_open_keywords):
        gui_log.insert(tk.END, "Membuka Spotify...\n")
        open_chrome("https://open.spotify.com")

    # Perintah cari lagu di Spotify
    elif any(keyword in command for keyword in spotify_search_keywords) and "youtube" not in command:
        gui_log.insert(tk.END, "Mode pencarian lagu diaktifkan\n")
        status_label.config(text="Masukkan judul lagu...")
        search_mode = True
        search_type = "spotify"
        search_start_time = time.time()
        gui_log.see(tk.END)
        return False

    # Perintah cari video di YouTube
    elif any(keyword in command for keyword in youtube_search_keywords):
        gui_log.insert(tk.END, "Mode pencarian video diaktifkan\n")
        status_label.config(text="Masukkan judul video...")
        search_mode = True
        search_type = "youtube"
        search_start_time = time.time()
        gui_log.see(tk.END)
        return False

    # Perintah buka YouTube
    elif any(keyword in command for keyword in youtube_open_keywords):
        gui_log.insert(tk.END, "Membuka YouTube...\n")
        open_chrome("https://youtube.com")

    #Perintah buka YouTube
    elif any(keyword in command for keyword in youtube_shorts_keywords):
        gui_log.insert(tk.END, "Membuka YouTube Shorts...\n")
        open_chrome("https://www.youtube.com/shorts/")    

    # Perintah tutup tab
    elif any(keyword in command for keyword in close_tab_keywords):
        gui_log.insert(tk.END, "Menutup tab...\n")
        if last_opened_url:
            if activate_chrome_window(last_opened_url):
                pyautogui.hotkey("ctrl", "w")
                gui_log.insert(tk.END, f"Tab untuk {last_opened_url} ditutup\n")
            else:
                pyautogui.hotkey("ctrl", "w")
                gui_log.insert(tk.END, "Tab aktif ditutup (fallback)\n")
        else:
            gui_log.insert(tk.END, "Tidak ada tab yang dibuka sebelumnya\n")

    # Perintah lain
    elif "klik video 1" in command:
        gui_log.insert(tk.END, "Mengklik video pertama...\n")
        if activate_youtube_window():
            pyautogui.click(x=424, y=290)
            time.sleep(1)
            gui_log.insert(tk.END, "Video pertama diklik\n")
        else:
            gui_log.insert(tk.END, "Jendela YouTube tidak ditemukan\n")
    elif "play" in command or "mainkan" in command:
        gui_log.insert(tk.END, "Memutar video...\n")
        if activate_youtube_window():
            pyautogui.click(x=426, y=320)
            gui_log.insert(tk.END, "Video diputar\n")
        else:
            gui_log.insert(tk.END, "Jendela YouTube tidak ditemukan\n")
    elif "pause" in command or "stop" in command or "jeda" in command:
        gui_log.insert(tk.END, "Menjeda video...\n")
        if activate_youtube_window():
            pyautogui.click(x=426, y=320)
            gui_log.insert(tk.END, "Video dijeda\n")
        else:
            gui_log.insert(tk.END, "Jendela YouTube tidak ditemukan\n")
    elif "facebook" in command:
        gui_log.insert(tk.END, "Membuka Facebook...\n")
        open_chrome("https://facebook.com")
    elif "google" in command:
        gui_log.insert(tk.END, "Membuka Google...\n")
        open_chrome("https://google.com")
    elif "tik tok" in command:
        gui_log.insert(tk.END, "Membuka TikTok...\n")
        open_chrome("https://www.tiktok.com")
    elif "scroll down" in command or "turun" in command:
        gui_log.insert(tk.END, "Scroll ke bawah...\n")
        for _ in range(5):
            pyautogui.scroll(-100)
        gui_log.insert(tk.END, "Scroll ke bawah selesai\n")
    elif "shorts" in command or "video pendek" in command:
        gui_log.insert(tk.END, "Membuka shorts...\n")
        open_chrome("https://www.youtube.com/shorts/")    
    elif "scroll up" in command or "naik" in command:
        gui_log.insert(tk.END, "Scroll ke atas...\n")
        for _ in range(5):
            pyautogui.scroll(100)
        gui_log.insert(tk.END, "Scroll ke atas selesai\n")
    elif "exit" in command or "berhenti" in command:
        gui_log.insert(tk.END, "Program dihentikan\n")
        os._exit(0)
    elif "reset" in command:
        gui_log.insert(tk.END, "Reset ke mode wake word\n")
        status_label.config(text="Mendengarkan wake word...")
        return True
    else:
        gui_log.insert(tk.END, "Perintah tidak dikenali\n")
    gui_log.see(tk.END)
    return False

# Fungsi mendengarkan wake word
def listen_for_wake_word(recognizer, mic_index, gui_log, status_label):
    with sr.Microphone(device_index=mic_index) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.dynamic_energy_threshold = True
        print("🎤 Mikrofon dikalibrasi")
        gui_log.insert(tk.END, "Mikrofon dikalibrasi\n")
        gui_log.see(tk.END)
        status_label.config(text="Mendengarkan wake word...")
        try:
            audio = recognizer.listen(source, timeout=5)
            phrase = recognizer.recognize_google(audio, language="id-ID").lower()
            print(f"🔎 Detected phrase: {phrase}")
            gui_log.insert(tk.END, f"Frasa terdeteksi: {phrase}\n")
            gui_log.see(tk.END)
            return phrase
        except sr.UnknownValueError:
            print("🛑 Tidak dikenali")
            gui_log.insert(tk.END, "Frasa tidak dikenali\n")
            return None
        except sr.WaitTimeoutError:
            print("🛑 Timeout, tidak ada suara terdeteksi")
            gui_log.insert(tk.END, "Timeout, tidak ada suara\n")
            return None
        except sr.RequestError as e:
            print(f"❌ RequestError: {e}")
            gui_log.insert(tk.END, f"Error: {e}\n")
            return None
        except Exception as e:
            print(f"❌ Error umum: {e}")
            gui_log.insert(tk.END, f"Error: {e}\n")
            return None

# Fungsi mendengarkan perintah
def listen_for_command(recognizer, mic_index, is_search_mode=False, gui_log=None, status_label=None):
    with sr.Microphone(device_index=mic_index) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        recognizer.pause_threshold = 1.5
        if is_search_mode:
            status_label.config(text="Masukkan judul lagu/video...")
            gui_log.insert(tk.END, "Menunggu judul lagu/video...\n")
            time.sleep(1)
        else:
            status_label.config(text="Mendengarkan perintah...")
            gui_log.insert(tk.END, "Mendengarkan perintah...\n")
        gui_log.see(tk.END)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10 if is_search_mode else 7)
            command = recognizer.recognize_google(audio, language="id-ID").lower()
            print(f"🔎 Detected command: {command}")
            gui_log.insert(tk.END, f"Perintah terdeteksi: {command}\n")
            gui_log.see(tk.END)
            return command
        except sr.UnknownValueError:
            print("🛑 Perintah tidak dikenali (UnknownValueError)")
            gui_log.insert(tk.END, "Perintah tidak dikenali\n")
            return None
        except sr.WaitTimeoutError:
            print("🛑 Timeout, tidak ada suara terdeteksi")
            gui_log.insert(tk.END, "Timeout, tidak ada suara\n")
            return None
        except sr.RequestError as e:
            print(f"❌ RequestError pada perintah: {e}")
            gui_log.insert(tk.END, f"Error: {e}\n")
            return None
        except Exception as e:
            print(f"❌ Error mendengar perintah: {e}")
            gui_log.insert(tk.END, f"Error: {e}\n")
            return None

# Fungsi utama loop asisten
def assistant_loop(gui_log, status_label):
    global search_mode, search_type, search_start_time
    recognizer = sr.Recognizer()
    mic_index = 1
    while True:
        phrase = listen_for_wake_word(recognizer, mic_index, gui_log, status_label)
        if phrase and ("hey assistant" in phrase or "hei asisten" in phrase or "hai asisten" in phrase):
            gui_log.insert(tk.END, "Mode perintah diaktifkan\n")
            gui_log.see(tk.END)
            break
    with sr.Microphone(device_index=mic_index) as source:
        recognizer.pause_threshold = 1.5
        while True:
            if search_mode and search_start_time and (time.time() - search_start_time > 15):
                print("⏰ Mode pencarian dibatalkan karena timeout (15 detik)")
                gui_log.insert(tk.END, "Pencarian dibatalkan (timeout 15 detik)\n")
                status_label.config(text="Mendengarkan perintah...")
                search_mode = False
                search_type = None
                search_start_time = None
                gui_log.see(tk.END)

            command = listen_for_command(recognizer, mic_index, search_mode, gui_log, status_label)
            if command:
                reset = execute_command(command, gui_log, status_label)
                if reset:
                    gui_log.insert(tk.END, "Kembali ke mode wake word\n")
                    gui_log.see(tk.END)
                    break
            elif search_mode:
                print("❌ Judul tidak dikenali, mode pencarian dibatalkan")
                gui_log.insert(tk.END, "Judul tidak dikenali, pencarian dibatalkan\n")
                status_label.config(text="Mendengarkan perintah...")
                search_mode = False
                search_type = None
                search_start_time = None
                gui_log.see(tk.END)

# Fungsi untuk menampilkan GUI ### REVISI
def show_gui(gui_log):
    global root
    try:
        print("🔍 Mencoba menampilkan GUI")
        gui_log.insert(tk.END, "Mencoba menampilkan GUI\n")
        gui_log.see(tk.END)
        if root:
            root.deiconify()  # Mengembalikan jendela jika diikonifikasi
            root.lift()  # Membawa jendela ke depan
            root.focus_force()  # Memaksa fokus ke jendela
            print("✅ GUI ditampilkan")
            gui_log.insert(tk.END, "GUI ditampilkan\n")
            gui_log.see(tk.END)
        else:
            print("❌ Root GUI tidak tersedia")
            gui_log.insert(tk.END, "Error: GUI tidak tersedia\n")
            gui_log.see(tk.END)
    except Exception as e:
        print(f"❌ Error saat menampilkan GUI: {e}")
        gui_log.insert(tk.END, f"Error menampilkan GUI: {e}\n")
        gui_log.see(tk.END)

# Fungsi untuk membuat system tray ### REVISI
def create_system_tray(gui_log, status_label):
    global tray_icon
    try:
        icon_image = Image.open("assistant_icon.ico")
    except:
        icon_image = create_default_icon()
    tray_icon = pystray.Icon("Voice Assistant", icon_image, "Voice Assistant", menu=pystray.Menu(
        pystray.MenuItem("Show GUI", lambda: show_gui(gui_log)), ### REVISI
        pystray.MenuItem("Exit", lambda: exit_program(gui_log, status_label))
    ))
    tray_icon.run()

# Fungsi untuk menghentikan program
def exit_program(gui_log, status_label):
    global tray_icon, root
    tray_icon.stop()
    gui_log.insert(tk.END, "Program dihentikan dari system tray\n")
    gui_log.see(tk.END)
    if root:
        root.destroy()  # Menutup jendela GUI ### REVISI
    os._exit(0)

# Animasi teks berdenyut
def pulse_animation(label, text, count=0):
    dots = "." * (count % 4)
    label.config(text=text + dots)
    label.after(500, pulse_animation, label, text, count + 1)

# GUI Modern
def start_gui():
    global root
    root = tk.Tk()
    root.title("Voice Assistant")
    root.geometry("400x500")
    root.configure(bg="#1e1e2f")
    root.resizable(False, False)

    # Gaya modern
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10, "bold"), padding=10)
    style.configure("TLabel", background="#1e1e2f", foreground="white")

    # Logo (placeholder, ganti dengan .png jika ada)
    try:
        logo_img = tk.PhotoImage(file="assistant_logo.png")
        logo_label = tk.Label(root, image=logo_img, bg="#1e1e2f")
        logo_label.image = logo_img
    except:
        logo_label = tk.Label(root, text="🎤 Voice Assistant", font=("Arial", 16, "bold"), fg="#00b7eb", bg="#1e1e2f")
    logo_label.pack(pady=10)

    # Status label
    status_label = tk.Label(root, text="Mendengarkan wake word...", font=("Arial", 12), fg="#00b7eb", bg="#1e1e2f")
    status_label.pack(pady=5)
    pulse_animation(status_label, "Mendengarkan wake word")

    # Log area
    log_frame = tk.Frame(root, bg="#1e1e2f")
    log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    gui_log = scrolledtext.ScrolledText(log_frame, height=15, width=40, bg="#2a2a3a", fg="white", font=("Arial", 10))
    gui_log.pack(fill=tk.BOTH, expand=True)
    gui_log.insert(tk.END, "Voice Assistant dimulai\n")
    gui_log.config(state="normal")

    # Tombol kontrol
    button_frame = tk.Frame(root, bg="#1e1e2f")
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Reset", command=lambda: execute_command("reset", gui_log, status_label)).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Exit", command=lambda: exit_program(gui_log, status_label)).pack(side=tk.LEFT, padx=5)

    return root, gui_log, status_label

def run_gui(): ### REVISI
    global root
    root, gui_log, status_label = start_gui()
    tray_thread = threading.Thread(target=create_system_tray, args=(gui_log, status_label))
    tray_thread.daemon = True
    tray_thread.start()

    try:
        while True:
            assistant_loop(gui_log, status_label)
    except KeyboardInterrupt:
        exit_program(gui_log, status_label)
    root.mainloop()

if __name__ == "__main__":
    run_gui()