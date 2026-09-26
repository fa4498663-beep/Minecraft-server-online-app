import os, socket, subprocess, threading, time
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window

KV = '''
ScreenManager:
    WelcomeScreen:
    DashboardScreen:

<WelcomeScreen>:
    name: 'welcome'
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.12, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: 'app mader fahim'
            font_size: '28sp'
            bold: True
            color: 0.9, 0.7, 0.1, 1
            size_hint_y: 0.7
            halign: 'center'

        Button:
            text: 'ENTER'
            size_hint: (1, 0.15)
            background_color: 0.2, 0.7, 0.3, 1
            font_size: '20sp'
            bold: True
            on_release: root.manager.current = 'dashboard'

<DashboardScreen>:
    name: 'dashboard'
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10
        canvas.before:
            Color:
                rgba: 0.08, 0.08, 0.1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: 'localhost ip 24/7 server maker Minecraft'
            font_size: '14sp'
            bold: True
            color: 0.8, 0.8, 0.8, 1
            size_hint_y: 0.08

        # IP Display Card
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.3
            padding: 10
            canvas.before:
                Color:
                    rgba: 0.15, 0.15, 0.18, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10,]

            Label:
                id: bedrock_ip
                text: 'Bedrock:\nIP: Offline\nPort: 19132'
                font_size: '16sp'
                bold: True
                color: 0.3, 0.9, 0.4, 1
                halign: 'center'

            Label:
                id: java_ip
                text: 'Java:\nIP: Offline\nPort: 25565'
                font_size: '16sp'
                bold: True
                color: 0.3, 0.7, 1, 1
                halign: 'center'

        # Main Controls
        BoxLayout:
            size_hint_y: 0.12
            spacing: 10
            Button:
                id: start_btn
                text: 'START'
                background_color: 0.1, 0.8, 0.2, 1
                bold: True
                on_release: app.start_server()
            Button:
                id: stop_btn
                text: 'STOP'
                background_color: 0.9, 0.2, 0.2, 1
                bold: True
                disabled: True
                on_release: app.stop_server()
            Button:
                id: restart_btn
                text: 'RESTART'
                background_color: 0.9, 0.6, 0.1, 1
                bold: True
                disabled: True
                on_release: app.restart_server()

        # Controls & Settings
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.35
            spacing: 5
            
            Label:
                text: 'Quick Server Settings'
                font_size: '14sp'
                bold: True
                color: 1, 0.8, 0.2, 1

            BoxLayout:
                spacing: 5
                Button:
                    text: 'Gamemode: Creative'
                    on_release: app.send_command('gamemode creative @a')
                Button:
                    text: 'Gamemode: Survival'
                    on_release: app.send_command('gamemode survival @a')

            BoxLayout:
                spacing: 5
                Button:
                    text: 'Diff: Easy'
                    on_release: app.send_command('difficulty easy')
                Button:
                    text: 'Diff: Hard'
                    on_release: app.send_command('difficulty hard')

            BoxLayout:
                spacing: 5
                TextInput:
                    id: player_name
                    hint_text: 'Player Name'
                    multiline: False
                Button:
                    text: 'Ban'
                    background_color: 0.8, 0.2, 0.2, 1
                    on_release: app.ban_player()
                Button:
                    text: 'Unban'
                    background_color: 0.2, 0.6, 0.8, 1
                    on_release: app.unban_player()

        # System Info Bar
        Label:
            id: sys_info
            text: 'RAM: -- | Free Storage: --'
            size_hint_y: 0.08
            font_size: '12sp'
            color: 0.6, 0.6, 0.6, 1
'''

class WelcomeScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class MCServerApp(App):
    def build(self):
        self.process = None
        self.server_dir = "/sdcard/mc_server"
        Clock.schedule_interval(self.update_system_stats, 3)
        return Builder.load_string(KV)

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def start_server(self):
        if not os.path.exists(self.server_dir):
            os.makedirs(self.server_dir)
        
        eula_path = os.path.join(self.server_dir, "eula.txt")
        if not os.path.exists(eula_path):
            with open(eula_path, "w") as f:
                f.write("eula=true\n")

        threading.Thread(target=self._run_process, daemon=True).start()

    def _run_process(self):
        try:
            ip = self.get_local_ip()
            cmd = ["java", "-Xms1024M", "-Xmx2048M", "-jar", "server.jar", "nogui"]
            self.process = subprocess.Popen(
                cmd, cwd=self.server_dir,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True
            )
            
            # Update UI
            dash = self.root.get_screen('dashboard')
            dash.ids.bedrock_ip.text = f"Bedrock:\nIP: {ip}\nPort: 19132"
            dash.ids.java_ip.text = f"Java:\nIP: {ip}\nPort: 25565"
            dash.ids.start_btn.disabled = True
            dash.ids.stop_btn.disabled = False
            dash.ids.restart_btn.disabled = False
        except Exception as e:
            pass

    def stop_server(self):
        if self.process:
            self.send_command("stop")
            self.process = None
        
        dash = self.root.get_screen('dashboard')
        dash.ids.bedrock_ip.text = "Bedrock:\nIP: Offline\nPort: 19132"
        dash.ids.java_ip.text = "Java:\nIP: Offline\nPort: 25565"
        dash.ids.start_btn.disabled = False
        dash.ids.stop_btn.disabled = True
        dash.ids.restart_btn.disabled = True

    def restart_server(self):
        self.stop_server()
        time.sleep(2)
        self.start_server()

    def send_command(self, cmd):
        if self.process and self.process.poll() is None:
            self.process.stdin.write(f"{cmd}\n")
            self.process.stdin.flush()

    def ban_player(self):
        dash = self.root.get_screen('dashboard')
        p_name = dash.ids.player_name.text.strip()
        if p_name:
            self.send_command(f"ban {p_name}")
            dash.ids.player_name.text = ""

    def unban_player(self):
        dash = self.root.get_screen('dashboard')
        p_name = dash.ids.player_name.text.strip()
        if p_name:
            self.send_command(f"pardon {p_name}")
            dash.ids.player_name.text = ""

    def update_system_stats(self, dt):
        try:
            import psutil
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            dash = self.root.get_screen('dashboard')
            dash.ids.sys_info.text = f"RAM: {ram.used // (1024*1024)}MB / {ram.total // (1024*1024)}MB | Free Storage: {disk.free // (1024*1024*1024)}GB"
        except Exception:
            pass

if __name__ == '__main__':
    MCServerApp().run()
