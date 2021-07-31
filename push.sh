#!/bin/sh

git fetch;
git pull;
git add *;
git commit -m "Internal push by script";
git push;
