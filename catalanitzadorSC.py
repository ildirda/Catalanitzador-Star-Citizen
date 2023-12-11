import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests

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
        with open(global_ini_path, 'w', encoding='utf-8-sig') as global_ini_file:
            global_ini_file.write(response.text)

        btn_instal·lar.pack_forget()
        verificar_traduccio(directori_de_treball)
    except requests.RequestException as e:
        messagebox.showerror("Error", f"No s'ha pogut descarregar el fitxer global.ini: {e}")


def llegir_directori_desat():
    try:
        with open("directori.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def desar_directori(directori):
    with open("directori.txt", "w") as file:
        file.write(directori)

def verificar_directori():
    directori_guardat = llegir_directori_desat()
    print(f"Directori guardat: {directori_guardat}")  # Línia de depuració
    if directori_guardat and os.path.isdir(directori_guardat):
        lbl_missatge.config(text=f"Treballant sobre el directori: {directori_guardat}")
        verificar_traduccio(directori_guardat)
        btn_seleccionar.pack_forget()
    else:
        comprovar_directori_defecte()


def mostrar_missatge_seleccio():
    lbl_missatge.config(text="Selecciona el directori on tens instal·lat Star Citizen. "
                             "Entra fins al directori LIVE i prem 'Selecciona carpeta'")
    btn_seleccionar.pack(side=tk.LEFT, padx=20, pady=(0, 10))

directori_de_treball = ""

def comprovar_directori_defecte():
    global directori_de_treball
    directori_defecte = r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE"
    if os.path.isdir(directori_defecte):
        directori_de_treball = directori_defecte
        lbl_missatge.config(text="Directori d'instal·lació per defecte localitzat.")
        verificar_traduccio(directori_defecte)
        btn_seleccionar.pack_forget()
    else:
        mostrar_missatge_seleccio()

def seleccionar_directori():
    global directori_de_treball
    directori_seleccionat = filedialog.askdirectory()
    if directori_seleccionat.endswith("LIVE") and os.path.isdir(directori_seleccionat):
        directori_de_treball = directori_seleccionat
        lbl_missatge.config(text=f"Directori seleccionat: {directori_seleccionat}")
        desar_directori(directori_seleccionat)
        verificar_traduccio(directori_seleccionat)
        btn_seleccionar.pack_forget()
    else:
        lbl_missatge.config(text="El directori seleccionat no és correcte. Ha de ser el directori LIVE de Star Citizen.")
        mostrar_missatge_seleccio()

def verificar_traduccio(directori):
    cfg_path = os.path.join(directori, "user.cfg")
    localization_path = os.path.join(directori, "data", "Localization", "spanish_(spain)", "global.ini")

    if not os.path.isfile(cfg_path) or not os.path.isfile(localization_path):
        lbl_missatge_traduccio.config(text="No s'ha detectat cap traducció.")
        btn_instal·lar.pack(side=tk.LEFT, padx=20, pady=(0, 10))
        btn_actualitzar.pack_forget()  # Ocultar el botó d'actualització
        return

    # A partir d'aquí, la traducció local existeix, comprovem les versions
    versio_local = "Desconeguda"
    versio_remota = "Desconeguda"

    # Comprovar la versió local
    with open(localization_path, 'r', encoding='utf-8') as file:
        for linia in file:
            if "mobiGlas_ui_mobiGlasName=mobiGlas" in linia:
                versio_local = linia.split('=')[-1].strip()
                break

    # Comprovar la versió remota
    try:
        url = "http://www.paraules.net/SC/global.ini"
        response = requests.get(url)
        response.raise_for_status()

        for linia in response.text.split('\n'):
            if "mobiGlas_ui_mobiGlasName=mobiGlas" in linia:
                versio_remota = linia.split('=')[-1].strip()
                break
    except requests.RequestException as e:
        versio_remota = "Error al comprovar la versió remota"

    # Actualitzar el missatge amb les versions
    missatge_versions = f"Versió de la traducció local: {versio_local}\nVersió de la traducció remota: {versio_remota}"
    lbl_missatge_traduccio.config(text=missatge_versions)

    # Mostrar el botó adequat segons la comparació de versions
    if versio_local == versio_remota:
        lbl_missatge_actualitzacio.config(fg="green", text="Ja tens l'última versió.")
        btn_actualitzar.pack_forget()
    else:
        lbl_missatge_actualitzacio.config(fg="red", text="Hi ha una traducció nova.")
        btn_actualitzar.pack(side=tk.LEFT, padx=20, pady=12)
        btn_instal·lar.pack_forget()  # Ocultar el botó d'instal·lació si ja hi ha una traducció



def actualitzar_traduccio():
    print(f"Actualitzant des de: {directori_de_treball}")  # Línia de depuració
    if not directori_de_treball:
        messagebox.showerror("Error", "No s'ha seleccionat cap directori.")
        return

    directori_traduccio = os.path.join(directori_de_treball, "data", "Localization", "spanish_(spain)")
    global_ini_path = os.path.join(directori_traduccio, "global.ini")

    try:
        url = "http://www.paraules.net/SC/global.ini"
        response = requests.get(url)
        response.raise_for_status()

        with open(global_ini_path, 'w', encoding='utf-8-sig') as global_ini_file:
            global_ini_file.write(response.text)

        verificar_traduccio(directori_de_treball)
    except requests.RequestException as e:
        messagebox.showerror("Error", f"No s'ha pogut descarregar el fitxer global.ini: {e}")


# Crear la finestra principal
finestra = tk.Tk()
finestra.title("Catalanitzador Star Citizen")
finestra.geometry("700x500")

# Estils
estil_text = {'font': ('Arial', 12)}

# Crear el marc per als widgets
marc_principal = tk.Frame(finestra)
marc_principal.pack(pady=20, padx=20, fill=tk.X)

# Crear els widgets
lbl_missatge = tk.Label(marc_principal, text="", **estil_text, wraplength=650, justify="left", anchor='w')
btn_seleccionar = tk.Button(marc_principal, text="Seleccionar directori LIVE", command=seleccionar_directori)
lbl_missatge_traduccio = tk.Label(marc_principal, text="", **estil_text, wraplength=650, justify="left", anchor='w')
# Canvi en la creació del botó btn_instal·lar per passar el directori_de_treball
btn_instal·lar = tk.Button(marc_principal, text="Instal·lar última versió de la traducció", command=lambda: instal·lar_traduccio(directori_de_treball))
lbl_missatge_actualitzacio = tk.Label(marc_principal, text="", **estil_text, wraplength=650, justify="left", anchor='w')
btn_actualitzar = tk.Button(marc_principal, text="Actualitzar a la última versió", command=actualitzar_traduccio)

# Organitzar els widgets dins del marc
lbl_missatge.pack(fill=tk.X, pady=12)
lbl_missatge_traduccio.pack(fill=tk.X, pady=12)
btn_seleccionar.pack(side=tk.LEFT, padx=20, pady=12)
lbl_missatge_actualitzacio.pack(fill=tk.X, pady=(12, 0))

# Iniciar la comprovació del directori
print("Iniciant la comprovació del directori...")  # Línia de depuració
verificar_directori()

# Iniciar l'interfície d'usuari
finestra.mainloop()
