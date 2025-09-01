import tkinter as tk

root = tk.Tk()
root.title("Tap Game")
root.geometry("400x600")
root.configure(bg="black")

# Countdown and score labels
countdown_label = tk.Label(root, text="Time: 30", font=("Arial", 20), fg="white", bg="black")
countdown_label.pack(side="left", anchor="n", padx=10, pady=10)

score_label = tk.Label(root, text="Score: 0", font=("Arial", 20), fg="white", bg="black")
score_label.pack(side="right", anchor="n", padx=10, pady=10)

# Game variables
score = 0
time_left = 30
counter = 1

# Button size
btn_width = 6
btn_height = 3

# Function to move button safely
def move_button():
    global score, counter
    if time_left <= 0:  # stop game
        return

    score += 1
    score_label.config(text=f"Score: {score}")

    # pseudo-random position
    x = (counter * 37) % 100 / 100
    y = (counter * 53) % 100 / 100
    counter += 1

    # clamp so button stays visible
    if x < 0.15: x = 0.15
    if x > 0.85: x = 0.85
    if y < 0.2: y = 0.2
    if y > 0.9: y = 0.9

    button.place(relx=x, rely=y, anchor="center")

# Countdown timer function
def update_timer():
    global time_left
    if time_left > 0:
        time_left -= 1
        countdown_label.config(text=f"Time: {time_left}")
        root.after(1000, update_timer)  # call again in 1 second
    else:
        end_game()

# End game function
def end_game():
    button.destroy()          # remove the button
    countdown_label.destroy() # remove the timer
    score_label.destroy()     # remove the top-right score label

    final_score = tk.Label(root, text=f"Final Score: {score}",
                           font=("Arial", 40, "bold"), fg="white", bg="black")
    final_score.place(relx=0.5, rely=0.5, anchor="center")

# Square button
button = tk.Button(root, text="", bg="red", activebackground="darkred",
                   width=btn_width, height=btn_height, borderwidth=0,
                   command=move_button)
button.place(relx=0.5, rely=0.5, anchor="center")

# Start countdown
update_timer()

root.mainloop()
