import tkinter as tk
import requests
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# Global variables to store time and power data for each trip meter
time_data = {f"trip_meter{i}": [] for i in range(1, 16)}
power_data = {f"trip_meter{i}": [] for i in range(1, 16)}

# Function to fetch the current measured_real_power for all trip meters
def fetch_current_value():
    for i in range(1, 16):
        selected_meter = f"trip_meter{i}"
        try:
            response = requests.get(f"http://localhost:6267/json/{selected_meter}/*")
            if response.status_code == 200:
                data = response.json()
                power = 0
                for item in data:
                    if 'clock' in item:
                        current_time = item['clock']
                    if 'measured_real_power' in item:
                        power = item['measured_real_power']
                        break
                
                # Convert the timestamp to a formatted datetime string
                current_time = datetime.datetime.utcfromtimestamp(int(current_time))
                formatted_time = current_time.strftime("%d/%m %H:%M:%S")
                
                # Append the current time and power value to the respective lists
                time_data[selected_meter].append(formatted_time)
                power_data[selected_meter].append(float(power.replace(" W", "").replace("+", "")))  # Convert to float
                
        except requests.RequestException as e:
            print(f"Error fetching data for {selected_meter}: {e}")

# Function to update the plot for all trip meters
def update_plot():
    for i in range(15):
        meter = f"trip_meter{i+1}"
        ax = axes[i]
        ax.clear()  # Clear the previous plot
        ax.plot(time_data[meter][-3:], power_data[meter][-3:], label=f"{meter} (W)", color='blue')
        ax.set_xlabel("Time", fontsize=5) 
        ax.set_ylabel("Power (W)", fontsize=5)
        ax.set_title(f"{meter} Power Over Time", fontsize=10)  # Set smaller font size for title
        ax.legend(fontsize=8)  # Set smaller font size for legend
    
    canvas.draw()  # Redraw the canvas with all plots

# Create the main window
root = tk.Tk()
root.title("Measured Real Power Visualization")

# Create a figure and axes for 15 trip meters in a 5x3 grid
fig, axes = plt.subplots(5, 3, figsize=(15, 15))  # 5 rows and 3 columns of plots
axes = axes.flatten()  # Flatten the 2D array of axes for easier indexing

# Adjust the spacing between plots
plt.subplots_adjust(hspace=0.5, wspace=0.5)  # Increase space between plots

# Create a canvas to embed the plots
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=20)

# Function to periodically fetch the current value for all trip meters
def periodic_update():
    fetch_current_value()  # Fetch data for all trip meters
    update_plot()  # Update the plots with the new data
    root.after(1000, periodic_update)  # Schedule the next update in 1 second (adjust as needed)

# Initialize the periodic update for the plots
periodic_update()

# Handle window close event
root.protocol("WM_DELETE_WINDOW", lambda: root.quit())

# Start the GUI main loop
root.mainloop()
