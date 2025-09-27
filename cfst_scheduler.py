#!/usr/bin/env python3
"""
Cloudflare Speed Test Scheduler
Automatically runs cfst.exe every 12 hours and pushes results to GitHub
重构版本 - 使用独立的GitHub上传器
"""

import os
import sys
import time
import subprocess
import datetime
import json
from pathlib import Path

# Import the new GitHub uploader
try:
    from github_uploader import GitHubUploader
except ImportError:
    print("Warning: github_uploader.py not found. GitHub upload functionality will be disabled.")

# Configuration
CONFIG = {
    "cfst_exe_path": r"cfst.exe",
    "result_csv_path": r"result.csv",
    "git_repo_path": ".",
    "schedule_interval_hours": 12,
    "backup_folder": "cfst_backups",
    "git_remote": "genequ",
    "git_branch": "main"
}

class CFSTAutomation:
    def __init__(self, config):
        self.config = config
        self.github_uploader = None
        self.setup_directories()
        self.setup_github_uploader()
        
    def setup_directories(self):
        """Create necessary directories"""
        backup_dir = Path(self.config["backup_folder"])
        backup_dir.mkdir(exist_ok=True)
        
    def setup_github_uploader(self):
        """Initialize GitHub uploader"""
        try:
            self.github_uploader = GitHubUploader(
                repo_path=self.config["git_repo_path"],
                result_file=self.config["result_csv_path"],
                remote_name=self.config["git_remote"],
                branch=self.config["git_branch"]
            )
            print("GitHub uploader initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize GitHub uploader: {e}")
            self.github_uploader = None
        
    def run_cfst_test(self):
        """Run the Cloudflare Speed Test"""
        print(f"[{datetime.datetime.now()}] Running Cloudflare Speed Test...")
        
        cfst_path = Path(self.config["cfst_exe_path"])
        if not cfst_path.exists():
            print(f"Error: cfst.exe not found at {cfst_path}")
            return False
            
        try:
            # Run cfst.exe with basic parameters - use simpler parameters for faster testing
            process = subprocess.Popen([
                str(cfst_path),
                # "-sl", "10",  # Download Speed
                "-tl", "150",  # Latency limit
                "-tp", "8443",  # Port to test
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
               text=True, encoding='utf-8', errors='ignore', 
               cwd=Path(self.config["cfst_exe_path"]).parent)
            
            # Wait for the process to complete with a timeout
            stdout, stderr = process.communicate(input='\n', timeout=300)
            
            if process.returncode == 0:
                print("Cloudflare Speed Test completed successfully")
                print(stdout)
                return True
            else:
                print(f"Error running cfst.exe: {stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("Cloudflare Speed Test timed out after 5 minutes")
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
        """Modify result.csv to append port 8443 after IP addresses and keep only the first 20 results"""
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
            
            # Process each line to append port 8443 after IP addresses
            modified_lines = []
            for i, line in enumerate(lines):
                if i == 0:  # Header line
                    # Keep the original column name "IP 地址"
                    modified_lines.append(line)
                else:  # Data lines
                    parts = line.split(',')
                    if len(parts) > 0:
                        # Append port 8443 to the IP address
                        ip_address = parts[0].strip()
                        if ip_address and not ip_address.startswith('#'):
                            parts[0] = f"{ip_address}:8443"
                        modified_line = ','.join(parts)
                        modified_lines.append(modified_line)
                    else:
                        modified_lines.append(line)
            
            # Keep header (first line) and first 20 data rows (lines 1-21)
            if len(modified_lines) > 21:  # Header + 20 data rows
                modified_lines = modified_lines[:21]  # Keep first 21 lines (header + 20 results)
                print(f"Modified result.csv to keep first 20 results (total lines: {len(modified_lines)})")
            else:
                print(f"Result file already has {len(modified_lines)-1} results, no modification needed")
            
            # Write back the modified content
            with open(result_path, 'w', encoding='utf-8') as file:
                file.writelines(modified_lines)
            
            print("Successfully modified result.csv - appended port 8443 to IP addresses")
            return True
            
        except Exception as e:
            print(f"Error modifying result.csv: {e}")
            return False
    
    def git_operations(self):
        """Perform Git operations using the new GitHub uploader"""
        if self.github_uploader is None:
            print("GitHub uploader not available. Using fallback method.")
            return self.git_operations_fallback()
        
        try:
            # Modify result file before Git operations
            if not self.modify_result_file():
                print("Failed to modify result file, skipping Git operations")
                return False
            
            # Use the new GitHub uploader
            return self.github_uploader.upload_to_github()
            
        except Exception as e:
            print(f"Error during GitHub upload: {e}")
            print("Falling back to original Git operations method")
            return self.git_operations_fallback()
    
    def git_operations_fallback(self):
        """Fallback Git operations method (original implementation)"""
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
            # Check if there are any changes to commit
            status_result = subprocess.run(["git", "status", "--porcelain", self.config["result_csv_path"]], 
                                         cwd=repo_path, capture_output=True, text=True)
            
            if not status_result.stdout.strip():
                print("No changes to result.csv, skipping Git operations")
                return True
            
            # Add the result file
            subprocess.run(["git", "add", self.config["result_csv_path"]], 
                         cwd=repo_path, check=True)
            
            # Commit with timestamp
            commit_message = f"CFST results {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], 
                         cwd=repo_path, check=True)
            
            # Try to push with auto-setup remote
            push_result = subprocess.run(["git", "push"], 
                                       cwd=repo_path, capture_output=True, text=True, timeout=60)
            
            if push_result.returncode == 0:
                print("Successfully pushed to GitHub")
                return True
            else:
                # If push fails due to upstream not set, try with --set-upstream
                if "no upstream branch" in push_result.stderr or "set-upstream" in push_result.stderr:
                    print("Setting upstream branch and retrying push...")
                    push_result = subprocess.run(["git", "push", "--set-upstream", "genequ", "main"], 
                                               cwd=repo_path, capture_output=True, text=True, timeout=60)
                    
                    if push_result.returncode == 0:
                        print("Successfully pushed to GitHub with upstream configured")
                        return True
                
                print(f"Git push failed: {push_result.stderr}")
                print("Git commit was successful, but push failed. The commit will be available for manual push later.")
                return False
                
        except subprocess.TimeoutExpired:
            print("Git push timed out after 60 seconds. Network may be unavailable.")
            print("Git commit was successful, but push failed. The commit will be available for manual push later.")
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
