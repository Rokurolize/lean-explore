#!/bin/bash

# Add potion_problem as a git submodule

echo "Adding potion_problem as a submodule..."

# Create external directory if it doesn't exist
mkdir -p external

# Add submodule (replace with actual Git URL)
# git submodule add https://github.com/[username]/potion_problem.git external/potion_problem

echo "Please provide the Git URL for potion_problem repository"
echo "Example: https://github.com/username/potion_problem.git"
read -p "Git URL: " GIT_URL

if [ -z "$GIT_URL" ]; then
    echo "Error: Git URL is required"
    exit 1
fi

# Add the submodule
git submodule add "$GIT_URL" external/potion_problem

# Initialize and update
git submodule update --init --recursive

# Update .env.example to use submodule path
sed -i 's|POTION_PROBLEM_PATH=.*|POTION_PROBLEM_PATH=./external/potion_problem|' .env.example

echo "Submodule added successfully!"
echo "Don't forget to update your .env file with the new path"