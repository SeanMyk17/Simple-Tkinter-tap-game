import tkinter as tk
import sqlite3
from tkinter import messagebox

player_name = ""
counter = 1
box_color = "red"  # CHANGED: set safe default color

# Database setup
conn = sqlite3.connect("user.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT UNIQUE,
        score INTEGER,
        box_color TEXT
    )
''')
conn.commit()

root = tk.Tk()
root.title("Tap Game")
root.geometry("400x600")
root.configure(bg="black")


# CHANGED: helper to safely destroy widgets that may not exist
def safe_destroy_widget(widget):
    try:
        widget.destroy()
    except Exception:
        pass


# CHANGED: validate color by trying to create a temporary widget
def is_valid_color(color_str):
    try:
        tmp = tk.Label(root, bg=color_str)
        tmp.destroy()
        return True
    except tk.TclError:
        return False


def game_menu():
    global username_label, username_entry, play_button, settings_button
    for w in root.winfo_children():
        w.destroy()

    username_label = tk.Label(root, text="USERNAME:", font=("Arial", 20), fg="white", bg="black")
    username_entry = tk.Entry(root, font=("Arial", 20))
    play_button = tk.Button(root, text="PLAY", bg="green", fg="white", font=("Arial", 20, "bold"),
                            command=start_game)
    settings_button = tk.Button(root, text="SETTINGS", bg="green", fg="white", font=("Arial", 20, "bold"),
                                command=game_settings)

    username_label.place(relx=0.5, rely=0.3, anchor="center")
    username_entry.place(relx=0.5, rely=0.4, anchor="center")
    play_button.place(relx=0.5, rely=0.5, anchor="center")
    settings_button.place(relx=0.5, rely=0.6, anchor="center")


def game_settings():
    global color_entry, save_color_button, cancel_button
    for w in root.winfo_children():
        w.destroy()
    box_label = tk.Label(root, text="BOX COLOR (e.g. red or #ff0000):", font=("Arial", 14), fg="white", bg="black")
    color_entry = tk.Entry(root, font=("Arial", 16))
    save_color_button = tk.Button(root, text="SAVE", bg="green", fg="white", font=("Arial", 16, "bold"),
                                  command=save_settings)
    cancel_button = tk.Button(root, text="CANCEL", bg="gray", fg="white", font=("Arial", 12),
                              command=game_menu)

    box_label.place(relx=0.5, rely=0.3, anchor="center")
    color_entry.place(relx=0.5, rely=0.4, anchor="center")
    save_color_button.place(relx=0.5, rely=0.5, anchor="center")
    cancel_button.place(relx=0.5, rely=0.6, anchor="center")


def save_settings():
    global box_color
    val = color_entry.get().strip()
    if not val:
        messagebox.showwarning("Warning", "Please enter a color name or hex code.")
        return
    if not is_valid_color(val):
        messagebox.showwarning("Warning", f"'{val}' is not a valid color.")
        return
    box_color = val  # CHANGED: apply chosen color
    game_menu()


def start_game():
    global player_name, countdown_label, score_label, highscore_label, button, score, time_left
    entered = username_entry.get().strip()
    if not entered:
        messagebox.showwarning("Warning", "Please enter a username.")
        return
    player_name = entered

    safe_destroy_widget(username_label)
    safe_destroy_widget(username_entry)
    safe_destroy_widget(play_button)
    safe_destroy_widget(settings_button)

    cursor.execute("SELECT score FROM user WHERE player_name=?", (player_name,))
    row = cursor.fetchone()
    highscore = row[0] if row and row[0] is not None else 0

    highscore_label = tk.Label(root, text=f"Highscore: {highscore}", font=("Arial", 20), fg="yellow", bg="black")
    highscore_label.pack(side="top", pady=10)

    countdown_label = tk.Label(root, text="Time: 30", font=("Arial", 20), fg="white", bg="black")
    countdown_label.pack(side="left", anchor="n", padx=10, pady=10)

    score_label = tk.Label(root, text="Score: 0", font=("Arial", 20), fg="white", bg="black")
    score_label.pack(side="right", anchor="n", padx=10, pady=10)

    score = 0
    time_left = 30

    btn_width = 6
    btn_height = 3

    # CHANGED: use validated box_color (safe default set above)
    button = tk.Button(root, text="", bg=box_color, activebackground="darkred",
                       width=btn_width, height=btn_height, borderwidth=0,
                       command=move_button)
    button.place(relx=0.5, rely=0.5, anchor="center")

    update_timer()


def move_button():
    global score, counter
    if time_left <= 0:
        return

    score += 1
    score_label.config(text=f"Score: {score}")

    width = root.winfo_width() or 400
    height = root.winfo_height() or 600

    x_rel = ((counter * 37) % max(1, width - 60)) / width
    y_rel = ((counter * 53) % max(1, height - 120)) / height
    counter += 1

    if x_rel < 0.12: x_rel = 0.12
    if x_rel > 0.88: x_rel = 0.88
    if y_rel < 0.18: y_rel = 0.18
    if y_rel > 0.82: y_rel = 0.82

    button.place(relx=x_rel, rely=y_rel, anchor="center")


def update_timer():
    global time_left
    if time_left > 0:
        time_left -= 1
        countdown_label.config(text=f"Time: {time_left}")
        root.after(1000, update_timer)
    else:
        end_game()


def end_game():
    safe_destroy_widget(button)
    safe_destroy_widget(countdown_label)
    safe_destroy_widget(score_label)
    safe_destroy_widget(highscore_label)

    cursor.execute("SELECT score FROM user WHERE player_name=?", (player_name,))
    row = cursor.fetchone()
    current_high = row[0] if row and row[0] is not None else 0

    if score > current_high:
        if row:
            cursor.execute("UPDATE user SET score=?, box_color=? WHERE player_name=?", (score, box_color, player_name))
        else:
            cursor.execute("INSERT INTO user (player_name, score, box_color) VALUES (?, ?, ?)",
                           (player_name, score, box_color))
        conn.commit()
        message = f"New Highscore: {score}!"
    else:
        message = f"Final Score: {score}"

    final_score = tk.Label(root, text=message, font=("Arial", 32, "bold"), fg="white", bg="black")
    final_score.place(relx=0.5, rely=0.45, anchor="center")

    def back_to_menu():
        safe_destroy_widget(final_score)
        safe_destroy_widget(back_btn)
        game_menu()

    back_btn = tk.Button(root, text="MAIN MENU", bg="green", fg="white", font=("Arial", 14, "bold"),
                         command=back_to_menu)
    back_btn.place(relx=0.5, rely=0.6, anchor="center")


# CHANGED: ensure DB closes cleanly on app exit
def on_app_close():
    try:
        conn.close()
    except Exception:
        pass
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_app_close)

# start
game_menu()
root.mainloop()
