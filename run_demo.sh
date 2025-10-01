#!/bin/bash

# Healthcare Payor AI System - Demo Launcher
# This script helps launch and manage demo sessions

echo "🏥 Healthcare Payor AI System - Demo Launcher"
echo "=============================================="
echo ""

# Check if app is running
check_app_status() {
    if curl -s http://localhost:8503 > /dev/null 2>&1; then
        echo "✅ App is running on http://localhost:8503"
        return 0
    else
        echo "❌ App is not running"
        return 1
    fi
}

# Start the app if not running
start_app() {
    echo "🚀 Starting the Healthcare Payor AI System..."
    ./start_mcp_app.sh &
    echo "⏳ Waiting for app to start..."
    sleep 10
    
    if check_app_status; then
        echo "✅ App started successfully!"
    else
        echo "❌ Failed to start app"
        exit 1
    fi
}

# Run demo script
run_demo() {
    echo "🎬 Starting demo script..."
    python3 demo_script.py
}

# Open browser
open_browser() {
    echo "🌐 Opening browser..."
    if command -v open > /dev/null; then
        open http://localhost:8503
    elif command -v xdg-open > /dev/null; then
        xdg-open http://localhost:8503
    else
        echo "Please open http://localhost:8503 in your browser"
    fi
}

# Show demo options
show_options() {
    echo "Demo Options:"
    echo "1. Check app status"
    echo "2. Start app"
    echo "3. Run interactive demo script"
    echo "4. Open browser to app"
    echo "5. Show demo guide"
    echo "6. Exit"
    echo ""
}

# Main menu
main_menu() {
    while true; do
        show_options
        read -p "Select option (1-6): " choice
        
        case $choice in
            1)
                check_app_status
                ;;
            2)
                start_app
                ;;
            3)
                if check_app_status; then
                    run_demo
                else
                    echo "❌ App not running. Please start it first."
                fi
                ;;
            4)
                if check_app_status; then
                    open_browser
                else
                    echo "❌ App not running. Please start it first."
                fi
                ;;
            5)
                echo "📖 Opening demo guide..."
                if command -v open > /dev/null; then
                    open DEMO_TRACK.md
                elif command -v xdg-open > /dev/null; then
                    xdg-open DEMO_TRACK.md
                else
                    echo "Please open DEMO_TRACK.md to view the demo guide"
                fi
                ;;
            6)
                echo "👋 Demo launcher ended. Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please select 1-6."
                ;;
        esac
        
        echo ""
        echo "Press Enter to continue..."
        read
        clear
    done
}

# Check if we're in the right directory
if [ ! -f "enhanced_healthcare_payor_app_mcp.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Make demo script executable
chmod +x demo_script.py

# Start main menu
main_menu
