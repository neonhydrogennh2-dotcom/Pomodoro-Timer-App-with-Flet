# Pomodoro-Timer-App-with-Flet

A minimalist Pomodoro timer built with Python and Flet.

The app focuses on fast performance, clean UI, and lightweight visual feedback instead of heavy animations or gamified systems.

Each completed Pomodoro session contributes to a growing starfield, creating a calm sense of progress over time.

---

## Features

- 25-minute Pomodoro timer
- Start, pause, resume, and reset controls
- SQLite session storage
- Daily session tracking
- Persistent focus history
- Lightweight architecture
- Cross-platform support via Flet

---

## Tech Stack

- Python
- Flet
- SQLite

---

## How It Works

### Timer System

The timer uses an asynchronous countdown loop built with Flet and asyncio.

When a Pomodoro session is completed:
1. The session is recorded in SQLite
2. The daily session counter updates
3. The visual feedback system reacts (planned feature)

---

## Database

SQLite is used for local persistence.

Current stored data includes:
- Session timestamps
- Session dates
- Daily session counts

---

## Planned Features

- Starfield visual feedback system
- Constellation unlocks
- Mini solar systems
- Galaxy progression
- Pan and zoom controls
- Lightweight animations

---

## Installation

Clone the repository:

```bash
git clone https://github.com/neonhydrogennh2-dotcom/Pomodoro-Timer-App-with-Flet.git
cd cosmic-pomodoro
```

Install dependencies:

```bash
pip install flet
```

Run the app:

```bash
python app.py
```

---

## Design Goals

This project intentionally avoids heavy graphics and complex animation systems.

The focus is:
- responsiveness
- simplicity
- calm visual feedback
- low system requirements
- maintainable architecture

---

## License

MIT License



