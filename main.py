import tkinter as tk
import sqlite3
import random
from tkinter import messagebox

# ---------- Database ----------
database_connection = sqlite3.connect("user.db")
database_cursor = database_connection.cursor()
database_cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT UNIQUE,
        score INTEGER DEFAULT 0,
        box_color TEXT DEFAULT 'red'
    )
''')
database_connection.commit()

# ---------- Globals ----------
current_player_name = ""
current_box_color = "red"
current_score = 0
seconds_left = 30

game_box = None
timer_label = None
score_display = None
highscore_display = None
final_message_label = None

app_window = tk.Tk()
app_window.title("Tap Game")
app_window.geometry("400x600")
app_window.configure(bg="black")

# ---------- Helpers ----------
def safe_destroy(widget):
    try:
        widget.destroy()
    except Exception:
        pass

def get_last_username():
    database_cursor.execute("SELECT player_name FROM user ORDER BY id DESC LIMIT 1")
    result = database_cursor.fetchone()
    return result[0] if result else ""

# ---------- Menu ----------
def show_menu(prefill_name=None):
    for widget in app_window.winfo_children():
        safe_destroy(widget)

    title_label = tk.Label(app_window, text="USERNAME:", font=("Arial", 20), fg="white", bg="black")
    title_label.place(relx=0.5, rely=0.25, anchor="center")

    global username_input
    username_input = tk.Entry(app_window, font=("Arial", 18))
    username_input.place(relx=0.5, rely=0.35, anchor="center", width=240)

    if prefill_name:
        username_input.insert(0, prefill_name)
    else:
        last_name = get_last_username()
        if last_name:
            username_input.insert(0, last_name)

    play_button = tk.Button(app_window, text="PLAY", font=("Arial", 18, "bold"),
                            bg="green", fg="white", command=start_game_from_menu)
    play_button.place(relx=0.5, rely=0.50, anchor="center", width=200, height=48)

    settings_button = tk.Button(app_window, text="SETTINGS", font=("Arial", 14),
                                bg="gray30", fg="white", command=lambda: show_settings(prefill=username_input.get().strip()))
    settings_button.place(relx=0.5, rely=0.62, anchor="center", width=200, height=40)

# ---------- Settings ----------
def show_settings(prefill=None):
    for widget in app_window.winfo_children():
        safe_destroy(widget)

    tk.Label(app_window, text="SETTINGS", font=("Arial", 22), fg="white", bg="black").place(relx=0.5, rely=0.18, anchor="center")

    tk.Label(app_window, text="Username (to save):", font=("Arial", 12), fg="white", bg="black").place(relx=0.5, rely=0.30, anchor="center")
    username_entry = tk.Entry(app_window, font=("Arial", 16))
    username_entry.place(relx=0.5, rely=0.36, anchor="center", width=260)
    if prefill:
        username_entry.insert(0, prefill)

    tk.Label(app_window, text="Box color (name or #hex):", font=("Arial", 12), fg="white", bg="black").place(relx=0.5, rely=0.45, anchor="center")
    color_entry = tk.Entry(app_window, font=("Arial", 16))
    color_entry.place(relx=0.5, rely=0.51, anchor="center", width=260)
    color_entry.insert(0, current_box_color)

    def save_and_back():
        name = username_entry.get().strip()
        color = color_entry.get().strip() or "red"
        if not name:
            messagebox.showwarning("Warning", "Please enter a username to save settings.")
            return
        try:
            test_label = tk.Label(app_window, bg=color)
            test_label.destroy()
        except tk.TclError:
            messagebox.showwarning("Warning", "Invalid color name/hex.")
            return
        database_cursor.execute("SELECT score FROM user WHERE player_name=?", (name,))
        result = database_cursor.fetchone()
        if result:
            database_cursor.execute("UPDATE user SET box_color=? WHERE player_name=?", (color, name))
        else:
            database_cursor.execute("INSERT INTO user (player_name, score, box_color) VALUES (?, ?, ?)", (name, 0, color))
        database_connection.commit()
        show_menu(prefill_name=name)

    tk.Button(app_window, text="SAVE", bg="green", fg="white", font=("Arial", 14), command=save_and_back).place(relx=0.5, rely=0.68, anchor="center", width=160, height=40)
    tk.Button(app_window, text="BACK", bg="gray30", fg="white", font=("Arial", 12), command=lambda: show_menu(prefill_name=username_entry.get().strip())).place(relx=0.5, rely=0.78, anchor="center", width=160, height=36)

# ---------- Game start helpers ----------
def start_game_from_menu():
    name = username_input.get().strip()
    begin_game_for(name)

def begin_game_for(name):
    global current_player_name, current_box_color, current_score, seconds_left, game_box
    if not name:
        messagebox.showwarning("Warning", "Please enter a username.")
        return
    current_player_name = name

    database_cursor.execute("SELECT score, box_color FROM user WHERE player_name=?", (current_player_name,))
    result = database_cursor.fetchone()
    if result:
        saved_highscore, saved_color = result
        if saved_color:
            current_box_color = saved_color
        saved_highscore = saved_highscore if saved_highscore is not None else 0
    else:
        saved_highscore = 0
        database_cursor.execute("INSERT OR IGNORE INTO user (player_name, score, box_color) VALUES (?, ?, ?)", (current_player_name, 0, current_box_color))
        database_connection.commit()

    for widget in app_window.winfo_children():
        safe_destroy(widget)

    global timer_label, highscore_display, score_display
    timer_label = tk.Label(app_window, text=f"Time: {seconds_left}", font=("Arial", 18), fg="white", bg="black")
    timer_label.place(relx=0.05, rely=0.05, anchor="w")

    highscore_display = tk.Label(app_window, text=f"Highscore: {saved_highscore}", font=("Arial", 18, "bold"), fg="yellow", bg="black")
    highscore_display.place(relx=0.5, rely=0.07, anchor="n")

    score_display = tk.Label(app_window, text=f"Score: 0", font=("Arial", 18), fg="white", bg="black")
    score_display.place(relx=0.95, rely=0.05, anchor="e")

    current_score = 0
    seconds_left = 30

    game_box = tk.Button(app_window, bg=current_box_color, activebackground="darkred", bd=0, command=on_box_click)
    game_box.place(relx=0.5, rely=0.55, anchor="center", width=70, height=70)

    update_timer_display()
    app_window.after(1000, game_tick)

# ---------- Game actions ----------
def on_box_click():
    global current_score
    if seconds_left <= 0:
        return
    current_score += 1
    score_display.config(text=f"Score: {current_score}")
    move_game_box()

def move_game_box():
    x = random.uniform(0.15, 0.85)
    y = random.uniform(0.25, 0.85)
    game_box.place(relx=x, rely=y, anchor="center")

def update_timer_display():
    timer_label.config(text=f"Time: {seconds_left}")
    score_display.config(text=f"Score: {current_score}")

def game_tick():
    global seconds_left
    if seconds_left > 0:
        seconds_left -= 1
        update_timer_display()
        app_window.after(1000, game_tick)
    else:
        finish_game()

# ---------- End game ----------
def finish_game():
    global final_message_label
    safe_destroy(game_box)
    safe_destroy(timer_label)
    safe_destroy(score_display)
    safe_destroy(highscore_display)

    database_cursor.execute("SELECT score FROM user WHERE player_name=?", (current_player_name,))
    result = database_cursor.fetchone()
    previous_highscore = result[0] if result and result[0] is not None else 0
    if current_score > previous_highscore:
        database_cursor.execute("UPDATE user SET score=?, box_color=? WHERE player_name=?", (current_score, current_box_color, current_player_name))
        database_connection.commit()
        message = f"New Highscore: {current_score}!"
    else:
        message = f"Final Score: {current_score}"

    final_message_label = tk.Label(app_window, text=message, font=("Arial", 28, "bold"), fg="white", bg="black")
    final_message_label.place(relx=0.5, rely=0.28, anchor="center")

    tk.Button(app_window, text="MENU", bg="blue", fg="white", font=("Arial", 16), command=lambda: show_menu(prefill_name=current_player_name)).place(relx=0.5, rely=0.52, anchor="center", width=200, height=42)
    tk.Button(app_window, text="RESTART", bg="green", fg="white", font=("Arial", 16), command=lambda: begin_game_for(current_player_name)).place(relx=0.5, rely=0.64, anchor="center", width=200, height=42)
    tk.Button(app_window, text="SETTINGS", bg="orange", fg="white", font=("Arial", 16), command=lambda: show_settings(prefill=current_player_name)).place(relx=0.5, rely=0.76, anchor="center", width=200, height=42)

# ---------- Start ----------
show_menu()

def on_close():
    try:
        database_connection.close()
    except Exception:
        pass
    app_window.destroy()

app_window.protocol("WM_DELETE_WINDOW", on_close)
app_window.mainloop()
