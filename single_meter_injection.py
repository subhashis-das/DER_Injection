import tkinter as tk
import requests
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# Global variables to store time and power data for {selected_meter}
selected_meter = "trip_meter1" 
time_data = {f"trip_meter{i}": [] for i in range(1, 14)}

power_data = {f"trip_meter{i}": [] for i in range(1, 14)}

is_injecting = False  # Flag to control continuous injection
injection_interval = 2  # Default injection interval (in seconds)

# Function to fetch the current measured_real_power from the server for {selected_meter}
def fetch_current_value():
    try:
        response = requests.get(f"http://localhost:6267/json/{selected_meter}/*")
        if response.status_code == 200:
            data = response.json()
            value = data
            power = 0
            for item in value:
                if 'clock' in item:
                    current_time = item['clock']
                if 'measured_real_power' in item:
                    power = item['measured_real_power']
                    break
            
            # Append the current time (in days) and value to the data lists
            current_time = datetime.datetime.utcfromtimestamp(int(current_time))
            formatted_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
            time_data[selected_meter].append(formatted_time)
            power_data[selected_meter].append(float(power.replace(" W", "").replace("+", "")))  # Convert to float
            update_plot()
            current_value_label["{selected_meter}"].config(text=f"Current {selected_meter}: {power}")
    except requests.RequestException as e:
        current_value_label["{selected_meter}"].config(text=f"Error: {e}")

# Function to update the plot for {selected_meter}
def update_plot():
    ax.clear()  # Clear the previous plot
    ax.plot(time_data[selected_meter][-5:], power_data[selected_meter][-5:], label=selected_meter+" (W)", color='blue')
    ax.set_xlabel("Time")
    ax.set_ylabel("Power (W)")
    ax.set_title(f"{selected_meter} Power Over Time")
    ax.legend()
    canvas.draw()  # Redraw the plot

# Function to inject the new value for {selected_meter}
def set_new_value():
    value = power_entry.get()  # Get the value entered in the input field
    try:
        # Send the new value to {selected_meter}
        response = requests.get(f"http://localhost:6267/json/{selected_meter}/measured_real_power={value} W")
        if response.status_code == 200:
            success_label.config(text=f"Successfully set value to {value} W for {selected_meter}", fg="green")
        else:
            success_label.config(text="Failed to set value.", fg="red")
    except requests.RequestException as e:
        success_label.config(text=f"Error: {e}", fg="red")

# Function to continuously inject the value at regular intervals
def inject_continuously():
    if is_injecting:
        value = power_entry.get()  # Get the value from the entry field
        try:
            # Send the new value to {selected_meter}
            response = requests.get(f"http://localhost:6267/json/{selected_meter}/measured_real_power={value} W")
            if response.status_code == 200:
                # Display the message "Injecting {value}W"
                success_label.config(text=f"Injecting {value}W at {injection_interval}s", fg="blue")
            else:
                success_label.config(text="Failed to inject value.", fg="red")
        except requests.RequestException as e:
            success_label.config(text=f"Error: {e}", fg="red")
        
        # Schedule the next injection based on the selected interval
        root.after(injection_interval * 1000, inject_continuously)  # Inject every x seconds

# Function to toggle the injection process (start/stop)
def toggle_injection():
    global is_injecting
    if is_injecting:
        # Stop injection
        is_injecting = False
        inject_button.config(text="Start Continuous Injection")
        success_label.config(text="Injection stopped.", fg="orange")
    else:
        # Start injection
        is_injecting = True
        inject_button.config(text="Stop Injection")
        inject_continuously()  # Start continuous injection immediately

# Function to update the injection interval based on the selected value from the dropdown
def update_injection_interval(*args):
    global injection_interval
    injection_interval = int(injection_interval_var.get())  # Update the interval

# Function to periodically fetch the current value for {selected_meter} every second
def periodic_update():
    fetch_current_value()
    root.after(1000, periodic_update)  # Schedule the next update in 1 second

# Function to update the selected trip meter
def update_trip_meter(*args):
    global selected_meter
    selected_meter = f"{trip_meter_var.get()}"
    print(selected_meter," is the selected meter")
    fetch_current_value()  # Fetch the current value for the selected meter
    

# Create the main window
root = tk.Tk()
root.title("Measured Real Power Visualization")

# Create the label, canvas, and other widgets for {selected_meter}
current_value_label = {}

# Create a figure and axis for the {selected_meter} plot
fig, ax = plt.subplots(figsize=(15, 5))  # Single plot for {selected_meter}

# Create a label to display the current measured_real_power value for {selected_meter}
current_value_label["{selected_meter}"] = tk.Label(root, text="Current {selected_meter}: N/A", font=("Arial", 12))
current_value_label["{selected_meter}"].pack(pady=5)

# Create a canvas to embed the plot for {selected_meter}
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=20)

# Create an input field to enter the power value (in watts)
power_entry_label = tk.Label(root, text="Enter Power Value (W):", font=("Arial", 14))
power_entry_label.pack(pady=5)
power_entry = tk.Entry(root, font=("Arial", 12))
power_entry.pack(pady=5)

# Create a submit button to set the new value for {selected_meter}
submit_button = tk.Button(root, text="Submit", font=("Arial", 14), command=set_new_value)
submit_button.pack(pady=10)

# Create a frame to hold the "Start Continuous Injection" button and the dropdown
frame_inject = tk.Frame(root)
frame_inject.pack(pady=10)

# Create a button to start or stop injecting values continuously
inject_button = tk.Button(frame_inject, text="Start Continuous Injection", font=("Arial", 14), command=toggle_injection)
inject_button.grid(row=0, column=0, padx=5)

trip_meter_var = tk.StringVar(root)
trip_meter_var.set("trip_meter1")  # Default value (trip_meter_1)

trip_meter_dropdown = tk.OptionMenu(root, trip_meter_var, *["trip_meter"+str(i) for i in range(1, 14)], command=update_trip_meter)
trip_meter_dropdown.pack(pady=10)



# Create a dropdown to select the injection interval (1, 2, 3, 4, 5 seconds)
injection_interval_var = tk.StringVar(root)
injection_interval_var.set("2")  # Default value

injection_interval_dropdown = tk.OptionMenu(frame_inject, injection_interval_var, "1", "2", "3", "4", "5", command=update_injection_interval)
injection_interval_dropdown.grid(row=0, column=1, padx=5)

# Create a label to display success or error messages
success_label = tk.Label(root, text="", font=("Arial", 10))
success_label.pack(pady=10)

# Initialize the start time for time conversion (when the program starts)
start_time = time.time()

# Start the periodic update for {selected_meter
periodic_update()

# Handle window close event
root.protocol("WM_DELETE_WINDOW", lambda: root.quit())

# Start the GUI main loop
root.mainloop()
