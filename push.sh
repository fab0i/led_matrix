#!/bin/sh

sudo git fetch;
sudo git pull;
sudo git add *;
sudo git commit -m "Internal push by script";
sudo git push;
