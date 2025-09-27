#!/usr/bin/env python3
"""
独立GitHub上传脚本
用于手动触发result.csv文件的上传到GitHub仓库
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径，以便导入github_uploader
sys.path.insert(0, str(Path(__file__).parent))

try:
    from github_uploader import GitHubUploader
except ImportError:
    print("Error: github_uploader.py not found in current directory")
    sys.exit(1)

def main():
    """主函数"""
    print("=== GitHub Upload Tool for CFST Results ===")
    print("This tool will upload result.csv to GitHub repository genequ/Proxy")
    print()
    
    # 检查result.csv文件是否存在
    result_file = Path("result.csv")
    if not result_file.exists():
        print("Error: result.csv file not found in current directory")
        print("Please make sure the file exists before running this tool")
        sys.exit(1)
    
    print(f"Found result.csv file ({result_file.stat().st_size} bytes)")
    
    # 初始化上传器
    try:
        uploader = GitHubUploader(
            repo_path=".",
            result_file="result.csv",
            remote_name="genequ",
            branch="main"
        )
    except Exception as e:
        print(f"Error initializing GitHub uploader: {e}")
        sys.exit(1)
    
    # 执行上传
    print("\nStarting upload process...")
    success = uploader.upload_to_github()
    
    if success:
        print("\n✅ Upload completed successfully!")
    else:
        print("\n❌ Upload failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
