#!/bin/bash

sudo apt-get install figlet

figlet -f small "Installing Dependencies"

sudo apt-get install python-webkit-dev

sudo apt-get install python-pip

sudo pip install pySmartDL

mkdir ZeroNet_Browser

cd ZeroNet_Browser

wget https://github.com/amol1000/ZeroNet_Browser/archive/master.zip

unzip master.zip

figlet -f small "ZERONET BORWSER INSTALLED"
