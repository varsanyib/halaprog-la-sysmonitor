import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from anomaly import AnomalyDetector

class SysMonitorGUI:
    def __init__(self, root, monitor):
        self.root = root
        self.monitor = monitor

        # Default historic data length
        self.history_len = 30 
        
        # Historic data lists
        self.cpu_history = []
        self.mem_history = []
        self.net_upload_history = []
        self.net_download_history = []

        self.anomaly_contamination = 0.005 # 0.5% anomaly rate
        self.anomaly_relearning_interval = 180 # Relearn every 180 samples
        self.anomaly_minimum_samples = 60 # Minimum samples to train
        self.anomaly_detector = AnomalyDetector(contamination=self.anomaly_contamination, min_samples=self.anomaly_minimum_samples)
        self.anomaly_score = 0.0 # Last anomaly score
        self.is_anomaly = False
        
        self._configure_root(root)
        
        self._configure_styles()
        
        self._create_widgets()

        self.update_data()


    def _configure_root(self, root):
        root.title("SysMonitor Dashboard")
        root.geometry("1280x720")


    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam") 
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#005A9C")
        style.configure("Value.TLabel", font=("Segoe UI", 10, "bold"), foreground="#333333")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#EEEEEE")
        style.configure("Treeview", font=("Segoe UI", 9))


    def _create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        dashboard_tab = ttk.Frame(notebook)
        settings_tab = ttk.Frame(notebook)
        
        notebook.add(dashboard_tab, text="📊 Monitor")
        notebook.add(settings_tab, text="⚙️ Beállítások")

        self._create_settings_tab(settings_tab)
        self._create_dashboard_tab(dashboard_tab)


    def _create_dashboard_tab(self, parent):
        main_frame = ttk.Frame(parent, padding="15", relief="groove")
        main_frame.pack(fill='both', expand=True)

        main_frame.grid_rowconfigure(0, weight=1) 
        main_frame.grid_rowconfigure(1, weight=1) 
        main_frame.grid_columnconfigure(0, weight=1) 

        stats_frame = self._create_statistics_section(main_frame)
        stats_frame.grid(row=0, column=0, sticky='nsew')
        

        graphs_frame = self._create_graphs_section(main_frame)
        graphs_frame.grid(row=1, column=0, sticky='nsew')
        

    def _create_statistics_section(self, parent):
        stats_frame = ttk.Frame(parent)
        
        ttk.Label(stats_frame, text="💻 Általános Rendszer Statisztikák", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        self.general_labels = {}
        
        # CPU, memory, storage
        self._create_general_data_widgets(stats_frame, "CPU:", 1, "cpu")
        self._create_general_data_widgets(stats_frame, "Memória:", 2, "memory")
        self._create_general_data_widgets(stats_frame, "Tárhely:", 3, "partitions")

        self.anomaly_label = ttk.Label(stats_frame, text="Rendszer állapota: Folyamatban 🕓", font=("Segoe UI", 10, "bold"), foreground="gray")
        self.anomaly_label.grid(row=1, column=1, sticky='e', padx=10, pady=5)
        stats_frame.grid_columnconfigure(1, weight=1)

        ttk.Separator(stats_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)

        # Hálózati Treeview
        ttk.Label(stats_frame, text="🌐 Hálózati Forgalom (Mbit/s)", style="Header.TLabel").grid(row=5, column=0, columnspan=2, sticky='w', pady=(10, 5))
        self.tree = self._create_network_treeview(stats_frame, 6)
        
        stats_frame.grid_rowconfigure(6, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1) 
        
        ttk.Label(stats_frame, text="📊 Grafikonok", style="Header.TLabel").grid(row=7, column=0, columnspan=2, sticky='w', pady=(10, 5))

        return stats_frame


    def _create_graphs_section(self, parent):
        graphs_frame = ttk.Frame(parent, padding="10", relief="sunken")

        self.fig, self.axes = self._setup_graphs()
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        return graphs_frame


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

    
    def _setup_graphs(self):
        fig = Figure(figsize=(10, 4), dpi=100)
        axs = [fig.add_subplot(1, 3, i+1) for i in range(3)] 
        
        fig.subplots_adjust(wspace=0.3, left=0.05, right=0.98, top=0.9, bottom=0.15)
        
        titles = ['CPU használat (%)', 'Memória használat (%)', 'Hálózati forgalom (Mbit/s)']
        
        for i, ax in enumerate(axs):
            ax.set_title(titles[i], fontsize=9)
            ax.tick_params(axis='both', which='major', labelsize=8)
            ax.set_ylim(0, 100)
            ax.set_yticks([0, 25, 50, 75, 100])
        
        axs[2].set_ylim(bottom=0)

        return fig, axs

    
    def update_data(self):
        if not self.monitor.data:
            self.root.after(1000, self.update_data)
            return

        latest_entry = self.monitor.data[-1]
        data = latest_entry['data']

        if not self.anomaly_detector.is_trained or (len(self.monitor.data) % self.anomaly_relearning_interval == 0 and len(self.monitor.data) > self.anomaly_detector.min_samples):
            if self.anomaly_detector.train(self.monitor.data):
                # print("Isolation Forest betanítva.")
                pass

        if self.anomaly_detector.is_trained:
            self.anomaly_score = self.anomaly_detector.predict_anomaly_score(data)
            
            self.is_anomaly = self.anomaly_score < 0 
            self._update_anomaly_label()
            
        cpu_data, mem_data, upload_data, download_data, x_data = self._process_historical_data(data)
        
        self._update_general_stats(data)

        self._update_network_treeview(data)
        
        self._update_graphs(cpu_data, mem_data, upload_data, download_data, x_data)

        self.root.after(1000, self.update_data)


    def _process_historical_data(self, data):
        self.cpu_history.append(data['cpu_usage_percent'])
        self.mem_history.append(data['memory_percent'])
            
        total_upload = sum(s['upload_mbps'] for s in data.get('network_stats', []))
        total_download = sum(s['download_mbps'] for s in data.get('network_stats', []))
        self.net_upload_history.append(total_upload)
        self.net_download_history.append(total_download)
        
        start_index = max(0, len(self.cpu_history) - self.history_len)
            
        cpu_data = self.cpu_history[start_index:]
        mem_data = self.mem_history[start_index:]
        upload_data = self.net_upload_history[start_index:]
        download_data = self.net_download_history[start_index:]
            
        x_data = list(range(len(cpu_data))) 
        
        return cpu_data, mem_data, upload_data, download_data, x_data


    def _update_general_stats(self, data):
        # CPU
        cpu_cores_text = ', '.join(f'{core:.1f}%' for core in data['cpu_usage_per_core_percent'])
        cpu_text = f"{data['cpu_usage_percent']:.1f}% @ {data['cpu_freq_current_mhz']} MHz - ({cpu_cores_text})"
        self.general_labels['cpu'].config(text=cpu_text)
            
        # Memory
        mem_text = f"{data['memory_used_gb']:.2f} GB / {data['memory_total_gb']:.2f} GB ({data['memory_used_gb'] / data['memory_total_gb'] * 100:.1f}%)"
        self.general_labels['memory'].config(text=mem_text)

        # Storage
        partitions_info = []
        for part in data.get('disk_usages', []):
            usage = part['usage']
            used_gb = usage['used'] / (1024 ** 3)
            total_gb = usage['total'] / (1024 ** 3)
            partitions_info.append(f"{part['mountpoint']} {used_gb:.2f} GB / {total_gb:.2f} GB ({usage['percent']}%)")

        self.general_labels['partitions'].config(text="; ".join(partitions_info))


    def _update_network_treeview(self, data):
        network_stats = data.get('network_stats', [])
        # Sort by network adapter name
        sorted_stats = sorted(network_stats, key=lambda x: x['interface']) 
            
        # Clear previous entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new, sorted data
        for stats in sorted_stats:
            self.tree.insert("", "end", values=(
                stats['interface'],
                f"{stats['upload_mbps']:.4f}",
                f"{stats['download_mbps']:.4f}",
                stats['errors_in'],
                stats['errors_out'],
                stats['dropped_in'],
                stats['dropped_out']
            ))

    
    def _update_graphs(self, cpu_data, mem_data, upload_data, download_data, x_data):
        # Clear previous lines on all axes
        for ax in self.axes:
            ax.clear()
        
        # CPU graph
        self.axes[0].plot(x_data, cpu_data, color='blue')
        self.axes[0].set_ylim(0, 100)
        self.axes[0].set_title('CPU használat (%)', fontsize=9)
            
        # Memory graph
        self.axes[1].plot(x_data, mem_data, color='green')
        self.axes[1].set_ylim(0, 100)
        self.axes[1].set_title('Memória használat (%)', fontsize=9)

        # Network graph
        self.axes[2].plot(x_data, upload_data, label='Feltöltés', color='orange')
        self.axes[2].plot(x_data, download_data, label='Letöltés', color='purple')
        self.axes[2].legend(loc='upper left', fontsize=7)
        self.axes[2].set_title('Hálózati forgalom (Mbit/s)', fontsize=9)
        self.axes[2].set_ylim(bottom=0)
        
        # Common axis settings (Time)
        self._configure_graph_time_axis(x_data)
                 
        # Redraw canvas
        self.canvas.draw()


    def _configure_graph_time_axis(self, x_data):
        current_history_length = len(x_data)
        
        # Only the two extreme points need to be marked
        x_ticks = [x_data[0], x_data[-1]] if x_data else []

        if len(self.monitor.data) > self.history_len:
            time_now = time.time()
            time_diff = time_now - current_history_length
            time_diff_string = time.strftime('%H:%M:%S', time.gmtime(time_diff))
        else:
            time_diff_string = f"-{time.strftime('%H:%M:%S', time.gmtime(current_history_length))}"
        
        x_labels = [f'{time_diff_string}', 'Most'] if x_data else []

        for ax in self.axes:
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(x_labels)
            ax.grid(True, linestyle=':', alpha=0.6)

    
    def _create_settings_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="📌 Beállítások", style="Header.TLabel").grid(row=0, column=0, sticky='w', pady=(0, 10))

        # Grafikon Történeti Időtartam
        ttk.Label(frame, text="Grafikon történeti időtartam (mp):").grid(row=1, column=0, sticky='w', pady=5)
        self.history_len_var = tk.IntVar(value=self.history_len)
        history_entry = ttk.Entry(frame, textvariable=self.history_len_var, width=10)
        history_entry.grid(row=1, column=1, sticky='w', pady=5)
        
        ttk.Separator(frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=15)
        ttk.Label(frame, text="🛠️ Rendszerállapot referenciaértékei", style="Header.TLabel").grid(row=3, column=0, sticky='w', pady=(0, 10))

        ttk.Label(frame, text="Szennyezettség (%):").grid(row=4, column=0, sticky='w', pady=5)
        self.contam_var = tk.DoubleVar(value=self.anomaly_contamination * 100) # Érték %-ban (pl. 0.5)
        contam_entry = ttk.Entry(frame, textvariable=self.contam_var, width=10)
        contam_entry.grid(row=4, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="Újratanítási időköz (mp):").grid(row=5, column=0, sticky='w', pady=5)
        self.relearn_var = tk.IntVar(value=self.anomaly_relearning_interval)
        relearn_entry = ttk.Entry(frame, textvariable=self.relearn_var, width=10)
        relearn_entry.grid(row=5, column=1, sticky='w', pady=5)

        ttk.Label(frame, text="Betanítási időköz (mp): ").grid(row=6, column=0, sticky='w', pady=5)
        self.min_samples_var = tk.IntVar(value=self.anomaly_minimum_samples)
        min_samples_entry = ttk.Entry(frame, textvariable=self.min_samples_var, width=10)
        min_samples_entry.grid(row=6, column=1, sticky='w', pady=5)
        
        apply_button = ttk.Button(frame, text="Alkalmaz", command=self.apply_settings)
        apply_button.grid(row=7, column=0, columnspan=2, pady=15)

    def apply_settings(self):
        try:
            new_len = int(self.history_len_var.get())
            if new_len < 1:
                raise ValueError("history_len")
            
            self.history_len = new_len
            self.cpu_history = self.cpu_history[-new_len:]
            self.mem_history = self.mem_history[-new_len:]
            self.net_upload_history = self.net_upload_history[-new_len:]
            self.net_download_history = self.net_download_history[-new_len:]

            new_contam_percent = float(self.contam_var.get())
            new_contam = new_contam_percent / 100.0
            if not (0.0 < new_contam <= 0.5):
                raise ValueError("contamination")
            self.anomaly_contamination = new_contam
            
            new_relearn = int(self.relearn_var.get())
            if new_relearn < 1:
                raise ValueError("relearning")
            self.anomaly_relearning_interval = new_relearn
            
            new_min_samples = int(self.min_samples_var.get())
            if new_min_samples < 5:
                raise ValueError("min_samples")
            self.anomaly_minimum_samples = new_min_samples
            
            self.anomaly_detector = AnomalyDetector(
                contamination=self.anomaly_contamination, 
                random_state=42, 
                min_samples=self.anomaly_minimum_samples
            )
            
            # Sikeres Üzenet
            messagebox.showinfo("Siker!", f"A beállítások sikeresen elmentve!")

        except ValueError as e:
            error_type = str(e)
            if "history_len" in error_type:
                msg = "Kérem, érvényes pozitív egész számot adjon meg a történeti időtartamhoz!"
            elif "contamination" in error_type:
                msg = "Kérem, 0 és 50% közötti értéket adjon meg a szennyezettséghez!"
            elif "relearning" in error_type:
                msg = "Kérem, érvényes pozitív egész számot adjon meg az újratanítási időközhöz!"
            elif "min_samples" in error_type:
                msg = "Kérem, legalább 5 mp értéket adjon meg a betanítási időközhöz!"
            else:
                msg = "Érvénytelen bemenet valamelyik mezőben. Kérem, ellenőrizze az értékeket!"
                
            messagebox.showerror("Hiba!", msg)

    def _update_anomaly_label(self):
        if self.is_anomaly:
            text = f"Rendszer állapota: Detektált anomália ⚠️ ({self.anomaly_score*100:.2f})"
            color = "red"
        else:
            text = f"Rendszer állapota: Normál működés ✅ ({self.anomaly_score*100:.2f})"
            color = "green"

        self.anomaly_label.config(text=text, foreground=color)