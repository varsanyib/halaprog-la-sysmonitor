import psutil
import time

class SysMonitor:
    def __init__(self):
        self.cpu_usage = psutil.cpu_percent(interval=1)
        self.memory_info = psutil.virtual_memory()
        self.disk_info = psutil.disk_usage('/')

        print(f"CPU Usage: {self.cpu_usage}%")
        print(f"Memory Usage: {self.memory_info.percent}%")
        print(f"Disk Usage: {self.disk_info.percent}%")

        print("Network current statistics:")
        net_now = psutil.net_io_counters(pernic=True)
        time.sleep(1)
        net_later = psutil.net_io_counters(pernic=True)
        for adapter in net_now.keys():
            sent_diff = (net_later[adapter].bytes_sent - net_now[adapter].bytes_sent) / (1024 * 1024)
            recv_diff = (net_later[adapter].bytes_recv - net_now[adapter].bytes_recv) / (1024 * 1024)
            print(f" - {adapter}")
            print(f"   - Upload Speed: {sent_diff * 8:.2f} Mbit/s")
            print(f"   - Download Speed: {recv_diff * 8:.2f} Mbit/s")
            print()

if __name__ == "__main__":
    monitor = SysMonitor()
