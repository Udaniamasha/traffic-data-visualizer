# Traffic Data Analysis & Visualization Tool 

## Overview
A Python-based application designed to analyze traffic survey data stored in CSV format. The tool processes raw logs to calculate statistics (vehicle types, speed violations, weather impact) and visualizes hourly traffic volume using a custom-built Histogram GUI.

## Features
- **Data Parsing:** Reads and cleanses complex CSV traffic logs.
- **Statistical Reporting:** Automatically generates a `results.txt` file summarizing total vehicles, truck percentages, and peak hours.
- **Interactive GUI:** Uses **Tkinter** to draw dynamic histograms comparing traffic volume between junctions.
- **Input Validation:** Robust error handling for dates and file formats.

## How to Run
1. Ensure Python 3.x is installed.
2. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/traffic-data-analyzer.git
3. Run the script:
   ```bash
   python main.py
4. When prompted, enter the date 01 01 2024 (to use the provided sample file).
## Technologies Used
- Python 3
- Tkinter (for GUI/Graphs)
- CSV Module
- Error Handling & Data Validation
