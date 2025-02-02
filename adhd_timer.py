import tkinter as tk
from tkinter import ttk
import time

# Global variables to track the timer state.
total_time = 0           # Total duration in seconds.
start_time = None        # Timestamp when the current run started.
accumulated_elapsed = 0  # Elapsed time from previous runs (for pause/resume).
timer_update_id = None   # Reference to the scheduled update (for canceling).

# Colors for the grid squares:
SPENT_COLOR = "white"  # Color for occupied (elapsed) time.
LEFT_COLOR  = "black"  # Color for remaining time.

# Grid configuration.
GRID_COUNT = 20                      # Number of mini-squares per row and column.
TOTAL_SQUARES = GRID_COUNT * GRID_COUNT  # Total number of mini-squares.

# ----------------------------
# Set Up the Main Window with Modern Styling
# ----------------------------
root = tk.Tk()
root.title("ADHD Friendly Timer")
root.configure(bg="#000000")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Ubuntu", 18, "bold"),
                padding=1,
                background="#000000",
                foreground="white")
style.map("TButton",
          background=[("active", "white"), ("pressed", "black"), ("!active", "black")],
          foreground=[("active", "black"), ("pressed", "white"), ("!active", "white")])

style.configure("TEntry", font=("Ubuntu", 20,"bold"))
style.configure("TLabel", background="#000000", foreground="white", font=("Ubuntu", 20,"bold"))


# ----------------------------
# Create the Control Panel (two rows)
# ----------------------------
control_frame = tk.Frame(root, bg="#000000")
control_frame.pack(pady=10)

# First row: Time set (label and entry).
time_frame = tk.Frame(control_frame, bg="#000000")
time_frame.pack()
set_time_label = ttk.Label(time_frame, text="SET TIME ")
set_time_label.pack(side="left", padx=(0, 5))
entry = ttk.Entry(time_frame, width=5)
entry.pack(side="left")
minutes_label = ttk.Label(time_frame, text=" MINUTES")
minutes_label.pack(side="left", padx=(5, 0))

# Second row: Buttons.
button_frame = tk.Frame(control_frame, bg="#000000")
button_frame.pack(pady=5)

start_button = ttk.Button(button_frame, text="Start", command=lambda: start_timer())
start_button.pack(side="left", padx=(10, 0))

stop_button = ttk.Button(button_frame, text="Stop", state="disabled", command=lambda: stop_timer())
stop_button.pack(side="left", padx=(10, 0))

clear_button = ttk.Button(button_frame, text="Clear", command=lambda: clear_timer(), style="Clear.TButton")
clear_button.pack(side="left", padx=(10, 0))

# ----------------------------
# Create the Canvas for the Timer Display
# ----------------------------
CANVAS_SIZE = 300
PADDING = 0

canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="#000000", highlightthickness=1)
canvas.pack(pady=10)

# Create a grid of mini-squares.
grid_rectangles = []
square_size = (CANVAS_SIZE - 2 * PADDING) / GRID_COUNT

for row in range(GRID_COUNT):
    for col in range(GRID_COUNT):
        x0 = PADDING + col * square_size
        y0 = PADDING + row * square_size
        x1 = x0 + square_size
        y1 = y0 + square_size
        # Initially, all squares are set to the LEFT_COLOR.
        rect = canvas.create_rectangle(x0, y0, x1, y1, fill=LEFT_COLOR, outline="white")
        grid_rectangles.append(rect)

# ----------------------------
# Timer Functions
# ----------------------------
def update_grid():
    """Update the mini-squares to represent the elapsed fraction of time."""
    global timer_update_id
    elapsed = (time.time() - start_time) + accumulated_elapsed
    ratio = min(elapsed / total_time, 1)  # Ensure ratio does not exceed 1.
    squares_to_fill = int(ratio * TOTAL_SQUARES)
    
    # Update each mini-square's color.
    for idx, rect in enumerate(grid_rectangles):
        if idx < squares_to_fill:
            canvas.itemconfig(rect, fill=SPENT_COLOR)
        else:
            canvas.itemconfig(rect, fill=LEFT_COLOR)
    
    if elapsed < total_time:
        timer_update_id = root.after(100, update_grid)  # Update every 100ms.
    else:
        # Timer finished: re-enable controls and disable Stop.
        entry.config(state="normal")
        start_button.config(state="normal")
        stop_button.config(state="disabled")
        timer_update_id = None

def start_timer():
    """
    Start or resume the timer.
    - If no timer is running or if the previous timer finished, read a new time from the entry.
    - If the entry is empty, default to 25 minutes (and update the entry field).
    - Otherwise, resume from where it left off.
    """
    global total_time, start_time, accumulated_elapsed, timer_update_id
    if total_time == 0 or accumulated_elapsed >= total_time:
        entry_value = entry.get().strip()
        if not entry_value:
            entry_value = "25"
            entry.delete(0, tk.END)
            entry.insert(0, entry_value)
        try:
            minutes_val = float(entry_value)
        except ValueError:
            return  # Invalid input; do nothing.
        total_time = minutes_val * 60  # Convert minutes to seconds.
        accumulated_elapsed = 0  # Reset elapsed time.
    start_time = time.time()
    entry.config(state="disabled")
    start_button.config(state="disabled")
    stop_button.config(state="normal")
    update_grid()


def stop_timer():
    """Pause the timer so it can resume later."""
    global timer_update_id, accumulated_elapsed, start_time
    if timer_update_id is not None:
        root.after_cancel(timer_update_id)
        timer_update_id = None
        elapsed_current = time.time() - start_time
        accumulated_elapsed += elapsed_current
        start_time = None  # Mark the timer as paused.
        start_button.config(state="normal")
        stop_button.config(state="disabled")

def clear_timer():
    """Clear the timer, reset the grid, and re-enable the input."""
    global total_time, start_time, accumulated_elapsed, timer_update_id
    if timer_update_id is not None:
        root.after_cancel(timer_update_id)
        timer_update_id = None
    total_time = 0
    start_time = None
    accumulated_elapsed = 0
    # Reset the grid to the LEFT_COLOR.
    for rect in grid_rectangles:
        canvas.itemconfig(rect, fill=LEFT_COLOR)
    entry.config(state="normal")
    start_button.config(state="normal")
    stop_button.config(state="disabled")

# ----------------------------
# Start the Tkinter Event Loop
# ----------------------------
root.mainloop()

