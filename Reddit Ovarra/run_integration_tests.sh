#!/bin/bash

# Script to run integration tests
# Starts the API server, runs tests, then stops the server

echo "Starting API server..."
cd "$(dirname "$0")"

# Start server in background
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Waiting for server to be ready..."
sleep 5

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "Server is ready!"
else
    echo "Server failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Run integration tests
echo ""
echo "Running integration tests..."
python3 test_integration.py
TEST_EXIT_CODE=$?

# Stop server
echo ""
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "Done!"
exit $TEST_EXIT_CODE
