# Focus & Task Timer

A lightweight, single-window desktop task timer and timesheet logger built for Debian Linux using Python and Tkinter.

## Features
* **Task Timer:** Start, pause, resume, and stop tasks with immediate event logging.
* **Task Notes:** Add optional notes when stopping a task.
* **Timesheet Totals:** Automatically calculates total logged time in both `HH:MM:SS` and decimal hours.
* **Log Archiving:** Save timestamped backups of your log and reset for a new timesheet period.
* **Reminder Alarm:** Set a countdown timer with a live remaining-time display, audio alert, and popup notification.

## Requirements
* Debian (or any Debian-based Linux distro)
* Python 3
* Tkinter (`python3-tk`)

## Installation & Usage

1. Install Tkinter if it is not already installed:
   ```bash
   sudo apt update && sudo apt install -y python3-tk
   ```

2. Clone this repository and navigate into the folder:
   ```bash
   git clone https://github.com
   cd focus-task-timer
   ```

3. Run the application:
   ```bash
   python3 focus_tracker.py
   ```

## Data Storage
All activity is saved locally in `task_log.txt` in the application directory. Clicking **Archive & Reset Log** creates a timestamped backup file (`task_log_YYYY-MM-DD_HHMMSS.txt`) and starts a fresh log.
