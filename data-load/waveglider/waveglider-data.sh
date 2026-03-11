#!/bin/bash

# --- Configuration ---
# Save to a 'waveglider' folder in the CURRENT directory, not the root.
OUTPUT_DIR="waveglider"
SCRIPTS=("waveglider-adcp.py" "waveglider-amps.py" "waveglider-telemetry.py" "waveglider-waves.py" "waveglider-weather.py")
VEHICLE="486778344"
START_DATE="2025-09-17T00:00:00Z"
# Use a static end date for consistency or use the dynamic one below
#END_DATE="2025-09-24T00:00:00Z" 
# #!/bin/bash

# # --- Configuration ---
# # Save to a 'waveglider' folder in the CURRENT directory, not the root.
# OUTPUT_DIR="waveglider"
# SCRIPTS=("waveglider-adcp.py" "waveglider-amps.py" "waveglider-telemetry.py" "waveglider-waves.py" "waveglider-weather.py")
# VEHICLE="486778344"
# #START_DATE="2025-09-17T00:00:00Z"
# START_DATE=$(date -v-7d +%Y-%m-%dT%TZ)
# # Use a static end date for consistency or use the dynamic one below
# #END_DATE="2025-09-24T00:00:00Z" 
# END_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ") # Use this for "now"

# # --- Execution ---
# mkdir -p "$OUTPUT_DIR" # Create the output folder if it doesn't exist

# # Loop through each script, run it, and save the output
# for script in "${SCRIPTS[@]}"; do
#   output_file="$OUTPUT_DIR/${script%.py}.json"
#   echo "Running $script -> saving to $output_file"
#   python3 "$script" --getReportData --vehicle "$VEHICLE" --startDate "$START_DATE" --endDate "$END_DATE" > "$output_file"
# done

# echo "All scripts have finished."

#!/bin/bash

# --- Configuration ---
# Save to a 'waveglider' folder in the CURRENT directory.
OUTPUT_DIR="waveglider"
SCRIPTS=("waveglider-adcp.py" "waveglider-amps.py" "waveglider-telemetry.py" "waveglider-waves.py" "waveglider-weather.py")
VEHICLE="486778344"

# --- Loop Configuration ---
# The first day to fetch data for.
LOOP_START_DATE="2025-10-16"
# The last day to fetch data for. Fetches up to (but not including) today.
# Add one day to today for LOOP_END_DATE (exclusive)
LOOP_END_DATE=$(date -j -v+1d +"%Y-%m-%d")

# --- Execution ---
mkdir -p "$OUTPUT_DIR" # Create the main output folder if it doesn't exist

current_date="$LOOP_START_DATE"

# Loop from LOOP_START_DATE until the processing date reaches LOOP_END_DATE
while [[ "$current_date" < "$LOOP_END_DATE" ]]; do

  # Define the start and end times for the current day's 24-hour period
  day_start="${current_date}T00:00:00Z"
  
  # Calculate the next day for the end date (exclusive)
  # This uses macOS/BSD 'date' syntax. See note below for Linux.
  next_date=$(date -j -v+1d -f "%Y-%m-%d" "$current_date" +"%Y-%m-%d")
  day_end="${next_date}T00:00:00Z"

  echo "--- Processing data for $current_date ---"

  # Loop through each script, run it for the current day, and save the output
  for script in "${SCRIPTS[@]}"; do
    # Modify the output filename to include the date prefix
    output_file="$OUTPUT_DIR/${script%.py}_${current_date}.json"
    echo "  Running $script -> saving to $output_file"
    python3 "$script" --getReportData --vehicle "$VEHICLE" --startDate "$day_start" --endDate "$day_end" > "$output_file"
  done
  
  # Move to the next date for the next loop iteration
  current_date="$next_date"
done

echo "All daily processing is complete."END_DATE=$(date +"%Y-%m-%dT%H:%M:%SZ") # Use this for "now"

# --- Execution ---
mkdir -p "$OUTPUT_DIR" # Create the output folder if it doesn't exist

# Loop through each script, run it, and save the output
for script in "${SCRIPTS[@]}"; do
  output_file="$OUTPUT_DIR/${script%.py}.json"
  echo "Running $script -> saving to $output_file"
  python3 "$script" --getReportData --vehicle "$VEHICLE" --startDate "$START_DATE" --endDate "$END_DATE" > "$output_file"
done

echo "All scripts have finished."
