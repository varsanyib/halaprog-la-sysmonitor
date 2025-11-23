import psutil
import time

class SysMonitor:
    def __init__(self, run_interval=1):
        self.data = []
        self.running = True
        self.run_interval = run_interval

    def collect_data(self):
        try:
            cpu_usage = psutil.cpu_percent()
            cpu_usage_cores = psutil.cpu_percent(percpu=True)
            cpu_freq = psutil.cpu_freq()
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            disk_usages = []

            for disk in psutil.disk_partitions():
                if disk.fstype:
                    disk_usages.append({
                        'mountpoint': disk.mountpoint,
                        'fstype': disk.fstype,
                        'usage': psutil.disk_usage(disk.mountpoint)._asdict()
                    })

            net_now = psutil.net_io_counters(pernic=True)
            time.sleep(1)
            net_later = psutil.net_io_counters(pernic=True)

            net_stats = []
            for adapter in net_now.keys():
                tx_bytes_diff = (net_later[adapter].bytes_sent - net_now[adapter].bytes_sent) / (1024 * 1024)
                rx_bytes_diff = (net_later[adapter].bytes_recv - net_now[adapter].bytes_recv) / (1024 * 1024)

                errin_diff = net_later[adapter].errin - net_now[adapter].errin
                errout_diff = net_later[adapter].errout - net_now[adapter].errout

                dropin_diff = net_later[adapter].dropin - net_now[adapter].dropin
                dropout_diff = net_later[adapter].dropout - net_now[adapter].dropout
                


                net_stats.append({
                    'interface': adapter,
                    'upload_mbps': round(tx_bytes_diff * 8, 4),
                    'download_mbps': round(rx_bytes_diff * 8, 4),
                    'errors_in': errin_diff,
                    'errors_out': errout_diff,
                    'dropped_in': dropin_diff,
                    'dropped_out': dropout_diff,
                })

            return {
                'cpu_usage_percent': round(cpu_usage, 2),
                'cpu_usage_per_core_percent': [round(core, 2) for core in cpu_usage_cores],
                'cpu_freq_current_mhz': round(cpu_freq.current),
                'memory_total_gb': round(memory_info.total / (1024 ** 3), 4),
                'memory_used_gb': round(memory_info.used / (1024 ** 3), 4),
                'memory_percent': round(memory_info.percent, 2),
                'disk_total_gb': round(disk_info.total / (1024 ** 3), 4),
                'disk_used_gb': round(disk_info.used / (1024 ** 3), 4),
                'disk_percent': round(disk_info.percent, 2),
                'disk_usages': disk_usages,
                'network_stats': net_stats
            }
        except Exception as e:
            return {'error': str(e)}

    def run(self):
        while self.running:
            self.data.append({'timestamp': round(time.time()), 'data': self.collect_data()})
            time.sleep(self.run_interval - 1) # Adjusted for the 1 second sleep in collect_data

    def stop(self):
        self.running = False