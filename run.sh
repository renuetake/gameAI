#!/bin/sh

echo "rm -rf breakout/screenshot"
rm -rf breakout/screenshot

echo "mkdir model/checkpoint"
mkdir model/checkpoint

echo "mkdir breakout/screenshot"
mkdir breakout/screenshot

echo "python run.py"
python run.py