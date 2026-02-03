import json
import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox
import requests

# Variables globals per indicar l'existència de LIVE i HOTFIX
hi_ha_live = False
hi_ha_hotfix = False
directori_de_treball = ""
CONFIG_FILE = "configuracio.json"

def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            dades = json.load(file)
        if isinstance(dades, dict):
            return dades
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {}

def desar_config(dades):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(dades, file)
    except OSError:
        pass

def carregar_preferencia_tema():
    dades = carregar_config()
    return dades.get("theme", "light")

def desar_preferencia_tema(theme):
    dades = carregar_config()
    dades["theme"] = theme
    desar_config(dades)

def instal·lar_traduccio(directori):
    # Crear el fitxer user.cfg
    cfg_path = os.path.join(directori, "user.cfg")
    with open(cfg_path, 'w', encoding='utf-8') as cfg_file:
        cfg_file.write("g_language = spanish_(spain)")

    # Crear l'estructura de directoris
    directori_traduccio = os.path.join(directori, "data", "Localization", "spanish_(spain)")
    os.makedirs(directori_traduccio, exist_ok=True)

    # Descarregar i guardar global.ini amb UTF-8 BOM
    url = "http://www.paraules.net/SC/global.ini"
    try:
        response = requests.get(url)
        response.raise_for_status()

        global_ini_path = os.path.join(directori_traduccio, "global.ini")
        with open(global_ini_path, 'wb') as global_ini_file:
            global_ini_file.write(response.content)  # Escriu el contingut en mode binari

    except requests.RequestException as e:
        messagebox.showerror("Error", f"No s'ha pogut descarregar el fitxer global.ini: {e}")


def llegir_directori_desat():
    dades = carregar_config()
    directori = dades.get("directori_base")
    if directori:
        return directori
    try:
        with open("directori.txt", "r") as file:
            directori = file.read().strip()
        if directori:
            dades["directori_base"] = directori
            desar_config(dades)
        return directori
    except FileNotFoundError:
        return None

def desar_directori(directori):
    dades = carregar_config()
    dades["directori_base"] = directori
    desar_config(dades)

def obtenir_base_dir(directori):
    base_name = os.path.basename(directori)
    if base_name.upper() in ["LIVE", "HOTFIX"]:
        return os.path.dirname(directori)
    return directori

def verificar_directori():
    directori_guardat = llegir_directori_desat()
    print(f"Directori guardat: {directori_guardat}")  # Línia de depuració
    if directori_guardat and os.path.isdir(directori_guardat):
        verificar_traduccio(directori_guardat)
    else:
        comprovar_directori_defecte()


def mostrar_missatge_seleccio():
    set_base_directory("")
    render_table([])
    update_alert(
        "warning",
        "Selecciona el directori base",
        "Entra a la carpeta StarCitizen per detectar els entorns disponibles.",
        False
    )

def comprovar_directori_defecte():
    # Declarem que farem servir les globals
    global directori_de_treball
    global hi_ha_live
    global hi_ha_hotfix

    directori_base_defecte = r"C:\Program Files\Roberts Space Industries\StarCitizen"
    directori_live = os.path.join(directori_base_defecte, "LIVE")
    directori_hotfix = os.path.join(directori_base_defecte, "HOTFIX")

    # Avaluem si existeix el directori LIVE i/o HOTFIX
    hi_ha_live = os.path.isdir(directori_live)
    print(f"directori LIVE: {hi_ha_live}")  # Línia de depuració
    hi_ha_hotfix = os.path.isdir(directori_hotfix)
    print(f"directori HOTFIX: {hi_ha_hotfix}")  # Línia de depuració

    # Prioritzem LIVE si hi és, si no HOTFIX
    if hi_ha_live or hi_ha_hotfix:
        directori_de_treball = directori_base_defecte
        print("Operant sobre el directori base per defecte")  # Línia de depuració
        verificar_traduccio(directori_de_treball)
    else:
        mostrar_missatge_seleccio()

def seleccionar_directori():
    global directori_de_treball, hi_ha_live, hi_ha_hotfix
    
    directori_seleccionat = filedialog.askdirectory()

    if not directori_seleccionat:
        # Si l'usuari cancela la selecció, no fem res
        return

    base_dir = obtenir_base_dir(directori_seleccionat)
    directori_live = os.path.join(base_dir, "LIVE")
    directori_hotfix = os.path.join(base_dir, "HOTFIX")

    hi_ha_live = os.path.isdir(directori_live)
    hi_ha_hotfix = os.path.isdir(directori_hotfix)

    if not (hi_ha_live or hi_ha_hotfix):
        messagebox.showerror(
            "Directori incorrecte",
            "El directori seleccionat no conté cap entorn LIVE o HOTFIX."
        )
        return

    directori_de_treball = base_dir
    desar_directori(base_dir)
    verificar_traduccio(base_dir)

def verificar_traduccio(directori):
    """
    Comprova si existeix LIVE i/o HOTFIX partint de 'directori'.
    Verifica la traducció als directoris que realment existeixin
    i mostra un missatge final sobre si cal o no actualitzar.
    """
    global hi_ha_live, hi_ha_hotfix, directori_de_treball

    base_dir = obtenir_base_dir(directori)
    directori_de_treball = base_dir
    set_base_directory(base_dir)

    directori_live = os.path.join(base_dir, "LIVE")
    directori_hotfix = os.path.join(base_dir, "HOTFIX")

    existeix_live = os.path.isdir(directori_live)
    existeix_hotfix = os.path.isdir(directori_hotfix)

    hi_ha_live = existeix_live
    hi_ha_hotfix = existeix_hotfix

    versio_remota = "Desconeguda"
    error_remot = False
    try:
        url = "http://www.paraules.net/SC/global.ini"
        response = requests.get(url)
        response.raise_for_status()
        for linia in response.text.split('\n'):
            if "mobiGlas_ui_mobiGlasName=mobiGlas" in linia:
                versio_remota = linia.split('Glas ')[-1].strip()
                break
        if not versio_remota or versio_remota == "Desconeguda":
            error_remot = True
    except requests.RequestException:
        error_remot = True
        versio_remota = "Error"

    def check_translation_info(directori_concret):
        cfg_path = os.path.join(directori_concret, "user.cfg")
        global_ini_path = os.path.join(directori_concret, "data", "Localization", "spanish_(spain)", "global.ini")

        te_traduccio = os.path.isfile(cfg_path) and os.path.isfile(global_ini_path)

        versio_local = "Desconeguda"
        if te_traduccio:
            with open(global_ini_path, 'r', encoding='utf-8') as f:
                for linia in f:
                    if "mobiGlas_ui_mobiGlasName=mobiGlas" in linia:
                        versio_local = linia.split('Glas ')[-1].strip()
                        break
        return versio_local, te_traduccio

    rows = []
    necessiten_actualitzacio = []

    def afegir_fila(nom_env, dir_path):
        versio_local, te_traduccio = check_translation_info(dir_path)
        display_path = os.path.normpath(dir_path)

        if error_remot:
            estat = "Error"
            color = COLORS["status_err"]
            versio_remota_mostrar = "Error"
        else:
            versio_remota_mostrar = versio_remota
            if not te_traduccio:
                estat = "Sense traduïr"
                color = COLORS["status_warn"]
                versio_local = "-"
                necessiten_actualitzacio.append(nom_env)
            elif versio_local == "Desconeguda" or versio_local != versio_remota:
                estat = "Desactualitzat"
                color = COLORS["status_warn"]
                necessiten_actualitzacio.append(nom_env)
            else:
                estat = "OK"
                color = COLORS["status_ok"]

        rows.append({
            "env": nom_env,
            "path": display_path,
            "local": versio_local,
            "remote": versio_remota_mostrar,
            "status": estat,
            "color": color,
        })

    if existeix_live:
        afegir_fila("LIVE", directori_live)
    if existeix_hotfix:
        afegir_fila("HOTFIX", directori_hotfix)

    render_table(rows)

    if not (existeix_live or existeix_hotfix):
        update_alert(
            "warning",
            "No s'han detectat entorns",
            "Selecciona el directori base de Star Citizen per continuar.",
            False
        )
        return

    if error_remot:
        update_alert(
            "danger",
            "No s'ha pogut obtenir la versió remota",
            "Comprova la connexió i torna-ho a provar.",
            False
        )
        return

    if len(necessiten_actualitzacio) == 0:
        update_alert(
            "success",
            "Tot actualitzat!",
            "Tots els directoris estan actualitzats a la versió més recent.",
            False
        )
    else:
        update_alert(
            "warning",
            "Hi ha entorns pendents d'actualitzar",
            "Prem el botó per actualitzar tots els entorns existents.",
            True
        )

def actualitzar_traduccio():
    global directori_de_treball, hi_ha_live, hi_ha_hotfix

    directori_guardat = llegir_directori_desat()
    base_dir = None

    if directori_guardat and os.path.isdir(directori_guardat):
        base_dir = obtenir_base_dir(directori_guardat)
    else:
        directori_base_defecte = r"C:\Program Files\Roberts Space Industries\StarCitizen"
        if os.path.isdir(directori_base_defecte):
            base_dir = directori_base_defecte
        else:
            possibles = [
                r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE",
                r"C:\Program Files\Roberts Space Industries\StarCitizen\HOTFIX",
            ]
            for path in possibles:
                if os.path.isdir(path):
                    base_dir = os.path.dirname(path)
                    break

    if not base_dir:
        messagebox.showerror(
            "Error",
            "No s'ha trobat cap directori LIVE o HOTFIX per defecte.\n"
            "Selecciona manualment el directori."
        )
        return

    directori_de_treball = base_dir
    desar_directori(base_dir)

    directori_live = os.path.join(base_dir, "LIVE")
    directori_hotfix = os.path.join(base_dir, "HOTFIX")

    hi_ha_live = os.path.isdir(directori_live)
    hi_ha_hotfix = os.path.isdir(directori_hotfix)

    def update_global_ini(dir_path):
        cfg_path = os.path.join(dir_path, "user.cfg")
        if not os.path.isfile(cfg_path):
            with open(cfg_path, 'w', encoding='utf-8') as cfg_file:
                cfg_file.write("g_language = spanish_(spain)")

        directori_traduccio = os.path.join(dir_path, "data", "Localization", "spanish_(spain)")
        os.makedirs(directori_traduccio, exist_ok=True)
        global_ini_path = os.path.join(directori_traduccio, "global.ini")

        try:
            url = "http://www.paraules.net/SC/global.ini"
            response = requests.get(url)
            response.raise_for_status()
            with open(global_ini_path, 'wb') as f:
                f.write(response.content)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"No s'ha pogut descarregar el fitxer global.ini: {e}")

    if hi_ha_live:
        update_global_ini(directori_live)
    if hi_ha_hotfix:
        update_global_ini(directori_hotfix)

    if not (hi_ha_live or hi_ha_hotfix):
        messagebox.showerror("Error", "No s'ha trobat cap directori LIVE o HOTFIX per actualitzar.")
        return

    verificar_traduccio(base_dir)

def create_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg, border, radius=16, padding=16, border_width=1):
        super().__init__(parent, bg=COLORS["bg"], highlightthickness=0, bd=0)
        self.card_bg = bg
        self.border = border
        self.radius = radius
        self.padding = padding
        self.border_width = border_width
        self.container = tk.Frame(self, bg=self.card_bg)
        self._window = self.create_window(
            self.padding,
            self.padding,
            anchor="nw",
            window=self.container,
        )
        self.bind("<Configure>", self._redraw)
        self.container.bind("<Configure>", self._sync_height)

    def _redraw(self, event=None):
        self.delete("card")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return
        create_rounded_rect(
            self,
            self.border_width,
            self.border_width,
            width - self.border_width,
            height - self.border_width,
            self.radius,
            fill=self.card_bg,
            outline=self.border,
            width=self.border_width,
            tags="card",
        )
        self.coords(self._window, self.padding, self.padding)
        self.itemconfigure(
            self._window,
            width=width - (self.padding * 2),
        )

    def _sync_height(self, event):
        target_height = event.height + (self.padding * 2)
        if self.winfo_height() != target_height:
            self.configure(height=target_height)
        self._redraw()

    def set_colors(self, bg, border):
        self.card_bg = bg
        self.border = border
        self.container.configure(bg=bg)
        self._redraw()

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg, fg, hover_bg, font, padx=16, pady=8, radius=12):
        self._font = tkfont.Font(font=font)
        self._text = text
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._padx = padx
        self._pady = pady
        self._radius = radius
        self._command = command

        text_width = self._font.measure(text)
        text_height = self._font.metrics("linespace")
        width = text_width + (self._padx * 2)
        height = text_height + (self._pady * 2)

        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, bd=0)
        self.configure(cursor="hand2")
        self._rect = create_rounded_rect(
            self,
            0,
            0,
            width,
            height,
            self._radius,
            fill=self._bg,
            outline="",
        )
        self._label = self.create_text(
            width / 2,
            height / 2,
            text=self._text,
            fill=self._fg,
            font=font,
        )
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_click(self, _event):
        if self._command:
            self._command()

    def _on_enter(self, _event):
        self.itemconfigure(self._rect, fill=self._hover_bg)

    def _on_leave(self, _event):
        self.itemconfigure(self._rect, fill=self._bg)

    def set_colors(self, bg, fg, hover_bg):
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self.itemconfigure(self._rect, fill=self._bg)
        self.itemconfigure(self._label, fill=self._fg)
        self.configure(bg=self.master["bg"])


class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, variable, command, bg_off, bg_on, knob, border, width=52, height=28, radius=14):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, bd=0)
        self._variable = variable
        self._command = command
        self._bg_off = bg_off
        self._bg_on = bg_on
        self._knob = knob
        self._border = border
        self._width = width
        self._height = height
        self._radius = radius
        self.bind("<Button-1>", self._toggle)
        self._variable.trace_add("write", self._redraw)
        self._redraw()

    def _toggle(self, _event):
        self._variable.set(not self._variable.get())
        if self._command:
            self._command()

    def _redraw(self, *_args):
        self.delete("all")
        fill = self._bg_on if self._variable.get() else self._bg_off
        create_rounded_rect(
            self,
            1,
            1,
            self._width - 1,
            self._height - 1,
            self._radius,
            fill=fill,
            outline=self._border,
        )
        knob_size = self._height - 6
        if self._variable.get():
            knob_x = self._width - knob_size - 3
        else:
            knob_x = 3
        self.create_oval(
            knob_x,
            3,
            knob_x + knob_size,
            3 + knob_size,
            fill=self._knob,
            outline="",
        )

    def set_colors(self, bg_off, bg_on, knob, border, host_bg):
        self._bg_off = bg_off
        self._bg_on = bg_on
        self._knob = knob
        self._border = border
        self.configure(bg=host_bg)
        self._redraw()

LIGHT_COLORS = {
    "bg": "#F2F6FB",
    "card": "#FFFFFF",
    "border": "#D9E2EF",
    "text_primary": "#1F2A44",
    "text_secondary": "#5B6B82",
    "accent": "#2563EB",
    "accent_dark": "#1D4ED8",
    "field_bg": "#F8FAFF",
    "table_header": "#F7FAFF",
    "success_bg": "#ECFDF3",
    "success_border": "#A7F3D0",
    "success_text": "#166534",
    "success_icon_bg": "#D1FAE5",
    "warning_bg": "#FFF7ED",
    "warning_border": "#FDBA74",
    "warning_text": "#9A3412",
    "warning_icon_bg": "#FFEDD5",
    "danger_bg": "#FEE2E2",
    "danger_border": "#FECACA",
    "danger_text": "#991B1B",
    "danger_icon_bg": "#FEE2E2",
    "status_ok": "#16A34A",
    "status_warn": "#F97316",
    "status_err": "#DC2626",
    "button_muted_bg": "#E5E7EB",
    "button_muted_hover": "#D1D5DB",
    "button_muted_text": "#1F2937",
    "toggle_knob": "#FFFFFF",
}

DARK_COLORS = {
    "bg": "#1C1F26",
    "card": "#252A33",
    "border": "#353C47",
    "text_primary": "#E5E9F2",
    "text_secondary": "#A7B0C0",
    "accent": "#4F8BFF",
    "accent_dark": "#3A74E6",
    "field_bg": "#20252E",
    "table_header": "#2A303A",
    "success_bg": "#1F2B24",
    "success_border": "#2F4A3A",
    "success_text": "#7CE9A0",
    "success_icon_bg": "#294034",
    "warning_bg": "#2D251C",
    "warning_border": "#5A3B20",
    "warning_text": "#F5B06E",
    "warning_icon_bg": "#3B2D1E",
    "danger_bg": "#2B2020",
    "danger_border": "#5A2A2A",
    "danger_text": "#F19999",
    "danger_icon_bg": "#3A2424",
    "status_ok": "#4ADE80",
    "status_warn": "#FB923C",
    "status_err": "#F87171",
    "button_muted_bg": "#313845",
    "button_muted_hover": "#3A4352",
    "button_muted_text": "#E5E9F2",
    "toggle_knob": "#E6EAF2",
}

CURRENT_THEME = carregar_preferencia_tema()
if CURRENT_THEME not in ("light", "dark"):
    CURRENT_THEME = "light"

COLORS = DARK_COLORS if CURRENT_THEME == "dark" else LIGHT_COLORS

# Crear la finestra principal
finestra = tk.Tk()
finestra.title("Catalanitzador Star Citizen")
finestra.geometry("1080x660")
finestra.minsize(1000, 620)

FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 11)
FONT_SECTION = (FONT_FAMILY, 12, "bold")
FONT_TABLE_HEADER = (FONT_FAMILY, 9, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BODY_STRONG = (FONT_FAMILY, 10, "bold")
FONT_ALERT_TITLE = (FONT_FAMILY, 11, "bold")
FONT_CTA = (FONT_FAMILY, 11, "bold")

finestra.configure(bg=COLORS["bg"])

main = tk.Frame(finestra, bg=COLORS["bg"])
main.pack(fill="both", expand=True, padx=24, pady=24)
main.grid_columnconfigure(0, weight=1)

header_frame = tk.Frame(main, bg=COLORS["bg"])
header_frame.grid(row=0, column=0, sticky="ew")
header_frame.grid_columnconfigure(0, weight=1)

lbl_titol = tk.Label(
    header_frame,
    text="Catalanitzador Star Citizen",
    bg=COLORS["bg"],
    fg=COLORS["text_primary"],
    font=FONT_TITLE,
)
lbl_titol.grid(row=0, column=0, sticky="w")

lbl_subtitol = tk.Label(
    header_frame,
    text="Instal·la o actualitza la traducció en LIVE i HOTFIX",
    bg=COLORS["bg"],
    fg=COLORS["text_secondary"],
    font=FONT_SUBTITLE,
)
lbl_subtitol.grid(row=1, column=0, sticky="w", pady=(2, 0))

card_directori = RoundedFrame(
    main,
    bg=COLORS["card"],
    border=COLORS["border"],
    radius=16,
    padding=16,
)
card_directori.grid(row=1, column=0, sticky="ew", pady=(18, 16))
card_directori.container.grid_columnconfigure(0, weight=1)

lbl_directori = tk.Label(
    card_directori.container,
    text="Directori base",
    bg=COLORS["card"],
    fg=COLORS["text_primary"],
    font=FONT_SECTION,
)
lbl_directori.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(16, 8))

directori_base_var = tk.StringVar(value="")
directori_wrap = tk.Frame(
    card_directori.container,
    bg=COLORS["field_bg"],
    highlightthickness=1,
    highlightbackground=COLORS["border"],
)
directori_wrap.grid(row=1, column=0, sticky="ew", padx=(20, 12), pady=(0, 16))
directori_wrap.grid_columnconfigure(0, weight=1)

entrada_directori = tk.Entry(
    directori_wrap,
    textvariable=directori_base_var,
    state="readonly",
    readonlybackground=COLORS["field_bg"],
    bd=0,
    fg=COLORS["text_primary"],
    font=FONT_BODY,
    highlightthickness=0,
)
entrada_directori.grid(row=0, column=0, sticky="ew", padx=12, pady=10)

btn_seleccionar = RoundedButton(
    card_directori.container,
    text="Seleccionar directori arrel",
    command=seleccionar_directori,
    bg=COLORS["button_muted_bg"],
    fg=COLORS["button_muted_text"],
    font=FONT_BODY_STRONG,
    hover_bg=COLORS["button_muted_hover"],
    padx=18,
    pady=8,
    radius=14,
)
btn_seleccionar.grid(row=1, column=1, sticky="e", padx=(0, 20), pady=(0, 16))

card_entorns = RoundedFrame(
    main,
    bg=COLORS["card"],
    border=COLORS["border"],
    radius=16,
    padding=16,
)
card_entorns.grid(row=2, column=0, sticky="ew")
card_entorns.container.grid_columnconfigure(0, weight=1)

lbl_entorns = tk.Label(
    card_entorns.container,
    text="Entorns detectats",
    bg=COLORS["card"],
    fg=COLORS["text_primary"],
    font=FONT_SECTION,
)
lbl_entorns.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 8))

table_header = tk.Frame(card_entorns.container, bg=COLORS["table_header"])
table_header.grid(row=1, column=0, sticky="ew", padx=20)

TABLE_COL_WIDTHS = [100, 420, 120, 120, 120]
headers = ["ENTORN", "RUTA", "VERSIÓ LOCAL", "VERSIÓ REMOTA", "ESTAT"]
header_labels = []
for idx, width in enumerate(TABLE_COL_WIDTHS):
    table_header.grid_columnconfigure(idx, minsize=width)
for idx, text in enumerate(headers):
    label = tk.Label(
        table_header,
        text=text,
        bg=COLORS["table_header"],
        fg=COLORS["text_secondary"],
        font=FONT_TABLE_HEADER,
        anchor="w",
        justify="left",
    )
    label.grid(row=0, column=idx, sticky="w", padx=8, pady=10)
    header_labels.append(label)

table_body = tk.Frame(card_entorns.container, bg=COLORS["card"])
table_body.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
for idx, width in enumerate(TABLE_COL_WIDTHS):
    table_body.grid_columnconfigure(idx, minsize=width)

alert_frame = RoundedFrame(
    main,
    bg=COLORS["success_bg"],
    border=COLORS["success_border"],
    radius=16,
    padding=16,
)
alert_frame.grid(row=3, column=0, sticky="ew", pady=(16, 0))
alert_frame.container.grid_columnconfigure(1, weight=1)

alert_icon = tk.Canvas(alert_frame.container, width=28, height=28, bg=COLORS["success_bg"], highlightthickness=0)
alert_icon.grid(row=0, column=0, padx=(16, 12), pady=16)

alert_text_frame = tk.Frame(alert_frame.container, bg=COLORS["success_bg"])
alert_text_frame.grid(row=0, column=1, sticky="w", pady=16)

alert_title = tk.Label(
    alert_text_frame,
    text="",
    bg=COLORS["success_bg"],
    fg=COLORS["success_text"],
    font=FONT_ALERT_TITLE,
)
alert_title.pack(anchor="w")

alert_message = tk.Label(
    alert_text_frame,
    text="",
    bg=COLORS["success_bg"],
    fg=COLORS["text_secondary"],
    font=FONT_BODY,
    wraplength=560,
    justify="left",
)
alert_message.pack(anchor="w", pady=(4, 0))

btn_actualitzar = RoundedButton(
    alert_frame.container,
    text="Actualitzar tots els entorns",
    command=actualitzar_traduccio,
    bg=COLORS["accent"],
    fg="white",
    font=FONT_CTA,
    hover_bg=COLORS["accent_dark"],
    padx=24,
    pady=10,
    radius=16,
)
btn_actualitzar.grid(row=0, column=2, padx=(0, 16), pady=16)
btn_actualitzar.grid_remove()

theme_var = tk.BooleanVar(value=CURRENT_THEME == "dark")

footer_frame = tk.Frame(main, bg=COLORS["bg"])
footer_frame.grid(row=4, column=0, sticky="ew", pady=(16, 0))
footer_frame.grid_columnconfigure(0, weight=1)
footer_frame.grid_columnconfigure(1, weight=0)
footer_frame.grid_columnconfigure(2, weight=0)

theme_label = tk.Label(
    footer_frame,
    text="Mode fosc",
    bg=COLORS["bg"],
    fg=COLORS["text_secondary"],
    font=FONT_BODY,
)
theme_label.grid(row=0, column=1, sticky="e", padx=(0, 8))

theme_toggle = ToggleSwitch(
    footer_frame,
    variable=theme_var,
    command=lambda: alternar_tema(),
    bg_off=COLORS["button_muted_bg"],
    bg_on=COLORS["accent"],
    knob=COLORS["toggle_knob"],
    border=COLORS["border"],
)
theme_toggle.grid(row=0, column=2, sticky="e")

def build_alert_styles():
    return {
        "success": {
            "bg": COLORS["success_bg"],
            "border": COLORS["success_border"],
            "text": COLORS["success_text"],
            "subtext": COLORS["text_secondary"],
            "icon_bg": COLORS["success_icon_bg"],
            "icon_fg": COLORS["success_text"],
            "icon_text": "✓",
        },
        "warning": {
            "bg": COLORS["warning_bg"],
            "border": COLORS["warning_border"],
            "text": COLORS["warning_text"],
            "subtext": COLORS["text_secondary"],
            "icon_bg": COLORS["warning_icon_bg"],
            "icon_fg": COLORS["warning_text"],
            "icon_text": "!",
        },
        "danger": {
            "bg": COLORS["danger_bg"],
            "border": COLORS["danger_border"],
            "text": COLORS["danger_text"],
            "subtext": COLORS["text_secondary"],
            "icon_bg": COLORS["danger_icon_bg"],
            "icon_fg": COLORS["danger_text"],
            "icon_text": "!",
        },
    }

ALERT_STYLES = build_alert_styles()
LAST_ROWS = []
LAST_ALERT = None

def set_base_directory(path):
    directori_base_var.set(path)

def render_table(rows):
    global LAST_ROWS
    LAST_ROWS = [dict(row) for row in rows]
    for child in table_body.winfo_children():
        child.destroy()

    if not rows:
        empty_label = tk.Label(
            table_body,
            text="",
            bg=COLORS["card"],
            fg=COLORS["text_secondary"],
            font=FONT_BODY,
        )
        empty_label.grid(row=0, column=0, sticky="w", pady=12)
        return

    for idx, row in enumerate(rows):
        row_index = idx * 2

        env_label = tk.Label(
            table_body,
            text=row["env"],
            bg=COLORS["card"],
            fg=COLORS["text_primary"],
            font=FONT_BODY_STRONG,
            anchor="w",
            justify="left",
        )
        env_label.grid(row=row_index, column=0, sticky="w", padx=8, pady=12)

        path_label = tk.Label(
            table_body,
            text=row["path"],
            bg=COLORS["card"],
            fg=COLORS["text_primary"],
            font=FONT_BODY,
            wraplength=TABLE_COL_WIDTHS[1] - 16,
            justify="left",
            anchor="w",
        )
        path_label.grid(row=row_index, column=1, sticky="w", padx=8, pady=12)

        local_label = tk.Label(
            table_body,
            text=row["local"],
            bg=COLORS["card"],
            fg=COLORS["text_primary"],
            font=FONT_BODY,
            anchor="w",
            justify="left",
        )
        local_label.grid(row=row_index, column=2, sticky="w", padx=8, pady=12)

        remote_label = tk.Label(
            table_body,
            text=row["remote"],
            bg=COLORS["card"],
            fg=COLORS["text_primary"],
            font=FONT_BODY,
            anchor="w",
            justify="left",
        )
        remote_label.grid(row=row_index, column=3, sticky="w", padx=8, pady=12)

        status_frame = tk.Frame(table_body, bg=COLORS["card"])
        status_frame.grid(row=row_index, column=4, sticky="w", padx=8, pady=12)

        status_dot = tk.Label(
            status_frame,
            text="●",
            bg=COLORS["card"],
            fg=row["color"],
            font=FONT_BODY_STRONG,
        )
        status_dot.pack(side=tk.LEFT, padx=(0, 6))

        status_label = tk.Label(
            status_frame,
            text=row["status"],
            bg=COLORS["card"],
            fg=row["color"],
            font=FONT_BODY_STRONG,
        )
        status_label.pack(side=tk.LEFT)

        if idx < len(rows) - 1:
            separator = tk.Frame(table_body, bg=COLORS["border"], height=1)
            separator.grid(row=row_index + 1, column=0, columnspan=5, sticky="ew")

def update_alert(kind, title, message, show_button):
    global LAST_ALERT
    LAST_ALERT = {
        "kind": kind,
        "title": title,
        "message": message,
        "show_button": show_button,
    }
    style = ALERT_STYLES[kind]
    alert_frame.set_colors(style["bg"], style["border"])
    alert_icon.configure(bg=style["bg"])
    alert_text_frame.configure(bg=style["bg"])
    alert_title.configure(text=title, fg=style["text"], bg=style["bg"])
    alert_message.configure(text=message, fg=style["subtext"], bg=style["bg"])

    alert_icon.delete("all")
    alert_icon.create_oval(2, 2, 26, 26, fill=style["icon_bg"], outline="")
    alert_icon.create_text(
        14,
        14,
        text=style["icon_text"],
        fill=style["icon_fg"],
        font=(FONT_FAMILY, 12, "bold"),
    )
    btn_actualitzar.configure(bg=alert_frame.container["bg"])

    if show_button:
        btn_actualitzar.grid()
    else:
        btn_actualitzar.grid_remove()

def aplicar_tema(theme):
    global COLORS, CURRENT_THEME, ALERT_STYLES

    CURRENT_THEME = theme
    COLORS = DARK_COLORS if theme == "dark" else LIGHT_COLORS
    ALERT_STYLES = build_alert_styles()

    if theme_var.get() != (theme == "dark"):
        theme_var.set(theme == "dark")

    finestra.configure(bg=COLORS["bg"])
    main.configure(bg=COLORS["bg"])
    header_frame.configure(bg=COLORS["bg"])
    lbl_titol.configure(bg=COLORS["bg"], fg=COLORS["text_primary"])
    lbl_subtitol.configure(bg=COLORS["bg"], fg=COLORS["text_secondary"])

    card_directori.configure(bg=COLORS["bg"])
    card_directori.set_colors(COLORS["card"], COLORS["border"])
    lbl_directori.configure(bg=COLORS["card"], fg=COLORS["text_primary"])
    directori_wrap.configure(
        bg=COLORS["field_bg"],
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["border"],
    )
    entrada_directori.configure(
        bg=COLORS["field_bg"],
        readonlybackground=COLORS["field_bg"],
        fg=COLORS["text_primary"],
    )
    btn_seleccionar.set_colors(
        COLORS["button_muted_bg"],
        COLORS["button_muted_text"],
        COLORS["button_muted_hover"],
    )

    card_entorns.configure(bg=COLORS["bg"])
    card_entorns.set_colors(COLORS["card"], COLORS["border"])
    lbl_entorns.configure(bg=COLORS["card"], fg=COLORS["text_primary"])
    table_header.configure(bg=COLORS["table_header"])
    for label in header_labels:
        label.configure(bg=COLORS["table_header"], fg=COLORS["text_secondary"])
    table_body.configure(bg=COLORS["card"])

    alert_frame.configure(bg=COLORS["bg"])
    btn_actualitzar.set_colors(COLORS["accent"], "white", COLORS["accent_dark"])

    footer_frame.configure(bg=COLORS["bg"])
    theme_label.configure(bg=COLORS["bg"], fg=COLORS["text_secondary"])
    theme_toggle.set_colors(
        COLORS["button_muted_bg"],
        COLORS["accent"],
        COLORS["toggle_knob"],
        COLORS["border"],
        COLORS["bg"],
    )

    if LAST_ROWS is not None:
        render_table(LAST_ROWS)
    if LAST_ALERT:
        update_alert(
            LAST_ALERT["kind"],
            LAST_ALERT["title"],
            LAST_ALERT["message"],
            LAST_ALERT["show_button"],
        )

    desar_preferencia_tema(theme)

def alternar_tema():
    theme = "dark" if theme_var.get() else "light"
    aplicar_tema(theme)

# Iniciar la comprovació del directori
print("Iniciant la comprovació del directori...")  # Línia de depuració
verificar_directori()

# Iniciar l'interfície d'usuari
finestra.mainloop()
