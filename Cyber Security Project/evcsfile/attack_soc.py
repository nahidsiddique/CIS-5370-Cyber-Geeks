# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 19:18:05 2023

@author: mhaider
"""

import ast
from datetime import datetime

file_path = "received_messages_CP_1.txt"

output_folder = "matlab_simulation"
output_path = f"{output_folder}/received_messages_CP_1.txt"

# Open the input file in read mode
with open(file_path, 'r') as file:
    # Read each line in the file
    lines = file.readlines()

# Open the output file in write mode
with open(output_path, 'w') as output_file:
    # Write the header line to the output file
    output_file.write(lines[0])

    # Iterate through the lines, starting from the second line (skipping the header)
    for line in lines[1:]:
        # Split the line into timestamp and message
        timestamp_str, message_str = line.strip().split(" - ", 1)

        # Convert the message string to a Python dictionary using ast.literal_eval
        message_dict = ast.literal_eval(message_str)

        # Update the 'capacity' value to 40
        message_dict['custom_data']['capacity'] = 40

        # Convert timestamp string to datetime object
        timestamp = datetime.fromisoformat(timestamp_str)

        # Format the timestamp to save only the time part (HH:MM:SS)
        formatted_time = timestamp.strftime('%H:%M:%S')

        # Print the timestamp and updated capacity
        print(f"Timestamp: {formatted_time}, SoC Level: {message_dict['custom_data']['capacity']}")

        # Convert the updated message dictionary back to a string
        updated_message_str = str(message_dict)

        # Write the updated line to the output file
        output_file.write(f"{formatted_time} - {updated_message_str}\n")

print("File has been modified and saved to:", output_path)
