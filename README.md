# Cloudflare Speed Test Automation

This script automatically runs Cloudflare Speed Test (cfst.exe) every 12 hours and pushes the results to GitHub.

## Files Overview

- `cfst_scheduler.py` - Main Python automation script
- `run_cfst.bat` - Windows batch script for manual execution or Task Scheduler
- `cfst.exe` - Cloudflare Speed Test executable
- `result.csv` - Generated results file (created by cfst.exe)

## Prerequisites

1. **Python 3.6+** - Required to run the scheduler script
2. **Git** - Required for GitHub operations (optional, script will skip if not available)

## Setup Instructions

### 1. Install Python
If Python is not installed, download and install it from [python.org](https://python.org)

### 2. Install Git (Optional, for GitHub integration)
Download and install Git from [git-scm.com](https://git-scm.com)

### 3. Set up Git Repository (Optional)
If you want to push results to GitHub:

#### For genequ/Proxy.git repository:
Run the automated setup script:
```cmd
setup_genequ_repo.bat
```

#### For other repositories:
```bash
# Initialize git repository
git init

# Add remote repository
git remote add origin https://github.com/yourusername/your-repo.git

# Configure git user (required for commits)
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

## Usage

### Manual Execution
Run the batch script manually:
```cmd
cd script
run_cfst.bat
```

Or run the Python script directly:
```cmd
cd script
python cfst_scheduler.py --run-once
```

### Scheduled Execution (Windows Task Scheduler)

#### Method 1: Using Windows Task Scheduler GUI
1. Open **Task Scheduler** (search for it in Start menu)
2. Click **Create Basic Task**
3. Name: "Cloudflare Speed Test Automation"
4. Trigger: **Daily** → Set to run every day
5. Action: **Start a program**
6. Program/script: Browse to `script\run_cfst.bat`
7. Start in: Browse to the `script` directory
8. Set to run with highest privileges

#### Method 2: Using Command Line (Administrator)
```cmd
# Create a scheduled task that runs every 12 hours
schtasks /create /tn "CFST Automation" /tr "C:\Users\geneq\Desktop\script\run_cfst.bat" /sc hourly /mo 12 /ru SYSTEM
```

## Configuration

Edit the `CONFIG` dictionary in `cfst_scheduler.py` to customize:

```python
CONFIG = {
    "cfst_exe_path": r"cfst_windows\cfst.exe",  # Path to cfst.exe
    "result_csv_path": r"cfst_windows\result.csv",  # Path to result file
    "git_repo_path": ".",  # Git repository path
    "schedule_interval_hours": 12,  # How often to run (hours)
    "backup_folder": "cfst_backups"  # Backup directory for old results
}
```

## Features

- **Automatic Testing**: Runs cfst.exe with optimized parameters
- **Backup System**: Creates timestamped backups of result files
- **Git Integration**: Automatically commits and pushes results to GitHub
- **Error Handling**: Graceful handling of failures
- **Logging**: Detailed console output with timestamps

## Troubleshooting

### Python Not Found
- Ensure Python is installed and in PATH
- Try `python --version` in command prompt

### Git Not Available
- The script will skip Git operations if Git is not installed
- Install Git or ignore Git-related warnings

### cfst.exe Not Found
- Ensure the file exists at the configured path
- Check file permissions

### Task Scheduler Issues
- Run Task Scheduler as Administrator
- Check the task's "History" tab for errors
- Ensure the batch file path is correct

## File Structure
```
Desktop/
└── script/
    ├── cfst_scheduler.py  # Main automation script
    ├── run_cfst.bat       # Windows batch script
    ├── cfst.exe           # Cloudflare Speed Test executable
    ├── result.csv         # Generated results (created by cfst.exe)
    └── README.md          # This file
```

## Monitoring

The script outputs detailed logs to the console. For scheduled tasks, check:
- Windows Event Viewer → Windows Logs → Application
- Task Scheduler task history
- Backup files in the `cfst_backups` directory

## Support

For issues with cfst.exe itself, refer to the original project:
https://github.com/XIU2/CloudflareSpeedTest
