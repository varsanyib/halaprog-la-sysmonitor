import threading
import time
from monitor import SysMonitor
from gui import SysMonitorGUI
import tkinter as tk

monitor = SysMonitor(run_interval=1)
monitor_thread = threading.Thread(target=monitor.run, daemon=True)

try:
    root = tk.Tk()
    app = SysMonitorGUI(root, monitor)
    monitor_thread.start()

    root.mainloop()

    while monitor_thread.is_alive():
        time.sleep(0.1)

    

except KeyboardInterrupt:
    monitor.stop()
    monitor_thread.join()