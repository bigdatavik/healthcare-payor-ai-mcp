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

# Stop the app
stop_app() {
    echo "🛑 Stopping the Healthcare Payor AI System..."
    # Kill any running streamlit processes (suppress output)
    pkill -f "streamlit run" 2>/dev/null
    pkill -f "enhanced_healthcare_payor_app_mcp.py" 2>/dev/null
    sleep 3
    
    if ! check_app_status; then
        echo "✅ App stopped successfully!"
    else
        echo "⚠️  App may still be running. Please check manually."
    fi
}

# Restart the app
restart_app() {
    echo "🔄 Restarting the Healthcare Payor AI System..."
    stop_app
    sleep 2
    start_app
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
    echo "3. Stop app"
    echo "4. Restart app"
    echo "5. Run interactive demo script"
    echo "6. Open browser to app"
    echo "7. Show sample test questions (UC Integration)"
    echo "8. Show demo guide"
    echo "9. Exit"
    echo ""
}

# Show sample test questions
show_test_questions() {
    echo ""
    echo "🧪 SAMPLE TEST QUESTIONS - Unity Catalog Integration"
    echo "===================================================="
    echo ""
    echo "These questions demonstrate how the AI agent can now seamlessly"
    echo "connect text documents with Unity Catalog member data:"
    echo ""
    echo "📋 MEMBER PROFILE QUESTIONS:"
    echo "• 'Tell me about member 1001 - what's their full profile?'"
    echo "• 'What is John Doe's plan type and when did it become effective?'"
    echo "• 'Show me member 1002's demographics and recent claims history'"
    echo ""
    echo "🔗 CROSS-REFERENCE QUESTIONS:"
    echo "• 'Member 1001 had a billing issue - what was their recent authorization about?'"
    echo "• 'Why was member 1002's claim denied? Check their prior authorization status'"
    echo "• 'Member 1003 appealed a surgery denial - what does their UC data show?'"
    echo ""
    echo "💰 CLAIMS & AUTHORIZATION CORRELATION:"
    echo "• 'Compare member 1001's paid claim with their approved prior authorization'"
    echo "• 'Member 1002 has a denied claim - what prior auth issues did they have?'"
    echo "• 'Show me the complete financial picture for member 1003'"
    echo ""
    echo "🏥 CLINICAL & ADMINISTRATIVE INTEGRATION:"
    echo "• 'Member 1001 called about CPT 99213 billing - check their plan coverage'"
    echo "• 'What's the status of member 1002's gallbladder surgery authorization and claims?'"
    echo "• 'Member 1003's knee surgery was denied - do they have other paid claims?'"
    echo ""
    echo "📊 ANALYTICS QUESTIONS:"
    echo "• 'Which members have both customer service issues and prior auth problems?'"
    echo "• 'Show me approval rates by member plan type (PLN101 vs PLN102)'"
    echo "• 'What's the correlation between member satisfaction and claim status?'"
    echo ""
    echo "🎯 BUSINESS INTELLIGENCE:"
    echo "• 'Identify members with high-value claims and authorization patterns'"
    echo "• 'Which plan type (PLN101/PLN102) has more billing disputes?'"
    echo "• 'Show member journey from authorization to claim to customer service'"
    echo ""
    echo "💡 ADVANCED SCENARIOS:"
    echo "• 'Member 1001 has multiple authorizations - are they for the same provider?'"
    echo "• 'Compare member 1002's urgent surgery request with their plan benefits'"
    echo "• 'Analyze member 1003's appeal timeline against their claim history'"
    echo ""
    echo "🔍 SPECIFIC DATA LOOKUPS:"
    echo "• 'What provider submitted the authorization for member 1001's preventive visit?'"
    echo "• 'Show me all interactions for member 1002 across all data sources'"
    echo "• 'Get complete timeline for member 1003 from first contact to resolution'"
    echo ""
    echo "To test these questions:"
    echo "1. Start the app (option 2)"
    echo "2. Open browser (option 4)"
    echo "3. Copy and paste these questions into the AI agent chat"
    echo "4. Observe how the agent uses both text documents AND UC data"
    echo ""
}

# Main menu
main_menu() {
    while true; do
        show_options
        read -p "Select option (1-9): " choice
        
        case $choice in
            1)
                check_app_status
                ;;
            2)
                start_app
                ;;
            3)
                stop_app
                ;;
            4)
                restart_app
                ;;
            5)
                if check_app_status; then
                    run_demo
                else
                    echo "❌ App not running. Please start it first."
                fi
                ;;
            6)
                if check_app_status; then
                    open_browser
                else
                    echo "❌ App not running. Please start it first."
                fi
                ;;
            7)
                show_test_questions
                ;;
            8)
                echo "📖 Opening demo guide..."
                if command -v open > /dev/null; then
                    open DEMO_GUIDE.md
                elif command -v xdg-open > /dev/null; then
                    xdg-open DEMO_GUIDE.md
                else
                    echo "Please open DEMO_GUIDE.md to view the demo guide"
                fi
                ;;
            9)
                echo "👋 Demo launcher ended. Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please select 1-9."
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
