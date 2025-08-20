#!/bin/bash

echo "EduPlan AI - Lesson Plan Generation System"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed"
    echo "Please install Python 3.9 or later and try again."
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import qdrant_client" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing dependencies. Please check requirements.txt"
        exit 1
    fi
fi

echo
echo "Select an option:"
echo "1. Start API server"
echo "2. Ingest sample documents"
echo "3. Generate a sample lesson plan"
echo "4. Exit"
echo

read -p "Enter your choice (1-4): " option

case $option in
    1)
        echo "Starting API server..."
        python3 src/main.py api
        ;;
    2)
        echo "Ingesting sample documents..."
        python3 src/main.py ingest data/sample_documents
        read -p "Press Enter to continue..."
        ;;
    3)
        read -p "Enter lesson plan query: " query
        read -p "Enter class filter (1-12, or leave empty): " class
        read -p "Enter subject filter (or leave empty): " subject
        
        if [ -n "$class" ] && [ -n "$subject" ]; then
            echo "Generating lesson plan..."
            python3 src/main.py generate "$query" --class-filter $class --subject-filter $subject
        elif [ -n "$class" ]; then
            echo "Generating lesson plan..."
            python3 src/main.py generate "$query" --class-filter $class
        else
            echo "Generating lesson plan..."
            python3 src/main.py generate "$query"
        fi
        read -p "Press Enter to continue..."
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option."
        read -p "Press Enter to continue..."
        ;;
esac

exit 0
