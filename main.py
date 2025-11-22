import threading
import time
from monitor import SysMonitor 

monitor = SysMonitor(run_interval=1)
monitor_thread = threading.Thread(target=monitor.run, daemon=True)

try:
    monitor_thread.start()
    
    while monitor_thread.is_alive():
        time.sleep(0.1)

except KeyboardInterrupt:
    monitor.running = False 
    monitor_thread.join()