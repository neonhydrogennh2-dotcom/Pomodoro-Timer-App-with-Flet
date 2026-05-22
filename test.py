import time 
import datetime 
import flet as ft 
import asyncio 
import sqlite3


class Database():
    def __init__(self):
        self.conn = sqlite3.connect("celestial.db", check_same_thread=False)
        self.create_table()
        
    def create_table(self):
        today_date = datetime.date.today().isoformat()
        c = self.conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT , 
        completed_at REAL NOT NULL, 
        date TEXT NOT NULL)""")

        self.conn.commit()

    def insert_session(self, date):
        c = self.conn.cursor()
        completed_at = time.time()
        c.execute("""INSERT INTO sessions (completed_at, date)
        VALUES (?,?)""", (completed_at, date)
        )
        self.conn.commit()

    def get_today_count(self, date):
        c = self.conn.cursor()
        c.execute(""" SELECT COUNT (*) FROM sessions WHERE date = ?""", (date,))

        return c.fetchone()[0]
    
    def close(self):
        self.conn.close()
    

class Pomodoro():
    def __init__(self):
        self.db = Database()
        self.state = "stopped"
        self.mode = "work" # "work" | "break"
        self.break_minutes = 1     # by default 
        self.duration_minutes = 25  # by default 
        self.total_seconds = self.duration_minutes * 60
        self.time_start = None 
        self.paused_at = 0
        self.paused_total = 0
        self.today_date = datetime.date.today().isoformat()
        self.session = self.db.get_today_count(self.today_date)
        self.remaining_seconds = self.total_seconds


        
    def start(self):
        if self.state == "stopped":
            self.time_start = time.time()
            self.paused_at = None 
            self.paused_total = 0
            self.total_seconds = self.remaining_seconds
            self.state = "running"

    def pause(self):
        if self.state == "running":
            self.paused_at = time.time()
            self.state = "paused"
    
    def resume(self):
        if self.state == "paused":
            self.paused_total += time.time() - self.paused_at # paused total means amount of time it was paused for
            self.paused_at = None 
            self.state = "running"

    def get_remaining_seconds(self):
        if self.state == "stopped":
            return self.remaining_seconds
        
        now = time.time()

        if self.state == "paused":
            now = self.paused_at
        
        elapsed = now - self.time_start - self.paused_total #elapsed = time passed 
        return max(0,int(self.total_seconds - elapsed)) #0 prevents negative values 
    
    def stop(self):
        if self.state in ("running","paused"):
            self.total_seconds = self.duration_minutes * 60
            self.remaining_seconds = self.total_seconds

            self.state = "stopped"
            self.time_start = None 
            self.paused_at = None
            self.paused_total = 0

    def completed_session(self):
        if self.state != "running":
            return 
        
        self.state = "stopped"
        #self.session += 1 
        self.time_start = None
        self.paused_at = None 
        self.paused_total = 0 
        #self.db.insert_session(self.today_date)
        #self.session = self.db.get_today_count(self.today_date)

    def check_completion(self):
        if self.state == "running" and self.get_remaining_seconds() == 0:
            self.on_complete()
            return True 
        return False 
            

    def formatted_time(self):
        seconds = self.get_remaining_seconds()
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"
    
    def on_complete(self):
        self.state = "stopped"
        self.time_start = None
        self.paused_at = None
        self.paused_total = 0

        if self.mode == "work":
            # Count session ONLY after work finishes
            self.db.insert_session(self.today_date)
            self.session = self.db.get_today_count(self.today_date)

            self.mode = "break"
        else:
            # Break finished → start work again
            self.mode = "work"

    def start_break(self):
        self.mode = "break"
        self.total_seconds = self.break_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.time_start = time.time()
        self.paused_total = 0
        self.state = "running"

    def start_work(self):
        self.mode = "work"
        self.total_seconds = self.duration_minutes * 60
        self.remaining_seconds = self.total_seconds
        self.time_start = time.time()
        self.paused_total = 0
        self.state = "running"


    
def app(page: ft.Page):
    page.title = "Celestial Pomodoro"
    page.horizontal_alignment = "center"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.window.width = 550 
    page.window.height = 600
    page.padding = 0
    page.bgcolor = "#161B36"
    page.fonts = {
    "Orbitron": "assets/Orbitron-Regular.ttf"
    }
    page.theme = ft.Theme(
    font_family="Orbitron"
    )
    start_sound = page.play_audio(src="sounds/start.mp3", autoplay=False)
    stop_sound = ft.Audio(src="sounds/stop.mp3", autoplay=False)
    end_sound = ft.Audio(src="sounds/completed.mp3", autoplay=False)

    page.overlay.extend([start_sound, stop_sound, end_sound])


    main = Pomodoro()

    Heading = ft.Text(value="Celestial Pomodoro", size=16,
    text_align=ft.TextAlign.CENTER, font_family="Orbitron") 

    timer_text = ft.Text(
        value="00:25",
        size=60,
        text_align=ft.TextAlign.CENTER,
        font_family="Orbitron"
    )

    status_text = ft.Text(
        value=f"Your Sessions: {main.session}",
        size=14,
        text_align=ft.TextAlign.CENTER,
        font_family="Orbitron"
    )

    async def tick():
        last_mode = main.mode

        while True:
            timer_text.value = main.formatted_time()

            if main.check_completion():
                end_sound.play()
                status_text.value = f"Your Sessions: {main.session}"

                if last_mode == "work" and main.mode == "break":
                    show_alert("Work session completed! Break started 💤")
                    page.play("")
                    main.start_break()

                elif last_mode == "break" and main.mode == "work":
                    show_alert("Break finished! Back to work 🚀")
                    end_sound.play("sounds/completed.mp3")
                    main.start_work()

                last_mode = main.mode
                mode_text.value = main.mode.upper()
                
            page.update()
            await asyncio.sleep(1)

    page.run_task(tick)

    def start_handler(e):
        main.start()
        page.play_audio("sounds/start.mp3")
        page.update()

    def stop_handler(e):
        main.stop()
        page.play_audio("sounds/stop.mp3")
        page.update()

    def on_duration_change(e):
        minutes = int(e.control.value)
        main.duration_minutes = minutes

        if main.state == "stopped" and main.mode == "work":
            main.total_seconds = minutes * 60
            main.remaining_seconds = main.total_seconds
            timer_text.value = f"{minutes:02d}:00"
            page.update()

    def show_alert(message):
        page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor="#1A237E",
        duration=3000,
        )
        page.snack_bar.open = True
        page.update()

    mode_text = ft.Text(
    value="WORK",
    size=12,
    color="#00E5FF"
    )


    start_btn_row=ft.Row([
            ft.Button("Start", on_click=start_handler, 
            height=50,
            width=100, 
            style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=15),
            color="#E0E0E0",
            bgcolor="#1A237E")),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        #expand=True
        )

    button_row=ft.Row([
            ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                    icon_size=30, 
                    tooltip="Resume",
                    on_click=lambda e: main.resume(),
                    style = ft.ButtonStyle(
                        color= "#0B1026",
                        bgcolor="#00E5FF"
                    )),
            ft.IconButton(
                    icon=ft.Icons.PAUSE,
                    icon_size=30, 
                    tooltip="Pause",
                    on_click=lambda e: main.pause(),
                    style = ft.ButtonStyle(
                        color= "#0B1026",
                        bgcolor="#00E5FF"
                    )),
            ft.IconButton(
                    icon=ft.Icons.STOP,
                    icon_size=30, 
                    tooltip="Cancel",
                    on_click=lambda e: stop_handler,
                    style = ft.ButtonStyle(
                        color= "#0B1026",
                        bgcolor="#00E5FF"
                    )),
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        #expand=True
        )
    
    duration_slider = ft.Slider(
        min=1,
        max=120,
        divisions=23,  
        value=25,
        label="{value} min",
        #on_change=on_duration_change, 
        )
    
    duration_slider.on_change = on_duration_change

    slider_container = ft.Container(
    content=duration_slider,
    width=310,              #For the adjusting the width of the slider 
    alignment=ft.Alignment.CENTER,
    )
    #Layout Section

    page.add(
        ft.Stack(
            expand=True,
            controls=[
                # 1. Background (Fills everything)
                ft.Image(
                    src="background.png",
                    fit=ft.BoxFit.COVER,
                    expand=True,
                    width=550,
                    height=600,
                ),
                
                # 2. UI Layer
                ft.Container(
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN, # Pushes content apart
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            # Top Padding/Spacer
                            ft.Container(height=40),
                            
                            # Center Group (Timer)
                            ft.Column(
                                [Heading, timer_text, slider_container, status_text, mode_text],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            
                            # Bottom Group (Buttons)
                            ft.Container(
                                content=ft.Column(
                                    [start_btn_row, button_row],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=20,
                                ),
                                margin=ft.Margin.only(bottom=40) # Padding from bottom edge
                            ),
                        ],
                    ),
                    expand=True,
                ),
            ],
        )
    )



ft.run(app,assets_dir="assets")




