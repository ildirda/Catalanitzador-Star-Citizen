import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests

# Variables globals per indicar l'existència de LIVE i HOTFIX
hi_ha_live = False
hi_ha_hotfix = False
directori_de_treball = ""

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
    lbl_missatge.config(text="Selecciona el directori on tens instal·lat Star Citizen.\nEntra fins al directori LIVE o HOTFIX i prem 'Selecciona carpeta'")
    btn_seleccionar.pack(side=tk.LEFT, padx=20, pady=(0, 10))

def comprovar_directori_defecte():
    # Declarem que farem servir les globals
    global directori_de_treball
    global hi_ha_live
    global hi_ha_hotfix

    directori_live = r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE"
    directori_hotfix = r"C:\Program Files\Roberts Space Industries\StarCitizen\HOTFIX"

    # Avaluem si existeix el directori LIVE i/o HOTFIX
    hi_ha_live = os.path.isdir(directori_live)
    print(f"directori LIVE: {hi_ha_live}")  # Línia de depuració
    hi_ha_hotfix = os.path.isdir(directori_hotfix)
    print(f"directori HOTFIX: {hi_ha_hotfix}")  # Línia de depuració

    # Prioritzem LIVE si hi és
    if hi_ha_live:
        directori_de_treball = directori_live
        print(f"Operant sobre LIVE per defecte")  # Línia de depuració
        lbl_missatge.config(text="Directori d'instal·lació per defecte (LIVE) localitzat.")
        verificar_traduccio(directori_de_treball)
        btn_seleccionar.pack_forget()
    elif hi_ha_hotfix:
        directori_de_treball = directori_hotfix
        print(f"Operant sobre HOTFIX per defecte")  # Línia de depuració
        lbl_missatge.config(text="Directori d'instal·lació per defecte (HOTFIX) localitzat.")
        verificar_traduccio(directori_de_treball)
        btn_seleccionar.pack_forget()
    else:
        mostrar_missatge_seleccio()

def seleccionar_directori():
    global directori_de_treball, hi_ha_live, hi_ha_hotfix
    
    directori_seleccionat = filedialog.askdirectory()

    if not directori_seleccionat:
        # Si l'usuari cancela la selecció, no fem res
        return

    # Extreiem el directori "pare" per comprovar l'existència de l'altre (LIVE o HOTFIX)
    # Exemple: si l'usuari selecciona c:\jocs\LIVE, root_dir serà c:\jocs
    root_dir = os.path.dirname(directori_seleccionat)

    # Cas 1: L'usuari ha escollit LIVE
    if directori_seleccionat.endswith("LIVE") and os.path.isdir(directori_seleccionat):
        hi_ha_live = True
        # Comprovem si també existeix la carpeta HOTFIX al mateix nivell
        hotfix_path = os.path.join(root_dir, "HOTFIX")
        hi_ha_hotfix = os.path.isdir(hotfix_path)

        directori_de_treball = directori_seleccionat
        lbl_missatge.config(text=f"Directori seleccionat: {directori_seleccionat}")
        desar_directori(directori_seleccionat)
        verificar_traduccio(directori_seleccionat)
        btn_seleccionar.pack_forget()

    # Cas 2: L'usuari ha escollit HOTFIX
    elif directori_seleccionat.endswith("HOTFIX") and os.path.isdir(directori_seleccionat):
        hi_ha_hotfix = True
        # Comprovem si també existeix la carpeta LIVE al mateix nivell
        live_path = os.path.join(root_dir, "LIVE")
        hi_ha_live = os.path.isdir(live_path)

        directori_de_treball = directori_seleccionat
        lbl_missatge.config(text=f"Directori seleccionat: {directori_seleccionat}")
        desar_directori(directori_seleccionat)
        verificar_traduccio(directori_seleccionat)
        btn_seleccionar.pack_forget()

    # Cas 3: El directori no és ni LIVE ni HOTFIX
    else:
        lbl_missatge.config(
            text="El directori seleccionat no és correcte. "
                 "Ha de ser el directori LIVE o HOTFIX de Star Citizen."
        )
        #mostrar_missatge_seleccio()

def verificar_traduccio(directori):
    """
    Comprova si existeix LIVE i/o HOTFIX partint de 'directori'.
    Verifica la traducció als directoris que realment existeixin
    i mostra un missatge final sobre si cal o no actualitzar.
    """
    import os
    import requests

    # -----------------------------
    # 1) Deduïm les rutes LIVE i HOTFIX a partir del directori
    # -----------------------------
    # Si 'directori' acaba en LIVE/HOTFIX, usem el pare com a base;
    # si no, assumim que 'directori' ja és la carpeta base.
    base_name = os.path.basename(directori)
    if base_name.upper() in ["LIVE", "HOTFIX"]:
        base_dir = os.path.dirname(directori)
    else:
        base_dir = directori  # Possiblement l’usuari ha seleccionat la carpeta base

    directori_live = os.path.join(base_dir, "LIVE")
    directori_hotfix = os.path.join(base_dir, "HOTFIX")

    # -----------------------------
    # 2) Comprovem quins directoris existeixen realment
    # -----------------------------
    existeix_live = os.path.isdir(directori_live)
    existeix_hotfix = os.path.isdir(directori_hotfix)

    # Si no en tenim cap, avisem i sortim
    if not existeix_live and not existeix_hotfix:
        lbl_missatge_traduccio.config(text="No s'ha detectat LIVE ni HOTFIX.")
        lbl_missatge_actualitzacio.config(fg="red", text="No hi ha cap directori LIVE ni HOTFIX per verificar.")
        return

    # -----------------------------
    # 3) Obtenir la versió remota de global.ini (només una vegada)
    # -----------------------------
    versio_remota = "Desconeguda"
    try:
        url = "http://www.paraules.net/SC/global.ini"
        response = requests.get(url)
        response.raise_for_status()
        for linia in response.text.split('\n'):
            if "mobiGlas_ui_mobiGlasName=mobiGlas" in linia:
                # Exemple de línia: "mobiGlas_ui_mobiGlasName=mobiGlas 3.19"
                versio_remota = linia.split('Glas ')[-1].strip()
                break
    except requests.RequestException:
        versio_remota = "Error al comprovar la versió remota"

    # -----------------------------
    # 4) Definim una funció auxiliar per a cada directori
    #    que comprova si user.cfg i global.ini hi són. 
    #    Si no hi són, instal·la la traducció. Després llegeix la versió local.
    # -----------------------------
    def check_and_install_if_missing(directori_concret):
        cfg_path = os.path.join(directori_concret, "user.cfg")
        global_ini_path = os.path.join(directori_concret, "data", "Localization", "spanish_(spain)", "global.ini")

        # Si no hi ha user.cfg o global.ini, instal·lem la traducció
        if not os.path.isfile(cfg_path) or not os.path.isfile(global_ini_path):
            instal·lar_traduccio(directori_concret)

        # Tornem a mirar la versió local (pot ser que s'acabi d'instal·lar)
        versio_local = "Desconeguda"
        if os.path.isfile(global_ini_path):
            with open(global_ini_path, 'r', encoding='utf-8') as f:
                for linia in f:
                    if "mobiGlas_ui_mobiGlasName=mobiGlas" in linia:
                        versio_local = linia.split('Glas ')[-1].strip()
                        break
        return versio_local

    # -----------------------------
    # 5) Verifiquem cadascun dels directoris existents
    # -----------------------------
    versions_locals = {}  # Guardarem: {"LIVE": "3.19", "HOTFIX": "Desconeguda", etc.}

    if existeix_live:
        versio_local_live = check_and_install_if_missing(directori_live)
        versions_locals["LIVE"] = versio_local_live

    if existeix_hotfix:
        versio_local_hotfix = check_and_install_if_missing(directori_hotfix)
        versions_locals["HOTFIX"] = versio_local_hotfix

    # -----------------------------
    # 6) Si la versió remota té error, avisem i sortim
    # -----------------------------
    if versio_remota == "Error al comprovar la versió remota":
        lbl_missatge_traduccio.config(text="No s'ha pogut obtenir la versió remota.")
        lbl_missatge_actualitzacio.config(
            fg="red",
            text="Error al comprovar la versió remota. No podem determinar si cal actualitzar."
        )
        return

    # -----------------------------
    # 7) Compare versions locals vs remota i preparem un missatge unificat
    # -----------------------------
    # - versions_locals pot contenir LIVE i/o HOTFIX
    # - Ex: {"LIVE": "3.19", "HOTFIX": "3.18"}
    necessiten_actualitzacio = []
    text_versions = []

    for nom_dir, versio_local in versions_locals.items():
        # Afegim info de cada directori
        text_versions.append(f"{nom_dir}: versió local = {versio_local}")

        # Decidim si cal actualitzar
        if versio_local == "Desconeguda":
            # No hem pogut llegir la versió, o no està correctament instal·lada
            necessiten_actualitzacio.append(nom_dir)
        elif versio_local != versio_remota:
            necessiten_actualitzacio.append(nom_dir)

    # Mostrem les versions actuals en lbl_missatge_traduccio
    text_versions = "\n".join(text_versions)
    text_final_versions = (
        f"Versió remota = {versio_remota}\n"
        f"{text_versions}"
    )
    lbl_missatge_traduccio.config(text=text_final_versions)

    # -----------------------------
    # 8) Mostrem un missatge agregat de si cal actualitzar
    # -----------------------------
    if len(necessiten_actualitzacio) == 0:
        # Cap directori necessita actualització
        lbl_missatge_actualitzacio.config(fg="green", text="Tots els directoris estan actualitzats.")
        btn_actualitzar.pack_forget()
    elif len(necessiten_actualitzacio) == 1:
        # Només un directori necessita actualització
        nom_dir = necessiten_actualitzacio[0]
        lbl_missatge_actualitzacio.config(fg="red", text=f"Cal actualitzar el directori {nom_dir}.")
        btn_actualitzar.pack(side=tk.LEFT, padx=20, pady=12)
    else:
        # Més d'un directori necessita actualització (probablement 2)
        noms = ", ".join(necessiten_actualitzacio)
        lbl_missatge_actualitzacio.config(
            fg="red",
            text=f"Cal actualitzar la traducció als directoris: {noms}."
        )
        btn_actualitzar.pack(side=tk.LEFT, padx=20, pady=12)

def actualitzar_traduccio():
    global directori_de_treball, hi_ha_live, hi_ha_hotfix

    # 1. Llegim el directori guardat, o provem el per defecte
    directori_guardat = llegir_directori_desat()
    if directori_guardat and os.path.isdir(directori_guardat):
        directori_de_treball = directori_guardat
    else:
        # Si no hi ha directori desat o és invàlid, mirem els predeterminats
        directori_live_defecte = r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE"
        directori_hotfix_defecte = r"C:\Program Files\Roberts Space Industries\StarCitizen\HOTFIX"

        existeix_live_defecte = os.path.isdir(directori_live_defecte)
        existeix_hotfix_defecte = os.path.isdir(directori_hotfix_defecte)

        # Prioritza LIVE si hi és, si no, HOTFIX, si no error
        if existeix_live_defecte:
            directori_de_treball = directori_live_defecte
        elif existeix_hotfix_defecte:
            directori_de_treball = directori_hotfix_defecte
        else:
            messagebox.showerror("Error", "No s'ha trobat cap directori LIVE ni HOTFIX per defecte.\n"
                                          "Selecciona manualment el directori.")
            return

    # 2. A partir del directori_de_treball, calculem les rutes LIVE i HOTFIX
    #    (Veure la lògica que fem servir a verificar_traduccio o similar)
    base_name = os.path.basename(directori_de_treball)
    if base_name.upper() in ["LIVE", "HOTFIX"]:
        base_dir = os.path.dirname(directori_de_treball)
    else:
        base_dir = directori_de_treball

    directori_live = os.path.join(base_dir, "LIVE")
    directori_hotfix = os.path.join(base_dir, "HOTFIX")

    # Comprovem quins existeixen realment
    hi_ha_live = os.path.isdir(directori_live)
    hi_ha_hotfix = os.path.isdir(directori_hotfix)

    # 3. Funció auxiliar que sobreescriu el global.ini en un directori concret
    def update_global_ini(dir_path):
        directori_traduccio = os.path.join(dir_path, "data", "Localization", "spanish_(spain)")
        os.makedirs(directori_traduccio, exist_ok=True)  # Per si de cas no existeix
        global_ini_path = os.path.join(directori_traduccio, "global.ini")

        try:
            url = "http://www.paraules.net/SC/global.ini"
            response = requests.get(url)
            response.raise_for_status()
            with open(global_ini_path, 'wb') as f:
                f.write(response.content)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"No s'ha pogut descarregar el fitxer global.ini: {e}")

    # 4. Actualitzem (sobreescrivim) el global.ini dels directoris que existeixin
    if hi_ha_live:
        update_global_ini(directori_live)
    if hi_ha_hotfix:
        update_global_ini(directori_hotfix)

    if not hi_ha_live and not hi_ha_hotfix:
        # Si no hi havia ni LIVE ni HOTFIX, avisem
        messagebox.showerror("Error", "No s'ha trobat cap directori LIVE ni HOTFIX per actualitzar.")
        return

    # 5. Verifiquem de nou l'estat de la traducció, per actualitzar labels i botons
    verificar_traduccio(directori_de_treball)


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
btn_seleccionar = tk.Button(marc_principal, text="Seleccionar directori LIVE o HOTFIX", command=seleccionar_directori)
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
