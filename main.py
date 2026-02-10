# Author: M.V.U Amasha
# Date: 24/12/2024
# Student ID: w2120299

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import csv
import os
from collections import defaultdict
from datetime import datetime

def validate_date_input():
    """
    Validates user input for a date in the format DD MM YYYY and checks for the existence of the corresponding CSV file.

    This function ensures robust validation of user input by:
    - Confirming that the inputs are numeric and within valid ranges:
        - Day: 1–31
        - Month: 1–12
        - Year: 2000–2024
    - Handling edge cases like invalid dates (e.g., February 30 or non-leap years).
    - Verifying the existence of a file named in the format 'traffic_dataDDMMYYYY.csv'.
    - If more than one file is present for the same day, gives options to user to chose which file is intended to be processed.
    If the input is valid and the file exists, the file path is returned. Otherwise, the user is prompted to correct their input.

    Returns:
        str: The validated file path of the traffic data CSV file or None if no file selected/error in inputs.
    """
    while True:
        try:
            # Request date inputs with clear guidance for format and valid ranges
            day = input("Please enter the day of the survey in the format DD (1-31): ").strip()

            # Check if the day is numeric and within the valid range
            if not day.isdigit():
                print("Integer required. Please enter a numeric value for the day.")
                continue
            day = int(day)  # Convert day to integer for comparison
            if not (1 <= day <= 31):
                print("Out of range. Please enter a day between 01 and 31.")
                continue

            month = input("Please enter the month of the survey in the format MM (1-12): ").strip()

            # Check if the month is numeric and within the valid range
            if not month.isdigit():
                print("Integer required. Please enter a numeric value for the month.")
                continue
            month = int(month)  # Convert month to integer for comparison
            if not (1 <= month <= 12):
                print("Out of range. Please enter a month between 01 and 12.")
                continue

            year = input("Please enter the year of the survey in the format YYYY (2000-2024): ").strip()

            # Check if the year is numeric and within the valid range
            if not year.isdigit():
                print("Integer required. Please enter a numeric value for the year.")
                continue
            year = int(year)  # Convert year to integer for comparison
            if not (2000 <= year <= 2024):
                print("Out of range. Please enter a year between 2000 and 2024.")
                continue
            

            # Validate the date using datetime to handle leap years and invalid dates
            try:
                date_str = datetime(year, month, day).strftime("%d%m%Y")  # Format as DDMMYYYY
            except ValueError:
                print("Invalid date. Please ensure the date exists (e.g., not February 30).")
                continue

            # Construct the expected file path
            file_prefix = "traffic_data"
            file_path_to_find = f"{file_prefix}{date_str}.csv"

            # Check if the file exists in the working directory and list the options
            files_found = [f for f in os.listdir('./') if f.endswith('.csv') and file_path_to_find in f]
            if not files_found:
              print(f"File with the given date '{file_path_to_find}'  not found. Please, verify your date and file name convention")
              continue
            if len(files_found) > 1:
                print(f"Multiple files found for {date_str}:")
                for i, file in enumerate(files_found, start=1):
                    print(f"{i}. {file}")
                while True:
                    try:
                        choice = int(input(f"Select a file (1-{len(files_found)}): ").strip()) - 1
                        if 0 <= choice < len(files_found):
                            selected_file = files_found[choice]
                            return os.path.join('./', selected_file), date_str
                        else:
                           print(f"Invalid choice. Please select a number between 1 and {len(files_found)}")
                    except ValueError:
                           print(f"Invalid input. Please enter a valid number between 1 and {len(files_found)}")
            else:
                 return os.path.join('./', files_found[0]), date_str

        except Exception as e:
            # Catch unexpected errors for debugging
            print(f"An unexpected error occurred: {e}. Please try again.")
            return None

def process_csv_data(file_path):
    """
    Processes traffic data from a specified CSV file and calculates key metrics.

    This function analyzes vehicle traffic data to generate a comprehensive summary of traffic patterns, 
    vehicle types, speed violations, and weather conditions. It performs the following tasks:
    - Reads data from the provided CSV file.
    - Aggregates counts of various vehicle types (trucks, bikes, electric vehicles).
    - Tracks speed limit violations.
    - Identifies traffic trends specific to key junctions (e.g., Elm Avenue, Hanley Junction).
    - Calculates metrics such as:
        - Total vehicles, trucks, bikes, and electric vehicles.
        - Percentage of scooters at Elm Avenue and trucks overall.
        - Peak traffic hours at Hanley Junction.
        - Average bicycles per hour and rain hours.
    - Handles incomplete or invalid data gracefully by skipping problematic rows.

    Args:
        file_path (str): The path to the traffic data CSV file.

    Returns:
        dict: A dictionary containing aggregated totals, calculated metrics, and detailed analysis results.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        RuntimeError: For any processing errors during analysis.
    """
    
    # Verify that the file exists before proceeding
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Initialize a dictionary to track totals for each category
    totals = {
        'total_vehicles': 0,
        'total_trucks': 0,
        'total_bikes': 0,
        'total_electric_vehicles': 0,
        'total_no_turn': 0,
        'total_speed_violations': 0,
        'total_rain_hours': 0,
        'total_elm_road': 0,
        'total_hanley_road': 0,
        'total_buses_north': 0,
        'total_scooters_elm': 0,
        'total_bicycle': 0,
    }
    # Dictionary to store counts for each hour at Hanley Junction
    hanley_counts_per_hour = {}
    # Set to track hours with bicycle activity
    bicycle_hours = set()
    # To store unique hours with rain
    rain_hours = set()  

    try:
        # Open the CSV file for reading
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            # Parse the CSV into a dictionary format for easy access to column names
            for row in reader:
                try:
                    # Extract and sanitize individual data fields from the current row
                    junction_name = row.get('JunctionName', '').strip()
                    travel_in = row.get('travel_Direction_in', '').strip()
                    travel_out = row.get('travel_Direction_out', '').strip()
                    vehicle_speed = int(row.get('VehicleSpeed', 0))
                    vehicle_type = row.get('VehicleType', '').strip()
                    is_electric = row.get('elctricHybrid', '').strip().lower() == "true"
                    weather_condition = row.get('Weather_Conditions', '').lower()
                    speed_limit = int(row.get('JunctionSpeedLimit', 0))
                    hour = row.get('timeOfDay', '00:00').split(':')[0]

                    # Update overall vehicle count
                    totals['total_vehicles'] += 1

                    # Count specific vehicle types
                    if vehicle_type == "Truck":
                        totals['total_trucks'] += 1
                    if vehicle_type in ["Bicycle", "Motorcycle", "Scooter"]:
                        totals['total_bikes'] += 1
                    if is_electric:
                        totals['total_electric_vehicles'] += 1
                    if travel_in == travel_out:
                        totals['total_no_turn'] += 1
                        
                    # Count speed violations    
                    if vehicle_speed > speed_limit:
                        totals['total_speed_violations'] += 1
                        
                    # Track rain hours based on weather conditions
                    if "rain" in weather_condition:
                        rain_hours.add(hour)    

                    # Specific processing for Elm Avenue  
                    if junction_name == "Elm Avenue/Rabbit Road":
                        totals['total_elm_road'] += 1
                        if travel_out == "N" and vehicle_type == "Buss":
                            totals['total_buses_north'] += 1
                        if vehicle_type == "Scooter":
                            totals['total_scooters_elm'] += 1

                    # Specific processing for Hanley Junction        
                    elif junction_name == "Hanley Highway/Westway":
                        totals['total_hanley_road'] += 1
                        hanley_counts_per_hour[hour] = hanley_counts_per_hour.get(hour, 0) + 1

                    # Track hours with bicycle activity
                    if vehicle_type == "Bicycle":
                        totals['total_bicycle'] += 1
                        bicycle_hours.add(hour)    

                except (ValueError, KeyError):
                    continue # Skip rows with incomplete or invalid data fields

        # Total rain hours
        totals['total_rain_hours'] = len(rain_hours)        

        # Calculate averages and percentages
        avg_bikes_per_hour = round(totals['total_bicycle'] / len(bicycle_hours)) if bicycle_hours else 0
        percentage_scooters_elm = round((totals['total_scooters_elm'] / totals['total_elm_road']) * 100) if totals['total_elm_road'] > 0 else 0
        percentage_trucks = round((totals['total_trucks'] / totals['total_vehicles']) * 100)

        # Identify peak traffic hours for Hanley Junction
        max_count = max(hanley_counts_per_hour.values(), default=0)
        peak_hours = [hour for hour, count in hanley_counts_per_hour.items() if count == max_count]
        peak_hour_ranges = [f"Between {hour}:00 and {int(hour)+1}:00" for hour in peak_hours]

        # Return results as a structured dictionary
        return {
            'file': file_path,
            'totals': totals,
            'avg_bikes_per_hour': avg_bikes_per_hour,
            'percentage_scooters_elm': percentage_scooters_elm,
            'percentage_trucks': percentage_trucks,
            'peak_hour_ranges': peak_hour_ranges,
            'hanley_counts_per_hour': hanley_counts_per_hour,
        }

    except Exception as e:
        # Raise an error for unexpected issues during processing
        raise RuntimeError(f"Error processing the file: {e}")

  
#  Task D: Histogram Display 

class HistogramApp:
    def __init__(self, traffic_data, date):
        """
        Initializes the histogram application with the traffic data and selected date.
        - traffic_data: List of dictionaries containing traffic data to be visualized.
        - date: The specific date for which the histogram is generated.
        """
        self.traffic_data = traffic_data
        self.date = date
        self.root = tk.Tk()  # Main Tkinter root window
        self.canvas = None  # Will hold the canvas for drawing
        self.canvas_width = 1300  # Customize based on data
        self.canvas_height = 500
        self.setup_window()  # Initializes the window layout and structure

    def setup_window(self):
        """
        Sets up the Tkinter window and canvas for drawing the histogram.
        - Initializes the window title, canvas, and calls methods to process data and draw the histogram.
        """
        self.root.title(f"Traffic Data Histogram - {self.date}")
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()  # Packs the canvas widget into the window
        self.process_data()  # Processes the traffic data
        self.draw_axes()  # Draws the x and y axes on the canvas
        self.draw_histogram()  # Draws the histogram bars
        self.add_legend()  # Adds the legend for the junctions

    def process_data(self):
        """
        Processes traffic data to count hourly volumes for each junction.
        - Initializes a dictionary to store traffic counts for each hour of the day and junction.
        - Iterates through the traffic data to populate this dictionary.
        """
        self.hourly_counts = {hour: {"Elm Avenue/Rabbit Road": 0, "Hanley Highway/Westway": 0} for hour in range(24)}

        for row in self.traffic_data:
            try:
                hour = int(row['timeOfDay'].split(':')[0])  # Extract hour from timeOfDay
                junction = row['JunctionName']
                if junction in self.hourly_counts[hour]:
                    self.hourly_counts[hour][junction] += 1  # Increment the traffic count for the given junction
            except ValueError:
                continue  # Skips rows with invalid data

    def draw_axes(self):
        """
        Draws the x and y axes of the histogram.
        - The x-axis represents hours of the day.
        - The y-axis represents traffic volume, labeled appropriately.
        """
        x0, y0 = 50, self.canvas_height - 50  # Starting coordinates for the axes
        x_end, y_end = self.canvas_width - 50, 50  # Ending coordinates for the axes

        # Drawing the axes lines
        self.canvas.create_line(x0, y0, x0, y_end, width=2)
        self.canvas.create_line(x0, y0, x_end, y0, width=2)
        
        # Labels for the axes
        self.canvas.create_text(25, (y0 + y_end) // 2, text="Traffic Volume", angle=90, font=("Helvetica", 14, "bold"))
        self.canvas.create_text((x0 + x_end) / 2, y0 + 40, text="Hours 00:00 to 24:00", font=("Helvetica", 10, "bold"))

    def draw_histogram(self):
        """
        Draws the histogram bars for traffic volume, with appropriate labels and scaling.
        - The histogram will have two bars per hour, one for each junction.
        - The bars' heights are proportional to the traffic volume.
        """
        bar_width = 20  # Width of each bar in the histogram
        gap = 1  # Gap between bars
        pair_gap = 10  # Gap between pairs of bars (one for each junction)
        max_count = max(max(counts.values()) for counts in self.hourly_counts.values())  # Find max traffic count

        x_offset = 70  # Initial horizontal offset for the first bar
        scale = (self.canvas_height - 150) / (max_count + 1) if max_count else 0  # Scale factor to adjust bar height based on max count
        colors = {"Elm Avenue/Rabbit Road": "gray", "Hanley Highway/Westway": "lightblue"}  # Colors for each junction

        # Loop through each hour and its corresponding traffic counts
        for hour, counts in self.hourly_counts.items():
            x = x_offset + hour * (bar_width * 2 + gap + pair_gap)  # Calculate x position for each hour's bars
            for junction, count in counts.items():
                y = self.canvas_height - 50 - count * scale  # Calculate y position based on the count
                color = colors[junction]  # Get the color for the junction
                self.canvas.create_rectangle(x - bar_width / 2, y, x + bar_width / 2, self.canvas_height - 50, fill=color, outline="black")
                self.canvas.create_text(x, y - 10, text=str(count), anchor=tk.S)  # Add text label showing the count
                x += bar_width + gap  # Move x position for the next bar
            # Add text label below the bars for each hour
            self.canvas.create_text(x_offset + hour * (bar_width * 2 + gap + pair_gap) + bar_width, self.canvas_height - 30, text=f"{hour:02d}:00", anchor=tk.N)

    def add_legend(self):
        """
        Adds a legend to the histogram to explain the color coding for junctions.
        - Displays colored boxes and their corresponding junction names.
        """
        legend_x, legend_y = self.canvas_width - 160, 50  # Starting position for the legend
        marker_size = 15  # Size of the color markers
        text_spacing = 20  # Vertical spacing between legend entries
        junctions = {"Elm Avenue/Rabbit Road": "gray", "Hanley Highway/Westway": "lightblue"}  # Junction names and their colors

        for junction, color in junctions.items():
            # Draw colored square marker for each junction
            self.canvas.create_rectangle(legend_x, legend_y, legend_x + marker_size, legend_y + marker_size, fill=color, outline="black")
            self.canvas.create_text(legend_x + marker_size + 5, legend_y + marker_size / 2, text=junction, anchor=tk.W)  # Label next to the marker
            legend_y += text_spacing  # Move down for the next legend entry

    def run(self):
        """
        Starts the Tkinter main loop to display the histogram.
        - Ensures the application window remains open to show the histogram.
        """
        self.root.mainloop()


#Task E: Code Loops to Handle Multiple CSV Files

class MultiCSVProcessor:
    def __init__(self):
        """
        Initializes the application for processing multiple CSV files.
        - Sets up an initial state where the current data is empty.
        """
        self.current_data = None  # Holds the currently loaded traffic data

    def load_csv_file(self, file_path):
        """
        Loads a CSV file and processes its data into a list of dictionaries.
        - file_path: The path to the CSV file to be loaded.
        - Returns a list of dictionaries containing the traffic data.
        """
        traffic_data = []
        try:
            with open(file_path, mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    traffic_data.append(row)  # Add each row to the traffic data list
            # Check if the CSV file is empty and print a message if so
            if not traffic_data:
                print(f"No data found in {file_path}.")
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")  # Print any error that occurs during file loading
        return traffic_data  # Return the loaded data

    def clear_previous_data(self):
        """
        Clears data from the previous run to process a new dataset.
        - Resets the current data to None before loading new data.
        """
        self.current_data = None

    def handle_user_interaction(self):
        """
        Handles user input for processing multiple files and loading CSV data.
        - Validates the date input, loads the file, and processes it.
        - Offers the user an option to load another dataset or exit.
        """
        while True:
            result = validate_date_input()  # Calls the date validation function
            if result:
                file_path, date_input = result  # Extracts the file path and date from the user input
                self.current_data = self.load_csv_file(file_path)  # Loads the selected file

                try:
                    # Process the CSV data and generate an analysis report
                    analysis_report = process_csv_data(file_path)

                    
                    with open('results.txt', 'w') as results_file:
                    
                        totals = analysis_report['totals']  # Contains totals for various categories (e.g., total vehicles)
                        outcomes = analysis_report  # Contains the full analysis report
                        hanley_counts_per_hour = analysis_report['hanley_counts_per_hour']  # Traffic counts per hour at Hanley Highway/Westway
                        outcomes_list = [
                            f"***************************",
                            f"Data file analyzed: {outcomes['file']}",  # Name of the data file analyzed
                            f"***************************\n",
                            f"The total number of vehicles recorded on the selected date: {totals['total_vehicles']}",  # Total vehicles
                            f"The total count of trucks passing through all junctions: {totals['total_trucks']}",  # Total trucks
                            f"The total count of electric vehicles recorded: {totals['total_electric_vehicles']}",  # Total electric vehicles
                            f"The total number of two-wheeled vehicles (bicycles, motorcycles, scooters): {totals['total_bikes']}",  # Total bikes
                            f"The total number of buses heading north from Elm Avenue/Rabbit Road junction: {totals['total_buses_north']}",  # Buses heading north
                            f"The total number of vehicles traveling straight through both junctions without turning: {totals['total_no_turn']}",  # Straight-through vehicles
                            f"The percentage of all recorded vehicles that are trucks: {outcomes['percentage_trucks']}%",  # Percentage of trucks
                            f"The average number of bicycles recorded per hour: {outcomes['avg_bikes_per_hour']}\n",  # Average bikes per hour
                            f"The total number of vehicles exceeding the speed limit: {totals['total_speed_violations']}",  # Total speed violations
                            f"The total number of vehicles recorded at Elm Avenue/Rabbit Road junction: {totals['total_elm_road']}",  # Total vehicles at Elm Avenue/Rabbit Road
                            f"The total number of vehicles recorded at Hanley Highway/Westway junction: {totals['total_hanley_road']}",  # Total vehicles at Hanley Highway/Westway
                            f"The percentage of vehicles at Elm Avenue/Rabbit Road that are scooters: {outcomes['percentage_scooters_elm']}%\n",  # Percentage of scooters at Elm Avenue/Rabbit Road
                            f"The highest number of vehicles recorded in a single hour at Hanley Highway/Westway: {max(hanley_counts_per_hour.values(), default=0)}",  # Maximum vehicles in an hour at Hanley Highway/Westway
                            f"The busiest traffic hours at Hanley Highway/Westway: {', '.join(outcomes['peak_hour_ranges'])}",  # Busiest hours at Hanley Highway/Westway
                            f"The total number of hours with rain on the selected date: {totals['total_rain_hours']}",  # Total hours with rain
                            "**************************************************"
                        ]
                        # Writing each line of the outcomes_list to the file
                        for line in outcomes_list:
                            results_file.write(f'{line}\n')  # Writes each line to the file with a newline character at the end

                    print("Analysis Report saved to results.txt")  # Inform the user that the report was saved

                except FileNotFoundError as e:
                    print(f"Error: {e}")  # Handles file not found error
                    continue
                except RuntimeError as e:
                    print(f"Error during processing: {e}")  # Handles runtime errors during processing
                    continue

                # Initialize and run the histogram app for the selected data
                app = HistogramApp(self.current_data, date_input)
                app.run()

                while True:
                    another_file = input("Do you want to select a data file for a different date? (Y/N): ").strip().lower()
                    if another_file == 'n':
                        print("Exiting program.")  # Inform the user that the program will exit
                        return
                    elif another_file == 'y':
                        self.clear_previous_data()  # Clear the current data for the next file
                        print("Loading another file...")  # Inform the user that a new file will be loaded 
                        break
                    else:
                        print("Invalid input. Please enter 'Y' or 'N'.")  # Handle invalid input      
        
            else:
                print("File selection canceled or an error occurred during date/file input. Trying Again")  # Debugging message
                continue

    def process_files(self):
        """
        Main loop for handling multiple CSV files until the user decides to quit.
        - Handles the loading, processing, and visualization of each file selected by the user.
        """
        self.clear_previous_data()  # Clears any previous data before starting the process
        self.handle_user_interaction()  # Handles user interaction for selecting files


# Main Execution
if __name__ == "__main__":
    processor = MultiCSVProcessor()  # Creates an instance of MultiCSVProcessor
    processor.process_files()  # Starts the process of handling multiple CSV files
   
