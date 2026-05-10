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
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.core.window import Window

# Farben und Konstanten
BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN = (0, 0.9, 1, 1)
GREEN = (0, 1, 0.5, 1)
RED = (1, 0.2, 0.2, 1)
YELLOW = (1, 0.8, 0, 1)
WHITE = (1, 1, 1, 1)

MAC_VARIANTS = ('00:1A:79:', 'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:', '55:93:EA:', '04:D6:AA:', '00:1B:79:', '00:2A:01:')
COMMON_PORTS = [80, 8080, 8880, 25461, 8000, 2082, 2086, 2095, 8443, 443]

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

# --- Screens ---

class PortalManagerScreen(Screen):
    def __init__(self, context, **kw):
        super().__init__(**kw)
        self.context = context
        # Pfad aus context beziehen oder Standard nutzen
        self.fav_file = self.context["paths"].get("fav_file", "/storage/emulated/0/Portals/favoriten_liste.json")
        
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
        if not os.path.exists(self.fav_file): return
        try:
            with open(self.fav_file, 'r') as f: data = json.load(f)
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
        if os.path.exists(self.fav_file):
            try:
                with open(self.fav_file, 'r') as f: data = json.load(f)
            except: pass
        if url not in data[p_type]:
            data[p_type].append(url)
            with open(self.fav_file, 'w') as f: json.dump(data, f)
            self.new_portal_input.text = ""; self.load_favs()

    def delete_portal(self, url, p_type):
        if not os.path.exists(self.fav_file): return
        with open(self.fav_file, 'r') as f: data = json.load(f)
        if url in data[p_type]: data[p_type].remove(url)
        with open(self.fav_file, 'w') as f: json.dump(data, f)
        self.load_favs()

    def copy_and_back(self, url):
        Clipboard.copy(url)
        self.manager.get_screen('main').portal_input.text = url
        self.manager.current = 'main'

    def go_back(self, *a): 
        self.manager.current = 'main'


class MagUltraScreen(Screen):
    def __init__(self, context, **kw):
        super().__init__(**kw)
        self.context = context
        self.box = BoxLayout(orientation="vertical", padding=[20, 35, 20, 20], spacing=15)
        Window.clearcolor = BG_DARK
        
        self.hits, self.checked, self.total_lines, self.running = 0, 0, 0, False
        self.hit_list, self.last_status, self.start_time = [], "READY", time.time()
        
        # UI Aufbau
        self.box.add_widget(Image(source=self.context["paths"]["png"], size_hint_y=None, height=320, allow_stretch=True, keep_ratio=False))
        
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
        
        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20, color=CYAN); self.box.add_widget(self.progress_label); self.pbar = ProgressBar(max=100, value=0, size_hint_y=None, height=10); self.box.add_widget(self.pbar)
        self.scroll = ScrollView(); self.log_display = Label(text="Ready...", font_size="14sp", size_hint_y=None, markup=True, halign="left", valign="top"); self.log_display.bind(size=self.log_display.setter('text_size')); self.scroll.add_widget(self.log_display); self.box.add_widget(self.scroll)
        
        bottom_row = BoxLayout(size_hint_y=None, height=110, spacing=15)
        self.start_btn = StyledButton(text="START MAC ULTRA", size_hint_x=0.7, on_press=self.toggle, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN)
        self.music_stop_btn = StyledButton(text="STOP MUSIC", size_hint_x=0.3, on_press=self.stop_audio, bg_color=(0.15, 0.05, 0.05, 1), color=RED)
        bottom_row.add_widget(self.start_btn); bottom_row.add_widget(self.music_stop_btn)
        self.box.add_widget(bottom_row)
        self.add_widget(self.box)

    def go_to_manager(self, *a):
        self.manager.get_screen("portals").load_favs()
        self.manager.current = "portals"

    def reset_start_button(self, *a):
        self.start_btn.text = "START MAC ULTRA"
        self.start_btn.color = GREEN
        self.start_btn.bg_color_inst.rgba = (0.05, 0.15, 0.1, 1)

    def create_stat_box(self, p, t, v, c):
        box = StyledCard(orientation="vertical", padding=8); box.add_widget(Label(text=t, font_size="11sp", color=(0.7,0.7,0.7,1))); lbl = Label(text=v, font_size="24sp", bold=True, color=c)
        box.add_widget(lbl); p.add_widget(box); return lbl

    def update_slider_label(self, i, v): self.detail_status.text, self.detail_status.color = ("ALLES SPEICHERN", GREEN) if v == 1 else ("NUR MAC/URL", RED)
    def load_combos(self): return sorted([f for f in os.listdir("/sdcard/Combo/") if f.endswith(".txt")]) if os.path.exists("/sdcard/Combo/") else ["NO FOLDER"]
    def load_portal_lists(self):
        p_dir = self.context["paths"].get("portals_dir", "/storage/emulated/0/Portals/")
        try:
            files = [f for f in os.listdir(p_dir) if f.endswith(".txt")]
            return sorted(files) + ["USE SINGLE"]
        except: return ["USE SINGLE"]

    def paste_clip(self, *a): self.portal_input.text = Clipboard.paste().strip()
    def stop_audio(self, *a):
        if "audio_player" in self.context:
            try: self.context["audio_player"].stop()
            except: pass

    def update_log_safe(self, t): Clock.schedule_once(lambda dt: self._do_log(t))
    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 10: self.hit_list.pop(0)
        self.log_display.text = "\n".join(self.hit_list); self.log_display.height = self.log_display.texture_size[1] + 20

    def refresh_ui(self, *a):
        self.pbar.value, self.hit_count_label.text = self.checked, str(self.hits)
        self.progress_label.text, self.status_code_label.text = f"PROGRESS: {self.checked} / {self.total_lines}", self.last_status
        el = time.time() - self.start_time
        if el > 0: self.cpm_label.text = str(int((self.checked / el) * 60))

    def toggle(self, *_):
        if not self.running:
            self.running = True
            if "audio_player" in self.context: self.context["audio_player"].play()
            self.start_btn.text, self.start_btn.color = "STOP MAC ULTRA", RED
            self.start_btn.bg_color_inst.rgba = (0.15, 0.05, 0.05, 1)
            Thread(target=lambda: asyncio.run(self.engine()), daemon=True).start()
        else: 
            self.running = False
            self.reset_start_button()

    async def engine(self):
        import httpx
        cfg = self.context.get("config", {}).get("locked_config", {})
        
        portals = []
        if self.portal_file_spinner.text not in ["SELECT PORTAL LIST", "USE SINGLE"]:
            p_path = os.path.join(self.context["paths"]["portals_dir"], self.portal_file_spinner.text)
            if os.path.exists(p_path):
                with open(p_path, 'r') as f: portals = [l.strip() for l in f if l.strip().startswith("http")]
        if not portals:
            single = self.portal_input.text.strip()
            if single.startswith("http"): portals = [single]
        
        if not portals:
            self.update_log_safe("[color=FF0000][ERROR][/color] No Portals!")
            self.running = False
            Clock.schedule_once(lambda dt: self.reset_start_button())
            return

        ctx = ssl.create_default_context()
        ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE

        if self.scan_mode.text == "COMBO FILE":
            path = f"/sdcard/Combo/{self.file_spinner.text}"
            if not os.path.exists(path): self.running = False; Clock.schedule_once(lambda dt: self.reset_start_button()); return
            with open(path, 'r', errors='ignore') as f: self.combo_data = [l.strip() for l in f if l.strip()]
        else:
            prefix = self.prefix_spinner.text if self.prefix_spinner.text != "MAC's" else "00:1A:79:"
            count = min(int(self.random_count.text or 500), cfg.get("max_random_count", 500))
            self.combo_data = [f"{prefix}{':'.join([f'{random.randint(0,255):02X}' for _ in range(3)])}" for _ in range(count)]

        self.total_lines, self.checked, self.hits, self.start_time = len(self.combo_data), 0, 0, time.time()
        Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))
        
        queue = asyncio.Queue()
        for l in self.combo_data: queue.put_nowait(l)
        
        num_bots = min(int(self.bot_slider.value), cfg.get("max_bots", 100))
        await asyncio.gather(*[self.worker(queue, ctx, portals) for _ in range(num_bots)])
        
        self.running = False
        Clock.schedule_once(lambda dt: self.reset_start_button())

    async def worker(self, queue, ctx, portals):
        import httpx
        while self.running and not queue.empty():
            line = await queue.get()
            for portal in portals:
                if not self.running: break
                try:
                    async with httpx.AsyncClient(verify=ctx, timeout=10) as client:
                        self.last_status = "200"
                except: self.last_status = "ERR"
            
            self.checked += 1
            Clock.schedule_once(lambda dt: self.refresh_ui())
            queue.task_done()
            await asyncio.sleep(self.delay_slider.value)

# --- Entry Point ---

def create_app_screen(context):
    """
    Initialisiert den ScreenManager für den Loader.
    """
    sm = ScreenManager()
    
    main = MagUltraScreen(context=context, name="main")
    portals = PortalManagerScreen(context=context, name="portals")
    
    sm.add_widget(main)
    sm.add_widget(portals)
    
    sm.current = "main"
    return sm
