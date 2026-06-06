# -*- coding: utf-8 -*-
import fitz
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk

Image.MAX_IMAGE_PIXELS = None


def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


APP_DIR = _app_dir()
RESIMLER_DIR = os.path.join(APP_DIR, "resimler")

# ─── Language / Translation support ───
import json

_SETTINGS_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "PDF_Create_Export_Edit")
_SETTINGS_FILE = os.path.join(_SETTINGS_DIR, "settings.json")

def _load_settings():
    try:
        with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_settings(data):
    try:
        os.makedirs(_SETTINGS_DIR, exist_ok=True)
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

_current_lang = _load_settings().get("lang", "tr")

_TRANS = {
    # General UI
    "PDF Yükle": "Load PDF",
    "Resim Yükle": "Load Image(s)",
    "Tümünü Seç": "Select All",
    "Seçimi Kaldır": "Deselect All",
    "PDF Metin Düzenle": "Edit PDF Text",
    "↑ Yukarı": "↑ Move Up",
    "↓ Aşağı": "↓ Move Down",
    "Resmi Düzenle": "Edit Image",
    "Seçilenleri PDF Yap": "Make PDF from Selected",
    "Seçileni Kaydet": "Save Selected",
    "Hakkında": "About",
    "Sağ Tuşa Ekle": "Add to Right-Click",
    "Sağ Tuştan Kaldır": "Remove from Right-Click",
    "PDF ↔ Resim Dönüştürücü": "PDF ↔ Image Converter",
    # CropEditor mode labels
    "Kes": "Cut",
    "F\u0131r\u00e7a": "Brush",
    "Boya/Sil": "Paint/Erase",
    "Alan Se\u00e7": "Select Area",
    "Metin": "Text",
    "\u00c7izgi": "Line",
    "Tek Ok": "Single Arrow",
    "\u00c7ift Ok": "Double Arrow",
    "K\u0131rp": "Crop",
    # CropEditor tooltips
    "Alan renklendirmek i\u00e7in s\u00fcr\u00fckleyin": "Drag to color the area",
    "F\u0131r\u00e7a ile \u00e7izin": "Draw with brush",
    "Se\u00e7ili renk ile boyay\u0131n": "Paint with selected color",
    "Se\u00e7im yap\u0131n: Ta\u015f\u0131/Kes/Boya": "Select: Move/Cut/Paint",
    "Metin eklemek i\u00e7in t\u0131klay\u0131n": "Click to add text",
    "\u00c7izgi \u00e7ekmek i\u00e7in s\u00fcr\u00fckleyin": "Drag to draw a line",
    "Ok \u00e7ekmek i\u00e7in s\u00fcr\u00fckleyin": "Drag to draw an arrow",
    "\u00c7ift y\u00f6nl\u00fc ok \u00e7ekin": "Draw a double-headed arrow",
    "G\u00f6r\u00fcnt\u00fcy\u00fc k\u0131rpmak i\u00e7in alan se\u00e7in": "Select area to crop image",
    # CropEditor selection buttons
    "✂ Kes": "✂ Cut",
    "Boya": "Fill",
    "Kopyala": "Copy",
    "Taşı": "Move",
    "Döndür": "Rotate",
    "↔ Yansı": "↔ Flip H",
    "↕ Yansı": "↕ Flip V",
    # CropEditor controls
    "Renk": "Color",
    "■ Palet": "■ Palette",
    "Kal\u0131nl\u0131k": "Thickness",
    "Yaz\u0131 Boyutu": "Font Size",
    # CropEditor bottom bar
    "Uygula": "Apply",
    "Geri Al": "Undo",
    "Kaydet": "Save",
    "Farklı Kaydet": "Save As",
    "Kapat": "Close",
    # Status messages
    "Araç seçin": "Select a tool",
    "Köşeyi sürükleyerek döndürün": "Drag corner to rotate",
    "{closest} kenarından sürükleyin": "Drag from {closest} edge",
    "Döndürme: {deg}°": "Rotation: {deg}°",
    "Yeniden boyutlandırma: {nw}x{nh}": "Resize: {nw}x{nh}",
    "Oransal küçült/büyüt: köşeden sürükleyin": "Scale: drag from corner",
    "Oransal: {nw}x{nh}": "Scale: {nw}x{nh}",
    "Döndürüldü: {deg}°": "Rotated: {deg}°",
    "Ölçeklendi": "Scaled",
    "Yeniden boyutlandı": "Resized",
    "Seçimi sürükleyin": "Drag the selection",
    "Kes: ({ix1},{iy1}) → ({ix2},{iy2})": "Cut: ({ix1},{iy1}) → ({ix2},{iy2})",
    "Görüntü kırpıldı: {w}x{h}": "Image cropped: {w}x{h}",
    "Taşı iptal": "Move cancelled",
    "Taşı: Uygula'ya basın": "Move: press Apply",
    "Seçim taşındı": "Selection moved",
    "Alan seçildi": "Area selected",
    "Metin eklendi: \"{text}\"": "Text added: \"{text}\"",
    "90 derece döndürüldü": "Rotated 90°",
    "Alan renklendirildi": "Area colored",
    "Taşı uygulandı": "Move applied",
    "Alan boyandı": "Area painted",
    "Alan kesildi": "Area cut",
    "Kopya oluştu, Uygula ile yapıştırın": "Copy created, paste with Apply",
    "Yatay yansıtıldı": "Flipped horizontally",
    "Dikey yansıtıldı": "Flipped vertically",
    "Alan döndürüldü: {angle}°": "Area rotated: {angle}°",
    "Seçimi sürükleyip bırakın": "Drag and release to move",
    "Geri alındı": "Undone",
    "Hazır": "Ready",
    "{n} görsel": "{n} image(s)",
    "0 görsel": "0 images",
    "{n} görsel yüklendi": "{n} image(s) loaded",
    "Sıralama güncellendi": "Order updated",
    "PDF işleniyor...": "Processing PDF...",
    "Hata: {e}": "Error: {e}",
    "Sayfa {n} - blok {idx} güncellendi": "Page {n} - block {idx} updated",
    "PDF oluşturuluyor...": "Creating PDF...",
    "PDF kaydedildi: {path}": "PDF saved: {path}",
    "{n} resim kaydedildi": "{n} image(s) saved",
    "PDF resimleri çıkarılıyor...": "Extracting PDF images...",
    # Dialog titles / messages
    "D\xfczenle": "Edit",
    "Renk Se\xe7": "Choose Color",
    "Renk Paleti": "Color Palette",
    "Metin Ekle": "Add Text",
    "PDF Metin Düzenle - {name}": "PDF Text Editor - {name}",
    "Kayıt klasörü": "Save folder",
    "Tam Ekran": "Fullscreen",
    "Pencere": "Window",
    "☒ Tam Ekran": "☒ Fullscreen",
    "☒ Pencere": "☒ Window",
    "Metin Blokları": "Text Blocks",
    "Metin İçeriği": "Text Content",
    "PDF Kaydet": "Save PDF",
    "Metin:": "Text:",
    "Ekle": "Add",
    "Açı (0-360):": "Angle (0-360):",
    "%{zoom}%": "%{zoom}%",
    # Messagebox content
    "Resim kaydedildi.": "Image saved.",
    "Resim kaydedildi:\n{path}": "Image saved:\n{path}",
    "PDF açılamadı: {e}": "Could not open PDF: {e}",
    "Uygulanamadı: {e}": "Could not apply: {e}",
    "PDF kaydedildi:\n{out}\n\nAçmak ister misiniz?": "PDF saved:\n{out}\n\nOpen it?",
    "Kaydedilemedi: {e}": "Could not save: {e}",
    "Önce resim seçin": "Select images first",
    "PDF kaydedildi:\n{pdf_path}": "PDF saved:\n{pdf_path}",
    "PDF oluşturulamadı:\n{e}": "Could not create PDF:\n{e}",
    "{n} resim kaydedildi.": "{n} image(s) saved.",
    "PDF resimleri çıkarılamadı:\n{e}": "Could not extract PDF images:\n{e}",
    "PDF oluşturuldu:\n{pdf_path}": "PDF created:\n{pdf_path}",
    "Desteklenmeyen dosya: {ext}": "Unsupported file: {ext}",
    "PDF kaydı eklenemedi: {e}": "Could not add PDF entry: {e}",
    "{ext} kaydı eklenemedi: {e}": "Could not add {ext} entry: {e}",
    # Misc
    "Sayfa çok büyük, render edilemiyor": "Page too large, cannot render",
    "Tüm Formatlar": "All Formats",
    "Renk Seçin:": "Choose Color:",
    "■ Özel Renk...": "■ Custom Color...",
    "Döndür 90": "Rotate 90",
    # Context menu
    "PDF Create Export Edit": "PDF Create Export Edit",
    "PDF Resim Çıkar": "Extract PDF Images",
    "PDF Metin Düzenle": "Edit PDF Text",
    "PDF Resim Çıkar (Seçimli)": "Extract PDF Images (Selective)",
    "Resim Düzenle": "Edit Image",
    "PDF yap": "Make PDF",
    "Tek Tek PDF yap": "Make PDF (Individual)",
    "Seçimli PDF yap": "Make PDF (Selective)",
    # About
    "PDF_Create_Export_Edit\n\nYazılım: Asri Akdeniz\nMail: asriakdeniz@gmail.com": "PDF_Create_Export_Edit\n\nSoftware: Asri Akdeniz\nMail: asriakdeniz@gmail.com",
    # Context menu notifications
    "PDF Create Export Edit sağ tık menüsüne eklendi.\nPDF ve resim dosyalarında PDF Create Export Edit altında kullanabilirsiniz.": "PDF Create Export Edit added to right-click menu.\nUse under PDF Create Export Edit for PDF and image files.",
    "PDF Create Export Edit sağ tık menüsünden kaldırıldı.": "PDF Create Export Edit removed from right-click menu.",
}

def _t(text):
    if _current_lang == "tr":
        return text
    return _TRANS.get(text, text)

def _set_lang(lang):
    global _current_lang
    _current_lang = lang
    _save_settings({"lang": lang})


def restart_app():
    python = sys.executable
    args = [python] + sys.argv
    if getattr(sys, "frozen", False):
        args = [sys.executable] + sys.argv[1:]
    os.execl(python, *args)

_btn_style = {
    "font": ("Segoe UI", 10, "bold"),
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0,
    "highlightthickness": 0,
    "padx": 4,
}


def _mkbtn(parent, text, command, bg="#3498db", fg="white", width=16, state=None):
    text = _t(text)
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
        width=width, **_btn_style,
    )
    if state is not None:
        btn.config(state=state)

    def _on_enter(e):
        btn.config(bg=_darken(bg))

    def _on_leave(e):
        btn.config(bg=bg)

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    return btn


def _darken(hex_color, factor=0.85):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = _t(text)
        self.tip = None
        self.after_id = None
        widget.bind("<Enter>", self._enter)
        widget.bind("<Leave>", self._leave)

    def _enter(self, e):
        self._schedule()

    def _leave(self, e):
        self._hide()

    def _schedule(self):
        self.after_id = self.widget.after(3000, self._hide)

    def _show(self):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 4
        y = self.widget.winfo_rooty()
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, bg="#ffffcc", fg="#333",
                 font=("Segoe UI", 9), padx=6, pady=2, relief="solid",
                 bd=1).pack()

    def _hide(self):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip:
            self.tip.destroy()
            self.tip = None

class CropEditor:
    MODE_CROP = "crop"
    MODE_PAINT = "paint"
    MODE_ERASER = "eraser"
    MODE_SELECTION = "selection"
    MODE_TEXT = "text"
    MODE_LINE = "line"
    MODE_ARROW = "arrow"
    MODE_ARROW_BOTH = "arrow_both"
    MODE_KIRP = "kirp"

    ICONS = {
        "crop": "\u2702", "paint": "\u270F", "eraser": "\u25CB",
        "selection": "\u2B1A", "text": "T", "line": "\u2571",
        "arrow": "\u2192", "arrow_both": "\u2194", "kirp": "\u25AD",
    }

    MODE_COLORS = {
        "crop": "#27ae60", "paint": "#3498db", "eraser": "#e67e22",
        "selection": "#e74c3c", "text": "#e74c3c", "line": "#1abc9c",
        "arrow": "#f39c12", "arrow_both": "#2c3e50", "kirp": "#8e44ad",
    }

    MODE_LABELS = {
        "crop": "Kes", "paint": "F\u0131r\u00e7a", "eraser": "Boya/Sil",
        "selection": "Alan Se\u00e7", "text": "Metin", "line": "\u00c7izgi",
        "arrow": "Tek Ok", "arrow_both": "\u00c7ift Ok", "kirp": "K\u0131rp",
    }

    HELP = {
        "crop": "Alan renklendirmek i\u00e7in s\u00fcr\u00fckleyin", "paint": "F\u0131r\u00e7a ile \u00e7izin",
        "eraser": "Se\u00e7ili renk ile boyay\u0131n", "selection": "Se\u00e7im yap\u0131n: Ta\u015f\u0131/Kes/Boya",
        "text": "Metin eklemek i\u00e7in t\u0131klay\u0131n", "line": "\u00c7izgi \u00e7ekmek i\u00e7in s\u00fcr\u00fckleyin",
        "arrow": "Ok \u00e7ekmek i\u00e7in s\u00fcr\u00fckleyin", "arrow_both": "\u00c7ift y\u00f6nl\u00fc ok \u00e7ekin",
        "kirp": "G\u00f6r\u00fcnt\u00fcy\u00fc k\u0131rpmak i\u00e7in alan se\u00e7in",
    }

    def __init__(self, parent, image_path, on_save=None):
        self.image_path = image_path
        self.on_save = on_save
        img = Image.open(image_path)
        if img.mode == "RGBA":
            self.img = Image.new("RGB", img.size, "white")
            self.img.paste(img, mask=img.split()[3])
        elif img.mode != "RGB":
            self.img = img.convert("RGB")
        else:
            self.img = img.copy()
        self.history = [self.img.copy()]
        self.mode = self.MODE_CROP
        self.brush_color = "#e74c3c"
        self.brush_size = 3
        self.font_size = 24
        self.crop_rect = None
        self.select_rect_coords = None
        self.select_rect_id = None
        self.zoom = 1.0
        self.line_start = None
        self.line_preview_id = None
        self.sel_rect = None
        self.sel_canvas_ids = []
        self.sel_move_mode = False
        self.sel_move_start = None
        self.sel_move_offset = None
        self.sel_content = None
        self.temp_rect_id = None
        self.move_dx = 0
        self.move_dy = 0
        self.float_img_id = None
        self.float_tk = None
        self.copy_mode = False
        self.handles = []
        self.handle_drag = None

        self.win = tk.Toplevel(parent)
        self.win.title(f"{_t('D\xfczenle')} \u2014 {os.path.basename(image_path)}")
        self.win.geometry("1100x760")
        self.win.minsize(900, 600)

        body = tk.Frame(self.win)
        body.pack(fill=tk.BOTH, expand=True)

        # ─── Left toolbar ───
        left = tk.Frame(body, bg="#2c3e50", width=140)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        self.tool_btns = {}
        for mode_id in self.ICONS:
            row = tk.Frame(left, bg="#2c3e50")
            row.pack(fill=tk.X, padx=4, pady=2)
            tk.Label(row, text=_t(self.MODE_LABELS.get(mode_id, mode_id)),
                     bg="#2c3e50", fg="#ccc", font=("Segoe UI", 8),
                     anchor="w", width=10).pack(side=tk.LEFT)
            icon = self.ICONS[mode_id]
            btn = tk.Button(row, text=icon, font=("Segoe UI", 11, "bold"),
                            bg="#2c3e50", fg="white", relief="flat", bd=0,
                            width=2, height=1, cursor="hand2",
                            command=lambda m=mode_id: self._set_mode(m))
            btn.pack(side=tk.RIGHT)
            self.tool_btns[mode_id] = btn
            ToolTip(btn, self.HELP.get(mode_id, ""))

        # ─── Controls below tools ───
        ctrl_frame = tk.Frame(left, bg="#2c3e50")
        ctrl_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=6)

        # ─── Selection buttons ───
        self.sel_frame = tk.Frame(ctrl_frame, bg="#2c3e50")
        self.sel_frame.pack(fill=tk.X)
        _sel_btn_style = lambda bg: dict(
            font=("Segoe UI", 8, "bold"), bg=bg, fg="white",
            disabledforeground="#ddd", relief="flat", bd=0,
            width=8, cursor="hand2", state=tk.DISABLED,
        )
        self.btn_makas = tk.Button(self.sel_frame, text=_t("\u2702 Kes"),
                                   command=self._sel_cut,
                                   **_sel_btn_style("#c0392b"))
        self.btn_makas.pack(pady=1)
        self.btn_boya = tk.Button(self.sel_frame, text=_t("Boya"),
                                  command=self._sel_fill,
                                  **_sel_btn_style("#27ae60"))
        self.btn_boya.pack(pady=1)
        self.btn_kopyala = tk.Button(self.sel_frame, text=_t("Kopyala"),
                                     command=self._sel_copy,
                                     **_sel_btn_style("#16a085"))
        self.btn_kopyala.pack(pady=1)
        self.btn_tasi = tk.Button(self.sel_frame, text=_t("Ta\u015f\u0131"),
                                   command=self._enter_move,
                                   **_sel_btn_style("#2980b9"))
        self.btn_tasi.pack(pady=1)
        self.btn_dondur = tk.Button(self.sel_frame, text=_t("D\xf6nd\xfcr"),
                                    command=self._sel_rotate,
                                    **_sel_btn_style("#8e44ad"))
        self.btn_dondur.pack(pady=1)
        self.btn_flip_h = tk.Button(self.sel_frame, text=_t("\u2194 Yans\u0131"),
                                    command=self._sel_flip_h,
                                    **_sel_btn_style("#d35400"))
        self.btn_flip_h.pack(pady=1)
        self.btn_flip_v = tk.Button(self.sel_frame, text=_t("\u2195 Yans\u0131"),
                                    command=self._sel_flip_v,
                                    **_sel_btn_style("#d35400"))
        self.btn_flip_v.pack(pady=1)
        sep_sel = tk.Frame(ctrl_frame, bg="#34495e", height=1)
        sep_sel.pack(fill=tk.X, pady=4)

        # ─── Color palette button ───
        from tkinter import colorchooser
        tk.Label(ctrl_frame, text=_t("Renk"), bg="#2c3e50", fg="#bbb",
                 font=("Segoe UI", 8)).pack()
        tk.Button(ctrl_frame, text=_t("\u25A0 Palet"),
                  font=("Segoe UI", 9, "bold"),
                  bg="#34495e", fg="white", relief="flat", bd=0,
                  cursor="hand2", command=self._open_palette).pack(pady=1)
        self.picker_btn = tk.Button(ctrl_frame, text="\u25A0 \u25A0 \u25A0",
                                    font=("Segoe UI", 9),
                                    fg=self.brush_color, bg="#2c3e50",
                                    relief="flat", bd=0, cursor="hand2",
                                    command=lambda: self._pick_color(colorchooser))
        self.picker_btn.pack(pady=1)

        tk.Label(ctrl_frame, text=_t("Kal\u0131nl\u0131k"), bg="#2c3e50", fg="#bbb",
                 font=("Segoe UI", 8)).pack()
        self.size_var = tk.IntVar(value=self.brush_size)
        tk.Spinbox(ctrl_frame, from_=1, to=30, width=3,
                   textvariable=self.size_var, font=("Segoe UI", 9),
                   command=self._update_brush_size, bd=0).pack()

        tk.Label(ctrl_frame, text=_t("Yaz\u0131 Boyutu"), bg="#2c3e50", fg="#bbb",
                 font=("Segoe UI", 8)).pack()
        self.font_var = tk.IntVar(value=self.font_size)
        tk.Spinbox(ctrl_frame, from_=8, to=200, width=3,
                   textvariable=self.font_var, font=("Segoe UI", 9),
                   command=self._update_font_size, bd=0).pack()

        sep = tk.Frame(ctrl_frame, bg="#34495e", height=1)
        sep.pack(fill=tk.X, pady=4)

        tk.Button(ctrl_frame, text="Dondur 90", font=("Segoe UI", 7, "bold"),
                  bg="#34495e", fg="white", relief="flat", bd=0,
                  cursor="hand2", command=self._rotate).pack(pady=1)

        self.zoom_lbl = tk.Label(ctrl_frame, text="%%100", bg="#2c3e50",
                                 fg="#bbb", font=("Segoe UI", 8))
        self.zoom_lbl.pack()

        # ─── Canvas area ───
        self.right_frame = tk.Frame(body, bg="#ecf0f1")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.orig_w, self.orig_h = self.img.size

        self.tk_img = None
        self.canvas = tk.Canvas(self.right_frame, bg="#bdc3c7", highlightthickness=0,
                                cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self._render()

        self._bind_canvas()

        # ─── Bottom bar ───
        bar = tk.Frame(self.win, bg="#f8f9fa", height=44)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        self.action_btn = _mkbtn(bar, "Uygula", self._do_action,
                                 bg="#27ae60", width=12)
        self.action_btn.pack(side=tk.LEFT, padx=6, pady=6)
        _mkbtn(bar, "Geri Al", self._undo, bg="#7f8c8d", width=10).pack(
            side=tk.LEFT, padx=4, pady=6)
        _mkbtn(bar, "Kaydet", self._save, bg="#2980b9", width=10).pack(
            side=tk.LEFT, padx=4, pady=6)
        _mkbtn(bar, "Farkl\u0131 Kaydet", self._save_as, bg="#1abc9c", width=14).pack(
            side=tk.LEFT, padx=4, pady=6)
        _mkbtn(bar, "Kapat", self.win.destroy, bg="#e74c3c", width=10).pack(
            side=tk.RIGHT, padx=6, pady=6)

        info = tk.Frame(self.win, bg="#f8f9fa", height=26)
        info.pack(fill=tk.X)
        info.pack_propagate(False)
        self.status = tk.Label(info, text=_t("Ara\u00e7 se\u00e7in"), bg="#f8f9fa",
                               fg="#555", font=("Segoe UI", 9))
        self.status.pack(side=tk.LEFT, padx=10)
        self.size_label = tk.Label(info, text=f"{self.orig_w}x{self.orig_h}",
                                   bg="#f8f9fa", fg="#888", font=("Segoe UI", 9))
        self.size_label.pack(side=tk.RIGHT, padx=10)

        self._set_mode(self.MODE_CROP)

    # ───── Scale / Zoom ─────
    def _calc_base_scale(self):
        if not hasattr(self, "canvas") or not self.canvas:
            self.base_scale = 1.0
            return
        cw = self.canvas.winfo_width() or 920
        ch = self.canvas.winfo_height() or 560
        self.base_scale = min(cw / self.orig_w, ch / self.orig_h, 2)

    def _effective_scale(self):
        return self.base_scale * self.zoom

    def _img_coords(self, cx, cy):
        s = self._effective_scale()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        dw = int(self.orig_w * s)
        dh = int(self.orig_h * s)
        ox = (cw - dw) // 2
        oy = (ch - dh) // 2
        return int((cx - ox) / s), int((cy - oy) / s)

    # ───── Handle interaction ─────
    def _handle_rotate_start(self, e):
        if not self.sel_rect:
            return
        import math
        x1, y1, x2, y2 = self.sel_rect
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        self.sel_content = self.img.crop(self.sel_rect).copy()
        self._hide_float()
        self._redraw_sel()
        ccx, ccy = self._canvas_coords(cx, cy)
        self.handle_drag = {
            "type": "rotate",
            "center": (cx, cy),
            "canvas_center": (ccx, ccy),
            "start_angle": math.atan2(e.y - ccy, e.x - ccx),
            "total_angle": 0,
        }
        self.status.config(text=_t("Köşeyi sürükleyerek döndürün"))

    def _handle_resize_start(self, e):
        if not self.sel_rect:
            return
        x1, y1, x2, y2 = self.sel_rect
        cx1, cy1 = self._canvas_coords(x1, y1)
        cx2, cy2 = self._canvas_coords(x2, y2)
        edges = {"top": (cy1, "y", y1), "bottom": (cy2, "y", y2),
                  "left": (cx1, "x", x1), "right": (cx2, "x", x2)}
        closest = None
        best = 999999
        for name, (cpos, axis, ival) in edges.items():
            d = abs(e.x - cpos) if axis == "x" else abs(e.y - cpos)
            if d < best:
                best = d
                closest = name
        if closest is None:
            return
        self.sel_content = self.img.crop(self.sel_rect).copy()
        self._hide_float()
        self.handle_drag = {
            "type": "resize",
            "edge": closest,
            "start_rect": self.sel_rect,
            "start_size": (x2 - x1, y2 - y1),
        }
        self.status.config(text=_t("{closest} kenarından sürükleyin").replace("{closest}", closest))

    def _handle_drag_rotate(self, e):
        if not self.handle_drag or self.handle_drag["type"] != "rotate":
            return
        import math
        ccx, ccy = self.handle_drag["canvas_center"]
        cur_angle = math.atan2(e.y - ccy, e.x - ccx)
        da = cur_angle - self.handle_drag["start_angle"]
        self.handle_drag["total_angle"] = da
        deg = math.degrees(da) % 360
        if self.sel_content is not None:
            rotated = self.sel_content.rotate(
                -deg, expand=True, resample=Image.BICUBIC, fillcolor="white")
            x1, y1, x2, y2 = self.sel_rect
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            rx = cx - rotated.width / 2
            ry = cy - rotated.height / 2
            self._hide_float()
            self._show_float(rx, ry, image=rotated)
        self.status.config(text=_t("Döndürme: {deg}°").replace("{deg}", f"{deg:.0f}"))

    def _handle_drag_resize(self, e):
        if not self.handle_drag or self.handle_drag["type"] != "resize":
            return
        x1, y1, x2, y2 = self.handle_drag["start_rect"]
        edge = self.handle_drag["edge"]
        ix, iy = self._img_coords(e.x, e.y)
        if edge == "left":
            x1 = min(ix, x2 - 10)
        elif edge == "right":
            x2 = max(ix, x1 + 10)
        elif edge == "top":
            y1 = min(iy, y2 - 10)
        elif edge == "bottom":
            y2 = max(iy, y1 + 10)
        new_rect = (x1, y1, x2, y2)
        nw = max(1, x2 - x1)
        nh = max(1, y2 - y1)
        if self.sel_content is not None:
            resized = self.sel_content.resize((nw, nh), Image.LANCZOS)
            self._hide_float()
            self._show_float(x1, y1, image=resized)
        self.sel_rect = new_rect
        self._hide_sel()
        self._redraw_sel()
        self.status.config(text=_t("Yeniden boyutlandırma: {nw}x{nh}").replace("{nw}", str(nw)).replace("{nh}", str(nh)))

    def _handle_scale_start(self, e, hcx, hcy):
        if not self.sel_rect:
            return
        x1, y1, x2, y2 = self.sel_rect
        # Determine opposite corner
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        ccx, ccy = self._canvas_coords(center_x, center_y)
        self.sel_content = self.img.crop(self.sel_rect).copy()
        self._hide_float()
        self.handle_drag = {
            "type": "scale",
            "start_rect": self.sel_rect,
            "anchor": (x1, y1, x2, y2),
            "canvas_anchor": (hcx, hcy),
            "opposite": (x1, y1, x2, y2),  # will compute which corner is fixed
            "aspect": (x2 - x1) / max(1, y2 - y1),
        }
        # Determine which corner is opposite
        if hcx < ccx and hcy < ccy:
            self.handle_drag["opposite"] = (x2, y2, x2, y2)  # top-left drag → bottom-right fixed
        elif hcx > ccx and hcy < ccy:
            self.handle_drag["opposite"] = (x1, y2, x1, y2)  # top-right drag → bottom-left fixed
        elif hcx < ccx and hcy > ccy:
            self.handle_drag["opposite"] = (x2, y1, x2, y1)  # bottom-left drag → top-right fixed
        else:
            self.handle_drag["opposite"] = (x1, y1, x1, y1)  # bottom-right drag → top-left fixed
        self.status.config(text=_t("Oransal küçült/büyüt: köşeden sürükleyin"))

    def _handle_drag_scale(self, e):
        if not self.handle_drag or self.handle_drag["type"] != "scale":
            return
        ox, oy, _, _ = self.handle_drag["opposite"]
        ix, iy = self._img_coords(e.x, e.y)
        aspect = self.handle_drag["aspect"]
        # Resize proportionally from the opposite corner
        dw = abs(ix - ox)
        dh = abs(iy - oy)
        if dw / max(1, dh) > aspect:
            dh = int(dw / aspect)
        else:
            dw = int(dh * aspect)
        if ix < ox:
            x1, x2 = ox - dw, ox
        else:
            x1, x2 = ox, ox + dw
        if iy < oy:
            y1, y2 = oy - dh, oy
        else:
            y1, y2 = oy, oy + dh
        if x2 - x1 < 10 or y2 - y1 < 10:
            return
        new_rect = (x1, y1, x2, y2)
        nw, nh = x2 - x1, y2 - y1
        if self.sel_content is not None:
            resized = self.sel_content.resize((nw, nh), Image.LANCZOS)
            self._hide_float()
            self._show_float(x1, y1, image=resized)
        self.sel_rect = new_rect
        self._hide_sel()
        self._redraw_sel()
        self.status.config(text=_t("Oransal: {nw}x{nh}").replace("{nw}", str(nw)).replace("{nh}", str(nh)))

    def _handle_release(self):
        if not self.handle_drag:
            return
        if self.handle_drag["type"] == "rotate":
            if self.sel_content is not None and self.handle_drag["total_angle"] != 0:
                import math
                self.history.append(self.img.copy())
                deg = math.degrees(self.handle_drag["total_angle"]) % 360
                content_rgba = self.sel_content.convert("RGBA")
                rotated_rgba = content_rgba.rotate(
                    -deg, expand=True, resample=Image.BICUBIC, fillcolor=(0,0,0,0))
                mask = rotated_rgba.split()[3]
                x1, y1, x2, y2 = self.sel_rect
                from PIL import ImageDraw
                draw = ImageDraw.Draw(self.img)
                draw.rectangle([x1, y1, x2, y2], fill="white")
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                rx = int(cx - rotated_rgba.width / 2)
                ry = int(cy - rotated_rgba.height / 2)
                self.img.paste(rotated_rgba, (rx, ry), mask=mask)
                self._hide_float()
                self.sel_content = None
                self._render()
                self._redraw_sel()
                self.status.config(text=_t("Döndürüldü: {deg}°").replace("{deg}", f"{deg:.0f}"))
        elif self.handle_drag["type"] in ("resize", "scale"):
            if self.sel_rect:
                x1, y1, x2, y2 = self.sel_rect
                nw = max(1, x2 - x1)
                nh = max(1, y2 - y1)
                content = self.img.crop(self.handle_drag["start_rect"]).copy()
                resized = content.resize((nw, nh), Image.LANCZOS)
                self.history.append(self.img.copy())
                from PIL import ImageDraw
                draw = ImageDraw.Draw(self.img)
                sr = self.handle_drag["start_rect"]
                draw.rectangle([sr[0], sr[1], sr[2], sr[3]], fill="white")
                self.img.paste(resized, (x1, y1))
                self._hide_float()
                self.sel_content = None
                self._render()
                self._redraw_sel()
                lbl = "Olceklendi" if self.handle_drag["type"] == "scale" else "Yeniden boyutlandi"
                self.status.config(text=f"{lbl}: {nw}x{nh}")
        self.handle_drag = None

    # ───── Mode ─────
    def _set_mode(self, mode):
        self.mode = mode
        for m, btn in self.tool_btns.items():
            c = self.MODE_COLORS[m] if m == mode else "#2c3e50"
            btn.config(bg=c)
        self._clear_overlays()
        self._cancel_float()
        self.crop_rect = None
        self.select_rect_coords = None
        self.line_start = None
        if self.select_rect_id:
            self.canvas.delete(self.select_rect_id)
            self.select_rect_id = None
        self.sel_move_mode = False
        self.sel_content = None
        self.action_btn.config(text="Uygula", state=tk.NORMAL)
        if mode != self.MODE_SELECTION:
            self.btn_makas.config(state=tk.DISABLED)
            self.btn_boya.config(state=tk.DISABLED)
            self.btn_kopyala.config(state=tk.DISABLED)
            self.btn_tasi.config(state=tk.DISABLED)
            self.btn_dondur.config(state=tk.DISABLED)
            self.btn_flip_h.config(state=tk.DISABLED)
            self.btn_flip_v.config(state=tk.DISABLED)
        self.status.config(text=_t(self.HELP.get(mode, "")))

    # ───── Color / Size ─────
    def _set_color(self, color):
        self.brush_color = color
        if hasattr(self, "picker_btn"):
            self.picker_btn.config(fg=color)

    def _pick_color(self, colorchooser):
        code, color = colorchooser.askcolor(title="Renk Sec",
                                            initialcolor=self.brush_color)
        if color:
            self._set_color(color)

    def _open_palette(self):
        dlg = tk.Toplevel(self.win)
        dlg.title("Renk Paleti")
        dlg.geometry("240x180")
        dlg.resizable(False, False)
        dlg.transient(self.win)
        dlg.grab_set()
        from tkinter import colorchooser
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f",
                  "#9b59b6", "#000000", "#ffffff"]
        tk.Label(dlg, text="Renk Secin:", font=("Segoe UI", 9, "bold"),
                 bg="#2c3e50", fg="white").pack(pady=(8, 4))
        c_row = tk.Frame(dlg, bg="#2c3e50")
        c_row.pack()
        for c in colors:
            fb = tk.Frame(c_row, width=22, height=22, bg=c, bd=1,
                          relief="sunken", cursor="hand2")
            fb.pack(side=tk.LEFT, padx=2)
            fb.bind("<Button-1>", lambda e, col=c: (self._set_color(col), dlg.destroy()))
        def _pick_and_close():
            code, color = colorchooser.askcolor(title="Renk Sec",
                                                initialcolor=self.brush_color)
            if color:
                self._set_color(color)
            dlg.destroy()
        tk.Button(dlg, text="\u25A0 Ozel Renk...", font=("Segoe UI", 9),
                  bg="#34495e", fg="white", relief="flat", bd=0, cursor="hand2",
                  command=_pick_and_close).pack(pady=(10, 4))

    def _update_brush_size(self):
        self.brush_size = self.size_var.get()

    def _update_font_size(self):
        self.font_size = self.font_var.get()

    # ───── Canvas bindings ─────
    def _bind_canvas(self):
        self.canvas.bind("<ButtonPress-1>", self._press)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Configure>", lambda e: self._on_resize())
        self.canvas.bind("<Motion>", self._on_motion)

    def _on_resize(self):
        self._calc_base_scale()
        self._render()

    def _on_wheel(self, e):
        if e.delta > 0:
            self.zoom = min(self.zoom * 1.1, 5.0)
        else:
            self.zoom = max(self.zoom / 1.1, 0.2)
        self.zoom_lbl.config(text=f"%{int(self.zoom*100)}")
        self._render()

    def _on_motion(self, e):
        if self.mode != self.MODE_SELECTION or not self.handles:
            self.canvas.config(cursor="cross")
            return
        on_handle = False
        on_scale = False
        on_edge = False
        for hcx, hcy, htype in self.handles:
            if abs(e.x - hcx) < 7 and abs(e.y - hcy) < 7:
                on_handle = True
                if htype == "scale":
                    on_scale = True
                elif htype == "edge":
                    on_edge = True
                break
        if on_scale:
            self.canvas.config(cursor="fleur")
        elif on_edge:
            self.canvas.config(cursor="sb_h_double_arrow")
        elif on_handle:
            self.canvas.config(cursor="crosshair")
        else:
            self.canvas.config(cursor="cross")

    # ───── Press / Drag / Release ─────
    def _press(self, e):
        self.start_x, self.start_y = e.x, e.y
        s = self._effective_scale()

        if self.mode in (self.MODE_PAINT, self.MODE_ERASER):
            self._draw_point(e.x, e.y)

        elif self.mode == self.MODE_CROP:
            self._clear_overlays()
            self.rect_id = self.canvas.create_rectangle(
                e.x, e.y, e.x, e.y, outline="#e74c3c", width=2, dash=(4, 2))

        elif self.mode == self.MODE_KIRP:
            self._clear_overlays()
            self.rect_id = self.canvas.create_rectangle(
                e.x, e.y, e.x, e.y, outline="#8e44ad", width=2, dash=(4, 2))

        elif self.mode == self.MODE_SELECTION:
            if self.handles:
                for hcx, hcy, htype in self.handles:
                    if abs(e.x - hcx) < 7 and abs(e.y - hcy) < 7:
                        if htype == "rotate":
                            self._handle_rotate_start(e)
                        elif htype == "scale":
                            self._handle_scale_start(e, hcx, hcy)
                        else:
                            self._handle_resize_start(e)
                        return
            if self.sel_rect and self._in_sel_canvas(e.x, e.y):
                self._hide_float()
                self.sel_move_mode = True
                self.sel_move_start = (e.x, e.y)
                ix, iy = self._img_coords(e.x, e.y)
                x1, y1, x2, y2 = self.sel_rect
                self.sel_move_offset = (ix - x1, iy - y1)
                self.sel_content = self.img.crop(self.sel_rect).copy()
                self.status.config(text=_t("Seçimi sürükleyin"))
            else:
                self._cancel_float()
                self.sel_rect = None
                self.sel_content = None
                self.temp_rect_id = self.canvas.create_rectangle(
                    e.x, e.y, e.x, e.y, outline="#e74c3c", width=2, dash=(4, 2))
                self.sel_rect = None
                self.sel_content = None
                self.temp_rect_id = self.canvas.create_rectangle(
                    e.x, e.y, e.x, e.y, outline="#e74c3c", width=2, dash=(4, 2))

        elif self.mode == self.MODE_TEXT:
            ix, iy = self._img_coords(e.x, e.y)
            self._add_text(ix, iy)

        elif self.mode in (self.MODE_LINE, self.MODE_ARROW, self.MODE_ARROW_BOTH):
            self.line_start = (e.x, e.y)

    def _drag(self, e):
        s = self._effective_scale()

        if self.mode in (self.MODE_PAINT, self.MODE_ERASER):
            self._draw_line(e.x, e.y)

        elif self.mode == self.MODE_CROP:
            if hasattr(self, "rect_id") and self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, e.x, e.y,
                outline="#e74c3c", width=2, dash=(4, 2))

        elif self.mode == self.MODE_KIRP:
            if hasattr(self, "rect_id") and self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, e.x, e.y,
                outline="#8e44ad", width=2, dash=(4, 2))

        elif self.mode == self.MODE_SELECTION:
            if self.handle_drag:
                t = self.handle_drag["type"]
                if t == "rotate":
                    self._handle_drag_rotate(e)
                elif t == "scale":
                    self._handle_drag_scale(e)
                else:
                    self._handle_drag_resize(e)
                return
            if self.sel_move_mode and self.sel_rect and self.sel_content is not None:
                self._hide_float()
                dx = e.x - self.sel_move_start[0]
                dy = e.y - self.sel_move_start[1]
                s2 = self._effective_scale()
                x1, y1, x2, y2 = self.sel_rect
                self.move_dx = int(dx / s2)
                self.move_dy = int(dy / s2)
                self._show_float(x1 + self.move_dx, y1 + self.move_dy)
            elif hasattr(self, "temp_rect_id") and self.temp_rect_id:
                self.canvas.delete(self.temp_rect_id)
                self.temp_rect_id = self.canvas.create_rectangle(
                    self.start_x, self.start_y, e.x, e.y,
                    outline="#e74c3c", width=2, dash=(4, 2))

        elif self.mode in (self.MODE_LINE, self.MODE_ARROW, self.MODE_ARROW_BOTH):
            if self.line_preview_id:
                self.canvas.delete(self.line_preview_id)
            self.line_preview_id = self.canvas.create_line(
                self.start_x, self.start_y, e.x, e.y,
                fill=self.brush_color, width=max(1, int(self.brush_size * s / 2)),
                arrow={"line": "none", "arrow": "last",
                       "arrow_both": "both"}[self.mode])

    def _release(self, e):
        if self.mode == self.MODE_CROP:
            x1, y1 = min(self.start_x, e.x), min(self.start_y, e.y)
            x2, y2 = max(self.start_x, e.x), max(self.start_y, e.y)
            if x2 - x1 < 5 or y2 - y1 < 5:
                return
            ix1, iy1 = self._img_coords(x1, y1)
            ix2, iy2 = self._img_coords(x2, y2)
            self.crop_rect = (ix1, iy1, ix2, iy2)
            self.status.config(
                text=f"Kes: ({ix1},{iy1}) \u2192 ({ix2},{iy2})")

        elif self.mode == self.MODE_KIRP:
            x1, y1 = min(self.start_x, e.x), min(self.start_y, e.y)
            x2, y2 = max(self.start_x, e.x), max(self.start_y, e.y)
            if x2 - x1 < 5 or y2 - y1 < 5:
                return
            ix1, iy1 = self._img_coords(x1, y1)
            ix2, iy2 = self._img_coords(x2, y2)
            self.history.append(self.img.copy())
            self.img = self.img.crop((ix1, iy1, ix2, iy2))
            self.orig_w, self.orig_h = self.img.size
            self.size_label.config(text=f"{self.orig_w}x{self.orig_h}")
            self._calc_base_scale()
            self._render()
            self.status.config(text=_t("Görüntü kırpıldı: {w}x{h}").replace("{w}", str(self.orig_w)).replace("{h}", str(self.orig_h)))

        elif self.mode == self.MODE_SELECTION:
            if self.handle_drag:
                self._handle_release()
                return
            if self.sel_move_mode and self.sel_move_start and self.sel_rect and self.sel_content is not None:
                dx = e.x - self.sel_move_start[0]
                dy = e.y - self.sel_move_start[1]
                s2 = self._effective_scale()
                dix = int(dx / s2)
                diy = int(dy / s2)
                self.sel_move_mode = False
                self.sel_move_start = None
                self.sel_move_offset = None
                if abs(dix) < 2 and abs(diy) < 2:
                    self.move_dx = 0
                    self.move_dy = 0
                    self._hide_float()
                    self._redraw_sel()
                    self.status.config(text=_t("Taşı iptal"))
                    return
                self.move_dx = dix
                self.move_dy = diy
                self.action_btn.config(state=tk.NORMAL)
                self._hide_float()
                x1, y1, x2, y2 = self.sel_rect
                self._render()
                self._show_float(x1 + dix, y1 + diy)
                self.status.config(text=_t("Taşı: Uygula'ya basın"))
                self.status.config(text=_t("Seçim taşındı"))
                return
            x1, y1 = min(self.start_x, e.x), min(self.start_y, e.y)
            x2, y2 = max(self.start_x, e.x), max(self.start_y, e.y)
            if x2 - x1 < 5 or y2 - y1 < 5:
                return
            ix1, iy1 = self._img_coords(x1, y1)
            ix2, iy2 = self._img_coords(x2, y2)
            self.sel_rect = (ix1, iy1, ix2, iy2)
            self._hide_sel()
            self._redraw_sel()
            self.select_rect_coords = self.sel_rect
            self.btn_makas.config(state=tk.NORMAL)
            self.btn_boya.config(state=tk.NORMAL)
            self.btn_kopyala.config(state=tk.NORMAL)
            self.btn_tasi.config(state=tk.NORMAL)
            self.btn_dondur.config(state=tk.NORMAL)
            self.btn_flip_h.config(state=tk.NORMAL)
            self.btn_flip_v.config(state=tk.NORMAL)
            self.status.config(text=_t("Alan seçildi"))

        elif self.mode in (self.MODE_LINE, self.MODE_ARROW, self.MODE_ARROW_BOTH):
            if self.line_start:
                self.history.append(self.img.copy())
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(self.img)
                x1, y1 = self._img_coords(self.start_x, self.start_y)
                x2, y2 = self._img_coords(e.x, e.y)
                lw = max(1, self.brush_size)
                draw.line([(x1, y1), (x2, y2)], fill=self.brush_color, width=lw)

                if self.mode in (self.MODE_ARROW, self.MODE_ARROW_BOTH):
                    self._draw_arrowhead(draw, x1, y1, x2, y2, lw)
                if self.mode == self.MODE_ARROW_BOTH:
                    self._draw_arrowhead(draw, x2, y2, x1, y1, lw)

                self.line_start = None
                if self.line_preview_id:
                    self.canvas.delete(self.line_preview_id)
                    self.line_preview_id = None
                self._render()

        self._clear_overlays()

    def _draw_arrowhead(self, draw, x1, y1, x2, y2, lw):
        import math
        angle = math.atan2(y2 - y1, x2 - x1)
        sz = max(10, lw * 4)
        p1 = (x2 - sz * math.cos(angle - 0.5),
              y2 - sz * math.sin(angle - 0.5))
        p2 = (x2 - sz * math.cos(angle + 0.5),
              y2 - sz * math.sin(angle + 0.5))
        draw.polygon([(x2, y2), p1, p2], fill=self.brush_color)

    # ───── Drawing helpers ─────
    def _draw_point(self, cx, cy):
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.img)
        r = self.brush_size / 2
        ix, iy = self._img_coords(cx, cy)
        draw.ellipse([ix - r, iy - r, ix + r, iy + r], fill=self.brush_color)
        self._render()

    def _draw_line(self, cx, cy):
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.img)
        sx, sy = self._img_coords(self.start_x, self.start_y)
        ex, ey = self._img_coords(cx, cy)
        draw.line([(sx, sy), (ex, ey)], fill=self.brush_color,
                  width=max(1, self.brush_size))
        self.start_x, self.start_y = cx, cy
        self._render()

    def _clear_overlays(self):
        if hasattr(self, "rect_id") and self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        if hasattr(self, "temp_rect_id") and self.temp_rect_id:
            self.canvas.delete(self.temp_rect_id)
            self.temp_rect_id = None

    # ───── Text ─────
    def _add_text(self, ix, iy):
        dlg = tk.Toplevel(self.win)
        dlg.title("Metin Ekle")
        dlg.geometry("320x120")
        dlg.resizable(False, False)
        dlg.transient(self.win)
        dlg.grab_set()

        tk.Label(dlg, text="Metin:", font=("Segoe UI", 10)).pack(pady=(12, 4))
        entry = tk.Entry(dlg, font=("Segoe UI", 10), width=30)
        entry.pack(padx=12)
        entry.focus_set()

        def on_ok():
            text = entry.get().strip()
            if text:
                self.history.append(self.img.copy())
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(self.img)
                try:
                    font = ImageFont.truetype("arial.ttf", self.font_size)
                except Exception:
                    font = ImageFont.load_default()
                draw.text((ix, iy), text, fill=self.brush_color, font=font)
                self._render()
                self.status.config(text=_t('Metin eklendi: "{text}"').replace("{text}", text))
            dlg.destroy()

        tk.Button(dlg, text="Ekle", command=on_ok,
                  bg="#27ae60", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", bd=0, padx=20, pady=4, cursor="hand2").pack(pady=8)
        entry.bind("<Return>", lambda e: on_ok())

    # ───── Rotate ─────
    def _rotate(self):
        self.history.append(self.img.copy())
        self.img = self.img.rotate(90, expand=True)
        self.orig_w, self.orig_h = self.img.size
        self.size_label.config(text=f"{self.orig_w}x{self.orig_h}")
        self._calc_base_scale()
        self._render()
        self.status.config(text=_t("90 derece döndürüldü"))

    # ───── Render ─────
    def _render(self):
        self._calc_base_scale()
        s = self._effective_scale()
        dw = max(1, int(self.orig_w * s))
        dh = max(1, int(self.orig_h * s))
        self.disp_img = self.img.resize((dw, dh), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(self.disp_img)
        self.canvas.delete("all")
        cx, cy = self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2
        if cx > 10 and cy > 10:
            self.canvas.create_image(cx, cy, anchor="center", image=self.tk_img)
        if self.mode == self.MODE_SELECTION and self.sel_rect:
            self._redraw_sel()
        if self.sel_content is not None and (self.move_dx or self.move_dy):
            x1, y1, x2, y2 = self.sel_rect
            self._show_float(x1 + self.move_dx, y1 + self.move_dy)

    # ───── Actions ─────
    def _do_action(self):
        if self.mode == self.MODE_CROP and self.crop_rect:
            self.history.append(self.img.copy())
            from PIL import ImageDraw
            draw = ImageDraw.Draw(self.img)
            x1, y1, x2, y2 = self.crop_rect
            draw.rectangle([x1, y1, x2, y2], fill=self.brush_color)
            self._render()
            self.crop_rect = None
            self._clear_overlays()
            self.status.config(text=_t("Alan renklendirildi"))
        elif self.sel_content is not None and (self.move_dx or self.move_dy):
            self.history.append(self.img.copy())
            x1, y1, x2, y2 = self.sel_rect
            w, h = x2 - x1, y2 - y1
            if not self.copy_mode:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(self.img)
                draw.rectangle([x1, y1, x1 + w, y1 + h], fill="white")
            nx, ny = x1 + self.move_dx, y1 + self.move_dy
            self.img.paste(self.sel_content, (nx, ny))
            self.sel_rect = (nx, ny, nx + w, ny + h)
            self._hide_float()
            self.move_dx = 0
            self.move_dy = 0
            self.sel_content = None
            self.copy_mode = False
            self.action_btn.config(state=tk.DISABLED)
            self._render()
            self.status.config(text=_t("Taşı uygulandı"))

    def _sel_fill(self):
        if not self.sel_rect:
            return
        self.history.append(self.img.copy())
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.img)
        x1, y1, x2, y2 = self.sel_rect
        draw.rectangle([x1, y1, x2, y2], fill=self.brush_color)
        self._render()
        self._redraw_sel()
        self.status.config(text=_t("Alan boyandı"))

    def _sel_cut(self):
        if not self.sel_rect:
            return
        self.history.append(self.img.copy())
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.img)
        x1, y1, x2, y2 = self.sel_rect
        draw.rectangle([x1, y1, x2, y2], fill="white")
        self._render()
        self._redraw_sel()
        self.status.config(text=_t("Alan kesildi"))

    def _sel_copy(self):
        if not self.sel_rect:
            return
        self.copy_mode = True
        self.sel_content = self.img.crop(self.sel_rect).copy()
        self._hide_float()
        self._redraw_sel()
        self._show_float(self.sel_rect[0], self.sel_rect[1])
        self.action_btn.config(state=tk.NORMAL)
        self.status.config(text=_t("Kopya oluştu, Uygula ile yapıştırın"))

    def _sel_flip_h(self):
        if not self.sel_rect:
            return
        self.history.append(self.img.copy())
        x1, y1, x2, y2 = self.sel_rect
        content = self.img.crop((x1, y1, x2, y2))
        flipped = content.transpose(Image.FLIP_LEFT_RIGHT)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.img)
        draw.rectangle([x1, y1, x2, y2], fill="white")
        self.img.paste(flipped, (x1, y1))
        self._render()
        self._redraw_sel()
        self.status.config(text=_t("Yatay yansıtıldı"))

    def _sel_flip_v(self):
        if not self.sel_rect:
            return
        self.history.append(self.img.copy())
        x1, y1, x2, y2 = self.sel_rect
        content = self.img.crop((x1, y1, x2, y2))
        flipped = content.transpose(Image.FLIP_TOP_BOTTOM)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(self.img)
        draw.rectangle([x1, y1, x2, y2], fill="white")
        self.img.paste(flipped, (x1, y1))
        self._render()
        self._redraw_sel()
        self.status.config(text=_t("Dikey yansıtıldı"))

    def _sel_rotate(self):
        if not self.sel_rect:
            return
        angle_str = simpledialog.askstring("D\xf6nd\xfcr", "A\xe7\u0131 (0-360):", initialvalue="90")
        if not angle_str:
            return
        try:
            angle = float(angle_str) % 360
        except ValueError:
            return
        from PIL import ImageDraw
        self.history.append(self.img.copy())
        x1, y1, x2, y2 = self.sel_rect
        w, h = x2 - x1, y2 - y1
        if w < 1 or h < 1:
            return
        content_rgba = self.img.crop((x1, y1, x2, y2)).convert("RGBA")
        rotated_rgba = content_rgba.rotate(angle, expand=True, resample=Image.BICUBIC, fillcolor=(0,0,0,0))
        mask = rotated_rgba.split()[3]
        draw = ImageDraw.Draw(self.img)
        draw.rectangle([x1, y1, x2, y2], fill="white")
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        rx = int(cx - rotated_rgba.width / 2)
        ry = int(cy - rotated_rgba.height / 2)
        self.img.paste(rotated_rgba, (rx, ry), mask=mask)
        self._hide_sel()
        self._redraw_sel()
        self._render()
        self.status.config(text=_t("Alan d\xf6nd\xfcr\xfcld\xfc: {angle}\xb0").replace("{angle}", str(angle)))

    def _enter_move(self):
        self.status.config(text=_t("Seçimi sürükleyip bırakın"))

    def _in_sel_canvas(self, cx, cy):
        if not self.sel_rect:
            return False
        s = self._effective_scale()
        x1, y1, x2, y2 = self.sel_rect
        ox = (self.canvas.winfo_width() - int(self.orig_w * s)) // 2
        oy = (self.canvas.winfo_height() - int(self.orig_h * s)) // 2
        px = int(x1 * s) + ox
        py = int(y1 * s) + oy
        qx = int(x2 * s) + ox
        qy = int(y2 * s) + oy
        return px <= cx <= qx and py <= cy <= qy

    def _canvas_coords(self, ix, iy):
        s = self._effective_scale()
        ox = (self.canvas.winfo_width() - int(self.orig_w * s)) // 2
        oy = (self.canvas.winfo_height() - int(self.orig_h * s)) // 2
        return (int(ix * s) + ox, int(iy * s) + oy)

    def _hide_sel(self):
        for cid in self.sel_canvas_ids:
            self.canvas.delete(cid)
        self.sel_canvas_ids.clear()

    def _redraw_sel(self):
        self._hide_sel()
        self.handles = []
        if not self.sel_rect:
            return
        x1, y1, x2, y2 = self.sel_rect
        cx1, cy1 = self._canvas_coords(x1, y1)
        cx2, cy2 = self._canvas_coords(x2, y2)
        r = self.canvas.create_rectangle(
            cx1, cy1, cx2, cy2, outline="#e74c3c", width=2, dash=(4, 2))
        self.sel_canvas_ids.append(r)
        # ── Draw handles ──
        hr = 5
        corners = [(cx1, cy1), (cx2, cy1), (cx1, cy2), (cx2, cy2)]
        corner_types = ["rotate", "scale", "scale", "rotate"]
        for i, (cx, cy) in enumerate(corners):
            fill = "#f39c12" if corner_types[i] == "scale" else "white"
            h = self.canvas.create_rectangle(
                cx - hr, cy - hr, cx + hr, cy + hr,
                fill=fill, outline="#e74c3c", width=2)
            self.sel_canvas_ids.append(h)
            self.handles.append((cx, cy, corner_types[i]))
        er = 4
        edges = [((cx1 + cx2) // 2, cy1), (cx2, (cy1 + cy2) // 2),
                 ((cx1 + cx2) // 2, cy2), (cx1, (cy1 + cy2) // 2)]
        for cx, cy in edges:
            h = self.canvas.create_rectangle(
                cx - er, cy - er, cx + er, cy + er,
                fill="#e74c3c", outline="white", width=1)
            self.sel_canvas_ids.append(h)
            self.handles.append((cx, cy, "edge"))

    def _hide_float(self):
        if self.float_img_id is not None:
            self.canvas.delete(self.float_img_id)
            self.float_img_id = None
        self.float_tk = None

    def _show_float(self, ix, iy, image=None):
        self._hide_float()
        src = image if image is not None else self.sel_content
        if src is None:
            return
        s = self._effective_scale()
        cw = int(src.width * s)
        ch = int(src.height * s)
        if cw < 1 or ch < 1:
            return
        disp = src.resize((cw, ch), Image.LANCZOS)
        self.float_tk = ImageTk.PhotoImage(disp)
        cx, cy = self._canvas_coords(ix, iy)
        self.float_img_id = self.canvas.create_image(cx, cy, anchor="nw", image=self.float_tk)
        cx2, cy2 = self._canvas_coords(ix + src.width, iy + src.height)
        r = self.canvas.create_rectangle(cx, cy, cx2, cy2, outline="#e74c3c", width=2, dash=(4, 2))
        self.sel_canvas_ids.append(r)

    def _cancel_float(self):
        self._hide_float()
        self.move_dx = 0
        self.move_dy = 0
        self.sel_content = None
        self._hide_sel()
        self.sel_rect = None
        self.copy_mode = False
        self.handle_drag = None
        self.btn_makas.config(state=tk.DISABLED)
        self.btn_boya.config(state=tk.DISABLED)
        self.btn_kopyala.config(state=tk.DISABLED)
        self.btn_tasi.config(state=tk.DISABLED)
        self.btn_dondur.config(state=tk.DISABLED)
        self.btn_flip_h.config(state=tk.DISABLED)
        self.btn_flip_v.config(state=tk.DISABLED)
        self.action_btn.config(state=tk.DISABLED)

    def _undo(self):
        if len(self.history) > 1:
            self.history.pop()
            self.img = self.history[-1].copy()
            self.orig_w, self.orig_h = self.img.size
            self.size_label.config(text=f"{self.orig_w}x{self.orig_h}")
            self._calc_base_scale()
            self._cancel_float()
            self._render()
            self.crop_rect = None
            self._clear_overlays()
            self.btn_makas.config(state=tk.DISABLED)
            self.btn_boya.config(state=tk.DISABLED)
            self.btn_kopyala.config(state=tk.DISABLED)
            self.btn_tasi.config(state=tk.DISABLED)
            self.btn_dondur.config(state=tk.DISABLED)
            self.btn_flip_h.config(state=tk.DISABLED)
            self.btn_flip_v.config(state=tk.DISABLED)
            self.action_btn.config(state=tk.DISABLED)
            self.status.config(text=_t("Geri alındı"))

    def _save(self):
        self.img.save(self.image_path)
        if self.on_save:
            self.on_save(self.image_path)
        messagebox.showinfo(_t("Bitti"), "Resim kaydedildi.")
        self.win.destroy()

    def _save_as(self):
        ftypes = [
            ("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp"),
            ("GIF", "*.gif"), ("TIFF", "*.tiff"), ("WEBP", "*.webp"),
            ("ICO", "*.ico"), ("T\u00fcm Formatlar", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff;*.webp;*.ico"),
        ]
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=ftypes,
            initialdir=os.path.dirname(self.image_path),
            initialfile=os.path.splitext(os.path.basename(self.image_path))[0])
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        fmt_map = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".bmp": "BMP",
                   ".gif": "GIF", ".tiff": "TIFF", ".tif": "TIFF", ".webp": "WEBP", ".ico": "ICO"}
        fmt = fmt_map.get(ext, "PNG")
        save_kw = {}
        if fmt == "JPEG":
            save_kw["quality"] = 95
        self.img.save(path, fmt, **save_kw)
        if self.on_save:
            self.on_save(path)
        messagebox.showinfo(_t("Bitti"), f"Resim kaydedildi:\n{path}")
        self.win.destroy()


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF_Create_Export_Edit")
        self.root.geometry("960x680")
        self.root.minsize(720, 480)

        self.image_dir = None
        self.images = []
        self.selection = {}
        self.thumb_refs = {}
        self.thumb_frames = {}

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def _build_ui(self):
        # ─── Header ───
        header = tk.Frame(self.root, bg="#1a252f", height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="PDF Image Export", fg="white", bg="#1a252f",
            font=("Segoe UI", 18, "bold"),
        ).pack(side=tk.LEFT, padx=20, pady=12)
        tk.Label(
            header, text=_t("PDF \u2194 Resim Dönüştürücü"),
            fg="#95a5a6", bg="#1a252f", font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, padx=6, pady=12)

        # ─── Toolbar (scrollable, 2 satır, gruplu hizalama) ───
        tbar_canvas = tk.Canvas(self.root, bg="#2c3e50", height=88, highlightthickness=0)
        tbar_canvas.pack(fill=tk.X)
        tbar_canvas.pack_propagate(False)

        toolbar = tk.Frame(tbar_canvas, bg="#2c3e50")
        toolbar.bind("<Configure>", lambda e: tbar_canvas.configure(
            scrollregion=tbar_canvas.bbox("all")))
        tbar_canvas.create_window((0, 0), window=toolbar, anchor="nw")
        tbar_canvas.bind("<MouseWheel>", lambda e: tbar_canvas.xview_scroll(
            -int(e.delta / 120), "units"))

        bg_color = "#2c3e50"

        def _group():
            g = tk.Frame(toolbar, bg=bg_color)
            g.pack(side=tk.LEFT, padx=2)
            r1 = tk.Frame(g, bg=bg_color)
            r1.pack(fill=tk.X, pady=(6, 3))
            r2 = tk.Frame(g, bg=bg_color)
            r2.pack(fill=tk.X, pady=(3, 6))
            return r1, r2

        # Grup 1: PDF Yükle / Resim Yükle — Tümünü Seç / Seçimi Kaldır
        g1r1, g1r2 = _group()
        _mkbtn(g1r1, "PDF Y\xfckle", self.open_pdf, bg="#3498db", width=14).pack(side=tk.LEFT, padx=6)
        _mkbtn(g1r1, "Resim Y\xfckle", self.open_images, bg="#3498db", width=14).pack(side=tk.LEFT, padx=6)
        _mkbtn(g1r2, "T\xfcm\xfcn\xfc Se\xe7", self.select_all, bg="#7f8c8d", width=14).pack(side=tk.LEFT, padx=6)
        _mkbtn(g1r2, "Se\xe7imi Kald\u0131r", self.deselect_all, bg="#7f8c8d", width=14).pack(side=tk.LEFT, padx=6)
        tk.Frame(toolbar, bg="#34495e", width=1).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        # Grup 2: PDF Metin Düzenle — ↑ Yukarı / ↓ Aşağı
        g2r1, g2r2 = _group()
        _mkbtn(g2r1, "PDF Metin D\xfczenle", self.edit_pdf_text, bg="#e67e22", width=22).pack(side=tk.LEFT, padx=6)
        mid = tk.Frame(g2r2, bg=bg_color)
        mid.pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        _mkbtn(mid, "\u2191 Yukar\u0131", self.move_up, bg="#8e44ad", width=10).pack(side=tk.LEFT)
        tk.Label(mid, text="  ", bg=bg_color).pack(side=tk.LEFT)
        _mkbtn(mid, "\u2193 A\u015fa\u011f\u0131", self.move_down, bg="#8e44ad", width=10).pack(side=tk.LEFT)
        tk.Frame(toolbar, bg="#34495e", width=1).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        # Grup 3: Resmi Düzenle / Seçilenleri PDF Yap / Seçileni Kaydet — Hakkında
        g3r1, g3r2 = _group()
        _mkbtn(g3r1, "Resmi D\xfczenle", self.crop_selected, bg="#27ae60", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r1, "Se\xe7ilenleri PDF Yap", self.make_pdf, bg="#e67e22", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r1, "Se\xe7ileni Kaydet", self.save_selected, bg="#2980b9", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r2, "Hakk\u0131nda", self.show_about, bg="#7f8c8d", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r2, "Sa\u011f Tu\u015fa Ekle", self.add_context_menu, bg="#27ae60", width=16).pack(side=tk.LEFT, padx=6)
        _mkbtn(g3r2, "Sa\u011f Tu\u015ftan Kald\u0131r", self.remove_context_menu, bg="#c0392b", width=16).pack(side=tk.LEFT, padx=6)
        tk.Frame(toolbar, bg="#34495e", width=1).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        _mkbtn(g3r2, "EN" if _current_lang == "tr" else "TR",
               self._toggle_lang, bg="#34495e", width=6).pack(side=tk.LEFT, padx=6)
        ttk.Separator(g3r2, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=4)
        _mkbtn(g3r2, "?", self.show_help, bg="#34495e", width=3).pack(side=tk.LEFT, padx=2)

        # ─── Thumbnail area ───
        container = tk.Frame(self.root, bg="#ecf0f1")
        container.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(container, bg="white", bd=1, relief="solid")
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.canvas_area = tk.Canvas(inner, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(inner, orient="vertical", command=self.canvas_area.yview)
        self.scrollable = tk.Frame(self.canvas_area, bg="white")

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas_area.configure(scrollregion=self.canvas_area.bbox("all")),
        )
        self.canvas_area.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas_area.configure(yscrollcommand=scrollbar.set)

        self.canvas_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ─── Status bar ───
        status_bar = tk.Frame(self.root, bg="#f8f9fa", height=30, bd=1, relief="sunken")
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)

        self.status_label = tk.Label(
            status_bar, text=_t("Haz\u0131r"), bg="#f8f9fa", fg="#555",
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.count_label = tk.Label(
            status_bar, text=_t("0 g\xf6rsel"), bg="#f8f9fa", fg="#888",
            font=("Segoe UI", 9),
        )
        self.count_label.pack(side=tk.RIGHT, padx=10)

        self.canvas_area.bind("<Configure>", lambda e: self._show_thumbs())

    def _set_status(self, text):
        self.status_label.config(text=_t(text))

    def _toggle_lang(self):
        global _current_lang
        new = "en" if _current_lang == "tr" else "tr"
        _set_lang(new)
        self.root.destroy()
        restart_app()

    def clear_thumbs(self):
        for w in self.scrollable.winfo_children():
            w.destroy()
        self.images = []
        self.selection = {}
        self.thumb_refs = {}
        self.thumb_frames = {}
        self.count_label.config(text=_t("0 g\xf6rsel"))

    def load_images(self, paths):
        self.clear_thumbs()
        self.images = paths
        self.image_dir = os.path.dirname(paths[0]) if paths else None
        self.selection = {p: tk.BooleanVar(value=False) for p in paths}
        self._show_thumbs()
        self._set_status(_t("{n} görsel yüklendi").replace("{n}", str(len(paths))))
        self.count_label.config(text=f"{len(paths)} g\xf6rsel")

    def _show_thumbs(self, *_):
        for w in self.scrollable.winfo_children():
            w.destroy()

        if not self.images:
            return

        cw = self.canvas_area.winfo_width() or 700
        cols = max(1, (cw - 20) // 165)

        row = col = 0
        for i, path in enumerate(self.images):
            frame = tk.Frame(
                self.scrollable, bg="white", bd=1, relief="solid",
                highlightbackground="#dcdde1", highlightthickness=1,
            )
            frame.grid(row=row, column=col, padx=8, pady=8, sticky="n")
            self.thumb_frames[path] = frame

            try:
                img = Image.open(path)
                img.thumbnail((150, 150), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
                self.thumb_refs[path] = tk_img
            except Exception:
                continue

            lbl = tk.Label(frame, image=tk_img, bg="white", cursor="hand2")
            lbl.pack(padx=4, pady=(4, 0))
            lbl.bind("<Double-Button-1>", lambda e, p=path: self.open_editor(p))

            cb = tk.Checkbutton(frame, variable=self.selection[path],
                                bg="white", cursor="hand2")
            cb.pack(pady=(2, 0))
            cb.bind("<Double-Button-1>", lambda e, p=path: self.open_editor(p))

            name = os.path.basename(path)
            tk.Label(frame, text=name, bg="white", fg="#555",
                     wraplength=150, font=("Segoe UI", 8)).pack(pady=(0, 4))

            frame.bind("<Button-1>", lambda e, p=path, idx=i: self._drag_start(e, p, idx))
            lbl.bind("<Button-1>", lambda e, p=path, idx=i: self._drag_start(e, p, idx))
            cb.bind("<Button-1>", lambda e, p=path, idx=i: self._drag_start(e, p, idx))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        self.scrollable.update_idletasks()

    def _drag_start(self, e, path, idx):
        self._drag_source_path = path
        self._drag_source_idx = idx
        self._drag_widget = e.widget
        self._drag_start_x = e.x_root
        self._drag_start_y = e.y_root
        self._drag_widget.config(cursor="fleur")
        self._drag_widget.bind("<B1-Motion>", self._drag_motion)
        self._drag_widget.bind("<ButtonRelease-1>", self._drag_drop)

    def _drag_motion(self, e):
        w = e.widget
        dx = e.x_root - self._drag_start_x
        dy = e.y_root - self._drag_start_y
        if abs(dx) > 15 or abs(dy) > 15:
            w.config(cursor="fleur")

    def _drag_drop(self, e):
        w = self._drag_widget if hasattr(self, "_drag_widget") else e.widget
        w.unbind("<B1-Motion>")
        w.unbind("<ButtonRelease-1>")
        w.config(cursor="")
        if not hasattr(self, "_drag_source_path"):
            return
        dx = e.x_root - self._drag_start_x
        dy = e.y_root - self._drag_start_y
        if abs(dx) < 20 and abs(dy) < 20:
            del self._drag_source_path
            del self._drag_widget
            return
        drop_x, drop_y = e.x_root, e.y_root
        kids = self.scrollable.winfo_children()
        best_idx = self._drag_source_idx
        best_dist = 999999
        for i, child in enumerate(kids):
            if child == self.thumb_frames.get(self._drag_source_path):
                continue
            cx = child.winfo_rootx() + child.winfo_width() // 2
            cy = child.winfo_rooty() + child.winfo_height() // 2
            d = (cx - drop_x) ** 2 + (cy - drop_y) ** 2
            if d < best_dist:
                best_dist = d
                best_idx = i
        if best_idx != self._drag_source_idx:
            item = self.images.pop(self._drag_source_idx)
            target = best_idx if best_idx < self._drag_source_idx else best_idx - 1
            self.images.insert(target, item)
            self._show_thumbs()
            self._set_status(_t("Sıralama güncellendi"))
        del self._drag_source_path
        del self._drag_widget

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path:
            return

        self._set_status(_t("PDF işleniyor..."))
        self.root.update()
        try:
            os.makedirs(RESIMLER_DIR, exist_ok=True)
            doc = fitz.open(path)
            base = os.path.splitext(os.path.basename(path))[0]
            paths = []
            for i in range(len(doc)):
                page = doc[i]
                pix = None
                for zoom in [2, 1, 0.5, 0.25]:
                    try:
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        break
                    except Exception:
                        continue
                if pix is None:
                    raise RuntimeError("Sayfa cok buyuk, render edilemiyor")
                img_path = os.path.join(RESIMLER_DIR, f"{base}_{i + 1}.png")
                pix.save(img_path)
                pix = None
                paths.append(img_path)
            doc.close()
            paths.sort(key=lambda x: int(x.rsplit("_", 1)[1].rsplit(".", 1)[0]))
            self.load_images(paths)
        except Exception as e:
            self._set_status(_t("Hata: {e}").replace("{e}", str(e)))
            messagebox.showerror(_t("Hata"), str(e))

    def open_images(self):
        paths = filedialog.askopenfilenames(
            filetypes=[("Resim", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        if paths:
            self.load_images(list(paths))

    def edit_pdf_text(self, path=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
            if not path:
                return
        try:
            doc = fitz.open(path)
        except Exception as e:
            messagebox.showerror(_t("Hata"), f"PDF a\xe7\x0131lamad\u0131: {e}")
            return
        dlg = tk.Toplevel(self.root)
        dlg.title(f"PDF Metin D\xfczenle - {os.path.basename(path)}")
        dlg.geometry("750x650")
        dlg.transient(self.root)
        dlg.grab_set()
        _fullscreen = False
        _saved_geom = "750x650"
        def _toggle_fullscreen():
            nonlocal _fullscreen, _saved_geom
            if not _fullscreen:
                _saved_geom = dlg.geometry()
                dlg.attributes("-fullscreen", True)
            else:
                dlg.attributes("-fullscreen", False)
                dlg.geometry(_saved_geom)
            _fullscreen = not _fullscreen
            fs_btn.config(text="\u25a2 Tam Ekran" if not _fullscreen else "\u25a2 Pencere")
        def _exit_fs(e):
            if _fullscreen:
                _toggle_fullscreen()
        dlg.bind("<Escape>", _exit_fs)
        top = tk.Frame(dlg, bg="#2c3e50", height=40)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        page_var = tk.IntVar(value=1)
        page_blocks = {}
        def _load_page():
            block_list.delete(0, tk.END)
            edit_text.delete("1.0", tk.END)
            pi = page_var.get() - 1
            if pi in page_blocks:
                blks = page_blocks[pi]
            else:
                try:
                    page = doc[pi]
                    blks = []
                    for b in page.get_text("dict")["blocks"]:
                        if b["type"] != 0:
                            continue
                        for line in b["lines"]:
                            for span in line["spans"]:
                                txt = span["text"].strip()
                                if txt:
                                    origin = span.get("origin", (span["bbox"][0], span["bbox"][3]))
                                    blks.append((
                                        span["bbox"][0], span["bbox"][1],
                                        span["bbox"][2], span["bbox"][3],
                                        txt, span["size"], span["font"],
                                        origin[0], origin[1]
                                    ))
                    page_blocks[pi] = blks
                except Exception as e:
                    messagebox.showerror(_t("Hata"), str(e))
                    return
            blocks_data.clear()
            for b in blks:
                blocks_data.append(b)
                block_list.insert(tk.END, b[4][:60])
        def _prev():
            if page_var.get() > 1:
                page_var.set(page_var.get() - 1)
                _load_page()
        def _next():
            if page_var.get() < len(doc):
                page_var.set(page_var.get() + 1)
                _load_page()
        tk.Button(top, text="\u25c0", font=("Segoe UI", 10, "bold"),
                  bg="#34495e", fg="white", relief="flat", bd=0,
                  cursor="hand2", command=_prev).pack(side=tk.LEFT, padx=4)
        tk.Label(top, textvariable=page_var, bg="#2c3e50", fg="white",
                 font=("Segoe UI", 10, "bold"), width=4).pack(side=tk.LEFT)
        tk.Button(top, text="\u25b6", font=("Segoe UI", 10, "bold"),
                  bg="#34495e", fg="white", relief="flat", bd=0,
                  cursor="hand2", command=_next).pack(side=tk.LEFT, padx=4)
        tk.Label(top, text=f"/ {len(doc)}", bg="#2c3e50", fg="#bbb",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=2)
        fs_btn = tk.Button(top, text="\u25a2 Tam Ekran", font=("Segoe UI", 9),
                           bg="#34495e", fg="#bbb", relief="flat", bd=0,
                           cursor="hand2", command=_toggle_fullscreen)
        fs_btn.pack(side=tk.RIGHT, padx=8)
        body = tk.Frame(dlg, bg="#ecf0f1")
        body.pack(fill=tk.BOTH, expand=True)
        left_frame = tk.Frame(body, bg="#2c3e50", width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)
        tk.Label(left_frame, text="Metin Bloklar\u0131", bg="#2c3e50", fg="#bbb",
                 font=("Segoe UI", 8)).pack(pady=(6, 2))
        block_list = tk.Listbox(left_frame, bg="#34495e", fg="white",
                                selectbackground="#27ae60", font=("Segoe UI", 9),
                                bd=0, highlightthickness=0, exportselection=0)
        block_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        right_frame = tk.Frame(body, bg="#ecf0f1")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(right_frame, text="Metin \u0130\xe7eri\u011fi", bg="#ecf0f1", fg="#555",
                 font=("Segoe UI", 9, "bold")).pack(pady=(8, 4))
        edit_text = tk.Text(right_frame, bg="white", fg="#333",
                            font=("Segoe UI", 10), wrap=tk.WORD, bd=1,
                            relief="solid", padx=6, pady=6)
        edit_text.pack(fill=tk.BOTH, expand=True, padx=8)
        bottom = tk.Frame(dlg, bg="#f8f9fa", height=44)
        bottom.pack(fill=tk.X)
        bottom.pack_propagate(False)
        blocks_data = []
        def _on_select(event):
            sel = block_list.curselection()
            if not sel:
                return
            idx = sel[0]
            if idx < len(blocks_data):
                edit_text.delete("1.0", tk.END)
                edit_text.insert("1.0", blocks_data[idx][4])
        block_list.bind("<<ListboxSelect>>", _on_select)
        def _apply():
            sel = block_list.curselection()
            if not sel:
                return
            idx = sel[0]
            if idx >= len(blocks_data):
                return
            b = blocks_data[idx]
            new_text = edit_text.get("1.0", tk.END).strip()
            if not new_text:
                return
            try:
                pi = page_var.get() - 1
                page = doc[pi]
                rect = fitz.Rect(b[0], b[1], b[2], b[3])
                page.add_redact_annot(rect, fill=(1, 1, 1))
                page.apply_redactions()
                fontsize = b[5] if b[5] > 0 else 11
                fontname = b[6] if len(b) > 6 else "helv"
                origin_y = b[8] if len(b) > 8 else b[1] + fontsize
                std_fonts = {"helv", "hebo", "heit", "nimb", "nimbus",
                             "times", "tibo", "tibt", "cour", "cobo", "cobt"}
                font_lower = fontname.lower().replace(" ", "")
                font_lower = font_lower.replace("-", "")
                if any(s in font_lower for s in std_fonts):
                    page.insert_text((b[0], origin_y), new_text,
                                    fontsize=fontsize, color=(0, 0, 0),
                                    fontname=fontname)
                else:
                    arial = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "arial.ttf")
                    if os.path.exists(arial):
                        page.insert_text((b[0], origin_y), new_text,
                                        fontsize=fontsize, color=(0, 0, 0),
                                        fontfile=arial, fontname="/ArialMT")
                    else:
                        page.insert_text((b[0], origin_y), new_text,
                                        fontsize=fontsize, color=(0, 0, 0))
                new_block = (b[0], b[1], b[2], b[3], new_text, b[5], b[6], b[7], b[8])
                blocks_data[idx] = new_block
                page_blocks[pi] = list(blocks_data)
                block_list.delete(idx)
                block_list.insert(idx, new_text[:60])
                block_list.selection_set(idx)
                self._set_status(_t("Sayfa {n} - blok {idx} güncellendi").replace("{n}", str(page_var.get())).replace("{idx}", str(idx)))
            except Exception as e:
                messagebox.showerror(_t("Hata"), f"Uygulanamad\u0131: {e}")
        def _save_pdf():
            out = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialdir=RESIMLER_DIR)
            if not out:
                return
            try:
                doc.save(out)
                res = messagebox.askyesno("Bitti", f"PDF kaydedildi:\n{out}\n\nA\xe7mak ister misiniz?")
                if res:
                    os.startfile(out)
            except Exception as e:
                messagebox.showerror(_t("Hata"), f"Kaydedilemedi: {e}")
        _mkbtn(bottom, "Uygula", _apply, bg="#27ae60", width=10).pack(
            side=tk.LEFT, padx=6, pady=6)
        _mkbtn(bottom, "PDF Kaydet", _save_pdf, bg="#2980b9", width=12).pack(
            side=tk.LEFT, padx=4, pady=6)
        _mkbtn(bottom, "Kapat", dlg.destroy, bg="#e74c3c", width=10).pack(
            side=tk.RIGHT, padx=6, pady=6)
        _load_page()

    def open_editor(self, path):

        def _on_save(p):
            self._refresh_thumb(p)

        CropEditor(self.root, path, on_save=_on_save)

    def _refresh_thumb(self, path):
        self._show_thumbs()

    def show_about(self):
        messagebox.showinfo(
            _t("Hakk\u0131nda"),
            _t("PDF_Create_Export_Edit\n\n"
               "Yaz\u0131l\u0131m: Asri Akdeniz\n"
               "Mail: asriakdeniz@gmail.com")
        )

    def show_help(self):
        title = _t("Yard\u0131m") if _current_lang == "tr" else "Help"
        if _current_lang == "tr":
            text = """\
PDF_Create_Export_Edit - Kullan\u0131m K\u0131lavuzu

========================================
1. PDF \u0130\u015flemleri
========================================

PDF Y\u00fckle:
  Bir PDF dosyas\u0131n\u0131 a\u00e7ar ve t\u00fcm sayfalar\u0131n\u0131 resim
  olarak g\u00f6sterir. Resimler resimler/ klas\u00f6r\u00fcne kaydedilir.

PDF Metin D\u00fczenle:
  Bir PDF'nin metin bloklar\u0131n\u0131 g\u00f6r\u00fcnt\u00fcler, d\u00fczenlemenize
  ve yeni PDF olarak kaydetmenize olanak tan\u0131r.

Sa\u011f Tu\u015fa Ekle:
  Windows sa\u011f t\u0131k men\u00fcs\u00fcne PDF Create Export Edit k\u0131sayollar\u0131n\u0131 ekler.
  PDF ve resim dosyalar\u0131na sa\u011f t\u0131klayarak h\u0131zl\u0131 eri\u015fim.

Sa\u011f Tu\u015ftan Kald\u0131r:
  PDF Create Export Edit sa\u011f t\u0131k men\u00fcs\u00fcn\u00fc kald\u0131r\u0131r.

========================================
2. Resim \u0130\u015flemleri
========================================

Resim Y\u00fckle:
  PNG, JPG, BMP, TIFF, GIF, WEBP dosyalar\u0131n\u0131 listeye ekler.

Resmi D\u00fczenle:
  Se\u00e7ili resmi CropEditor ile d\u00fczenler.
  Ara\u00e7lar: Kes, F\u0131r\u00e7a, Boya/Sil, Alan Se\u00e7, Metin,
  \u00c7izgi, Tek Ok, \u00c7ift Ok, K\u0131rp

Se\u00e7ilenleri PDF Yap:
  Se\u00e7ili resimlerden tek bir PDF olu\u015fturur.

Se\u00e7ileni Kaydet:
  Se\u00e7ili resim(ler)i farkl\u0131 formatta kaydeder.

========================================
3. CropEditor Ara\u00e7lar\u0131
========================================

Kes:      Fare ile alan\u0131 renklendirir/boyar.
F\u0131r\u00e7a: Serbest \u00e7izim yapar.
Boya/Sil: Belirtilen renkle boyar veya siler.
Alan Se\u00e7: Kare/dikd\u00f6rtgen se\u00e7im yapar.
Metin:    T\u0131klanan yere metin ekler.
\u00c7izgi:    \u00c7izgi \u00e7izer.
Tek Ok:   Tek y\u00f6nl\u00fc ok \u00e7izer.
\u00c7ift Ok: \u00c7ift y\u00f6nl\u00fc ok \u00e7izer.
K\u0131rp:     Alan se\u00e7ip g\u00f6r\u00fcnt\u00fcy\u00fc k\u0131rpar.

Se\u00e7im Sonras\u0131 \u0130\u015flemler:
- Kes: Se\u00e7ili alan\u0131 beyaz yapar
- Boya: Se\u00e7ili alan\u0131 renklendirir
- Kopyala: Se\u00e7imi kopyalar, Uygula ile yap\u0131\u015ft\u0131r\u0131n
- Ta\u015f\u0131: Se\u00e7imi ta\u015f\u0131r, Uygula ile yerle\u015ftirin
- D\u00f6nd\u00fcr: Se\u00e7imi a\u00e7\u0131l\u0131 d\u00f6nd\u00fcr\u00fcr
- Yans\u0131: Yatay/Dikey yans\u0131tma

K\u00f6\u015fe Tutama\u00e7lar\u0131:
- Beyaz kareler: S\u00fcr\u00fckleyerek d\u00f6nd\u00fcrme
- Turuncu kareler: Oransal \u00f6l\u00e7ekleme
- K\u0131rm\u0131z\u0131 kareler: Serbest yeniden boyutland\u0131rma

Alt \u00c7ubuk:
- Uygula: Ta\u015f\u0131ma/kopyalamay\u0131 tamamlar
- Geri Al: Son i\u015flemi geri al\u0131r
- Kaydet: Dosyan\u0131n \u00fczerine kaydeder
- Farkl\u0131 Kaydet: Yeni format/konumda kaydeder

========================================
4. PDF Metin D\u00fczenleyici
========================================
- Sol panelde metin bloklar\u0131n\u0131 g\u00f6r\u00fcn
- Bir blo\u011fa t\u0131klay\u0131n, i\u00e7eri\u011fi sa\u011f panelde d\u00fczenleyin
- Uygula: De\u011fi\u015fikli\u011fi ge\u00e7ici olarak uygular
- PDF Kaydet: De\u011fi\u015fikliklerle yeni PDF olu\u015fturur
- Tam Ekran: D\u00fczenleyiciyi b\u00fcy\u00fct\u00fcr
- \u25c0 \u25b6: Sayfalar aras\u0131 gezinti

========================================
5. Dil Se\u00e7imi
========================================
- EN butonu: T\u00fcrk\u00e7e'den \u0130ngilizce'ye ge\u00e7er
- TR butonu: \u0130ngilizce'den T\u00fcrk\u00e7e'ye ge\u00e7er
- Dil se\u00e7imi kaydedilir, program yeniden ba\u015flat\u0131l\u0131r

========================================
6. Komut Sat\u0131r\u0131 Kullan\u0131m\u0131
========================================
--extract-pdf <dosya.pdf>
  PDF'deki t\u00fcm sayfalar\u0131 resim olarak \u00e7\u0131kar\u0131r.

--edit-pdf <dosya.pdf>
  PDF metin d\u00fczenleyiciyi a\u00e7ar.

--edit-image <resim.png>
  CropEditor ile resmi d\u00fczenler.

--make-pdf <resim.png>
  Tek resmi PDF'e \u00e7evirir.

--combine-pdf <resim1.png> <resim2.png> ...
  Birden \u00e7ok resmi tek PDF'te birle\u015ftirir.

--edit-multi <resim1.png> <resim2.png> ...
  Resimleri CropEditor ile a\u00e7ar (se\u00e7imli).

--extract-pdf-gui <dosya.pdf>
  PDF resimlerini \u00e7\u0131kar\u0131p CropEditor ile a\u00e7ar.

========================================
7. S\u0131ralama
========================================
- \u2191 Yukar\u0131 / \u2193 A\u015fa\u011f\u0131: Se\u00e7ili g\u00f6rseli ta\u015f\u0131r
- S\u00fcr\u00fckle-b\u0131rak: G\u00f6rselleri fareyle s\u00fcr\u00fckleyerek s\u0131ralay\u0131n

========================================
8. Hakk\u0131nda
========================================
PDF_Create_Export_Edit
Yaz\u0131l\u0131m: Asri Akdeniz
Mail: asriakdeniz@gmail.com"""
        else:
            text = """\
PDF_Create_Export_Edit - User Guide

========================================
1. PDF Operations
========================================

Load PDF:
  Opens a PDF file and displays all pages as images.
  Images are saved to the resimler/ folder.

Edit PDF Text:
  View and edit text blocks of a PDF, save as a new PDF.

Add to Right-Click:
  Adds PDF Create Export Edit shortcuts to the Windows context menu.
  Quick access by right-clicking PDF and image files.

Remove from Right-Click:
  Removes PDF Create Export Edit from the right-click menu.

========================================
2. Image Operations
========================================

Load Image(s):
  Add PNG, JPG, BMP, TIFF, GIF, WEBP files to the list.

Edit Image:
  Opens the selected image in the CropEditor.
  Tools: Cut, Brush, Paint/Erase, Select Area, Text,
  Line, Single Arrow, Double Arrow, Crop

Make PDF from Selected:
  Creates a single PDF from selected images.

Save Selected:
  Saves selected image(s) in a different format.

========================================
3. CropEditor Tools
========================================

Cut:      Drag to color/fill an area.
Brush:    Freehand drawing.
Paint/Erase: Paint with selected color or erase.
Select Area: Make rectangular selection.
Text:     Click to add text.
Line:     Draw a line.
Single Arrow: Draw a single-headed arrow.
Double Arrow: Draw a double-headed arrow.
Crop:     Select area and crop the image.

Selection Actions:
- Cut: Makes selected area white
- Fill: Colors the selected area
- Copy: Copies selection, paste with Apply
- Move: Moves selection, place with Apply
- Rotate: Rotates selection by any angle
- Flip: Horizontal/Vertical flip

Corner Handles:
- White squares: Drag to rotate
- Orange squares: Proportional scale
- Red squares: Free resize

Bottom Bar:
- Apply: Confirm move/copy action
- Undo: Revert the last action
- Save: Overwrite the file
- Save As: Save in new format/location

========================================
4. PDF Text Editor
========================================
- View text blocks in the left panel
- Click a block, edit content in the right panel
- Apply: Temporarily apply the change
- Save PDF: Create a new PDF with changes
- Fullscreen: Enlarge the editor view
- \u25c0 \u25b6: Navigate between pages

========================================
5. Language Selection
========================================
- EN button: Switch from Turkish to English
- TR button: Switch from English to Turkish
- Language preference is saved, program restarts

========================================
6. Command Line Usage
========================================
--extract-pdf <file.pdf>
  Extracts all PDF pages as images.

--edit-pdf <file.pdf>
  Opens the PDF text editor.

--edit-image <image.png>
  Edits the image in CropEditor.

--make-pdf <image.png>
  Converts a single image to PDF.

--combine-pdf <img1.png> <img2.png> ...
  Combines multiple images into one PDF.

--edit-multi <img1.png> <img2.png> ...
  Opens images in CropEditor (selective).

--extract-pdf-gui <file.pdf>
  Extracts PDF images and opens in CropEditor.

========================================
7. Ordering
========================================
- \u2191 Move Up / \u2193 Move Down: Move selected image
- Drag-and-drop: Reorder images by dragging

========================================
8. About
========================================
PDF_Create_Export_Edit
Software: Asri Akdeniz
Mail: asriakdeniz@gmail.com"""

        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("700x600")
        win.minsize(500, 400)

        frame = tk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 10),
                              bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        text_widget.insert("1.0", text)
        text_widget.config(state=tk.DISABLED)

        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(win, bg="#f8f9fa")
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Button(btn_frame, text=_t("Kapat"), command=win.destroy,
                  bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2", width=12).pack(pady=4)

    def crop_selected(self):
        selected = [p for p, v in self.selection.items() if v.get()]
        if not selected:
            messagebox.showwarning(_t("Uyarı"), _t("Önce resim seçin"))
            return

        def _on_save(p):
            self._refresh_thumb(p)

        for p in selected:
            CropEditor(self.root, p, on_save=_on_save)

    def make_pdf(self):
        selected = [p for p, v in self.selection.items() if v.get()]
        if not selected:
            messagebox.showwarning(_t("Uyarı"), _t("Önce resim seçin"))
            return

        self._set_status(_t("PDF oluşturuluyor..."))
        self.root.update()

        try:
            images = [Image.open(p).convert("RGB") for p in selected]
            first_dir = os.path.dirname(selected[0])
            base = os.path.splitext(os.path.basename(selected[0]))[0]
            pdf_path = os.path.join(first_dir, f"{base}.pdf")
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            if len(images) == 1:
                images[0].save(pdf_path, "PDF")
            else:
                images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])
            self.root.title(f"PDF_Create_Export_Edit - {os.path.basename(pdf_path)}")
            self._set_status(_t("PDF kaydedildi: {path}").replace("{path}", pdf_path))
            messagebox.showinfo(_t("Bitti"), f"PDF kaydedildi:\n{pdf_path}")
        except Exception as e:
            self._set_status(_t("Hata: {e}").replace("{e}", str(e)))
            messagebox.showerror(_t("Hata"), f"PDF olu\u015fturulamad\u0131:\n{e}")

    def save_selected(self):
        selected = [p for p, v in self.selection.items() if v.get()]
        if not selected:
            messagebox.showwarning(_t("Uyarı"), _t("Önce resim seçin"))
            return
        out = filedialog.askdirectory(title="Kay\u0131t klas\xf6r\xfc", initialdir=APP_DIR)
        if not out:
            return
        for p in selected:
            img = Image.open(p)
            name = os.path.basename(p)
            img.save(os.path.join(out, name))
        self._set_status(_t("{n} resim kaydedildi").replace("{n}", str(len(selected))))
        messagebox.showinfo(_t("Bitti"), f"{len(selected)} resim kaydedildi.")

    def select_all(self):
        for v in self.selection.values():
            v.set(True)

    def deselect_all(self):
        for v in self.selection.values():
            v.set(False)

    def move_up(self):
        self._move_selection(-1)

    def move_down(self):
        self._move_selection(1)

    def _move_selection(self, direction):
        selected = [(i, p) for i, p in enumerate(self.images) if self.selection[p].get()]
        if not selected:
            messagebox.showwarning(_t("Uyarı"), _t("Önce resim seçin"))
            return
        n = len(self.images)
        new_order = list(self.images)
        if direction == -1:
            selected.sort(key=lambda x: x[0])
            for i, p in selected:
                if i == 0:
                    continue
                new_order[i], new_order[i - 1] = new_order[i - 1], new_order[i]
        else:
            selected.sort(key=lambda x: x[0], reverse=True)
            for i, p in selected:
                if i == n - 1:
                    continue
                new_order[i], new_order[i + 1] = new_order[i + 1], new_order[i]
        self.images = new_order
        self._show_thumbs()
        self._set_status(_t("Sıralama güncellendi"))

    # ───── Context menu (Windows sag tus - PDF Create Export Edit) ─────
    def add_context_menu(self):
        import winreg
        if getattr(sys, "frozen", False):
            exe = sys.executable
            icon = exe
            script = None
        else:
            exe = sys.executable
            script = os.path.abspath(__file__)
            icon = ""

        def _cmd(flag):
            if getattr(sys, "frozen", False):
                return f'"{exe}" {flag} "%1"'
            else:
                return f'"{exe}" "{script}" {flag} "%1"'

        _img_exts = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"]

        def _add_entries(base, ctx_key, items):
            """Create parent verb with ExtendedSubCommandsKey + sub-items under ctx_key."""
            # Parent verb
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, base)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "PDF Create Export Edit")
            winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "PDF Create Export Edit")
            full_ctx = "SystemFileAssociations" + ctx_key
            winreg.SetValueEx(key, "ExtendedSubCommandsKey", 0, winreg.REG_SZ, full_ctx)
            if icon:
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
            winreg.CloseKey(key)
            # Sub-items under context key
            for name, flag, label in items:
                sub = ctx_key + rf"\shell\{name}"
                k = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                    "Software\\Classes\\SystemFileAssociations" + sub)
                winreg.SetValueEx(k, "MUIVerb", 0, winreg.REG_SZ, label)
                winreg.CloseKey(k)
                k = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                    "Software\\Classes\\SystemFileAssociations" + sub + r"\command")
                winreg.SetValueEx(k, "", 0, winreg.REG_SZ, _cmd(flag))
                winreg.CloseKey(k)

        try:
            _add_entries(
                r"Software\Classes\SystemFileAssociations\.pdf\shell\ASRITools",
                r"\.pdf\ASRIToolsContext",
                [("01PDFResimCikar", "--extract-pdf", _t("PDF Resim \u00c7\u0131kar")),
                 ("02PDFMetinDuzenle", "--edit-pdf", _t("PDF Metin D\u00fczenle")),
                 ("03PDFResimCikarSecimli", "--extract-pdf-gui", _t("PDF Resim \u00c7\u0131kar (Se\u00e7imli)"))]
            )
        except Exception as e:
            messagebox.showerror(_t("Hata"), _t("PDF kayd\u0131 eklenemedi: {e}").replace("{e}", str(e)))
            return

        for ext in _img_exts:
            try:
                _add_entries(
                    f"Software\\Classes\\SystemFileAssociations\\{ext}\\shell\\ASRITools",
                    f"\\{ext}\\ASRIToolsContext",
                    [("01ResimDuzenle", "--edit-image", _t("Resim D\u00fczenle")),
                     ("02TekPDF", "--combine-pdf", _t("PDF yap")),
                     ("03TekTekPDF", "--make-pdf", _t("Tek Tek PDF yap")),
                     ("04SecimliPDF", "--edit-multi", _t("Se\u00e7imli PDF yap"))]
                )
            except Exception as e:
                messagebox.showerror(_t("Hata"), _t("{ext} kayd\u0131 eklenemedi: {e}").replace("{ext}", ext).replace("{e}", str(e)))
                return

        messagebox.showinfo(
            _t("Bitti"),
            _t("PDF Create Export Edit sa\u011f t\u0131k men\u00fcs\u00fcne eklendi.\n"
               "PDF ve resim dosyalar\u0131nda PDF Create Export Edit alt\u0131nda kullanabilirsiniz.")
        )

    def remove_context_menu(self):
        import winreg
        def _del(path):
            try:
                k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                i = 0
                while True:
                    try:
                        sub = winreg.EnumKey(k, 0)
                        _del(path + "\\" + sub)
                    except WindowsError:
                        break
                winreg.CloseKey(k)
            except Exception:
                pass
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
            except Exception:
                pass
        base = r"Software\Classes\SystemFileAssociations"
        targets = [[".pdf", "ASRITools"], [".pdf", "ASRIToolsContext"]]
        for ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"]:
            targets.append([ext, "ASRITools"])
            targets.append([ext, "ASRIToolsContext"])
            targets.append([ext, "ASRI_Combine_PDF"])
        for ext, key in targets:
            _del(f"{base}\\{ext}\\shell\\{key}")
            _del(f"{base}\\{ext}\\{key}")
        messagebox.showinfo(_t("Bitti"), _t("PDF Create Export Edit sağ tık menüsünden kaldırıldı."))

    def _extract_pdf(self, path):
        self._set_status(_t("PDF resimleri çıkarılıyor..."))
        self.root.update()
        try:
            os.makedirs(RESIMLER_DIR, exist_ok=True)
            doc = fitz.open(path)
            base = os.path.splitext(os.path.basename(path))[0]
            paths = []
            for i in range(len(doc)):
                page = doc[i]
                pix = None
                for zoom in [2, 1, 0.5, 0.25]:
                    try:
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        break
                    except Exception:
                        continue
                if pix is None:
                    raise RuntimeError("Sayfa cok buyuk, render edilemiyor")
                img_path = os.path.join(RESIMLER_DIR, f"{base}_{i + 1}.png")
                pix.save(img_path)
                pix = None
                paths.append(img_path)
            doc.close()
            paths.sort(key=lambda x: int(x.rsplit("_", 1)[1].rsplit(".", 1)[0]))
            self.load_images(paths)
        except Exception as e:
            self._set_status(_t("Hata: {e}").replace("{e}", str(e)))
            messagebox.showerror(_t("Hata"), f"PDF resimleri cikarilamadi:\n{e}")

    def _make_pdf_from_image(self, path):
        base = os.path.splitext(os.path.basename(path))[0]
        pdf_path = os.path.join(RESIMLER_DIR, f"{base}.pdf")
        os.makedirs(RESIMLER_DIR, exist_ok=True)
        img = Image.open(path).convert("RGB")
        img.save(pdf_path, "PDF")
        messagebox.showinfo(_t("Bitti"), f"PDF olusturuldu:\n{pdf_path}")

    def _handle_command_line(self, file_arg, mode=None, extra_files=None):
        if extra_files is None:
            extra_files = []
        if not file_arg or not os.path.exists(file_arg):
            return
        try:
            ext = os.path.splitext(file_arg)[1].lower()
            _img_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"}
            if mode == "extract-pdf" or (mode is None and ext == ".pdf"):
                self._extract_pdf(file_arg)
            elif mode == "edit-pdf":
                self.edit_pdf_text(file_arg)
            elif mode == "edit-image":
                self.load_images([file_arg])
                self.selection[file_arg].set(True)
                self.open_editor(file_arg)
            elif mode == "make-pdf":
                self._make_pdf_from_image(file_arg)
            elif mode == "combine-pdf":
                self._make_pdf_from_image(file_arg)
            elif mode == "extract-pdf-gui":
                self._extract_pdf(file_arg)
            elif mode == "edit-multi":
                all_files = [file_arg] + [f for f in extra_files if os.path.isfile(f)]
                if all_files:
                    self.load_images(all_files)
            elif ext == ".pdf":
                self.edit_pdf_text(file_arg)
            elif ext in _img_exts:
                self.load_images([file_arg])
                self.selection[file_arg].set(True)
                self.open_editor(file_arg)
            else:
                messagebox.showwarning(_t("Uyarı"), f"Desteklenmeyen dosya: {ext}")
        except Exception as e:
            messagebox.showerror(_t("Hata"), str(e))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    mode = None
    file_arg = None
    args = sys.argv[1:]
    if args and args[0].startswith("--"):
        mode = args[0][2:]
        file_arg = args[1] if len(args) > 1 else None
    elif args:
        file_arg = args[0]

    img_exts = {'.png','.jpg','.jpeg','.bmp','.tiff','.tif','.gif','.webp'}

    import tempfile, time

    def _collect_multi(file_path, tag):
        """Collect multi-file invocations via temp file + lock.
        Returns (is_primary, collected_list)."""
        lst = os.path.join(tempfile.gettempdir(), f"asri_{tag}_list.txt")
        lck = os.path.join(tempfile.gettempdir(), f"asri_{tag}_lock.txt")
        don = os.path.join(tempfile.gettempdir(), f"asri_{tag}_done.txt")
        # Clean stale files from crashed sessions (>10s old)
        _now = time.time()
        for _f in [lst, lck, don]:
            try:
                if os.path.getmtime(_f) < _now - 10:
                    os.remove(_f)
            except:
                pass
        if os.path.exists(don):
            return False, []
        # Write file path FIRST, then try lock
        try:
            with open(lst, "a", encoding="utf-8") as f:
                f.write(file_path + "\n")
        except:
            return False, []
        acquired = False
        for _ in range(100):
            if os.path.exists(don):
                return False, []
            try:
                fd = os.open(lck, os.O_CREAT | os.O_EXCL)
                os.close(fd)
                acquired = True
                break
            except FileExistsError:
                time.sleep(0.05)
        if acquired:
            time.sleep(0.5)
            if os.path.exists(don):
                try: os.remove(lst); os.remove(lck)
                except: pass
                return False, []
            with open(lst, "r", encoding="utf-8") as f:
                files = [line.strip() for line in f if line.strip()]
            if len(files) > 1:
                time.sleep(0.5)
                if os.path.exists(don):
                    try: os.remove(lst); os.remove(lck)
                    except: pass
                    return False, []
                with open(lst, "r", encoding="utf-8") as f:
                    files = [line.strip() for line in f if line.strip()]
            try:
                os.remove(lst)
                os.remove(lck)
                with open(don, "w") as f:
                    f.write("1")
            except:
                pass
            return True, files
        return False, []

    # Headless combine-pdf: combine all selected images into one PDF
    if mode == "combine-pdf" and file_arg and os.path.exists(file_arg):
        try:
            primary, files = _collect_multi(file_arg, "combine")
            if primary:
                files = [f for f in files if os.path.isfile(f) and os.path.splitext(f)[1].lower() in img_exts]
                files = list(dict.fromkeys(files))
                files.sort()
                if files:
                    first = files[0]
                    base = os.path.splitext(os.path.basename(first))[0]
                    pdf_path = os.path.join(os.path.dirname(first), f"{base}.pdf")
                    images = [Image.open(f).convert("RGB") for f in files]
                    images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:])
            sys.exit(0)
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(_t("Hata"), str(e))
            root.destroy()
            sys.exit(0)

    # Headless make-pdf: individual PDF per image
    if mode == "make-pdf" and file_arg and os.path.exists(file_arg):
        try:
            files = [os.path.abspath(f) for f in args[2:] if os.path.isfile(f)]
            files.insert(0, os.path.abspath(file_arg))
            files = list(dict.fromkeys(files))
            files = [f for f in files if os.path.splitext(f)[1].lower() in img_exts]
            for f in files:
                base = os.path.splitext(os.path.basename(f))[0]
                pdf_path = os.path.join(os.path.dirname(f), f"{base}.pdf")
                img = Image.open(f).convert("RGB")
                img.save(pdf_path, "PDF")
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(_t("Hata"), str(e))
            root.destroy()
        sys.exit(0)

    if mode == "extract-pdf" and file_arg and os.path.exists(file_arg):
        try:
            doc = fitz.open(file_arg)
            base = os.path.splitext(os.path.basename(file_arg))[0]
            pdf_dir = os.path.dirname(os.path.abspath(file_arg))
            out_dir = os.path.join(pdf_dir, f"{base}_resimler")
            os.makedirs(out_dir, exist_ok=True)
            for i in range(len(doc)):
                pix = doc[i].get_pixmap(matrix=fitz.Matrix(4, 4))
                pix.save(os.path.join(out_dir, f"{base}_{i + 1}.png"))
            doc.close()
        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(_t("Hata"), str(e))
            root.destroy()
        sys.exit(0)

    # edit-multi: collect all files via temp, then open App with them
    multi_files = None
    if mode == "edit-multi" and file_arg and os.path.exists(file_arg):
        try:
            primary, collected = _collect_multi(file_arg, "editmulti")
            if not primary:
                sys.exit(0)
            multi_files = [f for f in collected if os.path.isfile(f) and os.path.splitext(f)[1].lower() in img_exts]
            multi_files = list(dict.fromkeys(multi_files))
            multi_files.sort()
        except Exception:
            pass

    # extract-pdf-gui: just open App and let _handle_command_line load the PDF
    # (no headless handler, falls through)

    app = App()
    if multi_files:
        app.root.after(300, lambda: app._handle_command_line(multi_files[0], "edit-multi", multi_files[1:]))
    elif file_arg:
        extra_files = args[2:] if mode and len(args) > 2 else []
        app.root.after(300, lambda: app._handle_command_line(file_arg, mode, extra_files))
    app.run()
