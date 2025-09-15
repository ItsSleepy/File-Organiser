#!/usr/bin/env python3
"""
Intelligent File Organizer
==========================

Automatically sorts files in a folder into organized subfolders based on file type.
Supports various file categories including documents, images, videos, audio, and more.

Features:
- Automatic file type detection and categorization
- Safe file moving with duplicate handling
- Detailed logging of all operations
- Undo functionality to reverse organization
- Customizable file type mappings
- Dry run mode for preview before actual organization

Author: Isaac Camilleri
Date: September 2025
Version: 2.0
"""

import os
import sys
import shutil
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

class FileOrganizer:
    """
    Intelligent file organizer that categorizes files by type and moves them to appropriate folders.
    """
    
    def __init__(self, base_folder: str, log_level: str = "INFO"):
        """
        Initialize the FileOrganizer.
        
        Args:
            base_folder (str): Path to the folder to organize
            log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.base_folder = Path(base_folder).resolve()
        self.operations_log = []
        self.setup_logging(log_level)
        
        # File type mappings - easily customizable
        self.file_categories = {
            "Documents": {
                "extensions": [
                    ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", 
                    ".xls", ".xlsx", ".ppt", ".pptx", ".odp", ".ods",
                    ".csv", ".md", ".tex", ".epub", ".mobi"
                ],
                "description": "Documents and text files"
            },
            "Images": {
                "extensions": [
                    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
                    ".svg", ".webp", ".ico", ".raw", ".psd", ".ai", ".eps"
                ],
                "description": "Images and graphics"
            },
            "Videos": {
                "extensions": [
                    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm",
                    ".m4v", ".3gp", ".mpg", ".mpeg", ".m2v", ".mts"
                ],
                "description": "Video files"
            },
            "Audio": {
                "extensions": [
                    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
                    ".opus", ".aiff", ".au", ".ra", ".amr"
                ],
                "description": "Audio files"
            },
            "Archives": {
                "extensions": [
                    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
                    ".tar.gz", ".tar.bz2", ".tar.xz", ".deb", ".rpm"
                ],
                "description": "Compressed archives"
            },
            "Code": {
                "extensions": [
                    ".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h",
                    ".php", ".rb", ".go", ".rs", ".ts", ".jsx", ".tsx", ".vue",
                    ".scss", ".sass", ".less", ".sql", ".xml", ".json", ".yaml", ".yml"
                ],
                "description": "Source code and markup files"
            },
            "Executables": {
                "extensions": [
                    ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".app",
                    ".run", ".bin", ".appimage"
                ],
                "description": "Executable and installer files"
            },
            "Fonts": {
                "extensions": [
                    ".ttf", ".otf", ".woff", ".woff2", ".eot", ".fon", ".fnt"
                ],
                "description": "Font files"
            },
            "3D_Models": {
                "extensions": [
                    ".obj", ".fbx", ".dae", ".3ds", ".blend", ".ma", ".mb",
                    ".max", ".c4d", ".skp", ".stl", ".ply"
                ],
                "description": "3D model files"
            },
            "Data": {
                "extensions": [
                    ".db", ".sqlite", ".sqlite3", ".json", ".xml", ".csv",
                    ".tsv", ".log", ".bak", ".tmp"
                ],
                "description": "Data and database files"
            }
        }
    
    def setup_logging(self, log_level: str):
        """Setup logging configuration."""
        log_filename = f"file_organizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = self.base_folder / "organization_logs" / log_filename
        
        # Create logs directory if it doesn't exist
        log_path.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"File Organizer initialized for: {self.base_folder}")
    
    def get_file_category(self, file_path: Path) -> str:
        """
        Determine the category of a file based on its extension.
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            str: Category name or 'Others' if no match found
        """
        extension = file_path.suffix.lower()
        
        for category, info in self.file_categories.items():
            if extension in info["extensions"]:
                return category
        
        return "Others"
    
    def create_category_folders(self) -> Dict[str, Path]:
        """
        Create category folders in the base directory.
        
        Returns:
            Dict[str, Path]: Mapping of category names to folder paths
        """
        category_paths = {}
        
        for category in list(self.file_categories.keys()) + ["Others"]:
            folder_path = self.base_folder / category
            folder_path.mkdir(exist_ok=True)
            category_paths[category] = folder_path
            self.logger.debug(f"Ensured category folder exists: {folder_path}")
        
        return category_paths
    
    def handle_duplicate_filename(self, source: Path, destination: Path) -> Path:
        """
        Handle duplicate filenames by adding a counter.
        
        Args:
            source (Path): Source file path
            destination (Path): Intended destination path
            
        Returns:
            Path: Final destination path (possibly with counter)
        """
        if not destination.exists():
            return destination
        
        # If files are identical, skip moving
        if source.stat().st_size == destination.stat().st_size:
            try:
                if source.read_bytes() == destination.read_bytes():
                    self.logger.info(f"Identical file already exists, skipping: {source.name}")
                    return None
            except:
                pass  # If we can't read files, proceed with renaming
        
        # Add counter to filename
        counter = 1
        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent
        
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_destination = parent / new_name
            if not new_destination.exists():
                self.logger.info(f"Renamed to avoid duplicate: {destination.name} -> {new_name}")
                return new_destination
            counter += 1
    
    def organize_files(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Organize files in the base folder into category subfolders.
        
        Args:
            dry_run (bool): If True, only simulate the organization without moving files
            
        Returns:
            Dict[str, int]: Statistics of organized files by category
        """
        self.logger.info(f"Starting file organization {'(DRY RUN)' if dry_run else ''}")
        
        # Get all files in the base folder (not in subfolders)
        files_to_organize = [
            f for f in self.base_folder.iterdir() 
            if f.is_file() and not f.name.startswith('.') 
            and f.name != "file_organizer.py"  # Don't move the script itself
        ]
        
        if not files_to_organize:
            self.logger.info("No files found to organize")
            return {}
        
        # Create category folders
        if not dry_run:
            category_paths = self.create_category_folders()
        
        # Statistics tracking
        stats = {}
        
        for file_path in files_to_organize:
            try:
                category = self.get_file_category(file_path)
                
                if category not in stats:
                    stats[category] = 0
                
                if dry_run:
                    self.logger.info(f"[DRY RUN] Would move: {file_path.name} -> {category}/")
                    stats[category] += 1
                    continue
                
                # Determine destination
                destination_folder = category_paths[category]
                destination_file = destination_folder / file_path.name
                
                # Handle duplicates
                final_destination = self.handle_duplicate_filename(file_path, destination_file)
                
                if final_destination is None:
                    continue  # Skip identical files
                
                # Move the file
                shutil.move(str(file_path), str(final_destination))
                
                # Log the operation for potential undo
                operation = {
                    "action": "move",
                    "source": str(file_path),
                    "destination": str(final_destination),
                    "timestamp": datetime.now().isoformat(),
                    "category": category
                }
                self.operations_log.append(operation)
                
                self.logger.info(f"Moved: {file_path.name} -> {category}/{final_destination.name}")
                stats[category] += 1
                
            except Exception as e:
                self.logger.error(f"Error organizing {file_path.name}: {str(e)}")
        
        # Save operations log for undo functionality
        if not dry_run and self.operations_log:
            self.save_operations_log()
        
        return stats
    
    def save_operations_log(self):
        """Save the operations log for undo functionality."""
        log_file = self.base_folder / "organization_logs" / f"operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.operations_log, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Operations log saved: {log_file}")
    
    def undo_last_organization(self, operations_file: str = None) -> bool:
        """
        Undo the last file organization operation.
        
        Args:
            operations_file (str): Specific operations file to undo (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if operations_file:
            log_file = Path(operations_file)
        else:
            # Find the most recent operations log
            log_dir = self.base_folder / "organization_logs"
            if not log_dir.exists():
                self.logger.error("No operations logs found")
                return False
            
            log_files = list(log_dir.glob("operations_*.json"))
            if not log_files:
                self.logger.error("No operations log files found")
                return False
            
            log_file = max(log_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                operations = json.load(f)
            
            self.logger.info(f"Undoing {len(operations)} operations from {log_file.name}")
            
            # Reverse the operations
            for operation in reversed(operations):
                try:
                    destination = Path(operation["destination"])
                    source = Path(operation["source"])
                    
                    if destination.exists():
                        shutil.move(str(destination), str(source))
                        self.logger.info(f"Restored: {destination.name} -> {source.name}")
                    else:
                        self.logger.warning(f"File not found for undo: {destination}")
                        
                except Exception as e:
                    self.logger.error(f"Error undoing operation: {str(e)}")
            
            # Rename the log file to mark it as processed
            processed_log = log_file.with_suffix('.json.undone')
            log_file.rename(processed_log)
            
            self.logger.info("Undo operation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during undo operation: {str(e)}")
            return False
    
    def get_organization_preview(self) -> Dict[str, List[str]]:
        """
        Get a preview of how files would be organized without actually moving them.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping categories to lists of filenames
        """
        preview = {}
        
        files_to_organize = [
            f for f in self.base_folder.iterdir() 
            if f.is_file() and not f.name.startswith('.') 
            and f.name != "file_organizer.py"
        ]
        
        for file_path in files_to_organize:
            category = self.get_file_category(file_path)
            if category not in preview:
                preview[category] = []
            preview[category].append(file_path.name)
        
        return preview
    
    def print_statistics(self, stats: Dict[str, int]):
        """Print organization statistics in a formatted way."""
        if not stats:
            print("\n📂 No files were organized.")
            return
        
        print("\n" + "="*60)
        print("📊 FILE ORGANIZATION STATISTICS")
        print("="*60)
        
        total_files = sum(stats.values())
        print(f"📁 Total files organized: {total_files}")
        print("-" * 40)
        
        for category, count in sorted(stats.items()):
            percentage = (count / total_files) * 100
            print(f"📋 {category:<15}: {count:>3} files ({percentage:>5.1f}%)")
        
        print("="*60)


def interactive_mode():
    """Interactive mode for VS Code Run button or when no arguments provided."""
    print("🗂️  INTELLIGENT FILE ORGANIZER")
    print("=" * 50)
    print("Author: Isaac Camilleri")
    print("=" * 50)
    print()
    
    # Get folder to organize
    print("📁 SELECT FOLDER TO ORGANIZE:")
    print("1. Current directory")
    print("2. Downloads folder")
    print("3. Desktop")
    print("4. Custom path")
    print()
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            folder = "."
            break
        elif choice == "2":
            folder = os.path.join(os.path.expanduser("~"), "Downloads")
            break
        elif choice == "3":
            folder = os.path.join(os.path.expanduser("~"), "Desktop")
            break
        elif choice == "4":
            folder = input("Enter the full path to the folder: ").strip()
            if not folder:
                print("❌ Please enter a valid path")
                continue
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    # Validate folder exists
    if not os.path.exists(folder):
        print(f"❌ Folder does not exist: {folder}")
        return
    
    if not os.path.isdir(folder):
        print(f"❌ Path is not a directory: {folder}")
        return
    
    print(f"\n📂 Selected folder: {os.path.abspath(folder)}")
    print()
    
    # Show what would be organized
    try:
        organizer = FileOrganizer(folder)
        preview = organizer.get_organization_preview()
        
        if not preview:
            print("ℹ️  No files found to organize in this folder.")
            return
        
        print("👀 PREVIEW - Files that would be organized:")
        print("-" * 50)
        total_files = 0
        for category, files in preview.items():
            print(f"📁 {category}: {len(files)} files")
            total_files += len(files)
        print(f"\n📊 Total files to organize: {total_files}")
        print()
        
        # Choose operation mode
        print("🔧 OPERATION MODE:")
        print("1. Dry Run (Preview only - safe)")
        print("2. Organize Files (Actually move files)")
        print("3. Show detailed preview")
        print("4. Exit")
        print()
        
        while True:
            mode_choice = input("Enter your choice (1-4): ").strip()
            
            if mode_choice == "1":
                print("\n🔍 Running DRY RUN mode...")
                stats = organizer.organize_files(dry_run=True)
                organizer.print_statistics(stats)
                print("\n✅ Dry run completed! No files were moved.")
                break
                
            elif mode_choice == "2":
                print("\n⚠️  WARNING: This will actually move files!")
                confirm = input("Are you sure you want to continue? (y/N): ").strip().lower()
                
                if confirm == 'y':
                    print("\n🚀 Organizing files...")
                    stats = organizer.organize_files(dry_run=False)
                    organizer.print_statistics(stats)
                    
                    if stats:
                        print("\n✅ File organization completed successfully!")
                        print("💡 Check the organization_logs folder for detailed logs")
                        print("🔄 Use --undo argument to reverse this organization if needed")
                else:
                    print("❌ Operation cancelled.")
                break
                
            elif mode_choice == "3":
                print("\n" + "="*60)
                print("📋 DETAILED ORGANIZATION PREVIEW")
                print("="*60)
                
                for category, files in preview.items():
                    print(f"\n📁 {category} ({len(files)} files):")
                    for file in sorted(files):
                        print(f"   📄 {file}")
                print()
                continue
                
            elif mode_choice == "4":
                print("👋 Goodbye!")
                return
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Main function to run the file organizer."""
    # Check if running with command line arguments
    if len(sys.argv) > 1:
        # Command line mode
        parser = argparse.ArgumentParser(description="Intelligent File Organizer")
        parser.add_argument("folder", nargs='?', default=".", help="Folder to organize (default: current directory)")
        parser.add_argument("--dry-run", action="store_true", help="Preview organization without moving files")
        parser.add_argument("--undo", action="store_true", help="Undo the last organization")
        parser.add_argument("--preview", action="store_true", help="Show organization preview")
        parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Logging level")
        
        args = parser.parse_args()
        
        try:
            organizer = FileOrganizer(args.folder, args.log_level)
            
            if args.undo:
                success = organizer.undo_last_organization()
                if success:
                    print("✅ Undo operation completed successfully")
                else:
                    print("❌ Undo operation failed")
                    
            elif args.preview:
                preview = organizer.get_organization_preview()
                print("\n" + "="*60)
                print("👀 ORGANIZATION PREVIEW")
                print("="*60)
                
                for category, files in preview.items():
                    print(f"\n📁 {category} ({len(files)} files):")
                    for file in sorted(files):
                        print(f"   📄 {file}")
                        
            else:
                if args.dry_run:
                    print("🔍 Running in DRY RUN mode - no files will be moved")
                
                stats = organizer.organize_files(dry_run=args.dry_run)
                organizer.print_statistics(stats)
                
                if not args.dry_run and stats:
                    print("\n✅ File organization completed successfully!")
                    print("💡 Use --undo to reverse this organization if needed")
                    
        except KeyboardInterrupt:
            print("\n⚠️ Operation cancelled by user")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        # Interactive mode for VS Code Run button
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\n⚠️ Operation cancelled by user")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Keep window open in VS Code
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
