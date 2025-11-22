import tkinter as tk
from tkinter import ttk

class SysMonitorGUI:
    def __init__(self, root, monitor):
        self.root = root
        self.monitor = monitor
        root.title("SysMonitor")
        root.geometry("1280x720")
        
        style = ttk.Style()
        style.theme_use("clam") 
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#005A9C")
        style.configure("Value.TLabel", font=("Segoe UI", 10, "bold"), foreground="#333333")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#EEEEEE")
        style.configure("Treeview", font=("Segoe UI", 9))
        
        main_frame = ttk.Frame(root, padding="15", relief="groove")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="🚀 Általános Rendszer Statisztikák", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        self.general_labels = {}
        
        self._create_general_data_widgets(main_frame, "CPU:", 1, "cpu")
        self._create_general_data_widgets(main_frame, "Memória:", 2, "memory")
        self._create_general_data_widgets(main_frame, "Lemez:", 3, "disk")
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Label(main_frame, text="🌐 Hálózati Forgalom (Mb/s)", style="Header.TLabel").grid(row=5, column=0, columnspan=2, sticky='w', pady=(10, 5))

        self.tree = self._create_network_treeview(main_frame, 6)
        
        main_frame.grid_rowconfigure(6, weight=1) 
        main_frame.grid_columnconfigure(1, weight=1) 
        
        self.update_data()


    def _create_general_data_widgets(self, parent, label_text, row, key):
        ttk.Label(parent, text=label_text, width=15).grid(row=row, column=0, sticky='w', padx=5, pady=2)
        
        value_label = ttk.Label(parent, text="N/A", style="Value.TLabel")
        value_label.grid(row=row, column=1, sticky='w', padx=5, pady=2)
        
        self.general_labels[key] = value_label


    def _create_network_treeview(self, parent, row):
        columns = ("interface", "upload", "download", "errors_in", "errors_out", "dropped_in", "dropped_out")
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        headers = {
            "interface": ("Hálózati adapter", 150, "w"),
            "upload": ("Feltöltés sebesség (Mbit/s)", 110, "e"),
            "download": ("Letöltés sebesség (Mbit/s)", 110, "e"),
            "errors_in": ("Bejövő hibák", 80, "e"),
            "errors_out": ("Kimenő hibák", 80, "e"),
            "dropped_in": ("Bejövő elvesztett csomagok", 100, "e"),
            "dropped_out": ("Kimenő elvesztett csomagok", 100, "e")
        }
        
        for col, (text, width, anchor) in headers.items():
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor=anchor)

        tree.grid(row=row, column=0, columnspan=2, sticky='nsew')
        return tree


    def update_data(self):
        if self.monitor.data:
            latest_entry = self.monitor.data[-1]
            data = latest_entry['data']

            self.general_labels['cpu'].config(text=f"{data['cpu_usage_percent']:.1f}%")
            mem_text = f"{data['memory_used_gb']:.2f} GB / {data['memory_total_gb']:.2f} GB ({data['memory_percent']:.1f}%)"
            self.general_labels['memory'].config(text=mem_text)
            disk_text = f"{data['disk_used_gb']:.2f} GB / {data['disk_total_gb']:.2f} GB ({data['disk_percent']:.1f}%)"
            self.general_labels['disk'].config(text=disk_text)

            # Delete existing data in the treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Insert the new data
            for stats in data.get('network_stats', []):
                self.tree.insert("", "end", values=(
                    stats['interface'],
                    f"{stats['upload_mbps']:.4f}",
                    f"{stats['download_mbps']:.4f}",
                    stats['errors_in'],
                    stats['errors_out'],
                    stats['dropped_in'],
                    stats['dropped_out']
                ))

        self.root.after(1000, self.update_data)