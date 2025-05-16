import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import serial.tools.list_ports
import threading
import temperature
import sys
import io

# Redirect class for stdout/stderr to GUI
class TextRedirector(io.TextIOBase):
    def __init__(self, log_function):
        self.log = log_function

    def write(self, msg):
        if msg.strip():
            self.log(msg.strip())

# Log messages to the GUI output box
def log_message(msg):
    logbox.configure(state='normal')
    logbox.insert(ttk.END, msg + '\n')
    logbox.see(ttk.END)
    logbox.configure(state='disabled')

# Start the weather station logic
def start_weather_station():
    ports = list(serial.tools.list_ports.comports())
    esp_connected = any("COM" in port.device for port in ports)

    if not esp_connected:
        messagebox.showerror("ESP32 Not Found", "❌ No ESP32 device found. Please connect it.")
        log_message("❌ Error: No ESP32 device found. Please connect it.")
        return

    start_btn.configure(state=DISABLED)
    log_message("✅ ESP32 detected. Starting weather station...")

    def run_script():
        # Redirect stdout and stderr to GUI
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = TextRedirector(log_message)
        sys.stderr = TextRedirector(log_message)

        try:
            temperature._main()
            log_message("✅ Weather station script finished.")
        except Exception as e:
            log_message(f"❌ Error: {e}")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            start_btn.configure(state=NORMAL)

    threading.Thread(target=run_script, daemon=True).start()

# ---------- GUI Layout ----------

app = ttk.Window(themename="darkly")  # Themes: darkly, flatly, superhero, etc.
app.title("🌦️ Weather Station")
app.geometry("700x500")
app.minsize(500, 350)

# Title
title = ttk.Label(app, text="Weather Station Launcher", font=("Helvetica", 20, "bold"))
title.pack(pady=(20, 10))

# Start Button
start_btn = ttk.Button(app, text="Start Weather Station", bootstyle=PRIMARY, command=start_weather_station)
start_btn.pack(pady=10)

# Output Log Area
logbox = ttk.ScrolledText(app, height=15, font=("Courier", 10), state="disabled")
logbox.pack(fill=BOTH, expand=True, padx=10, pady=10)

log_message("🟢 Ready. Connect ESP32 and press 'Start Weather Station'.")

app.mainloop()
