# Import necessary libraries for GUI, numerical operations, map visualization, and file handling
import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
from scipy.spatial.distance import euclidean
from scipy.optimize import linear_sum_assignment
import csv
import folium
import webbrowser

class TSPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TSP for Accessible Public Transit")
        
        self.stops = []
        self.edit_mode = False
        
        # Create and configure main frame
        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        self.title_label = tk.Label(self.main_frame, text="TSP for Accessible Public Transit", font=("Arial", 15, "bold"))
        self.title_label.pack(pady=10)
        
        # Input frame
        self.input_frame = tk.Frame(self.main_frame)
        self.input_frame.pack(pady=10, padx=10, fill=tk.BOTH)
        
        # Labels and entries for stop details
        self.name_label = tk.Label(self.input_frame, text="Stop Name", font=("Arial", 11))
        self.name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.x_label = tk.Label(self.input_frame, text="Latitude", font=("Arial", 11))
        self.x_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        self.y_label = tk.Label(self.input_frame, text="Longitude", font=("Arial", 11))
        self.y_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        self.name_entry = tk.Entry(self.input_frame, font=("Arial", 11))
        self.name_entry.grid(row=1, column=0, padx=5, pady=5)
        
        self.x_entry = tk.Entry(self.input_frame, font=("Arial", 11))
        self.x_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.y_entry = tk.Entry(self.input_frame, font=("Arial", 11))
        self.y_entry.grid(row=1, column=2, padx=5, pady=5)
        
        # Buttons for actions
        self.add_button = tk.Button(self.input_frame, text="Add Stop", command=self.add_stop, font=("Arial", 11))
        self.add_button.grid(row=1, column=3, padx=10, pady=5, sticky="w")
        
        self.edit_button = tk.Button(self.input_frame, text="Edit Selected", command=self.edit_stop, font=("Arial", 11))
        self.edit_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.delete_button = tk.Button(self.input_frame, text="Delete Selected", command=self.delete_stop, font=("Arial", 11))
        self.delete_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        self.calculate_button = tk.Button(self.input_frame, text="Calculate Route", command=self.calculate_route, font=("Arial", 11))
        self.calculate_button.grid(row=2, column=2, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Listbox to display stops
        self.stops_list = tk.Listbox(self.main_frame, font=("Arial", 11), width=60, height=10)
        self.stops_list.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Save and load buttons
        self.save_button = tk.Button(self.main_frame, text="Save Data", command=self.save_data, font=("Arial", 11))
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.load_button = tk.Button(self.main_frame, text="Load Data", command=self.load_data, font=("Arial", 11))
        self.load_button.pack(side=tk.RIGHT, padx=10, pady=10)

    # Method to add a stop to the list
    def add_stop(self):
        name = self.name_entry.get()
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid coordinates")
            return
        
        # If in edit mode, delete the selected stop from the list and GUI
        if self.edit_mode:
            selected_index = self.stops_list.curselection()
            if selected_index:
                index = selected_index[0]
                self.stops_list.delete(index)
                del self.stops[index]
        
        # Add the new stop to the list and GUI
        self.stops.append((name, x, y))
        self.stops_list.insert(tk.END, f"{name}: ({x}, {y})")
        
        # Clear input fields after adding stop
        self.name_entry.delete(0, tk.END)
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)
        
        # Reset edit mode after adding
        self.edit_mode = False

    # Method to edit an existing stop
    def edit_stop(self):
        selected_index = self.stops_list.curselection()
        if not selected_index:
            messagebox.showerror("No Selection", "Please select a stop to edit")
            return
        
        index = selected_index[0]
        selected_stop = self.stops[index]
        
        # Populate input fields with current stop information for editing
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(tk.END, selected_stop[0])
        
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(tk.END, str(selected_stop[1]))
        
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(tk.END, str(selected_stop[2]))
        
        # Set edit mode to true
        self.edit_mode = True

    # Method to delete a selected stop
    def delete_stop(self):
        selected_index = self.stops_list.curselection()
        if not selected_index:
            messagebox.showerror("No Selection", "Please select a stop to delete")
            return
        
        index = selected_index[0]
        self.stops_list.delete(index)
        del self.stops[index]

    # Method to calculate the optimal route using the Hungarian algorithm
    def calculate_route(self):
        if len(self.stops) < 2:
            messagebox.showerror("Insufficient Data", "Please add at least two stops")
            return
        
        # Extract names and coordinates of stops
        names, coordinates = zip(*[(stop[0], (stop[1], stop[2])) for stop in self.stops])
        
        # Create distance matrix using Euclidean distances between coordinates
        distance_matrix = np.array([[euclidean(a, b) for b in coordinates] for a in coordinates])

        # Use the Hungarian algorithm to find optimal route
        row_ind, col_ind = linear_sum_assignment(distance_matrix)
        
        # Arrange stops in the optimal order
        ordered_stops = [names[i] for i in col_ind]
        
        # Display the optimal route on the map
        self.show_route(ordered_stops)

    # Method to visualize the route on an interactive map
    def show_route(self, ordered_stops):
        # Extract coordinates of stops in the optimal order
        coordinates = [(self.stops[idx][1], self.stops[idx][2]) for idx, name in enumerate(ordered_stops)]
        
        # Ensure the route returns to the starting point
        coordinates.append(coordinates[0])

        # Initialize the map centered around the first stop
        m = folium.Map(location=coordinates[0], zoom_start=14)
        
        # Add markers for each stop on the map
        for name, coord in zip(ordered_stops, coordinates):
            folium.Marker(location=coord, popup=name).add_to(m)
        
        # Add a polyline connecting all stops to represent the route
        folium.PolyLine(locations=coordinates, color='blue').add_to(m)

        # Save the map to an HTML file and open it in the default web browser
        map_file = "tsp_route_map.html"
        m.save(map_file)
        webbrowser.open(map_file)

    # Method to save current stop data to a CSV file
    def save_data(self):
        if not self.stops:
            messagebox.showerror("No Data", "There is no data to save")
            return
        
        # Ask user for file path to save CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            # Write stop data to CSV file
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Stop Name", "Latitude", "Longitude"])
                for stop in self.stops:
                    writer.writerow(stop)
            
            # Confirm successful data save
            messagebox.showinfo("Data Saved", "Data has been saved successfully")

    # Method to load stop data from a CSV file
    def load_data(self):
        # Ask user to select a CSV file to load data from
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            # Read stop data from selected CSV file
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # skip header row
                self.stops = []
                self.stops_list.delete(0, tk.END)
                for row in reader:
                    name, x, y = row
                    self.stops.append((name, float(x), float(y)))
                    self.stops_list.insert(tk.END, f"{name}: ({x}, {y})")
            
            # Confirm successful data load
            messagebox.showinfo("Data Loaded", "Data has been loaded successfully")

# Main program entry point
if __name__ == "__main__":
    # Create and run the TSP application GUI
    root = tk.Tk()
    app = TSPApp(root)
    root.mainloop()