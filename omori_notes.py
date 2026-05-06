import subprocess
import sys

# ─── VERSION CHECK ───────────────────────────────────────────────
# Checks if the user is running Python 3.12. If not, opens the
# download page in their browser and exits the program.
if sys.version_info < (3, 12) or sys.version_info >= (3, 13):
    import webbrowser
    print("=" * 50)
    print("Wrong Python version detected!")
    print(f"You are using Python {sys.version_info.major}.{sys.version_info.minor}")
    print("This program requires Python 3.12.")
    print("Opening the download page in your browser...")
    print("=" * 50)
    webbrowser.open("https://www.python.org/downloads/release/python-3120/")
    input("Press Enter to exit...")
    sys.exit()

# ─── AUTO-INSTALL PILLOW ─────────────────────────────────────────
# Tries to import Pillow (for image handling). If not installed,
# automatically installs it and imports it.
try:
    from PIL import Image, ImageTk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageTk

# ─── AUTO-INSTALL PYGAME ─────────────────────────────────────────
# Tries to import pygame (for music playback). If not installed,
# automatically installs it and imports it.
try:
    import pygame
except ImportError:
    if sys.version_info >= (3, 14):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame-ce"])
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

import tkinter as tk

# ─── MUSIC INITIALIZATION ────────────────────────────────────────
# Starts the pygame music mixer and plays the first song on loop
# as soon as the program opens.
pygame.mixer.init()
pygame.mixer.music.load("music/OMORI - Final Duet.mp3")
pygame.mixer.music.play(-1)

# ─── SOUNDS ──────────────────────────────────────────────────────
# Loads the click and hover sounds.
click_sound = pygame.mixer.Sound("sfx/universfield-computer-mouse-click-02-383961.wav")
hover_sound = pygame.mixer.Sound("sfx/dragon-studio-mouse-click-405462.wav")

def play_click():
    click_sound.play()

def play_hover():
    hover_sound.play()

# ─── HOVER EFFECT ────────────────────────────────────────────────
# Changes the button color to grey on hover and back to black on leave.
def on_hover(btn):
    btn.config(bg="#333333")

def on_leave(btn):
    btn.config(bg="black")

# ─── CHANGE MUSIC ────────────────────────────────────────────────
# Loads and plays a new song when the user selects one from
# the music player window. Loops the song indefinitely.
def change_music(song):
    pygame.mixer.music.load(f"music/{song}")
    pygame.mixer.music.play(-1)

# ─── MUSIC WINDOW TRACKER ────────────────────────────────────────
# Keeps track of whether the music window is already open
# to prevent multiple instances from appearing.
music_window_open = None

# ─── MUSIC PLAYER WINDOW ─────────────────────────────────────────
# Opens a separate popup window with a background image, song
# selection buttons, a volume slider, and a close button.
def show_music_window(event=None):
    global music_window_open

    # If the window is already open, just bring it to focus.
    if music_window_open and tk.Toplevel.winfo_exists(music_window_open):
        music_window_open.lift()
        return

    # Get the music icon's position on screen dynamically.
    canvas_x = my_canvas.winfo_rootx()
    canvas_y = my_canvas.winfo_rooty()
    icon_coords = my_canvas.coords(music_icon)
    icon_x = int(canvas_x + icon_coords[0])
    icon_y = int(canvas_y + icon_coords[1])

    music_window_open = tk.Toplevel(root)
    music_window_open.title("Omori Music Player")
    music_window_open.resizable(False, False)

    # Position the window below and to the left of the music icon.
    music_window_open.geometry(f"300x350+{icon_x - 350}+{icon_y + 250}")

    # Loads and displays the background image for the music window.
    music_bg_img = Image.open("bgi/1148181.png").resize((300, 350))
    music_bg = ImageTk.PhotoImage(music_bg_img)

    music_canvas = tk.Canvas(music_window_open, width=300, height=350)
    music_canvas.pack(fill="both", expand=True)
    music_canvas.create_image(0, 0, image=music_bg, anchor="nw")
    music_canvas.image = music_bg

    # Displays the "Select a Song" title text on the music window.
    music_canvas.create_text(150, 30, text="Select a Song", font=("Schoolbell", 16), fill="white")

    # List of songs with their display name and actual filename.
    songs = {
        "OMORI - Final Duet": "OMORI - Final Duet.mp3",
        "Good Morning (8-bit)": "Good Morning [8 Bit VRC6] (Arr. by Kamome Sano) (Ft. Jasminescorner) - OMORI.mp3",
        "OMORI (8-bit Remix)": "OMORI (8-bit remix).mp3"
    }

    # Creates a styled button for each song and places them on the canvas.
    for i, (label, filename) in enumerate(songs.items()):
        frame = tk.Frame(music_canvas, bg="white", padx=2, pady=2)
        btn = tk.Button(frame, text=label, font=("Schoolbell", 12), bg="black", fg="white", relief="flat", width=18, command=lambda s=filename: [play_click(), change_music(s)])
        btn.bind("<Enter>", lambda e, b=btn: [play_hover(), on_hover(b)])
        btn.bind("<Leave>", lambda e, b=btn: on_leave(b))
        btn.pack()
        music_canvas.create_window(150, 80 + i * 55, window=frame)

    # Displays the "Volume" label above the slider.
    music_canvas.create_text(150, 240, text="Volume", font=("Schoolbell", 14), fill="white")

    # Volume slider that adjusts the music volume in real time.
    volume_slider = tk.Scale(music_canvas, from_=0, to=100, orient="horizontal", length=200,
                             bg="black", fg="white", highlightthickness=0, troughcolor="white",
                             command=lambda v: pygame.mixer.music.set_volume(int(v) / 100))
    volume_slider.set(100)
    music_canvas.create_window(150, 280, window=volume_slider)

    # Close button that destroys the music player window.
    close_frame = tk.Frame(music_canvas, bg="white", padx=2, pady=2)
    close_btn = tk.Button(close_frame, text="Close", font=("Schoolbell", 12), bg="black", fg="white", relief="flat", width=18, command=lambda: [play_click(), music_window_open.destroy()])
    close_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(close_btn)])
    close_btn.bind("<Leave>", lambda e: on_leave(close_btn))
    close_btn.pack()
    music_canvas.create_window(150, 330, window=close_frame)

# ─── MAIN WINDOW SETUP ───────────────────────────────────────────
# Creates the main window, sets the title, icon, and maximizes it.
root = tk.Tk()
root.title("Omori Notes")
icon = tk.PhotoImage(file="bgi/icon/Omori-PNG-Image.png")
root.iconphoto(True, icon)
root.state("zoomed")

# Gets the screen width and height after maximizing.
root.update()
screen_width = root.winfo_width()
screen_height = root.winfo_height()

# ─── BACKGROUND IMAGE ────────────────────────────────────────────
# Loads and displays the background image centered on the canvas.
bg = tk.PhotoImage(file="bgi/1365265.png")

my_canvas = tk.Canvas(root, width=screen_width, height=screen_height)
my_canvas.pack(fill="both", expand=True)

my_canvas.create_image(screen_width // 2, screen_height // 2, image=bg, anchor="center")

btn_font = ("Schoolbell", 20)

# ─── WRITE BUTTON ────────────────────────────────────────────────
# A styled button with a white border that will open the notes
# writing feature when clicked.
write_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
write_btn = tk.Button(write_frame, text="Write", font=btn_font, bg="black", fg="white", relief="flat", width=10, height=2, command=play_click)
write_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(write_btn)])
write_btn.bind("<Leave>", lambda e: on_leave(write_btn))
write_btn.pack()

# ─── EXIT BUTTON ─────────────────────────────────────────────────
# A styled button with a white border that closes the program
# when clicked.
exit_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
exit_btn = tk.Button(exit_frame, text="Exit", font=btn_font, bg="black", fg="white", relief="flat", width=10, height=2, command=lambda: [play_click(), root.destroy()])
exit_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(exit_btn)])
exit_btn.bind("<Leave>", lambda e: on_leave(exit_btn))
exit_btn.pack()

# Places both buttons at initial position (moved by place_buttons).
write_window = my_canvas.create_window(0, 0, window=write_frame)
exit_window = my_canvas.create_window(0, 0, window=exit_frame)

# ─── BUTTON PLACEMENT ────────────────────────────────────────────
# Repositions the Write and Exit buttons relative to the window
# size so they stay in the correct spot on any resolution.
def place_buttons():
    w = root.winfo_width()
    h = root.winfo_height()
    my_canvas.coords(write_window, int(w * 0.41), int(h * 0.82))
    my_canvas.coords(exit_window, int(w * 0.61), int(h * 0.82))

# ─── CHARACTER/LOGO IMAGE ────────────────────────────────────────
# Loads and displays the Omori logo image on the canvas.
char_img = tk.PhotoImage(file="bgi/omori_logo.png")
my_canvas.create_image(
    int(screen_width * 0.49),
    int(screen_height * 0.45),
    image=char_img,
    anchor="center"
)

# ─── MUSIC ICON ──────────────────────────────────────────────────
# Loads the music button icon with transparency and places it
# on the canvas. Clicking it opens the music player window.
logo_pil = Image.open("bgi/music_logo.png").convert("RGBA").resize((300, 300))
logo_img = ImageTk.PhotoImage(logo_pil)
music_icon = my_canvas.create_image(
    int(screen_width * 1.0),
    int(screen_height * -0.04),
    image=logo_img,
    anchor="ne"
)
my_canvas.tag_bind(music_icon, "<Button-1>", show_music_window)

# ─── RESPONSIVE LAYOUT ───────────────────────────────────────────
# Calls place_buttons whenever the window is resized to keep
# the buttons in the correct position.
root.bind("<Configure>", lambda e: place_buttons())

# ─── START THE APP ───────────────────────────────────────────────
# Starts the tkinter main loop, keeping the window open.
root.mainloop()