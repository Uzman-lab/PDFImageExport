# -*- coding: utf-8 -*-
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS = None
from .utils import _mkbtn, _darken, ToolTip
from .translations import _t

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
        title_prefix = _t('D\xfczenle')
        self.win.title(f"{title_prefix} \u2014 {os.path.basename(image_path)}")
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


