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
        self.edit_mode = False  # Flag to indicate if we are editing an existing stop
        
        self.title_label = tk.Label(root, text="TSP for Accessible Public Transit", font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.input_frame = tk.Frame(root)
        self.input_frame.pack(pady=10)
        
        self.name_label = tk.Label(self.input_frame, text="Stop Name")
        self.name_label.grid(row=0, column=0, padx=5, pady=5)
        self.x_label = tk.Label(self.input_frame, text="Latitude")
        self.x_label.grid(row=0, column=1, padx=5, pady=5)
        self.y_label = tk.Label(self.input_frame, text="Longitude")
        self.y_label.grid(row=0, column=2, padx=5, pady=5)
        
        self.name_entry = tk.Entry(self.input_frame)
        self.name_entry.grid(row=1, column=0, padx=5, pady=5)
        self.x_entry = tk.Entry(self.input_frame)
        self.x_entry.grid(row=1, column=1, padx=5, pady=5)
        self.y_entry = tk.Entry(self.input_frame)
        self.y_entry.grid(row=1, column=2, padx=5, pady=5)
        
        self.add_button = tk.Button(self.input_frame, text="Add Stop", command=self.add_stop)
        self.add_button.grid(row=1, column=3, padx=5, pady=5)
        
        self.edit_button = tk.Button(self.input_frame, text="Edit Selected Stop", command=self.edit_stop)
        self.edit_button.grid(row=2, column=0, padx=5, pady=5, columnspan=1)
        
        self.delete_button = tk.Button(self.input_frame, text="Delete Selected Stop", command=self.delete_stop)
        self.delete_button.grid(row=2, column=1, padx=5, pady=5, columnspan=1)
        
        self.calculate_button = tk.Button(self.input_frame, text="Calculate Optimal Route", command=self.calculate_route)
        self.calculate_button.grid(row=2, column=2, padx=5, pady=5, columnspan=2)
        
        self.stops_list = tk.Listbox(root, width=50)
        self.stops_list.pack(pady=10)

        self.save_button = tk.Button(root, text="Save Data", command=self.save_data)
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.load_button = tk.Button(root, text="Load Data", command=self.load_data)
        self.load_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def add_stop(self):
        name = self.name_entry.get()
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid coordinates")
            return
        
        if self.edit_mode:
            selected_index = self.stops_list.curselection()
            if selected_index:
                index = selected_index[0]
                self.stops_list.delete(index)
                del self.stops[index]
        
        self.stops.append((name, x, y))
        self.stops_list.insert(tk.END, f"{name}: ({x}, {y})")
        
        self.name_entry.delete(0, tk.END)
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)
        
        self.edit_mode = False  # Reset edit mode after adding

    def edit_stop(self):
        selected_index = self.stops_list.curselection()
        if not selected_index:
            messagebox.showerror("No Selection", "Please select a stop to edit")
            return
        
        index = selected_index[0]
        selected_stop = self.stops[index]
        
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(tk.END, selected_stop[0])
        
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(tk.END, str(selected_stop[1]))
        
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(tk.END, str(selected_stop[2]))
        
        self.edit_mode = True  # Enter edit mode

    def delete_stop(self):
        selected_index = self.stops_list.curselection()
        if not selected_index:
            messagebox.showerror("No Selection", "Please select a stop to delete")
            return
        
        index = selected_index[0]
        self.stops_list.delete(index)
        del self.stops[index]

    def calculate_route(self):
        if len(self.stops) < 2:
            messagebox.showerror("Insufficient Data", "Please add at least two stops")
            return
        
        names, coordinates = zip(*[(stop[0], (stop[1], stop[2])) for stop in self.stops])
        distance_matrix = np.array([[euclidean(a, b) for b in coordinates] for a in coordinates])

        row_ind, col_ind = linear_sum_assignment(distance_matrix)
        
        ordered_stops = [names[i] for i in col_ind]
        
        self.show_route(ordered_stops)

    def show_route(self, ordered_stops):
        coordinates = [(self.stops[idx][1], self.stops[idx][2]) for idx, name in enumerate(ordered_stops)]
        coordinates.append(coordinates[0])  # return to the start

        # Initialize the map centered around the first stop
        m = folium.Map(location=coordinates[0], zoom_start=14)
        
        # Add the stops to the map
        for name, coord in zip(ordered_stops, coordinates):
            folium.Marker(location=coord, popup=name).add_to(m)
        
        # Add the route to the map
        folium.PolyLine(locations=coordinates, color='blue').add_to(m)

        # Save the map to an HTML file and open it in the default browser
        map_file = "tsp_route_map.html"
        m.save(map_file)
        webbrowser.open(map_file)

    def save_data(self):
        if not self.stops:
            messagebox.showerror("No Data", "There is no data to save")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Stop Name", "Latitude", "Longitude"])
                for stop in self.stops:
                    writer.writerow(stop)
            messagebox.showinfo("Data Saved", "Data has been saved successfully")

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # skip header
                self.stops = []
                self.stops_list.delete(0, tk.END)
                for row in reader:
                    name, x, y = row
                    self.stops.append((name, float(x), float(y)))
                    self.stops_list.insert(tk.END, f"{name}: ({x}, {y})")
            messagebox.showinfo("Data Loaded", "Data has been loaded successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = TSPApp(root)
    root.mainloop()