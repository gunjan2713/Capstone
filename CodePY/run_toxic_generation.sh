#!/bin/bash
# Helper script to generate toxic 2020 election data

echo "================================================"
echo "Toxic Content Generator for 2020 US Election"
echo "================================================"
echo ""

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY environment variable is not set."
    echo ""
    echo "Please set it using one of these methods:"
    echo ""
    echo "Method 1: Export for this session"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo "  python3 generate_toxic_election2020.py"
    echo ""
    echo "Method 2: Set inline when running"
    echo "  OPENAI_API_KEY='your-key-here' python3 generate_toxic_election2020.py"
    echo ""
    echo "Method 3: Pass as argument"
    echo "  python3 generate_toxic_election2020.py --api-key 'your-key-here'"
    echo ""
    read -p "Enter your OpenAI API key (or press Ctrl+C to cancel): " api_key
    if [ -z "$api_key" ]; then
        echo "No API key provided. Exiting."
        exit 1
    fi
    export OPENAI_API_KEY="$api_key"
    echo "✓ API key set for this session"
    echo ""
fi

# Get number of tweets from user or use default
if [ -z "$1" ]; then
    NUM_TWEETS=15000
    echo "Using default: 15,000 tweets"
else
    NUM_TWEETS=$1
    echo "Generating $NUM_TWEETS tweets"
fi

echo ""
echo "Starting generation..."
echo "This will take approximately $((NUM_TWEETS / 2 / 60)) minutes"
echo "Press Ctrl+C to stop at any time (progress will be saved)"
echo ""

# Run the generator
python3 generate_toxic_election2020.py --num-tweets "$NUM_TWEETS"

echo ""
echo "================================================"
echo "Generation complete!"
echo "Check election2020_toxic_synthetic.csv"
echo "================================================"



