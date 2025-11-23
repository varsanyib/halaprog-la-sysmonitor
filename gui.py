import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

class SysMonitorGUI:
    def __init__(self, root, monitor):
        self.root = root
        self.monitor = monitor
        self.history_len = 30

        root.title("SysMonitor Dashboard")
        root.geometry("1280x720")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        dashboard_tab = ttk.Frame(notebook)
        notebook.add(dashboard_tab, text="📊 Monitor")

        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="⚙️ Beállítások")

        self._create_settings_tab(settings_tab)
        
        self.cpu_history = []
        self.mem_history = []
        self.net_upload_history = []
        self.net_download_history = []
        self.time_history = []

        # Style configurations
        style = ttk.Style()
        style.theme_use("clam") 
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#005A9C")
        style.configure("Value.TLabel", font=("Segoe UI", 10, "bold"), foreground="#333333")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#EEEEEE")
        style.configure("Treeview", font=("Segoe UI", 9))
        
        # Main container frame
        main_frame = ttk.Frame(dashboard_tab, padding="15", relief="groove")
        main_frame.pack(fill='both', expand=True)

        # 1. Statistics (Top section)
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=0, column=0, sticky='nsew')
        
        ttk.Label(stats_frame, text="💻 Általános Rendszer Statisztikák", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 10))
        
        self.general_labels = {}
        
        self._create_general_data_widgets(stats_frame, "CPU:", 1, "cpu")
        self._create_general_data_widgets(stats_frame, "Memória:", 2, "memory")

        ttk.Separator(stats_frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Label(stats_frame, text="🌐 Hálózati Forgalom (Mbit/s)", style="Header.TLabel").grid(row=4, column=0, columnspan=2, sticky='w', pady=(10, 5))

        self.tree = self._create_network_treeview(stats_frame, 5)
        
        # Configure stats_frame layout
        stats_frame.grid_rowconfigure(5, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1) 

        ttk.Label(stats_frame, text="📊 Grafikonok", style="Header.TLabel").grid(row=6, column=0, columnspan=2, sticky='w', pady=(10, 5))

        graphs_frame = ttk.Frame(main_frame, padding="10", relief="sunken")
        graphs_frame.grid(row=1, column=0, sticky='nsew')
        
        # Configure main_frame grid for expansion
        main_frame.grid_rowconfigure(0, weight=1) 
        main_frame.grid_rowconfigure(1, weight=1) 
        main_frame.grid_columnconfigure(0, weight=1) 
        
        # Create Matplotlib figure and embed it into Tkinter
        self.fig, self.axes = self._create_graphs(graphs_frame)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Start automatic update cycle
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

    
    def _create_graphs(self, parent):
        fig = Figure(figsize=(10, 4), dpi=100)
        axs = [fig.add_subplot(1, 3, i+1) for i in range(3)] 
        
        fig.subplots_adjust(wspace=0.3, left=0.05, right=0.98, top=0.9, bottom=0.15)
        
        axs[0].set_title('CPU használat (%)', fontsize=9)
        axs[0].set_ylim(0, 100)
        axs[0].set_yticks([0, 25, 50, 75, 100])
        axs[0].tick_params(axis='both', which='major', labelsize=8)
        
        axs[1].set_title('Memória használat (%)', fontsize=9)
        axs[1].set_ylim(0, 100)
        axs[1].set_yticks([0, 25, 50, 75, 100])
        axs[1].tick_params(axis='both', which='major', labelsize=8)

        axs[2].set_title('Hálózati forgalom (Mbit/s)', fontsize=9)
        axs[2].tick_params(axis='both', which='major', labelsize=8)
        axs[2].set_ylim(bottom=0)

        return fig, axs

    def update_data(self):
        if self.monitor.data:
            latest_entry = self.monitor.data[-1]
            data = latest_entry['data']
            
            self.cpu_history.append(data['cpu_usage_percent'])
            self.mem_history.append(data['memory_percent'])
            
            # Calculate total network traffic for the graph
            total_upload = sum(s['upload_mbps'] for s in data.get('network_stats', []))
            total_download = sum(s['download_mbps'] for s in data.get('network_stats', []))
            self.net_upload_history.append(total_upload)
            self.net_download_history.append(total_download)
            
            self.time_history.append(len(self.time_history))
            
            start_index = max(0, len(self.cpu_history) - self.history_len)
            
            cpu_data = self.cpu_history[start_index:]
            mem_data = self.mem_history[start_index:]
            upload_data = self.net_upload_history[start_index:]
            download_data = self.net_download_history[start_index:]
            
            # The X-axis data should be relative indices for the displayed window
            x_data = list(range(len(cpu_data))) 
            
            self.general_labels['cpu'].config(text=f"{data['cpu_usage_percent']:.1f}%")
            
            # Memory data formatting
            mem_text = f"Felhasznált: {data['memory_used_gb']:.2f} GB / Összes: {data['memory_total_gb']:.2f} GB ({data['memory_percent']:.1f}%)"
            self.general_labels['memory'].config(text=mem_text)
            
            
            # 1. Sort the network stats list by the 'interface' key
            network_stats = data.get('network_stats', [])
            sorted_stats = sorted(network_stats, key=lambda x: x['interface']) 
            
            # 2. Clear previous entries
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 3. Insert new sorted data rows
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
            
            for ax in self.axes:
                ax.clear()
        
            self.axes[0].plot(x_data, cpu_data, color='blue')
            self.axes[0].set_ylim(0, 100)
            self.axes[0].set_title('CPU használat (%)', fontsize=9)
            
            self.axes[1].plot(x_data, mem_data, color='green')
            self.axes[1].set_ylim(0, 100)
            self.axes[1].set_title('Memória használat (%)', fontsize=9)

            self.axes[2].plot(x_data, upload_data, label='Feltöltés', color='orange')
            self.axes[2].plot(x_data, download_data, label='Letöltés', color='purple')
            self.axes[2].legend(loc='upper left', fontsize=7)
            self.axes[2].set_title('Hálózati forgalom (Mbit/s)', fontsize=9)
            self.axes[2].set_ylim(bottom=0)

            # All axes
            current_history_length = len(x_data)
            for ax in self.axes:
                ax.set_xticks([x_data[0], x_data[-1]])
                if len(self.monitor.data) > self.history_len:
                    # diff hh:mm:ss current_history_length value (sec)
                    time_now = time.time()
                    time_diff = time_now - current_history_length
                    time_diff_string = time.strftime('%H:%M:%S', time.gmtime(time_diff))
                else:
                    time_diff_string = f"-{time.strftime('%H:%M:%S', time.gmtime(current_history_length))}"
                ax.set_xticklabels([f'{time_diff_string}', 'Most'])
                ax.grid(True, linestyle=':', alpha=0.6)
                 
            # Redraw the canvas
            self.canvas.draw()

        # Schedule the next update (1 second interval)
        self.root.after(1000, self.update_data)

    def _create_settings_tab(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="📌 GUI Beállítások", style="Header.TLabel").grid(row=0, column=0, sticky='w', pady=(0, 10))

        ttk.Label(frame, text="Grafikon történeti időtartam:").grid(row=1, column=0, sticky='w', pady=5)
        self.history_len_var = tk.IntVar(value=self.history_len)
        history_entry = ttk.Entry(frame, textvariable=self.history_len_var, width=10)
        history_entry.grid(row=1, column=1, sticky='w', pady=5)

        apply_button = ttk.Button(frame, text="Alkalmaz", command=self.apply_settings)
        apply_button.grid(row=2, column=0, columnspan=2, pady=12)

    def apply_settings(self):
        try:
            new_len = int(self.history_len_var.get())
            if new_len < 1:
                raise ValueError
            self.history_len = new_len
            messagebox.showinfo("Siker!", f"A történeti időtartam sikeresen {new_len} másodpercre lett beállítva.")

        except ValueError:
            messagebox.showerror("Hiba!", "Kérem, érvényes pozitív egész számot adjon meg a történeti időtartamhoz!")