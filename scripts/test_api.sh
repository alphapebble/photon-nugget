#!/bin/bash
# Test script for Solar Sage API

# Set default values
HOST="localhost"
PORT="8000"
LAT="37.7749"
LON="-122.4194"
LOCATION_ID="home"
SYSTEM_CAPACITY="5.0"
ELECTRICITY_RATE="0.25"
FEED_IN_TARIFF="0.10"

# Function to display usage information
usage() {
    echo "Usage: $0 [options] <test_name>"
    echo ""
    echo "Options:"
    echo "  -h, --host HOST          API host (default: localhost)"
    echo "  -p, --port PORT          API port (default: 8000)"
    echo "  -l, --lat LATITUDE       Latitude (default: 37.7749)"
    echo "  -o, --lon LONGITUDE      Longitude (default: -122.4194)"
    echo "  -i, --id LOCATION_ID     Location ID (default: home)"
    echo "  -c, --capacity CAPACITY  System capacity in kW (default: 5.0)"
    echo "  -e, --rate RATE          Electricity rate in currency per kWh (default: 0.25)"
    echo "  -f, --feed-in RATE       Feed-in tariff in currency per kWh (default: 0.10)"
    echo "  --help                   Display this help message"
    echo ""
    echo "Test Names:"
    echo "  health                   Test the health endpoint"
    echo "  chat                     Test the basic chat endpoint"
    echo "  weather-chat             Test the weather-enhanced chat endpoint"
    echo "  solar-chat               Test the solar-enhanced chat endpoint"
    echo "  solar-forecast           Test the solar forecast endpoint"
    echo "  all                      Run all tests"
    echo ""
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -l|--lat)
            LAT="$2"
            shift 2
            ;;
        -o|--lon)
            LON="$2"
            shift 2
            ;;
        -i|--id)
            LOCATION_ID="$2"
            shift 2
            ;;
        -c|--capacity)
            SYSTEM_CAPACITY="$2"
            shift 2
            ;;
        -e|--rate)
            ELECTRICITY_RATE="$2"
            shift 2
            ;;
        -f|--feed-in)
            FEED_IN_TARIFF="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            TEST_NAME="$1"
            shift
            ;;
    esac
done

# Check if test name is provided
if [ -z "$TEST_NAME" ]; then
    echo "Error: No test name provided"
    usage
fi

# Base URL
BASE_URL="http://$HOST:$PORT"

# Function to test the health endpoint
test_health() {
    echo "Testing health endpoint..."
    curl -X GET "$BASE_URL/"
    echo ""
}

# Function to test the basic chat endpoint
test_chat() {
    echo "Testing basic chat endpoint..."
    curl -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d "{
            \"query\": \"What factors affect solar panel efficiency?\"
        }"
    echo ""
}

# Function to test the weather-enhanced chat endpoint
test_weather_chat() {
    echo "Testing weather-enhanced chat endpoint..."
    curl -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d "{
            \"query\": \"How will the weather affect my solar production today?\",
            \"lat\": $LAT,
            \"lon\": $LON,
            \"include_weather\": true
        }"
    echo ""
}

# Function to test the solar-enhanced chat endpoint
test_solar_chat() {
    echo "Testing solar-enhanced chat endpoint..."
    curl -X POST "$BASE_URL/chat" \
        -H "Content-Type: application/json" \
        -d "{
            \"query\": \"How much solar energy can I expect to produce tomorrow?\",
            \"lat\": $LAT,
            \"lon\": $LON,
            \"include_weather\": true,
            \"location_id\": \"$LOCATION_ID\",
            \"system_capacity_kw\": $SYSTEM_CAPACITY,
            \"electricity_rate\": $ELECTRICITY_RATE,
            \"feed_in_tariff\": $FEED_IN_TARIFF,
            \"include_solar_forecast\": true
        }"
    echo ""
}

# Function to test the solar forecast endpoint
test_solar_forecast() {
    echo "Testing solar forecast endpoint..."
    curl -X POST "$BASE_URL/solar/forecast" \
        -H "Content-Type: application/json" \
        -d "{
            \"latitude\": $LAT,
            \"longitude\": $LON,
            \"location_id\": \"$LOCATION_ID\",
            \"system_capacity_kw\": $SYSTEM_CAPACITY
        }"
    echo ""
}

# Run the specified test
case "$TEST_NAME" in
    health)
        test_health
        ;;
    chat)
        test_chat
        ;;
    weather-chat)
        test_weather_chat
        ;;
    solar-chat)
        test_solar_chat
        ;;
    solar-forecast)
        test_solar_forecast
        ;;
    all)
        test_health
        echo ""
        test_chat
        echo ""
        test_weather_chat
        echo ""
        test_solar_chat
        echo ""
        test_solar_forecast
        ;;
    *)
        echo "Error: Unknown test name '$TEST_NAME'"
        usage
        ;;
esac
