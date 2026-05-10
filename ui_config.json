import os, asyncio, time, urllib.parse, socket, random, ssl, json, uuid
from datetime import datetime
from threading import Thread

# Kivy Imports
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
from kivy.uix.modalview import ModalView
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.core.window import Window

# Android Media Player Setup
try:
    from jnius import autoclass
    MediaPlayer = autoclass("android.media.MediaPlayer")
    mPlayer = MediaPlayer()
    HAS_JNIUS = True
except:
    HAS_JNIUS = False

# Farben und Konstanten (Original Git-Style)
BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN = (0, 0.9, 1, 1)
GREEN = (0, 1, 0.5, 1)
RED = (1, 0.2, 0.2, 1)
YELLOW = (1, 0.8, 0, 1)
WHITE = (1, 1, 1, 1)

MAC_VARIANTS = ('00:1A:79:', 'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:', '55:93:EA:', '04:D6:AA:', '00:1B:79:', '00:2A:01:')

# --- UI Komponenten ---

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

# --- Favoriten ModalView (Ersatz für Screen) ---

class PortalManagerView(ModalView):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.size_hint = (0.95, 0.9)
        self.background_color = [0,0,0,0]
        self.fav_file = main_screen.context["paths"].get("fav_file", "/storage/emulated/0/Portals/favoriten_liste.json")
        
        container = StyledCard(orientation="vertical", padding=20, spacing=15, bg_color=BG_DARK)
        container.add_widget(Label(text="[color=00E6FF][b]FAVORITEN MANAGER[/b][/color]", markup=True, size_hint_y=None, height=60, font_size="22sp"))
        
        input_card = StyledCard(orientation="vertical", size_hint_y=None, height=180, padding=10, spacing=10)
        self.new_portal_input = TextInput(hint_text="http://url.com:8080", multiline=False, height=50, size_hint_y=None, background_color=(0.1, 0.1, 0.1, 1), foreground_color=WHITE)
        row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.type_spinner = StyledSpinner(text="MAC PORTAL", values=("MAC PORTAL", "M3U PORTAL"), color=CYAN)
        add_btn = StyledButton(text="HINZUFÜGEN", color=GREEN, on_press=self.add_portal)
        row.add_widget(self.type_spinner); row.add_widget(add_btn)
        input_card.add_widget(self.new_portal_input); input_card.add_widget(row)
        container.add_widget(input_card)
        
        lists_container = BoxLayout(spacing=10)
        self.mac_list = GridLayout(cols=1, spacing=5, size_hint_y=None); self.mac_list.bind(minimum_height=self.mac_list.setter('height'))
        self.m3u_list = GridLayout(cols=1, spacing=5, size_hint_y=None); self.m3u_list.bind(minimum_height=self.m3u_list.setter('height'))
        sc1 = ScrollView(); sc1.add_widget(self.mac_list); sc2 = ScrollView(); sc2.add_widget(self.m3u_list)
        lists_container.add_widget(sc1); lists_container.add_widget(sc2)
        container.add_widget(lists_container)
        
        container.add_widget(StyledButton(text="ZURÜCK", size_hint_y=None, height=60, on_press=self.dismiss, color=RED))
        self.add_widget(container)
        self.load_favs()

    def load_favs(self):
        self.mac_list.clear_widgets(); self.m3u_list.clear_widgets()
        if not os.path.exists(self.fav_file): return
        try:
            with open(self.fav_file, 'r', encoding="utf-8") as f: data = json.load(f)
            for url in data.get("mac", []): self.mac_list.add_widget(self.create_entry(url))
            for url in data.get("m3u", []): self.m3u_list.add_widget(self.create_entry(url))
        except: pass

    def create_entry(self, url):
        btn = StyledButton(text=url[:35], font_size="11sp", size_hint_y=None, height=45, on_press=lambda x: self.select_portal(url))
        return btn

    def add_portal(self, *a):
        url = self.new_portal_input.text.strip()
        if not url.startswith("http"): return
        p_type = "mac" if "MAC" in self.type_spinner.text else "m3u"
        data = {"mac": [], "m3u": []}
        if os.path.exists(self.fav_file):
            try:
                with open(self.fav_file, 'r', encoding="utf-8") as f: data = json.load(f)
            except: pass
        if url not in data[p_type]:
            data[p_type].append(url)
            with open(self.fav_file, 'w', encoding="utf-8") as f: json.dump(data, f)
            self.new_portal_input.text = ""; self.load_favs()

    def select_portal(self, url):
        self.main_screen.portal_input.text = url
        self.dismiss()

# --- Haupt Screen (1:1 aus git.py) ---

class MagUltraScreen(Screen):
    def __init__(self, context, **kw):
        super().__init__(**kw)
        self.context = context
        self.box = BoxLayout(orientation="vertical", padding=[20, 35, 20, 20], spacing=15)
        Window.clearcolor = BG_DARK
        
        # Variablen aus git.py
        self.working_proxies, self.proxy_list, self.use_proxies = [], [], False
        self.hits, self.checked, self.total_lines, self.running = 0, 0, 0, False
        self.hit_list, self.last_status, self.start_time = [], "READY", time.time()
        
        # 1. Banner
        self.box.add_widget(Image(source=self.context["paths"]["png"], size_hint_y=None, height=320))
        
        # 2. Stats
        stats = GridLayout(cols=3, size_hint_y=None, height=110, spacing=15)
        self.cpm_label = self.create_stat_box(stats, "CPM", "0", YELLOW)
        self.status_code_label = self.create_stat_box(stats, "STATUS", "READY", CYAN)
        self.hit_count_label = self.create_stat_box(stats, "HITS", "0", GREEN)
        self.box.add_widget(stats)
        
        # 3. Portal Card
        url_card = StyledCard(orientation="vertical", size_hint_y=None, height=380, padding=15, spacing=12)
        self.portal_input = TextInput(text="http://", multiline=False, size_hint_y=None, height=75, background_color=(0.1,0.1,0.1,1), foreground_color=WHITE, padding=[10,20])
        
        filter_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.portal_file_spinner = StyledSpinner(text="PORTAL LISTE", values=self.load_portal_lists(), size_hint_x=0.6, color=YELLOW)
        self.country_filter = TextInput(hint_text="LAND", multiline=False, size_hint_x=0.4, background_color=(0.1,0.1,0.1,1), foreground_color=WHITE)
        filter_row.add_widget(self.portal_file_spinner); filter_row.add_widget(self.country_filter)
        
        det_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.engine_mode = StyledSpinner(text="MAC SCAN", values=("MAC SCAN", "M3U SCAN"), size_hint_x=0.4, color=CYAN)
        self.detail_slider = Slider(min=0, max=1, value=0, step=1, size_hint_x=0.2); self.detail_status = Label(text="NUR URL", color=RED, size_hint_x=0.4)
        self.detail_slider.bind(value=self.update_slider_label)
        det_row.add_widget(self.engine_mode); det_row.add_widget(self.detail_slider); det_row.add_widget(self.detail_status)
        
        btn_row = BoxLayout(spacing=15, size_hint_y=None, height=75)
        btn_row.add_widget(StyledButton(text="PASTE", on_press=lambda x: setattr(self.portal_input, 'text', Clipboard.paste()), color=CYAN))
        btn_row.add_widget(StyledButton(text="FAVORITEN", on_press=self.open_favs, color=YELLOW))
        url_card.add_widget(self.portal_input); url_card.add_widget(filter_row); url_card.add_widget(det_row); url_card.add_widget(btn_row); self.box.add_widget(url_card)
        
        # 4. Proxy Card (Wiederhergestellt)
        proxy_card = StyledCard(orientation="vertical", size_hint_y=None, height=160, padding=15, spacing=10)
        p_row = BoxLayout(spacing=10)
        self.proxy_source = StyledSpinner(text="OFF", values=("OFF", "SOCKS4", "SOCKS5", "HTTP"), size_hint_x=0.3, color=YELLOW)
        self.proxy_spinner = StyledSpinner(text="SELECT PROXY", values=self.load_proxies(), size_hint_x=0.5, color=CYAN)
        self.proxy_toggle_btn = StyledButton(text="LOAD", size_hint_x=0.2, color=CYAN, on_press=self.toggle_proxy)
        p_row.add_widget(self.proxy_source); p_row.add_widget(self.proxy_spinner); p_row.add_widget(self.proxy_toggle_btn)
        proxy_card.add_widget(p_row); self.box.add_widget(proxy_card)
        
        # 5. Config Card
        cfg_card = StyledCard(orientation="vertical", size_hint_y=None, height=340, padding=15, spacing=10)
        m_row = BoxLayout(spacing=10, size_hint_y=None, height=60)
        self.scan_mode = StyledSpinner(text="COMBO FILE", values=("COMBO FILE", "RANDOM SCAN")); self.prefix_spinner = StyledSpinner(text="MAC's", values=MAC_VARIANTS, color=YELLOW)
        m_row.add_widget(self.scan_mode); m_row.add_widget(self.prefix_spinner)
        self.file_spinner = StyledSpinner(text="SELECT COMBO", values=self.load_combos(), height=60, color=CYAN)
        self.random_count = TextInput(text="1000", input_filter="int", height=60, halign="center", background_color=(0.1,0.1,0.1,1), foreground_color=WHITE)
        
        delay_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.delay_label = Label(text="0.10s", color=YELLOW, size_hint_x=0.2); self.delay_slider = Slider(min=0.0, max=2.0, value=0.1, step=0.05, size_hint_x=0.8)
        self.delay_slider.bind(value=lambda i, v: setattr(self.delay_label, 'text', f"{v:.2f}s")); delay_row.add_widget(self.delay_label); delay_row.add_widget(self.delay_slider)
        
        bot_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.bot_label = Label(text="BOTS: 40", color=CYAN, size_hint_x=0.3); self.bot_slider = Slider(min=1, max=100, value=40, step=1, size_hint_x=0.7)
        self.bot_slider.bind(value=lambda i, v: setattr(self.bot_label, 'text', f"BOTS: {int(v)}")); bot_row.add_widget(self.bot_label); bot_row.add_widget(self.bot_slider)
        cfg_card.add_widget(m_row); cfg_card.add_widget(self.file_spinner); cfg_card.add_widget(self.random_count); cfg_card.add_widget(delay_row); cfg_card.add_widget(bot_row); self.box.add_widget(cfg_card)
        
        # 6. Progress & Log
        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20, color=CYAN); self.box.add_widget(self.progress_label)
        self.pbar = ProgressBar(max=100, value=0, size_hint_y=None, height=10); self.box.add_widget(self.pbar)
        self.scroll = ScrollView(); self.log_display = Label(text="Bereit...", size_hint_y=None, markup=True); self.log_display.bind(size=self.log_display.setter('text_size')); self.scroll.add_widget(self.log_display); self.box.add_widget(self.scroll)
        
        # 7. Buttons
        bottom_row = BoxLayout(size_hint_y=None, height=110, spacing=15)
        self.start_btn = StyledButton(text="START MAC ULTRA", size_hint_x=0.7, on_press=self.toggle, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN)
        self.music_stop_btn = StyledButton(text="STOP MUSIC", size_hint_x=0.3, on_press=self.stop_audio, bg_color=(0.15, 0.05, 0.05, 1), color=RED)
        bottom_row.add_widget(self.start_btn); bottom_row.add_widget(self.music_stop_btn)
        self.box.add_widget(bottom_row); self.add_widget(self.box)

    # --- Logik Methoden ---
    
    def open_favs(self, *a): PortalManagerView(main_screen=self).open()

    def toggle_proxy(self, *a):
        if self.proxy_source.text == "OFF": return
        path = f"/storage/emulated/0/proxies/{self.proxy_spinner.text}"
        if os.path.exists(path):
            with open(path, 'r') as f: self.proxy_list = [l.strip() for l in f if l.strip()]
            self.use_proxies = True
            self.update_log_safe(f"[color=00FFFF][PROXY][/color] {len(self.proxy_list)} geladen.")

    def play_audio(self):
        if HAS_JNIUS:
            try:
                mp3 = self.context["paths"]["mp3"]
                if os.path.exists(mp3):
                    mPlayer.reset(); mPlayer.setDataSource(mp3); mPlayer.prepare(); mPlayer.start()
            except: pass

    def stop_audio(self, *a):
        if HAS_JNIUS:
            try: mPlayer.stop()
            except: pass

    def update_log_safe(self, t): Clock.schedule_once(lambda dt: self._do_log(t))
    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 15: self.hit_list.pop(0)
        self.log_display.text = "\n".join(self.hit_list); self.log_display.height = self.log_display.texture_size[1] + 20

    def refresh_ui(self, *a):
        self.pbar.value, self.hit_count_label.text = self.checked, str(self.hits)
        self.progress_label.text, self.status_code_label.text = f"PROGRESS: {self.checked} / {self.total_lines}", self.last_status
        el = time.time() - self.start_time
        if el > 0: self.cpm_label.text = str(int((self.checked / el) * 60))

    def update_slider_label(self, i, v): self.detail_status.text, self.detail_status.color = ("ALLES SPEICHERN", GREEN) if v == 1 else ("NUR URL", RED)

    def reset_start_button(self, *a):
        self.start_btn.text, self.start_btn.color = "START MAC ULTRA", GREEN
        self.start_btn.bg_color_inst.rgba = (0.05, 0.15, 0.1, 1)

    def toggle(self, *_):
        if not self.running:
            self.running = True; self.play_audio()
            self.start_btn.text, self.start_btn.color = "STOP SCAN", RED
            self.start_btn.bg_color_inst.rgba = (0.15, 0.05, 0.05, 1)
            Thread(target=lambda: asyncio.run(self.engine_dummy()), daemon=True).start()
        else: 
            self.running = False; self.reset_start_button()

    async def engine_dummy(self):
        self.total_lines = 100; self.checked = 0; self.hits = 0; self.start_time = time.time()
        Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))
        while self.running and self.checked < self.total_lines:
            await asyncio.sleep(self.delay_slider.value)
            self.checked += 1
            if random.random() > 0.9: self.hits += 1; self.update_log_safe(f"[color=00FF80]HIT:[/color] Portal Match @ {self.checked}")
            Clock.schedule_once(lambda dt: self.refresh_ui())
        self.running = False; Clock.schedule_once(self.reset_start_button)

    def create_stat_box(self, p, t, v, c):
        box = StyledCard(orientation="vertical", padding=8); box.add_widget(Label(text=t, font_size="11sp", color=(0.7,0.7,0.7,1))); lbl = Label(text=v, font_size="24sp", bold=True, color=c)
        box.add_widget(lbl); p.add_widget(box); return lbl

    def load_proxies(self):
        try: return sorted([f for f in os.listdir("/storage/emulated/0/proxies/") if f.endswith(".txt")])
        except: return ["MANUELL"]

    def load_combos(self):
        try: return sorted([f for f in os.listdir("/sdcard/Combo/") if f.endswith(".txt")])
        except: return ["NO FILES"]

    def load_portal_lists(self):
        p_dir = self.context["paths"].get("portals_dir", "/storage/emulated/0/Portals/")
        try: return sorted([f for f in os.listdir(p_dir) if f.endswith(".txt")]) + ["MANUELL"]
        except: return ["MANUELL"]

# --- Entry Point ---

def create_app_screen(context):
    return MagUltraScreen(context=context, name="main")
