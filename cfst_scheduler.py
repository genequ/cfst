#!/usr/bin/env python3
"""
Cloudflare Speed Test Scheduler
Automatically runs cfst.exe every 12 hours and pushes results to GitHub
重构版本 - 集成GitHub上传功能，推送到genequ/csft仓库
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
    "backup_folder": "cfst_backups",
    "git_remote": "cfst",
    "git_branch": "main",
    "git_repo_url": "https://github.com/genequ/cfst.git"
}

class GitHubUploader:
    """集成GitHub上传功能"""
    def __init__(self, repo_path=".", result_file="result.csv", remote_name="cfst", branch="main", repo_url="https://github.com/genequ/cfst.git"):
        self.repo_path = Path(repo_path)
        self.result_file = result_file
        self.remote_name = remote_name
        self.branch = branch
        self.repo_url = repo_url
        
    def check_git_availability(self):
        """检查Git是否可用"""
        try:
            result = subprocess.run(["git", "--version"], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Git is not available or not installed")
            return False
    
    def setup_git_repository(self):
        """设置Git仓库"""
        if not self.is_git_repository():
            print("Initializing new Git repository...")
            subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
        
        # 添加远程仓库
        try:
            subprocess.run(["git", "remote", "add", self.remote_name, self.repo_url], 
                         cwd=self.repo_path, capture_output=True, check=True)
            print(f"Added remote repository: {self.remote_name} -> {self.repo_url}")
        except subprocess.CalledProcessError:
            # 如果远程已存在，更新URL
            subprocess.run(["git", "remote", "set-url", self.remote_name, self.repo_url], 
                         cwd=self.repo_path, check=True)
            print(f"Updated remote repository: {self.remote_name} -> {self.repo_url}")
    
    def is_git_repository(self):
        """检查当前目录是否为Git仓库"""
        return (self.repo_path / ".git").exists()
    
    def check_result_file_exists(self):
        """检查result.csv文件是否存在"""
        result_path = self.repo_path / self.result_file
        if not result_path.exists():
            print(f"Error: {self.result_file} not found at {result_path}")
            return False
        return True
    
    def has_changes_to_commit(self):
        """检查是否有需要提交的更改"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", self.result_file],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"Error checking git status: {e}")
            return False
    
    def git_add(self):
        """添加文件到Git暂存区"""
        try:
            subprocess.run(
                ["git", "add", self.result_file],
                cwd=self.repo_path,
                check=True
            )
            print(f"Added {self.result_file} to git staging area")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error adding file to git: {e}")
            return False
    
    def git_commit(self):
        """提交更改"""
        try:
            commit_message = f"CFST results update {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                check=True
            )
            print(f"Committed changes: {commit_message}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error committing changes: {e}")
            return False
    
    def git_push(self):
        """推送到远程仓库"""
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"Attempting git push (attempt {attempt + 1}/{max_retries})...")
                result = subprocess.run(
                    ["git", "push", self.remote_name, self.branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2分钟超时
                )
                
                if result.returncode == 0:
                    print("Successfully pushed to GitHub")
                    return True
                else:
                    # 检查是否需要设置上游分支
                    if "no upstream branch" in result.stderr or "set-upstream" in result.stderr:
                        print("Setting upstream branch...")
                        setup_result = subprocess.run(
                            ["git", "push", "--set-upstream", self.remote_name, self.branch],
                            cwd=self.repo_path,
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        if setup_result.returncode == 0:
                            print("Successfully pushed to GitHub with upstream configured")
                            return True
                    
                    print(f"Git push failed (attempt {attempt + 1}): {result.stderr}")
                    
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                    
            except subprocess.TimeoutExpired:
                print(f"Git push timed out (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
            
            except Exception as e:
                print(f"Unexpected error during git push (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        print("All git push attempts failed")
        return False
    
    def upload_to_github(self):
        """主上传方法 - 完整的GitHub上传流程"""
        print(f"\n=== Starting GitHub Upload Process at {datetime.datetime.now()} ===")
        
        # 1. 检查前置条件
        if not self.check_git_availability():
            return False
        
        # 2. 设置Git仓库
        self.setup_git_repository()
        
        if not self.check_result_file_exists():
            return False
        
        # 3. 检查是否有更改需要提交
        if not self.has_changes_to_commit():
            print("No changes to result.csv. Skipping upload.")
            return True
        
        # 4. 执行Git操作
        if not self.git_add():
            return False
        
        if not self.git_commit():
            return False
        
        if not self.git_push():
            print("Git push failed, but commit was successful. Manual push may be needed later.")
            return False
        
        print("=== GitHub Upload Process Completed Successfully ===\n")
        return True

class CFSTAutomation:
    def __init__(self, config):
        self.config = config
        self.github_uploader = GitHubUploader(
            repo_path=self.config["git_repo_path"],
            result_file=self.config["result_csv_path"],
            remote_name=self.config["git_remote"],
            branch=self.config["git_branch"],
            repo_url=self.config["git_repo_url"]
        )
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
        """Perform Git operations using the integrated GitHub uploader"""
        try:
            # Modify result file before Git operations
            if not self.modify_result_file():
                print("Failed to modify result file, skipping Git operations")
                return False
            
            # Use the integrated GitHub uploader
            return self.github_uploader.upload_to_github()
            
        except Exception as e:
            print(f"Error during GitHub upload: {e}")
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
