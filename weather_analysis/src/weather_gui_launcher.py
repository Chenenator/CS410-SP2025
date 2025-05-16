## @file weather_gui_launcher.py
#  @brief GUI launcher for the ESP32-based weather station using ttkbootstrap.
#  @details Provides a user-friendly interface to trigger the weather data logging
#  script (`temperature.py`) and display log output directly in a scrollable text widget.
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import serial.tools.list_ports
import threading
import temperature
import sys
import io

## @class TextRedirector
#  @brief Redirects standard output/error streams to the GUI's log display.
#  @details Custom `TextIOBase` subclass that pushes terminal output into the Tkinter GUI.
class TextRedirector(io.TextIOBase):

    ## @brief Constructor
    #  @param log_function Callback that handles writing log messages to the GUI.
    def __init__(self, log_function):
        self.log = log_function

    ## @brief Writes messages to the GUI log box.
    #  @param msg The string message to display.
    def write(self, msg):
        if msg.strip():
            self.log(msg.strip())

## @brief Appends log messages to the GUI output box.
#  @param msg The message to display.
def log_message(msg):
    logbox.configure(state='normal')
    logbox.insert(ttk.END, msg + '\n')
    logbox.see(ttk.END)
    logbox.configure(state='disabled')

## @brief Starts the weather station by detecting ESP32 and running the script.
#  @details Checks if ESP32 is connected via serial, runs `temperature._main()` in a thread,
#  and redirects stdout/stderr to the GUI logbox.
def start_weather_station():
    ports = list(serial.tools.list_ports.comports())
    esp_connected = any("COM" in port.device for port in ports)

    if not esp_connected:
        messagebox.showerror("ESP32 Not Found", "❌ No ESP32 device found. Please connect it.")
        log_message("❌ Error: No ESP32 device found. Please connect it.")
        return

    start_btn.configure(state=DISABLED)
    log_message("✅ ESP32 detected. Starting weather station...")

    ## @brief Inner thread function to run the weather station script.
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
## @var app
#  @brief Main Tkinter window using ttkbootstrap theme.
app = ttk.Window(themename="darkly")  # Themes: darkly, flatly, superhero, etc.
app.title("🌦️ Weather Station")
app.geometry("700x500")
app.minsize(500, 350)

## @var title
#  @brief GUI title label.
title = ttk.Label(app, text="Weather Station Launcher", font=("Helvetica", 20, "bold"))
title.pack(pady=(20, 10))

## @var start_btn
#  @brief Button to trigger ESP32 data collection and logging.
start_btn = ttk.Button(app, text="Start Weather Station", bootstyle=PRIMARY, command=start_weather_station)
start_btn.pack(pady=10)

## @var logbox
#  @brief Scrollable text area to show real-time log output.
logbox = ttk.ScrolledText(app, height=15, font=("Courier", 10), state="disabled")
logbox.pack(fill=BOTH, expand=True, padx=10, pady=10)

log_message("🟢 Ready. Connect ESP32 and press 'Start Weather Station'.")

app.mainloop()
