#!/bin/bash

# Loads of comments for educational purpouses :)

BIN=/usr/local/bin
CS=~/.cheatsheet

# Ask for the administrator password upfront
sudo -v &> /dev/null
#     | └─ hide output
#     └─ version

# Copy binary
sudo cp -i bin/cheatsheet ${BIN}
#        └─ interactive mode

# Create alias
sudo ln -si ${BIN}/cheatsheet ${BIN}/cs
#        |└─ interactive mode	
#        └─ symbolic

# Give execution rights to both
sudo chmod a+rx ${BIN}/cheatsheet ${BIN}/cs
#          | |└─ execution right
#          | └─ read right
#          └─ everybody

# Create cheatsheet directory
[ ! -d $CS ] && mkdir $CS
#    └─ directory exists

# Copy cheatsheets
cp -ri cheatsheets/. $CS
#   ||             └─ copy contents not the dir itself
#   |└─ interactive mode
#   └─ recursive