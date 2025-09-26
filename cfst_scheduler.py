#!/usr/bin/env python3
"""
Cloudflare Speed Test Scheduler
Automatically runs cfst.exe every 12 hours and pushes results to GitHub
"""

import os
import sys
import time
import subprocess
import datetime
import json
from pathlib import Path

# Configuration
CONFIG = {
    "cfst_exe_path": r"cfst.exe",
    "result_csv_path": r"result.csv",
    "git_repo_path": ".",
    "schedule_interval_hours": 12,
    "backup_folder": "cfst_backups"
}

class CFSTAutomation:
    def __init__(self, config):
        self.config = config
        self.setup_directories()
        
    def setup_directories(self):
        """Create necessary directories"""
        backup_dir = Path(self.config["backup_folder"])
        backup_dir.mkdir(exist_ok=True)
        
    def run_cfst_test(self):
        """Run the Cloudflare Speed Test"""
        print(f"[{datetime.datetime.now()}] Running Cloudflare Speed Test...")
        
        cfst_path = Path(self.config["cfst_exe_path"])
        if not cfst_path.exists():
            print(f"Error: cfst.exe not found at {cfst_path}")
            return False
            
        try:
            # Run cfst.exe with basic parameters - use simpler parameters for faster testing
            result = subprocess.run([
                str(cfst_path),
                # "-sl", "10",  # Download Speed
                "-tl", "150",  # Latency limit
                "-tp", "8443",  # Port to test
            ], capture_output=True, text=True, encoding='utf-8', errors='ignore', cwd=Path(self.config["cfst_exe_path"]).parent)
            
            if result.returncode == 0:
                print("Cloudflare Speed Test completed successfully")
                print(result.stdout)
                return True
            else:
                print(f"Error running cfst.exe: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Exception while running cfst.exe: {e}")
            return False
    
    def backup_result_file(self):
        """Create a timestamped backup of the result file"""
        result_path = Path(self.config["result_csv_path"])
        if not result_path.exists():
            print("No result.csv file found to backup")
            return False
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"result_{timestamp}.csv"
        backup_path = Path(self.config["backup_folder"]) / backup_name
        
        try:
            import shutil
            shutil.copy2(result_path, backup_path)
            print(f"Backup created: {backup_path}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def modify_result_file(self):
        """Modify result.csv to keep only the first 20 results"""
        result_path = Path(self.config["result_csv_path"])
        print(f"Checking if result file exists: {result_path}")
        if not result_path.exists():
            print("No result.csv file found to modify")
            return False
            
        try:
            # Read the entire file
            with open(result_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            print(f"Original file has {len(lines)} lines")
            
            # Keep header (first line) and first 20 data rows (lines 1-21)
            if len(lines) > 21:  # Header + 20 data rows
                lines = lines[:21]  # Keep first 21 lines (header + 20 results)
                print(f"Modified result.csv to keep first 20 results (total lines: {len(lines)})")
            else:
                print(f"Result file already has {len(lines)-1} results, no modification needed")
                return True
            
            # Write back the modified content
            with open(result_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            
            print("Successfully modified result.csv")
            return True
            
        except Exception as e:
            print(f"Error modifying result.csv: {e}")
            return False
    
    def git_operations(self):
        """Perform Git operations (commit and push)"""
        repo_path = Path(self.config["git_repo_path"])
        
        # Check if this is a git repository
        if not (repo_path / ".git").exists():
            print("Not a Git repository. Git operations skipped.")
            return False
            
        try:
            # Check if git is available
            subprocess.run(["git", "--version"], capture_output=True, check=True)
        except:
            print("Git is not available. Git operations skipped.")
            return False
            
        try:
            # Modify result file before Git operations
            if not self.modify_result_file():
                print("Failed to modify result file, skipping Git operations")
                return False
            
            # Add the result file
            subprocess.run(["git", "add", self.config["result_csv_path"]], 
                         cwd=repo_path, check=True)
            
            # Commit with timestamp
            commit_message = f"CFST results {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], 
                         cwd=repo_path, check=True)
            
            # Push to remote
            push_result = subprocess.run(["git", "push"], 
                                       cwd=repo_path, capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print("Successfully pushed to GitHub")
                return True
            else:
                print(f"Git push failed: {push_result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"Error during Git operations: {e}")
            return False
    
    def run_single_cycle(self):
        """Run one complete cycle of testing and Git operations"""
        print(f"\n=== CFST Automation Cycle Started at {datetime.datetime.now()} ===")
        
        # Run the speed test
        if not self.run_cfst_test():
            print("Speed test failed, skipping Git operations")
            return False
            
        # Backup the result file
        self.backup_result_file()
        
        # Perform Git operations
        git_success = self.git_operations()
        
        print(f"=== CFST Automation Cycle Completed at {datetime.datetime.now()} ===\n")
        return git_success
    
    def run_scheduled(self):
        """Run the automation on a 12-hour schedule"""
        print("Starting CFST Automation Scheduler")
        print(f"Will run every {self.config['schedule_interval_hours']} hours")
        print("Press Ctrl+C to stop the scheduler")
        
        try:
            while True:
                self.run_single_cycle()
                
                # Calculate next run time
                next_run = datetime.datetime.now() + datetime.timedelta(
                    hours=self.config["schedule_interval_hours"]
                )
                print(f"Next run scheduled for: {next_run}")
                
                # Wait for the next cycle
                time.sleep(self.config["schedule_interval_hours"] * 3600)
                
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")
        except Exception as e:
            print(f"Scheduler error: {e}")

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cloudflare Speed Test Automation")
    parser.add_argument("--run-once", action="store_true", 
                       help="Run one cycle and exit")
    parser.add_argument("--schedule", action="store_true",
                       help="Run on a 12-hour schedule (default)")
    
    args = parser.parse_args()
    
    automation = CFSTAutomation(CONFIG)
    
    if args.run_once:
        automation.run_single_cycle()
    else:
        automation.run_scheduled()

if __name__ == "__main__":
    main()
