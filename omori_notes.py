import subprocess
import sys
from PIL import Image, ImageTk
import tkinter as tk

try:
    import pygame
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

pygame.mixer.init()
pygame.mixer.music.load("music/OMORI - Final Duet.mp3")
pygame.mixer.music.play(-1)

def change_music(song):
    pygame.mixer.music.load(f"music/{song}")
    pygame.mixer.music.play(-1)

def show_music_window(event=None):
    music_win = tk.Toplevel(root)
    music_win.title("Music Player")
    music_win.geometry("300x350")
    music_win.resizable(False, False)

    music_bg_img = Image.open("bgi/1148181.png").resize((300, 350))
    music_bg = ImageTk.PhotoImage(music_bg_img)

    music_canvas = tk.Canvas(music_win, width=300, height=350)
    music_canvas.pack(fill="both", expand=True)
    music_canvas.create_image(0, 0, image=music_bg, anchor="nw")
    music_canvas.image = music_bg

    music_canvas.create_text(150, 30, text="Select a Song", font=("Schoolbell", 16), fill="white")

    songs = {
        "OMORI - Final Duet": "OMORI - Final Duet.mp3",
        "Good Morning (8-bit)": "Good Morning [8 Bit VRC6] (Arr. by Kamome Sano) (Ft. Jasminescorner) - OMORI.mp3",
        "OMORI (8-bit Remix)": "OMORI (8-bit remix).mp3"
    }

    for i, (label, filename) in enumerate(songs.items()):
        frame = tk.Frame(music_canvas, bg="white", padx=2, pady=2)
        btn = tk.Button(frame, text=label, font=("Schoolbell", 12), bg="black", fg="white", relief="flat", width=18, command=lambda s=filename: change_music(s))
        btn.pack()
        music_canvas.create_window(150, 80 + i * 55, window=frame)

    music_canvas.create_text(150, 240, text="Volume", font=("Schoolbell", 14), fill="white")

    volume_slider = tk.Scale(music_canvas, from_=0, to=100, orient="horizontal", length=200,
                             bg="black", fg="white", highlightthickness=0, troughcolor="white",
                             command=lambda v: pygame.mixer.music.set_volume(int(v) / 100))
    volume_slider.set(100)
    music_canvas.create_window(150, 280, window=volume_slider)

    close_frame = tk.Frame(music_canvas, bg="white", padx=2, pady=2)
    close_btn = tk.Button(close_frame, text="Close", font=("Schoolbell", 12), bg="black", fg="white", relief="flat", width=18, command=music_win.destroy)
    close_btn.pack()
    music_canvas.create_window(150, 330, window=close_frame)

root = tk.Tk()
root.title("Omori Notes")
icon = tk.PhotoImage(file="bgi/icon/Omori-PNG-Image.png")
root.iconphoto(True, icon)
root.state("zoomed")

root.update()
screen_width = root.winfo_width()
screen_height = root.winfo_height()

bg = tk.PhotoImage(file="bgi/1365265.png")

my_canvas = tk.Canvas(root, width=screen_width, height=screen_height)
my_canvas.pack(fill="both", expand=True)

my_canvas.create_image(screen_width // 2, screen_height // 2, image=bg, anchor="center")

btn_font = ("Schoolbell", 20)

write_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
write_btn = tk.Button(write_frame, text="Write", font=btn_font, bg="black", fg="white", relief="flat", width=10, height=2)
write_btn.pack()

exit_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
exit_btn = tk.Button(exit_frame, text="Exit", font=btn_font, bg="black", fg="white", relief="flat", command=root.destroy, width=10, height=2)
exit_btn.pack()

my_canvas.create_window(int(screen_width * 0.41), int(screen_height * 0.82), window=write_frame)
my_canvas.create_window(int(screen_width * 0.61), int(screen_height * 0.82), window=exit_frame)

char_img = tk.PhotoImage(file="bgi/omori_logo.png")
my_canvas.create_image(680, 340, image=char_img, anchor="center")

logo_pil = Image.open("bgi/music_logo.png").convert("RGBA").resize((300, 300))
logo_img = ImageTk.PhotoImage(logo_pil)
music_icon = my_canvas.create_image(1250, 100, image=logo_img, anchor="center")
my_canvas.tag_bind(music_icon, "<Button-1>", show_music_window)

root.mainloop()