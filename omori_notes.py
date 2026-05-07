import subprocess
import sys
import random
import os
import json
from datetime import datetime

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

# ─── HOVER HELPERS ───────────────────────────────────────────────
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

# ─── MUSIC WINDOW ────────────────────────────────────────────────
# We store the last known screen position for the bgm button so
# show_music_window can position itself even when called from the
# write interface (where music_icon doesn't exist on the canvas).
_bgm_screen_x = [100]
_bgm_screen_y = [100]
music_window_open = None

def show_music_window(event=None):
    global music_window_open

    if music_window_open and tk.Toplevel.winfo_exists(music_window_open):
        music_window_open.lift()
        return

    win_x = _bgm_screen_x[0] - 320
    win_y = _bgm_screen_y[0] + 20

    music_window_open = tk.Toplevel(root)
    music_window_open.title("Omori Music Player")
    music_window_open.resizable(False, False)
    music_window_open.geometry(f"300x350+{win_x}+{win_y}")

    music_bg_img = Image.open("bgi/1148181.png").resize((300, 350))
    music_bg     = ImageTk.PhotoImage(music_bg_img)

    mc = tk.Canvas(music_window_open, width=300, height=350)
    mc.pack(fill="both", expand=True)
    mc.create_image(0, 0, image=music_bg, anchor="nw")
    mc.image = music_bg

    mc.create_text(150, 30, text="Select a Song", font=("Schoolbell", 16), fill="white")

    songs = {
        "OMORI - Final Duet":  "OMORI - Final Duet.mp3",
        "Good Morning (8-bit)": "Good Morning [8 Bit VRC6] (Arr. by Kamome Sano) (Ft. Jasminescorner) - OMORI.mp3",
        "OMORI (8-bit Remix)": "OMORI (8-bit remix).mp3",
    }
    for i, (label, filename) in enumerate(songs.items()):
        frame = tk.Frame(mc, bg="white", padx=2, pady=2)
        btn   = tk.Button(frame, text=label, font=("Schoolbell", 12),
                          bg="black", fg="white", relief="flat", width=18,
                          command=lambda s=filename: [play_click(), change_music(s)])
        btn.bind("<Enter>", lambda e, b=btn: [play_hover(), on_hover(b)])
        btn.bind("<Leave>", lambda e, b=btn: on_leave(b))
        btn.pack()
        mc.create_window(150, 80 + i * 55, window=frame)

    mc.create_text(150, 240, text="Volume", font=("Schoolbell", 14), fill="white")
    vol = tk.Scale(mc, from_=0, to=100, orient="horizontal", length=200,
                   bg="black", fg="white", highlightthickness=0, troughcolor="white",
                   command=lambda v: pygame.mixer.music.set_volume(int(v) / 100))
    vol.set(100)
    mc.create_window(150, 280, window=vol)

    close_frame = tk.Frame(mc, bg="white", padx=2, pady=2)
    close_btn   = tk.Button(close_frame, text="Close", font=("Schoolbell", 12),
                            bg="black", fg="white", relief="flat", width=18,
                            command=lambda: [play_click(), music_window_open.destroy()])
    close_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(close_btn)])
    close_btn.bind("<Leave>", lambda e: on_leave(close_btn))
    close_btn.pack()
    mc.create_window(150, 330, window=close_frame)


# ─── FILE HANDLING ────────────────────────────────────────────────
NOTES_FILE = "notes_data.json"
TRASH_FILE = "trash_data.json"

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}, 0
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        data   = {int(k): v for k, v in raw.items()}
        max_id = max(data.keys(), default=0)
        return data, max_id
    except (json.JSONDecodeError, ValueError):
        return {}, 0

def write_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

notes_data, _notes_max = load_json(NOTES_FILE)
trash_data, _trash_max = load_json(TRASH_FILE)

note_counter  = [_notes_max]
trash_counter = [_trash_max]
active_note_id = [None]

def save_notes(): write_json(NOTES_FILE, notes_data)
def save_trash(): write_json(TRASH_FILE, trash_data)


# ─── COLOUR PALETTE ──────────────────────────────────────────────
DARK            = "#2d2e2e"
DARK_LIGHT      = "#3a3b3b"
BORDER_CLR      = "#555555"
ACCENT          = "#c8c8c8"
ACTIVE_TAB      = "#4a4b4b"
LINE_CLR        = "#555555"
BTN_DELETE_BG   = "#6b2020"
BTN_DELETE_HOV  = "#8b2020"
BTN_SAVE_BG     = "#1e4a2f"
BTN_SAVE_HOV    = "#2a6b40"
BTN_BIN_BG      = "#3a3020"
BTN_BIN_HOV     = "#5a4a30"

HAND_FONT    = ("Schoolbell", 14)
HAND_FONT_SM = ("Schoolbell", 12)
HAND_FONT_LG = ("Schoolbell", 18)

SIDEBAR_W = 160
TOPBAR_H  = 50

_write_refs = {}


# ─── HELPERS ─────────────────────────────────────────────────────
def _draw_star_bg():
    """Tile the starry background across the full canvas."""
    try:
        raw = Image.open("bgi/9k.png").convert("RGB")
        iw, ih = raw.size
        tiled  = Image.new("RGB", (screen_width, screen_height))
        for y in range(0, screen_height, ih):
            for x in range(0, screen_width, iw):
                tiled.paste(raw, (x, y))
        photo = ImageTk.PhotoImage(tiled)
        my_canvas.create_image(0, 0, image=photo, anchor="nw")
        my_canvas.star_photo = photo
    except Exception:
        my_canvas.create_rectangle(0, 0, screen_width, screen_height,
                                   fill="black", outline="")


# ═══════════════════════════════════════════════════════════════════
#  WRITE INTERFACE
# ═══════════════════════════════════════════════════════════════════
def go_to_write_interface():
    play_click()
    my_canvas.delete("all")
    my_canvas.configure(bg="black")
    _draw_star_bg()

    pad = 30
    bx1, by1 = pad, pad
    bx2, by2 = screen_width - pad, screen_height - pad

    my_canvas.create_rectangle(bx1, by1, bx2, by2,
                                fill=DARK, outline=BORDER_CLR, width=2)

    # ── top bar ───────────────────────────────────────────────────
    ty2 = by1 + TOPBAR_H
    my_canvas.create_rectangle(bx1, by1, bx2, ty2,
                                fill=DARK, outline=BORDER_CLR, width=2)

    # ── Create (far left) ─────────────────────────────────────────
    create_btn = tk.Button(my_canvas, text="Create", font=HAND_FONT_LG,
                           bg=DARK, fg=ACCENT, relief="flat", cursor="hand2",
                           activebackground=ACTIVE_TAB, activeforeground="white",
                           command=create_new_note)
    create_btn.bind("<Enter>", lambda e: on_hover_dark(create_btn, ACTIVE_TAB))
    create_btn.bind("<Leave>", lambda e: on_leave_dark(create_btn, DARK))
    my_canvas.create_window(bx1 + 65, by1 + TOPBAR_H // 2, window=create_btn)

    # ── Random quote (centre) ─────────────────────────────────────
    my_canvas.create_text((bx1 + bx2) // 2, by1 + TOPBAR_H // 2,
                           text=random.choice(QUOTES),
                           font=("Schoolbell", 17), fill=ACCENT)

    # ── Bin button (right of centre, before bgm) ──────────────────
    bin_top_btn = tk.Button(my_canvas, text="🗑 Bin", font=HAND_FONT_LG,
                            bg=DARK, fg=ACCENT, relief="flat", cursor="hand2",
                            activebackground=ACTIVE_TAB, activeforeground="white",
                            command=go_to_bin_interface)
    bin_top_btn.bind("<Enter>", lambda e: on_hover_dark(bin_top_btn, ACTIVE_TAB))
    bin_top_btn.bind("<Leave>", lambda e: on_leave_dark(bin_top_btn, DARK))
    my_canvas.create_window(bx2 - 130, by1 + TOPBAR_H // 2, window=bin_top_btn)

    # ── BGM button (far right) — records screen pos for popup ─────
    bgm_btn = tk.Button(my_canvas, text="bgm", font=HAND_FONT_LG,
                        bg=DARK, fg=ACCENT, relief="flat", cursor="hand2",
                        activebackground=ACTIVE_TAB, activeforeground="white")
    bgm_btn.bind("<Enter>", lambda e: on_hover_dark(bgm_btn, ACTIVE_TAB))
    bgm_btn.bind("<Leave>", lambda e: on_leave_dark(bgm_btn, DARK))

    def _open_bgm_from_write():
        bgm_btn.update_idletasks()
        _bgm_screen_x[0] = bgm_btn.winfo_rootx() + bgm_btn.winfo_width()
        _bgm_screen_y[0] = bgm_btn.winfo_rooty() + bgm_btn.winfo_height()
        play_click()
        show_music_window()

    bgm_btn.config(command=_open_bgm_from_write)
    my_canvas.create_window(bx2 - 45, by1 + TOPBAR_H // 2, window=bgm_btn)
    _write_refs["bgm_btn"] = bgm_btn

    # ── sidebar ───────────────────────────────────────────────────
    sx2 = bx1 + SIDEBAR_W
    my_canvas.create_rectangle(bx1, ty2, sx2, by2,
                                fill=DARK, outline=BORDER_CLR, width=2)
    sb_h = by2 - ty2 - 4

    sb_scroll = tk.Scrollbar(my_canvas, orient="vertical",
                              bg=DARK, troughcolor=DARK_LIGHT, width=12)
    sb_canvas = tk.Canvas(my_canvas, bg=DARK, highlightthickness=0)
    sb_canvas.configure(yscrollcommand=sb_scroll.set)
    sb_scroll.configure(command=sb_canvas.yview)

    my_canvas.create_window(sx2 - 14, ty2 + 2,
                             window=sb_scroll, anchor="nw", width=14, height=sb_h)
    my_canvas.create_window(bx1 + 2,  ty2 + 2,
                             window=sb_canvas, anchor="nw",
                             width=SIDEBAR_W - 18, height=sb_h)

    inner_frame = tk.Frame(sb_canvas, bg=DARK)
    inner_win   = sb_canvas.create_window(0, 0, window=inner_frame, anchor="nw")

    inner_frame.bind("<Configure>",
                     lambda e: sb_canvas.configure(scrollregion=sb_canvas.bbox("all")))
    sb_canvas.bind("<Configure>",
                   lambda e: sb_canvas.itemconfig(inner_win, width=e.width))

    def _mw(e): sb_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    sb_canvas.bind("<MouseWheel>", _mw)
    inner_frame.bind("<MouseWheel>", _mw)

    _write_refs["sb_canvas"]   = sb_canvas
    _write_refs["inner_frame"] = inner_frame

    # ── note editor ───────────────────────────────────────────────
    note_area = tk.Frame(my_canvas, bg=DARK, highlightthickness=0)
    my_canvas.create_window(sx2 + 2, ty2 + 2, window=note_area, anchor="nw",
                             width=bx2 - sx2 - 4, height=by2 - ty2 - 4)
    _write_refs["note_area"] = note_area

    build_note_panel(note_area)
    refresh_sidebar()

    # Back button
    back_btn = tk.Button(my_canvas, text="← Back", font=HAND_FONT_SM,
                         bg="black", fg="#888", relief="flat", cursor="hand2",
                         activebackground="black", activeforeground=ACCENT,
                         command=go_to_main_interface)
    my_canvas.create_window(pad + 40, screen_height - 14, window=back_btn)


# ─── NOTE PANEL ──────────────────────────────────────────────────
def build_note_panel(parent):
    for w in parent.winfo_children():
        w.destroy()

    note_id = active_note_id[0]
    data    = notes_data.get(note_id, {})
    on      = note_id is not None

    # heading
    hf = tk.Frame(parent, bg=DARK)
    hf.pack(fill="x", padx=14, pady=(10, 2))
    tk.Label(hf, text=f"Note {note_id}" if on else "No note selected",
             font=("Schoolbell", 20, "bold"), bg=DARK, fg=ACCENT,
             anchor="w").pack(side="left")
    tk.Frame(parent, bg=BORDER_CLR, height=1).pack(fill="x", padx=8)

    # title + date
    td = tk.Frame(parent, bg=DARK)
    td.pack(fill="x", padx=14, pady=(8, 0))
    title_entry = tk.Entry(td, font=HAND_FONT, bg=DARK_LIGHT, fg=ACCENT,
                           relief="flat", insertbackground=ACCENT,
                           highlightthickness=1, highlightcolor=BORDER_CLR,
                           highlightbackground=BORDER_CLR,
                           disabledbackground=DARK, disabledforeground="#555",
                           state="normal" if on else "disabled")
    title_entry.insert(0, data.get("title", ""))
    title_entry.pack(side="left", expand=True, fill="x", ipady=5)
    _write_refs["title_entry"] = title_entry

    tk.Label(td, text=data.get("date", datetime.now().strftime("%Y-%m-%d")),
             font=HAND_FONT, bg=DARK, fg="#888", anchor="e"
             ).pack(side="right", padx=(10, 0))
    tk.Frame(parent, bg=LINE_CLR, height=1).pack(fill="x", padx=14, pady=(8, 0))

    # text area
    tc = tk.Frame(parent, bg=DARK)
    tc.pack(fill="both", expand=True, padx=14, pady=8)
    text_widget = tk.Text(tc, font=("Schoolbell", 15),
                          bg=DARK_LIGHT, fg=ACCENT, relief="flat", wrap=tk.WORD,
                          insertbackground=ACCENT, spacing1=8, spacing3=8,
                          highlightthickness=0, borderwidth=0,
                          selectbackground=ACTIVE_TAB, selectforeground="white",
                          state="normal" if on else "disabled")
    text_widget.pack(side="left", fill="both", expand=True)
    if on and data.get("content"):
        text_widget.insert("1.0", data["content"])
    _write_refs["text_widget"] = text_widget

    txt_sb = tk.Scrollbar(tc, command=text_widget.yview, bg=DARK, troughcolor=DARK_LIGHT)
    txt_sb.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=txt_sb.set)

    # ── button bar: Save | Delete ────────────────────────────────
    btn_bar = tk.Frame(parent, bg=DARK)
    btn_bar.pack(fill="x", padx=14, pady=(0, 14))

    def _soft_delete():
        """Move current note to trash and refresh."""
        if active_note_id[0] is None:
            return
        confirm = messagebox.askyesno("Delete Note",
                                      "Move this note to the bin?")
        if not confirm:
            return
        nid  = active_note_id[0]
        note = notes_data.pop(nid, {})
        # Store in trash with deletion timestamp
        trash_counter[0] += 1
        tid = trash_counter[0]
        trash_data[tid] = {
            "title":        note.get("title", f"Note {nid}") or f"Note {nid}",
            "original_id":  nid,
            "deleted_date": datetime.now().strftime("%Y-%m-%d"),
            "content":      note.get("content", ""),
        }
        save_notes()
        save_trash()
        active_note_id[0] = None
        refresh_sidebar()
        build_note_panel(parent)

    def _save_note():
        if active_note_id[0] is None:
            return
        notes_data[active_note_id[0]] = {
            "title":   title_entry.get().strip() or f"Note {active_note_id[0]}",
            "date":    datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": text_widget.get("1.0", tk.END).strip(),
        }
        save_notes()
        refresh_sidebar()
        flash = tk.Label(parent, text="✓ Saved!", font=HAND_FONT_SM,
                         bg="#1e3a2f", fg="#6fcf97", padx=10, pady=4)
        flash.place(relx=0.5, rely=0.97, anchor="s")
        parent.after(1500, flash.destroy)

    # Save (green)
    save_btn = tk.Button(btn_bar, text="Save",
                         font=("Schoolbell", 15, "bold"),
                         bg=BTN_SAVE_BG, fg="white",
                         activebackground=BTN_SAVE_HOV, activeforeground="white",
                         relief="flat", bd=0, cursor="hand2", padx=16, pady=8,
                         state="normal" if on else "disabled", command=_save_note)
    save_btn.bind("<Enter>", lambda e: on_hover_dark(save_btn, BTN_SAVE_HOV) if on else None)
    save_btn.bind("<Leave>", lambda e: on_leave_dark(save_btn, BTN_SAVE_BG) if on else None)
    save_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

    # Delete (red) — moves note to bin
    del_btn = tk.Button(btn_bar, text="Delete",
                        font=("Schoolbell", 15, "bold"),
                        bg=BTN_DELETE_BG, fg="white",
                        activebackground=BTN_DELETE_HOV, activeforeground="white",
                        relief="flat", bd=0, cursor="hand2", padx=16, pady=8,
                        state="normal" if on else "disabled", command=_soft_delete)
    del_btn.bind("<Enter>", lambda e: on_hover_dark(del_btn, BTN_DELETE_HOV) if on else None)
    del_btn.bind("<Leave>", lambda e: on_leave_dark(del_btn, BTN_DELETE_BG) if on else None)
    del_btn.pack(side="left", expand=True, fill="x")


# ─── SIDEBAR ─────────────────────────────────────────────────────
def refresh_sidebar():
    inner_frame = _write_refs.get("inner_frame")
    sb_canvas   = _write_refs.get("sb_canvas")
    if not inner_frame or not sb_canvas:
        return

    for w in inner_frame.winfo_children():
        w.destroy()

    for nid in sorted(notes_data.keys()):
        is_active  = (nid == active_note_id[0])
        bg_c       = ACTIVE_TAB if is_active else DARK
        label_text = notes_data[nid].get("title", "").strip() or f"Note {nid}"

        btn = tk.Button(inner_frame, text=label_text, font=HAND_FONT,
                        bg=bg_c, fg=ACCENT,
                        activebackground=ACTIVE_TAB, activeforeground="white",
                        relief="flat", anchor="w", cursor="hand2",
                        pady=8, padx=10,
                        command=lambda n=nid: select_note(n))
        btn.bind("<Enter>", lambda e, b=btn, o=bg_c: on_hover_dark(b, ACTIVE_TAB))
        btn.bind("<Leave>", lambda e, b=btn, o=bg_c: on_leave_dark(b, o))
        btn.pack(fill="x")
        tk.Frame(inner_frame, bg=BORDER_CLR, height=1).pack(fill="x")

    inner_frame.update_idletasks()
    sb_canvas.configure(scrollregion=sb_canvas.bbox("all"))


def select_note(nid):
    active_note_id[0] = nid
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
        "content": "",
    }
    active_note_id[0] = nid
    note_area = _write_refs.get("note_area")
    if note_area:
        build_note_panel(note_area)
    refresh_sidebar()
    sb = _write_refs.get("sb_canvas")
    if sb:
        sb.after(60, lambda: sb.yview_moveto(1.0))


# ═══════════════════════════════════════════════════════════════════
#  BIN / TRASH INTERFACE
# ═══════════════════════════════════════════════════════════════════
def go_to_bin_interface():
    play_click()
    my_canvas.delete("all")
    my_canvas.configure(bg="black")
    _draw_star_bg()

    pad = 30
    bx1, by1 = pad, pad
    bx2, by2 = screen_width - pad, screen_height - pad

    # outer box
    my_canvas.create_rectangle(bx1, by1, bx2, by2,
                                fill=DARK, outline=BORDER_CLR, width=2)

    # ── header row ───────────────────────────────────────────────
    hdr_y2 = by1 + TOPBAR_H
    my_canvas.create_rectangle(bx1, by1, bx2, hdr_y2,
                                fill=DARK, outline=BORDER_CLR, width=2)
    my_canvas.create_text(bx1 + 20, by1 + TOPBAR_H // 2,
                           text="Recently deleted:",
                           font=("Schoolbell", 18, "bold"),
                           fill=ACCENT, anchor="w")

    # ── scrollable list area ──────────────────────────────────────
    # Reserve space at the bottom for the Back button bar
    footer_h = 60
    list_y1  = hdr_y2
    list_y2  = by2 - footer_h
    list_h   = list_y2 - list_y1 - 4

    list_scroll = tk.Scrollbar(my_canvas, orient="vertical",
                                bg=DARK, troughcolor=DARK_LIGHT, width=12)
    list_canvas = tk.Canvas(my_canvas, bg=DARK, highlightthickness=0)
    list_canvas.configure(yscrollcommand=list_scroll.set)
    list_scroll.configure(command=list_canvas.yview)

    my_canvas.create_window(bx2 - 14, list_y1 + 2,
                             window=list_scroll, anchor="nw", width=14, height=list_h)
    my_canvas.create_window(bx1 + 2,  list_y1 + 2,
                             window=list_canvas, anchor="nw",
                             width=bx2 - bx1 - 18, height=list_h)

    rows_frame = tk.Frame(list_canvas, bg=DARK)
    rows_win   = list_canvas.create_window(0, 0, window=rows_frame, anchor="nw")

    rows_frame.bind("<Configure>",
                    lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
    list_canvas.bind("<Configure>",
                     lambda e: list_canvas.itemconfig(rows_win, width=e.width))

    def _mw(e): list_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    list_canvas.bind("<MouseWheel>", _mw)
    rows_frame.bind("<MouseWheel>", _mw)

    def _rebuild_rows():
        for w in rows_frame.winfo_children():
            w.destroy()

        if not trash_data:
            tk.Label(rows_frame, text="The bin is empty.",
                     font=HAND_FONT, bg=DARK, fg="#666").pack(pady=20)
            return

        for tid in sorted(trash_data.keys()):
            item  = trash_data[tid]
            title = item.get("title", f"Note {tid}")
            date  = item.get("deleted_date", "?")

            row = tk.Frame(rows_frame, bg=DARK)
            row.pack(fill="x", padx=10, pady=3)

            # Note title (left, expands)
            tk.Label(row, text=title, font=HAND_FONT, bg=DARK, fg=ACCENT,
                     anchor="w", width=20).pack(side="left", padx=(0, 10))

            # Date
            tk.Label(row, text=date, font=HAND_FONT_SM, bg=DARK,
                     fg="#888", anchor="w", width=14).pack(side="left", padx=(0, 10))

            # Restore button
            def _restore(t=tid):
                item = trash_data.pop(t, {})
                note_counter[0] += 1
                nid = note_counter[0]
                notes_data[nid] = {
                    "title":   item.get("title", f"Note {nid}"),
                    "date":    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "content": item.get("content", ""),
                }
                save_notes()
                save_trash()
                _rebuild_rows()

            restore_btn = tk.Button(row, text="restore", font=HAND_FONT_SM,
                                    bg=BTN_SAVE_BG, fg="white",
                                    activebackground=BTN_SAVE_HOV,
                                    relief="flat", cursor="hand2", padx=8, pady=3,
                                    command=_restore)
            restore_btn.pack(side="left", padx=(0, 6))

            # Permanent delete button
            def _perm_delete(t=tid):
                confirm = messagebox.askyesno(
                    "Permanent Delete",
                    "Permanently delete this note? This cannot be undone.")
                if confirm:
                    trash_data.pop(t, None)
                    save_trash()
                    _rebuild_rows()

            del_btn = tk.Button(row, text="Delete", font=HAND_FONT_SM,
                                bg=BTN_DELETE_BG, fg="white",
                                activebackground=BTN_DELETE_HOV,
                                relief="flat", cursor="hand2", padx=8, pady=3,
                                command=_perm_delete)
            del_btn.pack(side="left")

            # divider
            tk.Frame(rows_frame, bg=BORDER_CLR, height=1).pack(fill="x", padx=10)

    _rebuild_rows()

    # ── footer: Back button ───────────────────────────────────────
    footer_y = list_y2
    my_canvas.create_rectangle(bx1, footer_y, bx2, by2,
                                fill=DARK, outline=BORDER_CLR, width=2)

    back_frame = tk.Frame(my_canvas, bg=DARK, padx=4, pady=4)
    back_inner = tk.Button(back_frame, text="Back", font=("Schoolbell", 15, "bold"),
                           bg=DARK_LIGHT, fg=ACCENT, relief="flat",
                           cursor="hand2", padx=20, pady=6,
                           command=go_to_write_interface)
    back_inner.bind("<Enter>", lambda e: on_hover_dark(back_inner, ACTIVE_TAB))
    back_inner.bind("<Leave>", lambda e: on_leave_dark(back_inner, DARK_LIGHT))
    back_inner.pack()
    my_canvas.create_window(bx1 + 70, footer_y + footer_h // 2, window=back_frame)


# ═══════════════════════════════════════════════════════════════════
#  MAIN INTERFACE
# ═══════════════════════════════════════════════════════════════════
def go_to_main_interface():
    my_canvas.delete("all")
    my_canvas.configure(bg="black")

    my_canvas.create_image(screen_width // 2, screen_height // 2, image=bg, anchor="center")
    my_canvas.create_image(int(screen_width * 0.49), int(screen_height * 0.45),
                            image=char_img, anchor="center")

    global write_frame, exit_frame, music_icon

    write_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
    wb = tk.Button(write_frame, text="Write", font=btn_font,
                   bg="black", fg="white", relief="flat", width=10, height=2,
                   command=go_to_write_interface)
    wb.bind("<Enter>", lambda e: [play_hover(), on_hover(wb)])
    wb.bind("<Leave>", lambda e: on_leave(wb))
    wb.pack()

    exit_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
    eb = tk.Button(exit_frame, text="Exit", font=btn_font,
                   bg="black", fg="white", relief="flat", width=10, height=2,
                   command=lambda: [play_click(), root.destroy()])
    eb.bind("<Enter>", lambda e: [play_hover(), on_hover(eb)])
    eb.bind("<Leave>", lambda e: on_leave(eb))
    eb.pack()

    ww = my_canvas.create_window(0, 0, window=write_frame)
    ew = my_canvas.create_window(0, 0, window=exit_frame)

    def _place():
        w, h = root.winfo_width(), root.winfo_height()
        my_canvas.coords(ww, int(w * 0.41), int(h * 0.82))
        my_canvas.coords(ew, int(w * 0.61), int(h * 0.82))

    _place()
    root.bind("<Configure>", lambda e: _place())

    music_icon = my_canvas.create_image(
        int(screen_width * 1.0), int(screen_height * -0.04),
        image=logo_img, anchor="ne")

    def _open_bgm_main(event=None):
        _bgm_screen_x[0] = root.winfo_x() + root.winfo_width() - 10
        _bgm_screen_y[0] = root.winfo_y() + 40
        show_music_window()

    my_canvas.tag_bind(music_icon, "<Button-1>", _open_bgm_main)


# ═══════════════════════════════════════════════════════════════════
#  BOOT
# ═══════════════════════════════════════════════════════════════════
root = tk.Tk()
root.title("Omori Notes")
icon = tk.PhotoImage(file="bgi/icon/Omori-PNG-Image.png")
root.iconphoto(True, icon)
root.state("zoomed")
root.update()

screen_width  = root.winfo_width()
screen_height = root.winfo_height()

bg = tk.PhotoImage(file="bgi/1365265.png")

my_canvas = tk.Canvas(root, width=screen_width, height=screen_height)
my_canvas.pack(fill="both", expand=True)
my_canvas.create_image(screen_width // 2, screen_height // 2, image=bg, anchor="center")

btn_font = ("Schoolbell", 20)

char_img = tk.PhotoImage(file="bgi/omori_logo.png")
my_canvas.create_image(int(screen_width * 0.49), int(screen_height * 0.45),
                        image=char_img, anchor="center")

logo_pil = Image.open("bgi/music_logo.png").convert("RGBA").resize((300, 300))
logo_img = ImageTk.PhotoImage(logo_pil)
music_icon = my_canvas.create_image(
    int(screen_width * 1.0), int(screen_height * -0.04),
    image=logo_img, anchor="ne")

def _open_bgm_boot(event=None):
    _bgm_screen_x[0] = root.winfo_x() + root.winfo_width() - 10
    _bgm_screen_y[0] = root.winfo_y() + 40
    show_music_window()

my_canvas.tag_bind(music_icon, "<Button-1>", _open_bgm_boot)

write_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
write_btn   = tk.Button(write_frame, text="Write", font=btn_font,
                        bg="black", fg="white", relief="flat", width=10, height=2,
                        command=go_to_write_interface)
write_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(write_btn)])
write_btn.bind("<Leave>", lambda e: on_leave(write_btn))
write_btn.pack()

exit_frame = tk.Frame(my_canvas, bg="white", padx=4, pady=4)
exit_btn   = tk.Button(exit_frame, text="Exit", font=btn_font,
                       bg="black", fg="white", relief="flat", width=10, height=2,
                       command=lambda: [play_click(), root.destroy()])
exit_btn.bind("<Enter>", lambda e: [play_hover(), on_hover(exit_btn)])
exit_btn.bind("<Leave>", lambda e: on_leave(exit_btn))
exit_btn.pack()

write_window = my_canvas.create_window(0, 0, window=write_frame)
exit_window  = my_canvas.create_window(0, 0, window=exit_frame)

def place_buttons():
    w, h = root.winfo_width(), root.winfo_height()
    my_canvas.coords(write_window, int(w * 0.41), int(h * 0.82))
    my_canvas.coords(exit_window,  int(w * 0.61), int(h * 0.82))

place_buttons()
root.bind("<Configure>", lambda e: place_buttons())

root.mainloop()