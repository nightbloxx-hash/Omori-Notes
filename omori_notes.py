import subprocess
import sys
import random
import os
import json                          # ← was missing
from datetime import datetime        # ← was missing

QUOTES = [
    "Write what you feel.",
    "Memories fade, notes stay.",
    "Small thoughts matter.",
    "Your mind is a story.",
    "Every note has a meaning.",
    "Ideas begin here.",
    "Silence speaks in writing.",
    "Capture the moment.",
    "Thoughts become words.",
    "Write your own world."
]

# ─── VERSION CHECK ───────────────────────────────────────────────
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
try:
    from PIL import Image, ImageTk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageTk

# ─── AUTO-INSTALL PYGAME ─────────────────────────────────────────
try:
    import pygame
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

import tkinter as tk
from tkinter import messagebox

# ─── MUSIC INITIALIZATION ────────────────────────────────────────
pygame.mixer.init()
pygame.mixer.music.load("music/OMORI - Final Duet.mp3")
pygame.mixer.music.play(-1)

# ─── SOUNDS ──────────────────────────────────────────────────────
click_sound = pygame.mixer.Sound("sfx/universfield-computer-mouse-click-02-383961.wav")
hover_sound = pygame.mixer.Sound("sfx/dragon-studio-mouse-click-405462.wav")

def play_click():
    click_sound.play()

def play_hover():
    hover_sound.play()

# ─── HOVER EFFECTS ───────────────────────────────────────────────
def on_hover(btn):
    btn.config(bg="#333333")

def on_leave(btn):
    btn.config(bg="black")

def on_hover_dark(btn, hover_color="#4a4b4b"):
    btn.config(bg=hover_color)

def on_leave_dark(btn, normal_color="#3a3b3b"):
    btn.config(bg=normal_color)

# ─── CHANGE MUSIC ────────────────────────────────────────────────
def change_music(song):
    pygame.mixer.music.load(f"music/{song}")
    pygame.mixer.music.play(-1)

# ─── MUSIC WINDOW TRACKER ────────────────────────────────────────
music_window_open = None

# ─── MUSIC PLAYER WINDOW ─────────────────────────────────────────
def show_music_window(event=None):
    global music_window_open

    if music_window_open and tk.Toplevel.winfo_exists(music_window_open):
        music_window_open.lift()
        return

    canvas_x = my_canvas.winfo_rootx()
    canvas_y = my_canvas.winfo_rooty()
    icon_coords = my_canvas.coords(music_icon)
    icon_x = int(canvas_x + icon_coords[0])
    icon_y = int(canvas_y + icon_coords[1])

    music_window_open = tk.Toplevel(root)
    music_window_open.title("Omori Music Player")
    music_window_open.resizable(False, False)
    music_window_open.geometry(f"300x350+{icon_x - 350}+{icon_y + 250}")

    music_bg_img = Image.open("bgi/1148181.png").resize((300, 350))
    music_bg = ImageTk.PhotoImage(music_bg_img)

    music_canvas = tk.Canvas(music_window_open, width=300, height=350)
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
        btn = tk.Button(frame, text=label, font=("Schoolbell", 12), bg="black", fg="white",
                        relief="flat", width=18,
                        command=lambda s=filename: [play_click(), change_music(s)])
        btn.bind("<Enter>", lambda e, b=btn: [play_hover(), on_hover(b)])
        btn.bind("<Leave>", lambda e, b=btn: on_leave(b))
        btn.pack()
        music_canvas.create_window(150, 80 + i * 55, window=frame)

    music_canvas.create_text(150, 240, text="Volume", font=("Schoolbell", 14), fill="white")

    volume_slider = tk.Scale(music_canvas, from_=0, to=100, orient="horizontal", length=200,
                             bg="black", fg="white", highlightthickness=0, troughcolor="white",
                             command=lambda v: pygame.mixer.music.set_volume(int(v) / 100))
    volume_slider.set(100)
    music_canvas.create_window(150, 280, window=volume_slider)

    close_frame = tk.Frame(music_canvas, bg="white", padx=2, pady=2)
    close_btn = tk.Button(close_frame, text="Close", font=("Schoolbell", 12), bg="black", fg="white",
                          relief="flat", width=18,
                          command=lambda: [play_click(), music_window_open.destroy()])
    close_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(close_btn)])
    close_btn.bind("<Leave>", lambda e: on_leave(close_btn))
    close_btn.pack()
    music_canvas.create_window(150, 330, window=close_frame)


# ──────────────────────────────────────────────
#  FILE HANDLING  (JSON persistence)
# ──────────────────────────────────────────────

NOTES_FILE = "notes_data.json"

def load_notes_from_file():
    """Load notes from JSON on startup. Returns (dict, max_id)."""
    if not os.path.exists(NOTES_FILE):
        return {}, 0
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        data = {int(k): v for k, v in raw.items()}
        max_id = max(data.keys(), default=0)
        return data, max_id
    except (json.JSONDecodeError, ValueError):
        return {}, 0

def save_notes_to_file():
    """Write notes_data to JSON file."""
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes_data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
#  WRITE INTERFACE — colours
# ──────────────────────────────────────────────

notes_data, _loaded_max = load_notes_from_file()
note_counter   = [_loaded_max]
active_note_id = [None]

DARK       = "#2d2e2e"       # all UI panels (top bar, sidebar, write area)
DARK_LIGHT = "#3a3b3b"       # input / button background
BORDER_CLR = "#555555"
ACCENT     = "#c8c8c8"       # light text on dark
ACTIVE_TAB = "#4a4b4b"       # highlighted note tab
LINE_CLR   = "#555555"

# Visible button colours (so Save / Delete are easy to spot)
BTN_DELETE_BG     = "#6b2020"
BTN_DELETE_HOVER  = "#8b2020"
BTN_SAVE_BG       = "#1e4a2f"
BTN_SAVE_HOVER    = "#2a6b40"

HAND_FONT    = ("Schoolbell", 14)
HAND_FONT_SM = ("Schoolbell", 12)
HAND_FONT_LG = ("Schoolbell", 18)

SIDEBAR_W = 160
TOPBAR_H  = 50

_write_refs = {}


# ──────────────────────────────────────────────
#  WRITE INTERFACE — layout
# ──────────────────────────────────────────────

def go_to_write_interface():
    play_click()
    my_canvas.delete("all")
    my_canvas.configure(bg="black")

    # ── tiled starry background (9k.png) ──────────────────────────
    try:
        star_img_raw = Image.open("bgi/9k.png").convert("RGB")
        sw, sh = screen_width, screen_height
        iw, ih = star_img_raw.size

        # tile the image to fill the screen
        tiled = Image.new("RGB", (sw, sh))
        for y in range(0, sh, ih):
            for x in range(0, sw, iw):
                tiled.paste(star_img_raw, (x, y))

        star_photo = ImageTk.PhotoImage(tiled)
        my_canvas.create_image(0, 0, image=star_photo, anchor="nw")
        my_canvas.star_photo = star_photo          # keep reference
    except Exception:
        # fallback: plain black background
        my_canvas.create_rectangle(0, 0, screen_width, screen_height,
                                   fill="black", outline="")

    pad = 30
    box_x1, box_y1 = pad, pad
    box_x2, box_y2 = screen_width - pad, screen_height - pad

    # outer container — semi-transparent look with dark border
    my_canvas.create_rectangle(box_x1, box_y1, box_x2, box_y2,
                                fill=DARK, outline=BORDER_CLR, width=2)

    # ── top bar (#2d2e2e) ─────────────────────────────────────────
    top_y2 = box_y1 + TOPBAR_H
    my_canvas.create_rectangle(box_x1, box_y1, box_x2, top_y2,
                                fill=DARK, outline=BORDER_CLR, width=2)

    create_btn = tk.Button(my_canvas, text="Create", font=HAND_FONT_LG,
                           bg=DARK, fg=ACCENT, relief="flat", cursor="hand2",
                           activebackground=ACTIVE_TAB, activeforeground="white",
                           command=create_new_note)
    create_btn.bind("<Enter>", lambda e: on_hover_dark(create_btn, ACTIVE_TAB))
    create_btn.bind("<Leave>", lambda e: on_leave_dark(create_btn, DARK))
    my_canvas.create_window(box_x1 + 65, box_y1 + TOPBAR_H // 2, window=create_btn)
    _write_refs["create_btn"] = create_btn

    # random writing quote in centre
    my_canvas.create_text((box_x1 + box_x2) // 2, box_y1 + TOPBAR_H // 2,
                           text=random.choice(QUOTES),
                           font=("Schoolbell", 17), fill=ACCENT)

    bgm_btn = tk.Button(my_canvas, text="bgm", font=HAND_FONT_LG,
                        bg=DARK, fg=ACCENT, relief="flat", cursor="hand2",
                        activebackground=ACTIVE_TAB, activeforeground="white",
                        command=show_music_window)
    bgm_btn.bind("<Enter>", lambda e: on_hover_dark(bgm_btn, ACTIVE_TAB))
    bgm_btn.bind("<Leave>", lambda e: on_leave_dark(bgm_btn, DARK))
    my_canvas.create_window(box_x2 - 45, box_y1 + TOPBAR_H // 2, window=bgm_btn)
    _write_refs["bgm_btn"] = bgm_btn

    # ── sidebar (#2d2e2e) with scroll ─────────────────────────────
    sidebar_x2 = box_x1 + SIDEBAR_W
    my_canvas.create_rectangle(box_x1, top_y2, sidebar_x2, box_y2,
                                fill=DARK, outline=BORDER_CLR, width=2)

    sb_h = box_y2 - top_y2 - 4

    sb_scroll = tk.Scrollbar(my_canvas, orient="vertical",
                              bg=DARK, troughcolor=DARK_LIGHT, width=12)
    sb_canvas = tk.Canvas(my_canvas, bg=DARK, highlightthickness=0)
    sb_canvas.configure(yscrollcommand=sb_scroll.set)
    sb_scroll.configure(command=sb_canvas.yview)

    my_canvas.create_window(sidebar_x2 - 14, top_y2 + 2,
                             window=sb_scroll, anchor="nw", width=14, height=sb_h)
    my_canvas.create_window(box_x1 + 2, top_y2 + 2,
                             window=sb_canvas, anchor="nw",
                             width=SIDEBAR_W - 18, height=sb_h)

    inner_frame = tk.Frame(sb_canvas, bg=DARK)
    inner_win   = sb_canvas.create_window(0, 0, window=inner_frame, anchor="nw")

    def _on_inner_resize(event):
        sb_canvas.configure(scrollregion=sb_canvas.bbox("all"))

    def _on_canvas_resize(event):
        sb_canvas.itemconfig(inner_win, width=event.width)

    inner_frame.bind("<Configure>", _on_inner_resize)
    sb_canvas.bind("<Configure>", _on_canvas_resize)

    def _on_mousewheel(event):
        sb_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    sb_canvas.bind("<MouseWheel>", _on_mousewheel)
    inner_frame.bind("<MouseWheel>", _on_mousewheel)

    _write_refs["sb_canvas"]   = sb_canvas
    _write_refs["inner_frame"] = inner_frame

    # ── note editor (#2d2e2e) right panel ─────────────────────────
    note_x1   = sidebar_x2
    note_area = tk.Frame(my_canvas, bg=DARK, highlightthickness=0)
    my_canvas.create_window(note_x1 + 2, top_y2 + 2,
                             window=note_area, anchor="nw",
                             width=box_x2 - note_x1 - 4,
                             height=box_y2 - top_y2 - 4)
    _write_refs["note_area"] = note_area

    build_note_panel(note_area)
    refresh_sidebar()

    # Back button
    back_btn = tk.Button(my_canvas, text="← Back", font=HAND_FONT_SM,
                         bg="black", fg="#888", relief="flat", cursor="hand2",
                         activebackground="black", activeforeground=ACCENT,
                         command=go_to_main_interface)
    my_canvas.create_window(pad + 40, screen_height - 14, window=back_btn)
    _write_refs["back_btn"] = back_btn


def build_note_panel(parent):
    """Build the right-hand note editor inside *parent* Frame."""
    for w in parent.winfo_children():
        w.destroy()

    note_id = active_note_id[0]
    data    = notes_data.get(note_id, {})
    enabled = note_id is not None

    # ── heading ───────────────────────────────────────────────────
    hf = tk.Frame(parent, bg=DARK)
    hf.pack(fill="x", padx=14, pady=(10, 2))
    tk.Label(hf,
             text=f"Note {note_id}" if enabled else "No note selected",
             font=("Schoolbell", 20, "bold"),
             bg=DARK, fg=ACCENT, anchor="w").pack(side="left")

    tk.Frame(parent, bg=BORDER_CLR, height=1).pack(fill="x", padx=8)

    # ── title + date row ──────────────────────────────────────────
    td = tk.Frame(parent, bg=DARK)
    td.pack(fill="x", padx=14, pady=(8, 0))

    title_entry = tk.Entry(td, font=HAND_FONT,
                           bg=DARK_LIGHT, fg=ACCENT,
                           relief="flat", insertbackground=ACCENT,
                           highlightthickness=1,
                           highlightcolor=BORDER_CLR,
                           highlightbackground=BORDER_CLR,
                           disabledbackground=DARK,
                           disabledforeground="#555")
    title_entry.insert(0, data.get("title", ""))
    if not enabled:
        title_entry.config(state="disabled")
    title_entry.pack(side="left", expand=True, fill="x", ipady=5)
    _write_refs["title_entry"] = title_entry

    tk.Label(td,
             text=data.get("date", datetime.now().strftime("%Y-%m-%d")),
             font=HAND_FONT, bg=DARK, fg="#888", anchor="e"
             ).pack(side="right", padx=(10, 0))

    tk.Frame(parent, bg=LINE_CLR, height=1).pack(fill="x", padx=14, pady=(8, 0))

    # ── text / writing area (#2d2e2e with lighter input bg) ───────
    tc = tk.Frame(parent, bg=DARK)
    tc.pack(fill="both", expand=True, padx=14, pady=8)

    text_widget = tk.Text(tc, font=("Schoolbell", 15),
                          bg=DARK_LIGHT, fg=ACCENT,
                          relief="flat", wrap=tk.WORD,
                          insertbackground=ACCENT,
                          spacing1=8, spacing3=8,
                          highlightthickness=0, borderwidth=0,
                          selectbackground=ACTIVE_TAB,
                          selectforeground="white",
                          state="normal" if enabled else "disabled")
    text_widget.pack(side="left", fill="both", expand=True)
    if enabled and data.get("content"):
        text_widget.insert("1.0", data["content"])
    _write_refs["text_widget"] = text_widget

    txt_sb = tk.Scrollbar(tc, command=text_widget.yview,
                          bg=DARK, troughcolor=DARK_LIGHT)
    txt_sb.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=txt_sb.set)

    # ── Delete / Save buttons (clearly visible) ───────────────────
    btn_bar = tk.Frame(parent, bg=DARK)
    btn_bar.pack(fill="x", padx=14, pady=(0, 14))

    def delete_note():
        if active_note_id[0] is None:
            return
        confirm = messagebox.askyesno("Delete Note",
                                      "Are you sure you want to delete this note?")
        if not confirm:
            return
        if active_note_id[0] in notes_data:
            del notes_data[active_note_id[0]]
            save_notes_to_file()
        active_note_id[0] = None
        refresh_sidebar()
        build_note_panel(parent)

    def save_note():
        if active_note_id[0] is None:
            return
        notes_data[active_note_id[0]] = {
            "title":   title_entry.get().strip() or f"Note {active_note_id[0]}",
            "date":    datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": text_widget.get("1.0", tk.END).strip()
        }
        save_notes_to_file()
        refresh_sidebar()
        flash = tk.Label(parent, text="✓ Saved!", font=HAND_FONT_SM,
                         bg="#1e3a2f", fg="#6fcf97", relief="flat", padx=10, pady=4)
        flash.place(relx=0.5, rely=0.97, anchor="s")
        parent.after(1500, flash.destroy)

    # Delete — red-tinted so it's clearly distinguishable
    del_btn = tk.Button(btn_bar, text="Delete",
                        font=("Schoolbell", 15, "bold"),
                        bg=BTN_DELETE_BG, fg="white",
                        activebackground=BTN_DELETE_HOVER, activeforeground="white",
                        relief="flat", bd=0, cursor="hand2",
                        padx=20, pady=8,
                        state="normal" if enabled else "disabled",
                        command=delete_note)
    del_btn.bind("<Enter>", lambda e: on_hover_dark(del_btn, BTN_DELETE_HOVER) if enabled else None)
    del_btn.bind("<Leave>", lambda e: on_leave_dark(del_btn, BTN_DELETE_BG) if enabled else None)
    del_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

    # Save — green-tinted so it stands out positively
    save_btn = tk.Button(btn_bar, text="Save",
                         font=("Schoolbell", 15, "bold"),
                         bg=BTN_SAVE_BG, fg="white",
                         activebackground=BTN_SAVE_HOVER, activeforeground="white",
                         relief="flat", bd=0, cursor="hand2",
                         padx=20, pady=8,
                         state="normal" if enabled else "disabled",
                         command=save_note)
    save_btn.bind("<Enter>", lambda e: on_hover_dark(save_btn, BTN_SAVE_HOVER) if enabled else None)
    save_btn.bind("<Leave>", lambda e: on_leave_dark(save_btn, BTN_SAVE_BG) if enabled else None)
    save_btn.pack(side="left", expand=True, fill="x")


def refresh_sidebar():
    """Rebuild the scrollable sidebar list of notes."""
    inner_frame = _write_refs.get("inner_frame")
    sb_canvas   = _write_refs.get("sb_canvas")
    if not inner_frame or not sb_canvas:
        return

    for w in inner_frame.winfo_children():
        w.destroy()

    for nid in sorted(notes_data.keys()):
        is_active = (nid == active_note_id[0])
        bg_c = ACTIVE_TAB if is_active else DARK

        note_title = notes_data[nid].get("title", "").strip()
        label_text = note_title if note_title else f"Note {nid}"

        btn = tk.Button(inner_frame,
                        text=label_text,
                        font=HAND_FONT,
                        bg=bg_c, fg=ACCENT,
                        activebackground=ACTIVE_TAB, activeforeground="white",
                        relief="flat", anchor="w",
                        cursor="hand2", pady=8, padx=10,
                        command=lambda n=nid: select_note(n))
        btn.bind("<Enter>", lambda e, b=btn, orig=bg_c: on_hover_dark(b, ACTIVE_TAB))
        btn.bind("<Leave>", lambda e, b=btn, orig=bg_c: on_leave_dark(b, orig))
        btn.pack(fill="x")
        tk.Frame(inner_frame, bg=BORDER_CLR, height=1).pack(fill="x")

    inner_frame.update_idletasks()
    sb_canvas.configure(scrollregion=sb_canvas.bbox("all"))


def select_note(note_id):
    active_note_id[0] = note_id
    note_area = _write_refs.get("note_area")
    if note_area:
        build_note_panel(note_area)
    refresh_sidebar()


def create_new_note():
    note_counter[0] += 1
    nid = note_counter[0]
    notes_data[nid] = {
        "title":   "",
        "date":    datetime.now().strftime("%Y-%m-%d %H:%M"),
        "content": ""
    }
    active_note_id[0] = nid
    note_area = _write_refs.get("note_area")
    if note_area:
        build_note_panel(note_area)
    refresh_sidebar()
    # Auto-scroll sidebar to show the newest note at the bottom
    sb_canvas = _write_refs.get("sb_canvas")
    if sb_canvas:
        sb_canvas.after(60, lambda: sb_canvas.yview_moveto(1.0))


# ──────────────────────────────────────────────
#  MAIN INTERFACE
# ──────────────────────────────────────────────

def go_to_main_interface():
    """Return to the main menu."""
    my_canvas.delete("all")
    my_canvas.configure(bg="black")

    my_canvas.create_image(screen_width // 2, screen_height // 2, image=bg, anchor="center")
    my_canvas.create_image(
        int(screen_width * 0.49),
        int(screen_height * 0.45),
        image=char_img, anchor="center")

    global write_frame, exit_frame, music_icon

    # Write button
    write_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
    write_btn_main = tk.Button(write_frame, text="Write", font=btn_font,
                               bg="black", fg="white", relief="flat",
                               width=10, height=2,
                               command=go_to_write_interface)
    write_btn_main.bind("<Enter>", lambda e: [play_hover(), on_hover(write_btn_main)])
    write_btn_main.bind("<Leave>", lambda e: on_leave(write_btn_main))
    write_btn_main.pack()

    # Exit button
    exit_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
    exit_btn_main = tk.Button(exit_frame, text="Exit", font=btn_font,
                              bg="black", fg="white", relief="flat",
                              width=10, height=2,
                              command=lambda: [play_click(), root.destroy()])
    exit_btn_main.bind("<Enter>", lambda e: [play_hover(), on_hover(exit_btn_main)])
    exit_btn_main.bind("<Leave>", lambda e: on_leave(exit_btn_main))
    exit_btn_main.pack()

    write_win  = my_canvas.create_window(0, 0, window=write_frame)
    exit_win   = my_canvas.create_window(0, 0, window=exit_frame)

    def _place():
        w = root.winfo_width()
        h = root.winfo_height()
        my_canvas.coords(write_win, int(w * 0.41), int(h * 0.82))
        my_canvas.coords(exit_win,  int(w * 0.61), int(h * 0.82))

    _place()
    root.bind("<Configure>", lambda e: _place())

    # Music icon
    music_icon = my_canvas.create_image(
        int(screen_width * 1.0),
        int(screen_height * -0.04),
        image=logo_img, anchor="ne")
    my_canvas.tag_bind(music_icon, "<Button-1>", show_music_window)


# ──────────────────────────────────────────────
#  BOOT
# ──────────────────────────────────────────────

root = tk.Tk()
root.title("Omori Notes")
icon = tk.PhotoImage(file="bgi/icon/Omori-PNG-Image.png")
root.iconphoto(True, icon)
root.state("zoomed")

root.update()
screen_width  = root.winfo_width()
screen_height = root.winfo_height()

# Main background
bg = tk.PhotoImage(file="bgi/1365265.png")

my_canvas = tk.Canvas(root, width=screen_width, height=screen_height)
my_canvas.pack(fill="both", expand=True)
my_canvas.create_image(screen_width // 2, screen_height // 2, image=bg, anchor="center")

btn_font = ("Schoolbell", 20)

# Character / logo
char_img = tk.PhotoImage(file="bgi/omori_logo.png")
my_canvas.create_image(
    int(screen_width * 0.49),
    int(screen_height * 0.45),
    image=char_img, anchor="center")

# Music icon
logo_pil = Image.open("bgi/music_logo.png").convert("RGBA").resize((300, 300))
logo_img = ImageTk.PhotoImage(logo_pil)
music_icon = my_canvas.create_image(
    int(screen_width * 1.0),
    int(screen_height * -0.04),
    image=logo_img, anchor="ne")
my_canvas.tag_bind(music_icon, "<Button-1>", show_music_window)

# Write button
write_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
write_btn = tk.Button(write_frame, text="Write", font=btn_font,
                      bg="black", fg="white", relief="flat",
                      width=10, height=2,
                      command=go_to_write_interface)          # ← FIXED (was play_click)
write_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(write_btn)])
write_btn.bind("<Leave>", lambda e: on_leave(write_btn))
write_btn.pack()

# Exit button
exit_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
exit_btn = tk.Button(exit_frame, text="Exit", font=btn_font,
                     bg="black", fg="white", relief="flat",
                     width=10, height=2,
                     command=lambda: [play_click(), root.destroy()])
exit_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(exit_btn)])
exit_btn.bind("<Leave>", lambda e: on_leave(exit_btn))
exit_btn.pack()

write_window = my_canvas.create_window(0, 0, window=write_frame)
exit_window  = my_canvas.create_window(0, 0, window=exit_frame)

def place_buttons():
    w = root.winfo_width()
    h = root.winfo_height()
    my_canvas.coords(write_window, int(w * 0.41), int(h * 0.82))
    my_canvas.coords(exit_window,  int(w * 0.61), int(h * 0.82))

place_buttons()
root.bind("<Configure>", lambda e: place_buttons())

root.mainloop()


