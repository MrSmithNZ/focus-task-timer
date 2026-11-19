import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import datetime
import os
import re
import shutil
import subprocess

LOG_FILE = "task_log.txt"


class FocusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Focus & Task Timer")
        self.root.geometry("600x540")

        # Timer state
        self.running = False
        self.paused = False
        self.start_time = None
        self.accumulated_seconds = 0
        self.current_task = ""

        # Alarm state
        self.alarm_target = None

        # --- UI: Task Timer Section ---
        timer_frame = tk.LabelFrame(root, text="Task Timer", padx=10, pady=10)
        timer_frame.pack(fill="x", padx=10, pady=5)

        self.task_label = tk.Label(
            timer_frame,
            text="Current Task: None",
            font=("Sans", 10, "italic")
        )
        self.task_label.pack(anchor="w")

        self.clock_label = tk.Label(
            timer_frame,
            text="00:00:00",
            font=("Monospace", 28, "bold")
        )
        self.clock_label.pack(pady=5)

        btn_frame = tk.Frame(timer_frame)
        btn_frame.pack()

        self.start_btn = tk.Button(
            btn_frame,
            text="Start Task",
            width=12,
            bg="#d4edda",
            command=self.start_timer
        )
        self.start_btn.pack(side="left", padx=5)

        self.pause_btn = tk.Button(
            btn_frame,
            text="Pause",
            width=12,
            bg="#fff3cd",
            state="disabled",
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(
            btn_frame,
            text="Stop & Log",
            width=12,
            bg="#f8d7da",
            state="disabled",
            command=self.stop_timer
        )
        self.stop_btn.pack(side="left", padx=5)

        # --- UI: Countdown Alarm Section ---
        alarm_frame = tk.LabelFrame(root, text="Reminder Alarm", padx=10, pady=10)
        alarm_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(alarm_frame, text="Minutes:").pack(side="left")

        self.alarm_entry = tk.Entry(alarm_frame, width=6)
        self.alarm_entry.insert(0, "60")
        self.alarm_entry.pack(side="left", padx=5)

        self.set_alarm_btn = tk.Button(
            alarm_frame,
            text="Set Alarm",
            command=self.set_alarm
        )
        self.set_alarm_btn.pack(side="left", padx=5)

        self.clear_alarm_btn = tk.Button(
            alarm_frame,
            text="Clear",
            state="disabled",
            command=self.clear_alarm
        )
        self.clear_alarm_btn.pack(side="left", padx=2)

        self.alarm_status = tk.Label(
            alarm_frame,
            text="No alarm set",
            fg="gray",
            font=("Monospace", 10, "bold")
        )
        self.alarm_status.pack(side="right", padx=5)

        # --- UI: Log Display & Timesheet Summary Section ---
        log_frame = tk.LabelFrame(root, text=f"Task Log ({LOG_FILE})", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        summary_bar = tk.Frame(log_frame)
        summary_bar.pack(fill="x", pady=(0, 6))

        self.total_label = tk.Label(
            summary_bar,
            text="Total Logged: 00:00:00 (0.00 hrs)",
            font=("Sans", 11, "bold"),
            fg="#155724"
        )
        self.total_label.pack(side="left")

        self.archive_btn = tk.Button(
            summary_bar,
            text="Archive & Reset Log",
            font=("Sans", 8),
            command=self.archive_and_reset_log
        )
        self.archive_btn.pack(side="right")

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(
            log_frame,
            height=10,
            yscrollcommand=scrollbar.set,
            font=("Monospace", 9)
        )
        self.log_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)

        # Initialize log file and start background tick
        self.load_log()
        self.update_loop()

    # --- Timer Logic ---
    def start_timer(self):
        task = simpledialog.askstring(
            "New Task",
            "What task are you focusing on?",
            parent=self.root
        )
        if not task or not task.strip():
            return

        self.current_task = task.strip()
        self.accumulated_seconds = 0
        self.start_time = time.time()
        self.running = True
        self.paused = False

        self.append_log(f"STARTED: {self.current_task}")

        self.task_label.config(text=f"Current Task: {self.current_task}")
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal", text="Pause")
        self.stop_btn.config(state="normal")

    def toggle_pause(self):
        if not self.running:
            return

        if not self.paused:
            self.accumulated_seconds += time.time() - self.start_time
            self.paused = True
            elapsed_str = self.format_seconds(int(self.accumulated_seconds))
            self.append_log(f"PAUSED: {self.current_task} (at {elapsed_str})")

            self.task_label.config(text=f"Current Task: {self.current_task} [PAUSED]")
            self.pause_btn.config(text="Resume")
        else:
            self.start_time = time.time()
            self.paused = False
            self.append_log(f"RESUMED: {self.current_task}")

            self.task_label.config(text=f"Current Task: {self.current_task}")
            self.pause_btn.config(text="Pause")

    def stop_timer(self):
        if not self.running:
            return

        if not self.paused:
            self.accumulated_seconds += time.time() - self.start_time

        total_elapsed = int(self.accumulated_seconds)
        self.running = False
        self.paused = False

        notes = simpledialog.askstring(
            "Task Notes",
            "Any notes for this task? (Leave blank for none)",
            parent=self.root
        )

        duration_str = self.format_seconds(total_elapsed)
        if notes and notes.strip():
            self.append_log(
                f"STOPPED: {self.current_task} — Total: {duration_str} | Notes: {notes.strip()}"
            )
        else:
            self.append_log(f"STOPPED: {self.current_task} — Total: {duration_str}")

        # Reset UI
        self.accumulated_seconds = 0
        self.clock_label.config(text="00:00:00")
        self.task_label.config(text="Current Task: None")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled", text="Pause")
        self.stop_btn.config(state="disabled")

    # --- Alarm Logic ---
    def set_alarm(self):
        try:
            mins = float(self.alarm_entry.get())
            if mins <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter a positive number of minutes."
            )
            return

        self.alarm_target = time.time() + (mins * 60)
        self.clear_alarm_btn.config(state="normal")
        self.update_alarm_display()

    def clear_alarm(self):
        self.alarm_target = None
        self.alarm_status.config(text="No alarm set", fg="gray")
        self.clear_alarm_btn.config(state="disabled")

    def update_alarm_display(self):
        if not self.alarm_target:
            return
        remaining = max(0, int(self.alarm_target - time.time()))
        target_dt = datetime.datetime.fromtimestamp(self.alarm_target).strftime("%H:%M:%S")
        self.alarm_status.config(
            text=f"{self.format_seconds(remaining)} left (at {target_dt})",
            fg="blue"
        )

    def trigger_alarm(self):
        self.clear_alarm()
        self.play_sound()
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        messagebox.showwarning("Time's Up!", "Your reminder timer has finished!")
        self.root.attributes("-topmost", False)

    def play_sound(self):
        sound_paths = [
            "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga",
            "/usr/share/sounds/freedesktop/stereo/complete.oga",
            "/usr/share/sounds/alsa/Front_Center.wav"
        ]
        for path in sound_paths:
            if os.path.exists(path):
                player = "paplay" if path.endswith(".oga") else "aplay"
                try:
                    subprocess.Popen(
                        [player, path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    return
                except FileNotFoundError:
                    pass
        self.root.bell()

    # --- Helpers, Totals & Main Loop ---
    def append_log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"[{timestamp}] {message}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        self.load_log()

    def calculate_total_seconds(self, content):
        matches = re.findall(r"STOPPED:.*?— Total: (\d+):(\d{2}):(\d{2})", content)
        total_secs = 0
        for hrs, mins, secs in matches:
            total_secs += int(hrs) * 3600 + int(mins) * 60 + int(secs)
        return total_secs

    def load_log(self):
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("=== Task Focus Log ===\n")

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        total_secs = self.calculate_total_seconds(content)
        formatted_total = self.format_seconds(total_secs)
        decimal_hours = total_secs / 3600.0
        self.total_label.config(
            text=f"Total Logged: {formatted_total} ({decimal_hours:.2f} hrs)"
        )

        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, content)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def archive_and_reset_log(self):
        if self.running:
            messagebox.showwarning(
                "Timer Active",
                "Please stop your current task before archiving the log."
            )
            return

        confirm = messagebox.askyesno(
            "Archive & Reset",
            "Save a backup copy of the current log and start a fresh log file?"
        )
        if not confirm:
            return

        stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_name = f"task_log_{stamp}.txt"
        if os.path.exists(LOG_FILE):
            shutil.copy2(LOG_FILE, backup_name)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"=== Task Focus Log (Started {now_str}) ===\n")

        self.load_log()
        messagebox.showinfo(
            "Archived",
            f"Previous log saved as {backup_name} and current log reset."
        )

    def format_seconds(self, total_seconds):
        hrs, rem = divmod(total_seconds, 3600)
        mins, secs = divmod(rem, 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    def update_loop(self):
        if self.running and not self.paused:
            current_elapsed = int(self.accumulated_seconds + (time.time() - self.start_time))
            self.clock_label.config(text=self.format_seconds(current_elapsed))

        if self.alarm_target:
            if time.time() >= self.alarm_target:
                self.trigger_alarm()
            else:
                self.update_alarm_display()

        self.root.after(500, self.update_loop)


if __name__ == "__main__":
    root = tk.Tk()
    app = FocusApp(root)
    root.mainloop()

