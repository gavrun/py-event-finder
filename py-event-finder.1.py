# TBD

import os
import re
from datetime import datetime

# Function to recursively find log files matching a filename pattern
def find_log_files(root_folder, filename_pattern):
    matching_files = []
    # Walk through the directory tree rooted at root_folder
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            # Check if the filename matches the given pattern
            if re.match(filename_pattern, filename):
                matching_files.append(os.path.join(dirpath, filename))
    return matching_files

# Function to extract multiple patterns from files
def extract_patterns_from_files(files, patterns):
    # Initialize a dictionary to store extracted data for each pattern
    extracted_data = {name: [] for name in patterns}
    
    # Iterate over each file
    for file_path in files:
        with open(file_path, 'r') as file:
            # Read each line in the file
            for line in file:
                # Attempt to match each pattern in the line
                for name, pattern in patterns.items():
                    match = re.search(pattern, line)
                    if match:
                        extracted_data[name].append(match.group(1))
    
    return extracted_data

# Customizable logic functions. What ever you need to find out and understand from logs goes to Main function from here as Logic functions.
def process_extracted_data(extracted_data):
    # Convert extracted timestamps into datetime objects
    datetime_objects = {
        'start': [(datetime.strptime(ts, "%d.%m.%Y %H:%M:%S.%f"), "Start") for ts in extracted_data['start']],
        'finish': [(datetime.strptime(ts, "%d.%m.%Y %H:%M:%S.%f"), "Finish") for ts in extracted_data['finish']],
        'synth': [datetime.strptime(ts, "%d.%m.%Y %H:%M:%S.%f") for ts in extracted_data['synth']],
        'complete': [datetime.strptime(ts, "%d.%m.%Y %H:%M:%S.%f") for ts in extracted_data['complete']],
        'retention': [datetime.strptime(ts, "%d.%m.%Y %H:%M:%S.%f") for ts in extracted_data['retention']]
        # If a new pattern is added, you need to add it here as well
        # Example: 'new_event': [datetime.strptime(ts, "%d.%m.%Y %H:%M:%S.%f") for ts in extracted_data['new_event']]
    }
    
    # Combine 'start' and 'finish' events and sort them
    combined_events = datetime_objects['start'] + datetime_objects['finish']
    combined_events.sort(key=lambda x: x[0])

    # Extract the day of the week for each event
    week_days = [dt.strftime("%A") for dt, _ in combined_events]

    # Check if the date matches day of the week. Example: Synthetic full schedule for the first Monday of the month.
    first_monday_flags = []
    for dt, _ in combined_events:
        if dt.strftime("%A") == "Monday" and dt.day <= 7:
            first_monday_flags.append("First Monday")
        else:
            first_monday_flags.append("")

    # Check if the event date matches any 'synth' dates
    synth_flags = []
    for dt, _ in combined_events:
        match_found = any(synth_dt.date() == dt.date() for synth_dt in datetime_objects['synth'])
        if match_found:
            synth_flags.append("Synth")
        else:
            synth_flags.append("")

    # Check if the event date matches any 'complete' dates
    complete_flags = []
    for dt, _ in combined_events:
        match_found = any(complete_dt.date() == dt.date() for complete_dt in datetime_objects['complete'])
        if match_found:
            complete_flags.append("Complete")
        else:
            complete_flags.append("")

    # Check if the event date matches any 'retention' dates
    retention_flags = []
    for dt, _ in combined_events:
        match_found = any(retention_dt.date() == dt.date() for retention_dt in datetime_objects['retention'])
        if match_found:
            retention_flags.append("Retention")
        else:
            retention_flags.append("")

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
    
    # Print the results with appropriate flags
    for ts, event, wd, fm, rf, sf, cf in output_data:
        output = f"{ts}, {event}, {wd}"
        if fm:
            output += f", {fm}"
        if rf:
            output += f", {rf}"
        if sf:
            output += f", {sf}" 
        if cf:
            output += f", {cf}"   
        print(output)

# Main function 
def main():
    root_folder = 'E:\\share\\2024-08-14T074507_VeeamBackupLogs'  # Replace with root folder path
    filename_pattern = r".*Task.*"  # Pattern to match .log files
    
    # Define patterns for extraction from logs and add new timestamp patterns
    patterns = {
        'start': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*Processing object",
        'finish': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*has been completed, status",
        'synth': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*Creating synthetic full backup",
        'complete': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*Synthetic full backup created successfully",
        'retention': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*\[RetentionAlgorithm\] Storages to delete"
        # If you add a new timestamp pattern, you need to include it here
        # Example: 'new_event': r"\[(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\].*New event description"
    }
    
    # Find log files
    log_files = find_log_files(root_folder, filename_pattern)
    
    # Extract patterns from files
    extracted_data = extract_patterns_from_files(log_files, patterns)
    
    # Process the extracted data with custom logic
    process_extracted_data(extracted_data)

# Execute the main function
if __name__ == "__main__":
    main()
