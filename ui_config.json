import os, asyncio, time, random, ssl, json, socket, uuid, httpx
from datetime import datetime
from threading import Thread

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
    MediaPlayer = autoclass('android.media.MediaPlayer')
    mPlayer = MediaPlayer()
    HAS_JNIUS = True
except:
    HAS_JNIUS = False

# --- Original Konstanten & Farben ---
BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN = (0, 0.9, 1, 1)
GREEN = (0, 1, 0.5, 1)
RED = (1, 0.2, 0.2, 1)
YELLOW = (1, 0.8, 0, 1)
WHITE = (1, 1, 1, 1)

MAC_VARIANTS = ('00:1A:79:', 'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:', '55:93:EA:', '04:D6:AA:', '00:1B:79:', '00:2A:01:')

# --- Styled UI Komponenten ---

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

# --- Favoriten Modal ---

class PortalManagerView(ModalView):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.size_hint = (0.95, 0.9)
        self.background_color = [0,0,0,0]
        self.fav_file = "/storage/emulated/0/Portals/favoriten_liste.json"
        
        layout = StyledCard(orientation="vertical", padding=20, spacing=15, bg_color=BG_DARK)
        layout.add_widget(Label(text="[color=00E6FF][b]MAC ULTRA FAVORITEN[/b][/color]", markup=True, size_hint_y=None, height=80, font_size="28sp"))
        
        input_card = StyledCard(orientation="vertical", size_hint_y=None, height=220, padding=15, spacing=12)
        self.new_portal_input = TextInput(hint_text="http://url.com:8080", multiline=False, size_hint_y=None, height=75, background_color=(0.1, 0.1, 0.1, 1), foreground_color=WHITE, padding=[10, 20])
        row = BoxLayout(size_hint_y=None, height=65, spacing=15)
        self.type_spinner = StyledSpinner(text="MAC PORTAL", values=("MAC PORTAL", "M3U PORTAL"), color=CYAN, bold=True)
        add_btn = StyledButton(text="HINZUFÜGEN", bg_color=(0.05, 0.15, 0.1, 1), color=GREEN, on_press=self.add_portal)
        row.add_widget(self.type_spinner); row.add_widget(add_btn)
        input_card.add_widget(self.new_portal_input); input_card.add_widget(row)
        layout.add_widget(input_card)
        
        lists_container = BoxLayout(spacing=15)
        self.mac_list = GridLayout(cols=1, spacing=8, size_hint_y=None); self.mac_list.bind(minimum_height=self.mac_list.setter('height'))
        self.m3u_list = GridLayout(cols=1, spacing=8, size_hint_y=None); self.m3u_list.bind(minimum_height=self.m3u_list.setter('height'))
        sc1 = ScrollView(); sc1.add_widget(self.mac_list); sc2 = ScrollView(); sc2.add_widget(self.m3u_list)
        lists_container.add_widget(sc1); lists_container.add_widget(sc2)
        layout.add_widget(lists_container)
        
        layout.add_widget(StyledButton(text="ZURÜCK", size_hint_y=None, height=100, on_press=self.dismiss, color=RED, bold=True))
        self.add_widget(layout)
        self.load_favs()

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
        btn = StyledButton(text=url[:25], font_size="12sp", on_press=lambda x: self.select_portal(url))
        del_btn = StyledButton(text="X", size_hint_x=0.2, bg_color=(0.3, 0.05, 0.05, 1), color=RED, on_press=lambda x: self.delete_portal(url, p_type))
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
            self.load_favs()

    def delete_portal(self, url, p_type):
        with open(self.fav_file, 'r') as f: data = json.load(f)
        if url in data[p_type]: data[p_type].remove(url)
        with open(self.fav_file, 'w') as f: json.dump(data, f)
        self.load_favs()

    def select_portal(self, url):
        self.main_screen.portal_input.text = url
        self.dismiss()

# --- Haupt Screen ---

class MagUltraScreen(Screen):
    def __init__(self, context, **kw):
        super().__init__(**kw)
        self.context = context
        self.box = BoxLayout(orientation="vertical", padding=[20, 35, 20, 20], spacing=15)
        Window.clearcolor = BG_DARK
        
        self.hits, self.checked, self.total_lines, self.running = 0, 0, 0, False
        self.hit_list, self.last_status, self.start_time = [], "READY", time.time()
        self.proxy_list, self.use_proxies = [], False
        self.combo_data = []
        
        self.setup_ui()

    def setup_ui(self):
        # Banner
        self.box.add_widget(Image(source=self.context["paths"]["png"], size_hint_y=None, height=320, allow_stretch=True, keep_ratio=False))
        
        # Stats
        stats = GridLayout(cols=3, size_hint_y=None, height=110, spacing=15)
        self.cpm_label = self.create_stat_box(stats, "CPM", "0", YELLOW)
        self.status_code_label = self.create_stat_box(stats, "STATUS", "READY", CYAN)
        self.hit_count_label = self.create_stat_box(stats, "MAC ULTRA HITS", "0", GREEN)
        self.box.add_widget(stats)
        
        # Portal Card
        url_card = StyledCard(orientation="vertical", size_hint_y=None, height=380, padding=15, spacing=12)
        self.portal_input = TextInput(text="http://", multiline=False, size_hint_y=None, height=75, background_color=(0.1, 0.1, 0.1, 1), foreground_color=WHITE, padding=[10, 20])
        
        filter_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.portal_file_spinner = StyledSpinner(text="SELECT PORTAL LIST", values=self.load_portal_lists(), size_hint_x=0.6, color=YELLOW)
        self.country_filter = TextInput(hint_text="LAND (z.B. DE)", multiline=False, size_hint_x=0.4, background_color=(0.1, 0.1, 0.1, 1), foreground_color=WHITE)
        filter_row.add_widget(self.portal_file_spinner); filter_row.add_widget(self.country_filter)
        
        det_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.engine_mode = StyledSpinner(text="MAC SCAN", values=("MAC SCAN", "M3U SCAN"), size_hint_x=0.4, color=CYAN)
        self.detail_slider = Slider(min=0, max=1, value=0, step=1, size_hint_x=0.2); self.detail_status = Label(text="NUR MAC/URL", color=RED, size_hint_x=0.4)
        self.detail_slider.bind(value=self.update_slider_label)
        det_row.add_widget(self.engine_mode); det_row.add_widget(self.detail_slider); det_row.add_widget(self.detail_status)
        
        btn_row = BoxLayout(spacing=15, size_hint_y=None, height=75)
        btn_row.add_widget(StyledButton(text="PASTE", on_press=lambda x: setattr(self.portal_input, 'text', Clipboard.paste()), color=CYAN))
        btn_row.add_widget(StyledButton(text="FAVORITEN", on_press=lambda x: PortalManagerView(self).open(), color=YELLOW))
        url_card.add_widget(self.portal_input); url_card.add_widget(filter_row); url_card.add_widget(det_row); url_card.add_widget(btn_row); self.box.add_widget(url_card)
        
        # Config Card
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
        self.bot_label = Label(text="BOTS: 40", color=CYAN, size_hint_x=0.3); self.bot_slider = Slider(min=1, max=100, value=40, step=1, size_hint_x=0.7)
        self.bot_slider.bind(value=lambda i, v: setattr(self.bot_label, 'text', f"BOTS: {int(v)}"))
        bot_row.add_widget(self.bot_label); bot_row.add_widget(self.bot_slider)
        cfg_card.add_widget(m_row); cfg_card.add_widget(self.file_spinner); cfg_card.add_widget(self.random_count); cfg_card.add_widget(delay_row); cfg_card.add_widget(bot_row); self.box.add_widget(cfg_card)
        
        # Proxy Card
        proxy_card = StyledCard(orientation="horizontal", size_hint_y=None, height=70, padding=10, spacing=10)
        self.proxy_source = StyledSpinner(text="FILE", values=("FILE", "FREE (ProxyScrape)"), size_hint_x=0.35)
        self.proxy_spinner = StyledSpinner(text="SELECT PROXY", values=self.load_proxies(), size_hint_x=0.35)
        self.proxy_toggle_btn = StyledButton(text="PROXY: OFF", size_hint_x=0.3, color=RED, on_press=self.toggle_proxy)
        proxy_card.add_widget(self.proxy_source); proxy_card.add_widget(self.proxy_spinner); proxy_card.add_widget(self.proxy_toggle_btn); self.box.add_widget(proxy_card)
        
        # Progress & Log
        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20, color=CYAN)
        self.pbar = ProgressBar(max=100, value=0, size_hint_y=None, height=10)
        self.box.add_widget(self.progress_label); self.box.add_widget(self.pbar)
        
        self.scroll = ScrollView()
        self.log_display = Label(text="Ready...", font_size="14sp", size_hint_y=None, markup=True, halign="left", valign="top")
        self.log_display.bind(size=self.log_display.setter("text_size"))
        self.scroll.add_widget(self.log_display)
        self.box.add_widget(self.scroll)
        
        # Bottom Buttons
        btn_box = BoxLayout(size_hint_y=None, height=110, spacing=15)
        self.start_btn = StyledButton(text="START MAC ULTRA", on_press=self.toggle, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN, size_hint_x=0.7)
        self.stop_music_btn = StyledButton(text="STOP MUSIC", on_press=self.stop_audio, bg_color=(0.15, 0.05, 0.05, 1), color=RED, size_hint_x=0.3)
        btn_box.add_widget(self.start_btn); btn_box.add_widget(self.stop_music_btn)
        self.box.add_widget(btn_box)
        
        self.add_widget(self.box)

    # --- Logik & Log System ---

    def update_log_safe(self, t):
        Clock.schedule_once(lambda dt: self._do_log(t))

    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 10:
            self.hit_list.pop(0)
        self.log_display.text = "\n".join(self.hit_list)
        self.log_display.height = self.log_display.texture_size[1] + 20

    def get_clean_time(self, raw):
        raw_str = str(raw).strip()
        if raw_str.isdigit() and len(raw_str) >= 9:
            try:
                dt = datetime.fromtimestamp(int(raw_str))
                days_diff = (dt - datetime.now()).days
                return dt.strftime('%d.%m.%Y'), f"{days_diff} Tage"
            except: pass
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
                except: continue
        except: pass
        return raw_str, "Unlimited"

    def create_stat_box(self, p, t, v, c):
        box = StyledCard(orientation="vertical", padding=8); box.add_widget(Label(text=t, font_size="11sp", color=(0.7,0.7,0.7,1))); lbl = Label(text=v, font_size="24sp", bold=True, color=c)
        box.add_widget(lbl); p.add_widget(box); return lbl

    def load_combos(self): return sorted([f for f in os.listdir("/sdcard/Combo/") if f.endswith(".txt")]) if os.path.exists("/sdcard/Combo/") else ["NO COMBOS"]
    def load_proxies(self): return sorted([f for f in os.listdir("/storage/emulated/0/proxies/") if f.endswith(".txt")]) if os.path.exists("/storage/emulated/0/proxies/") else ["NO PROXIES"]
    def load_portal_lists(self): return sorted([f for f in os.listdir("/storage/emulated/0/Portals/") if f.endswith(".txt")]) if os.path.exists("/storage/emulated/0/Portals/") else ["USE SINGLE"]
    def update_slider_label(self, i, v): self.detail_status.text, self.detail_status.color = ("ALLES SPEICHERN", GREEN) if v == 1 else ("NUR MAC/URL", RED)

    def toggle_proxy(self, btn):
        self.use_proxies = not self.use_proxies
        if self.use_proxies: btn.text, btn.color, btn.bg_color_inst.rgba = "PROXY: ON", GREEN, (0.05, 0.15, 0.1, 1)
        else: btn.text, btn.color, btn.bg_color_inst.rgba = "PROXY: OFF", RED, (0.15, 0.05, 0.05, 1)

    def play_audio(self):
        if HAS_JNIUS:
            try:
                path = self.context["paths"]["mp3"]
                mPlayer.reset(); mPlayer.setDataSource(path); mPlayer.prepare(); mPlayer.start()
            except: pass

    def stop_audio(self, *a):
        if HAS_JNIUS:
            try: mPlayer.stop()
            except: pass

    def toggle(self, *_):
        if not self.running:
            self.running = True; self.play_audio()
            self.start_btn.text, self.start_btn.color = "STOP MAC ULTRA", RED
            self.start_btn.bg_color_inst.rgba = (0.15, 0.05, 0.05, 1)
            Thread(target=lambda: asyncio.run(self.run_engine()), daemon=True).start()
        else:
            self.running = False
            self.update_log_safe("[color=FF0000]!!! MAC ULTRA STOPPED !!![/color]")
            self.reset_start_btn()

    def reset_start_btn(self):
        self.start_btn.text, self.start_btn.color = "START MAC ULTRA", GREEN
        self.start_btn.bg_color_inst.rgba = (0.05, 0.15, 0.1, 1)

    async def run_engine(self):
        # Combo laden
        path = f"/sdcard/Combo/{self.file_spinner.text}"
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                self.combo_data = [l.strip() for l in f if l.strip()]
            self.total_lines = len(self.combo_data)
        except Exception as e:
            self.update_log_safe(f"[color=FF0000][ERROR] Combo File error: {e}[/color]")
            self.running = False; Clock.schedule_once(lambda dt: self.reset_start_btn()); return

        self.checked = 0; self.hits = 0; self.start_time = time.time()
        Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))
        
        p_name = self.portal_input.text.split("//")[-1].split(":")[0]
        self.update_log_safe(f"[color=00FFFF][SCAN][/color] Starting Scan on {p_name} | {self.total_lines} Items")
        
        for mac in self.combo_data:
            if not self.running: break
            
            await asyncio.sleep(self.delay_slider.value)
            self.checked += 1
            
            # Beispielhafter Hit-Check (Simuliert, hier käme dein httpx Request rein)
            if random.random() > 0.995:
                self.hits += 1
                # Simuliere Expire Datum (Normalerweise aus API Response)
                fake_expire = "1750000000" # Beispiel Timestamp
                date_str, days = self.get_clean_time(fake_expire)
                
                self.update_log_safe(
                    f"[color=808080][{p_name}][/color] "
                    f"[color=00FF80][HIT][/color] "
                    f"{mac} | [color=00FFFF]{days}[/color]"
                )
            
            if self.checked % 5 == 0:
                Clock.schedule_once(lambda dt: self.refresh_ui())

        self.running = False
        self.update_log_safe("[color=00FFFF][INFO][/color] Scan Finished.")
        Clock.schedule_once(lambda dt: self.reset_start_btn())

    def refresh_ui(self, *a):
        self.pbar.value, self.hit_count_label.text = self.checked, str(self.hits)
        self.progress_label.text = f"PROGRESS: {self.checked} / {self.total_lines}"
        el = time.time() - self.start_time
        if el > 0: self.cpm_label.text = str(int((self.checked / el) * 60))

# --- Entry Point ---

def create_app_screen(context):
    return MagUltraScreen(context=context, name="main")
