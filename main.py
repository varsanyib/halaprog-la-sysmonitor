import threading
import time
from monitor import SysMonitor
from gui import SysMonitorGUI
import tkinter as tk

monitor = SysMonitor(run_interval=1)
monitor_thread = threading.Thread(target=monitor.run, daemon=True)

def on_closing():
    monitor.stop()
    monitor_thread.join()
    root.destroy() 


if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", on_closing)
    

        app = SysMonitorGUI(root, monitor)

        monitor_thread.start()

        root.mainloop()

        while monitor_thread.is_alive():
            time.sleep(0.1)

    except KeyboardInterrupt:
        monitor.stop()
        monitor_thread.join()