# Automatic result.csv Commit System

This system automatically commits the `result.csv` file to the GitHub repository's default branch each time the Cloudflare Speed Test runs.

## Overview

The automation system consists of:
- `cfst_scheduler.py` - Main Python script that handles the automation
- `auto_commit_result.bat` - Easy-to-use batch file for manual runs
- Git configuration for automatic upstream branch setup

## How It Works

1. **Cloudflare Speed Test Execution**: The script runs `cfst.exe` to perform speed tests
2. **Result File Processing**: The `result.csv` file is modified to:
   - Append port `8443` to IP addresses
   - Keep only the first 20 results
3. **Backup Creation**: A timestamped backup is created in the `cfst_backups` folder
4. **Git Operations**: 
   - Checks for changes to `result.csv`
   - Commits changes with a timestamped message
   - Pushes to the remote GitHub repository

## Usage

### Manual Run (Single Cycle)
```bash
# Using Python script directly
python cfst_scheduler.py --run-once

# Using batch file (recommended for Windows)
auto_commit_result.bat
```

### Scheduled Run (Every 12 Hours)
```bash
python cfst_scheduler.py --schedule
```

## Git Configuration

The system is configured to:
- Automatically set up upstream branches when pushing
- Handle network connectivity issues gracefully
- Timeout after 60 seconds if GitHub is unreachable

## Error Handling

The script includes robust error handling for:
- **Network connectivity issues**: If GitHub is unreachable, commits are still made locally and can be pushed manually later
- **Git configuration issues**: Automatically handles upstream branch setup
- **File processing errors**: Continues operation even if individual steps fail

## File Structure

```
.
├── cfst_scheduler.py      # Main automation script
├── auto_commit_result.bat # Easy batch file for manual runs
├── result.csv            # Current speed test results
├── cfst_backups/         # Timestamped backups of result files
└── AUTO_COMMIT_SETUP.md  # This documentation
```

## Requirements

- Python 3.x
- Git installed and configured
- `cfst.exe` in the same directory
- Network connectivity to GitHub (for automatic pushes)

## Troubleshooting

### Git Push Fails
If you see "Git push failed" messages:
1. Check your internet connection
2. Verify GitHub is accessible
3. The commit is still made locally - you can push manually later using:
   ```bash
   git push
   ```

### No Changes Detected
If the script reports "No changes to result.csv":
- This is normal if the speed test results haven't changed
- The script only commits when there are actual changes

### Manual Push
If automatic pushes fail, you can always push manually:
```bash
git push
```

## Automation Schedule

By default, the system runs every 12 hours. You can modify the schedule by editing the `CONFIG` dictionary in `cfst_scheduler.py`:

```python
CONFIG = {
    # ... other settings ...
    "schedule_interval_hours": 12,  # Change this value
}
```

The system is now fully configured to automatically commit `result.csv` to your GitHub repository's default branch each time the speed test runs.
