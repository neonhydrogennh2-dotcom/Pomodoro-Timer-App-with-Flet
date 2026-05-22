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
        self.total_seconds = 25
        self.time_start = None 
        self.paused_at = 0
        self.paused_total = None 
        self.today_date = datetime.date.today().isoformat()
        self.session = self.db.get_today_count(self.today_date)

        
    def start(self):
        if self.state == "stopped":
            self.time_start = time.time()
            self.paused_at = None 
            self.paused_total = 0
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

    def remaining_seconds(self):
        if self.state == "stopped":
            return self.total_seconds
        
        now = time.time()

        if self.state == "paused":
            now = self.paused_at
        
        elapsed = now - self.time_start - self.paused_total #elapsed = time passed 
        return max(0,int(self.total_seconds - elapsed)) #0 prevents negative values 
    
    def stop(self):
        if self.state in ("running","paused"):
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
        self.db.insert_session(self.today_date)
        self.session = self.db.get_today_count(self.today_date)

    def check_completion(self):
        if self.state == "running" and self.remaining_seconds() == 0:
            self.completed_session()
            return True 
        return False 
            

    def formatted_time(self):
        seconds = self.remaining_seconds()
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

def app(page: ft.Page):
    page.title = "Celestial Pomodoro"
    Heading = ft.Text(value="Celestial Pomodoro", size=12,
    text_align=ft.TextAlign.CENTER, font_family="Arial") 
    page.horizontal_alignment = "center"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.window.width = 550 
    page.window.height = 600
    page.padding = 10 
    page.bgcolor = "#161B36"
    main = Pomodoro()

    timer_text = ft.Text(
        value="00:25",
        size=45,
        text_align=ft.TextAlign.CENTER,
        font_family="Arial"
    )

    status_text = ft.Text(
        value=f"Your Sessions: {main.session}",
        size=12,
        text_align=ft.TextAlign.CENTER,
        font_family="Arial"
    )

    async def tick():
        while True:
            timer_text.value = main.formatted_time()

            if main.check_completion():
                status_text.value = f"Your Sessions: {main.session}"
                
            page.update()
            await asyncio.sleep(1)

    page.run_task(tick)

    def start_handler(e):
        main.start()
        page.update()

    #Timer Section

    page.add(
        ft.Column(
        [
        Heading,
        timer_text,
        status_text,
        ], 
        alignment=ft.MainAxisAlignment.CENTER, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True, 
        spacing=2
        )
    )

    #Button rows 

    page.add(
        ft.Row([
            ft.Button("Start", on_click=start_handler, 
            height=40,
            width=100,  
            style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=25),
            bgcolor="#35475F")),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=1,
        ),

    )

    page.add(
        ft.Row([
            ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                    icon_size=20, 
                    tooltip="Resume",
                    on_click=lambda e: main.resume(),
                    style = ft.ButtonStyle(
                        color= "#0B1026",
                        bgcolor="#35475F"
                    )),
            ft.Button("Start", on_click=start_handler, 
                      height=40, 
                      style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25), bgcolor="#35475F")),
            ft.Button("Pause", on_click=lambda e: main.pause(), 
                      height=40, 
                      style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25), bgcolor="#35475F")),
            ft.IconButton(
                    icon=ft.Icons.STOP,
                    icon_size=20, 
                    tooltip="Cancel",
                    on_click=lambda e: main.stop(),
                    style = ft.ButtonStyle(
                        color= "#0B1026",
                        bgcolor="#35475F"
                    )),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        expand= True, 
        ),
    )

ft.run(app)




