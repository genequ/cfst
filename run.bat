@echo off
if exist result.csv del result.csv
python cfst_scheduler.py --schedule
