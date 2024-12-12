import re

def remove_timestamps(input_file, output_file=None):
    # Regular expression to match the timestamp at the beginning of the line
    timestamp_pattern = r'^[^:]*: '

    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Remove the timestamp from each line
    cleaned_lines = [re.sub(timestamp_pattern, '', line) for line in lines]

    # If output_file is provided, write the cleaned data to the output file
    if output_file:
        with open(output_file, 'w') as outfile:
            outfile.writelines(cleaned_lines)
    else:
        # Otherwise, overwrite the original file
        with open(input_file, 'w') as infile:
            infile.writelines(cleaned_lines)

    print(f"Processed file saved as {output_file if output_file else input_file}")

# Example usage:
input_file = '2024-08-15_Helios_DLB_BMWixIsoMon_IP_4_ID_50.json'
output_file = 'cleaned_2024-08-15_Helios_DLB_BMWixIsoMon_IP_4_ID_50.json'  # Optional, can leave as None to overwrite

remove_timestamps(input_file, output_file)
