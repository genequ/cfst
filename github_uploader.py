#!/usr/bin/env python3
"""
GitHub Uploader for CFST Results
专门处理result.csv文件的上传到GitHub仓库
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path
import time

class GitHubUploader:
    def __init__(self, repo_path=".", result_file="result.csv", remote_name="genequ", branch="main"):
        self.repo_path = Path(repo_path)
        self.result_file = result_file
        self.remote_name = remote_name
        self.branch = branch
        
    def check_git_availability(self):
        """检查Git是否可用"""
        try:
            result = subprocess.run(["git", "--version"], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Git is not available or not installed")
            return False
    
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
        
        if not self.is_git_repository():
            print("Not a Git repository. Skipping upload.")
            return False
        
        if not self.check_result_file_exists():
            return False
        
        # 2. 检查是否有更改需要提交
        if not self.has_changes_to_commit():
            print("No changes to result.csv. Skipping upload.")
            return True
        
        # 3. 执行Git操作
        if not self.git_add():
            return False
        
        if not self.git_commit():
            return False
        
        if not self.git_push():
            print("Git push failed, but commit was successful. Manual push may be needed later.")
            return False
        
        print("=== GitHub Upload Process Completed Successfully ===\n")
        return True

def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload CFST results to GitHub")
    parser.add_argument("--repo-path", default=".", help="Path to Git repository")
    parser.add_argument("--result-file", default="result.csv", help="Result CSV file name")
    parser.add_argument("--remote", default="genequ", help="Git remote name")
    parser.add_argument("--branch", default="main", help="Git branch name")
    
    args = parser.parse_args()
    
    uploader = GitHubUploader(
        repo_path=args.repo_path,
        result_file=args.result_file,
        remote_name=args.remote,
        branch=args.branch
    )
    
    success = uploader.upload_to_github()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
