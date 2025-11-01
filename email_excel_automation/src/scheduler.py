
import schedule
import time
from typing import Callable

def run_daily(job_func: Callable, hour: int = 8, minute: int = 0):
    # schedule job every day at HH:MM
    schedule_time = f"{hour:02d}:{minute:02d}"
    schedule.every().day.at(schedule_time).do(job_func)
    print(f"Scheduled daily job at {schedule_time}. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped by user.")
