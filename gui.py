import tkinter as tk

class SysMonitorGUI:
    def __init__(self, root, monitor):
        self.root = root
        self.monitor = monitor
        root.title("System Monitor")

        self.label = tk.Label(root, text="System Monitor Running...")
        self.label.pack()

        self.update_button = tk.Button(root, text="Get Current Data", command=self.update_data)
        self.update_button.pack()

        self.data_text = tk.Text(root, height=15, width=50)
        self.data_text.pack()

    def update_data(self):
        latest_data = self.monitor.data[-1] if self.monitor.data else {}
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(tk.END, str(latest_data))