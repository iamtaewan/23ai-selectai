#!/bin/bash

# Find and kill all processes started with "streamlit run"
pkill -9 -f "streamlit run app.py"

# Optional: Confirm if all processes have been terminated
if pgrep -f "streamlit run" > /dev/null; then
    echo "Some Streamlit processes are still running."
else
    echo "All Streamlit processes have been terminated."
fi