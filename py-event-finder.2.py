# TBD

import os
import re
from datetime import datetime

# Convert timestamp and try catch wrong regex

def convert_to_datetime(timestamp):
    return datetime.strptime(timestamp, "%d.%m.%Y %H:%M:%S.%f")  # Convert timestamp to datetime object

def match_pattern(line, pattern):
    try:
        return re.search(pattern, line)  # Match a line against the given regex pattern
    except re.error as e:
        print(f"Regex error: {e}")
        return None

# Find and open log files, try catch io issues

def find_log_files(root_folder, filename_pattern):
    matching_files = []
    for dirpath, _, filenames in os.walk(root_folder): # Walk through the directory tree rooted at root_folder and check if the filename matches the given pattern
        for filename in filenames:
            if re.match(filename_pattern, filename): 
                matching_files.append(os.path.join(dirpath, filename))  # Add matching files to the list
    return matching_files

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.readlines()  # Read all lines from a log file
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return []

# Extract multiple patterns from files

def extract_patterns_from_files(files, patterns):
    extracted_data = {name: [] for name in patterns}  # Initialize storage for extracted data
    for file_path in files: # Iterate over each file, read each line, attempt to match each pattern in the line
        lines = read_file(file_path)
        for line in lines:
            for name, pattern in patterns.items():
                match = match_pattern(line, pattern)
                if match:
                    extracted_data[name].append(match.group(1))  # Store matched data
    return extracted_data

# Process extracted data (for whatever you need to find out and understand from logs)

def process_extracted_data(extracted_data):
    # Convert extracted timestamps into datetime objects
    datetime_objects = {
        'start': [(convert_to_datetime(ts), "Start") for ts in extracted_data['start']],
        'finish': [(convert_to_datetime(ts), "Finish") for ts in extracted_data['finish']],
        'synth': [convert_to_datetime(ts) for ts in extracted_data['synth']],
        'complete': [convert_to_datetime(ts) for ts in extracted_data['complete']],
        'retention': [convert_to_datetime(ts) for ts in extracted_data['retention']]
        # Add a new entry here for additional timestamp patterns
        # Example: 'new_event': [datetime.strptime(ts, "%d.%m.%Y %H:%M:%S.%f") for ts in extracted_data['new_event']]
    }
    
    combined_events = datetime_objects['start'] + datetime_objects['finish']  # Combine 'start' and 'finish' events
    combined_events.sort(key=lambda x: x[0])  # Sort events by timestamp
    
    # Get the day of the week for each event
    week_days = [dt.strftime("%A") for dt, _ in combined_events]  
    
    # Check if the date matches day of the week. Example: Synthetic full schedule for the first Monday of the month.
    first_monday_flags = ["First Monday" if dt.strftime("%A") == "Monday" and dt.day <= 7 else "" for dt, _ in combined_events]
    
    # Check if the event date matches any 'synth' dates
    synth_flags = ["Synth" if any(synth_dt.date() == dt.date() for synth_dt in datetime_objects['synth']) else "" for dt, _ in combined_events]
    
    # Check if the event date matches any 'complete' dates
    complete_flags = ["Complete" if any(complete_dt.date() == dt.date() for complete_dt in datetime_objects['complete']) else "" for dt, _ in combined_events]
    
    # Check if the event date matches any 'retention' dates
    retention_flags = ["Retention" if any(retention_dt.date() == dt.date() for retention_dt in datetime_objects['retention']) else "" for dt, _ in combined_events]

    # Example Output: Combine all flags into the final output
    output_data = list(zip(
        [dt.strftime("%d.%m.%Y %H:%M:%S.%f") for dt, _ in combined_events],
        [event for _, event in combined_events],
        week_days,
        first_monday_flags,
        synth_flags,
        complete_flags,
        retention_flags
    ))
    
    for ts, event, wd, fm, sf, cf, rf in output_data: # Output the results with appropriate flags
        output = f"{ts}, {event}, {wd}"
        if fm:
            output += f", {fm}"
        if sf:
            output += f", {sf}"
        if cf:
            output += f", {cf}"   
        if rf:
            output += f", {rf}"   
        print(output)
        # Add a new entry here when additional timestamp patterns added

# Main function

def main():
    # Define root folder path where logs unpacked
    root_folder = 'E:\\share\\2024-08-14T074507_VeeamBackupLogs'
    # Define pattern for finding specific log files
    filename_pattern = r".*Task.*"  
    
    # Define patterns for extraction from logs and add new timestamp patterns
    patterns = {
        'start': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*Processing object",
        'finish': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*has been completed, status",
        'synth': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*Creating synthetic full backup",
        'complete': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*Synthetic full backup created successfully",
        'retention': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*\[RetentionAlgorithm\] Storages to delete"
        # Add a new entry here for additional patterns
        # Example: 'new_event': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*new event text from log line"
    }
    
    log_files = find_log_files(root_folder, filename_pattern)
    extracted_data = extract_patterns_from_files(log_files, patterns)
    process_extracted_data(extracted_data)

if __name__ == "__main__":
    main()
