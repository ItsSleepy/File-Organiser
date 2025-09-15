# File Organizer Script

An intelligent Python script that automatically sorts files into organized folders based on file type. Perfect for cleaning up Downloads folders, Desktop clutter, or any messy directory.

## 🌟 Features

- **Smart Categorization**: Automatically sorts files by type (Images, Documents, Audio, Video, etc.)
- **Dry Run Mode**: Preview what will be organized before making changes
- **Duplicate Handling**: Intelligently renames duplicate files to avoid conflicts
- **Undo Functionality**: Automatically creates undo scripts to reverse organization
- **Comprehensive Logging**: Detailed logs of all operations
- **Command Line Interface**: Easy to use from terminal/command prompt
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📁 File Categories

The script organizes files into the following categories:

- **Images**: JPG, PNG, GIF, SVG, WebP, etc.
- **Documents**: PDF, DOC, TXT, XLS, PPT, CSV, etc.
- **Audio**: MP3, WAV, FLAC, AAC, OGG, etc.
- **Video**: MP4, AVI, MKV, MOV, WMV, etc.
- **Archives**: ZIP, RAR, 7Z, TAR, GZ, etc.
- **Code**: PY, JS, HTML, CSS, Java, C++, etc.
- **Executables**: EXE, MSI, DEB, RPM, DMG, etc.
- **Data**: JSON, XML, YAML, SQL, DB, etc.
- **Fonts**: TTF, OTF, WOFF, etc.
- **3D Models**: OBJ, FBX, DAE, 3DS, BLEND, etc.
- **Others**: Any files that don't match the above categories

## 🚀 Quick Start

### Basic Usage

```bash
# Organize current directory (DRY RUN - safe preview)
python file_organizer.py --dry-run

# Organize specific folder (DRY RUN)
python file_organizer.py "C:\Users\YourName\Downloads" --dry-run

# Actually organize files (after previewing)
python file_organizer.py "C:\Users\YourName\Downloads"

# Preview organization structure
python file_organizer.py --preview
```

### Command Line Options

| Option          | Description                                             |
| --------------- | ------------------------------------------------------- |
| `folder`      | Path to folder to organize (default: current directory) |
| `--dry-run`   | Preview organization without moving files               |
| `--undo`      | Undo the last organization                              |
| `--preview`   | Show organization preview                               |
| `--log-level` | Set logging level (DEBUG, INFO, WARNING, ERROR)         |

## 📊 Example Output

```
🔍 Running in DRY RUN mode - no files will be moved
2025-09-15 10:30:15 - INFO - File Organizer initialized for: C:\Users\YourName\Downloads
2025-09-15 10:30:15 - INFO - Starting file organization (DRY RUN)
2025-09-15 10:30:15 - INFO - [DRY RUN] Would move: vacation.jpg -> Images/
2025-09-15 10:30:15 - INFO - [DRY RUN] Would move: report.pdf -> Documents/
2025-09-15 10:30:15 - INFO - [DRY RUN] Would move: song.mp3 -> Audio/

============================================================
📊 FILE ORGANIZATION STATISTICS
============================================================
📁 Total files organized: 147
----------------------------------------
📋 Audio          :  12 files ( 8.2%)
📋 Archives       :   5 files ( 3.4%)
📋 Code           :   3 files ( 2.0%)
📋 Documents      :  45 files (30.6%)
📋 Images         :  23 files (15.6%)
📋 Others         :  34 files (23.1%)
📋 Video          :   8 files ( 5.4%)
============================================================
```

## 🔄 Undo Organization

The script automatically creates undo functionality:

```bash
# Undo the last organization
python file_organizer.py --undo
```

## 🛡️ Safety Features

- **Dry Run Mode**: Test before making changes with `--dry-run`
- **Duplicate Detection**: Automatically renames files if duplicates exist
- **Comprehensive Logging**: All operations are logged with timestamps
- **Undo Functionality**: Easy reversal of organization
- **Error Handling**: Graceful handling of permission issues or file locks
- **Skip System Files**: Ignores hidden files and system files

## 📝 Logging

The script creates detailed logs in the target folder:

- `organization_logs/file_organizer_YYYYMMDD_HHMMSS.log`: Detailed operation log
- `organization_logs/operations_YYYYMMDD_HHMMSS.json`: Operations log for undo functionality

## 🔧 Customization

You can easily customize the file categories by editing the `file_categories` dictionary in the script:

```python
self.file_categories = {
    'Images': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', ...],
        'description': 'Images and graphics'
    },
    'Documents': {
        'extensions': ['.pdf', '.doc', '.docx', '.txt', ...],
        'description': 'Documents and text files'
    },
    # Add or modify categories as needed
}
```

## ⚠️ Important Notes

- **Backup First**: Always backup important files before organizing
- **Use Dry Run**: Test with `--dry-run` first to see what will happen
- **Administrator Rights**: May need admin rights for system folders
- **File Locks**: Files in use by other programs cannot be moved
- **Hidden Files**: Hidden files (starting with .) are ignored

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied**: Run terminal as administrator
2. **File in Use**: Close programs using the files
3. **Path Not Found**: Check folder path spelling and existence
4. **No Files Moved**: Files might already be organized or filtered out

### Getting Help

Check the log file for detailed error messages. The log file is created in the target folder's `organization_logs` directory.

## 💡 Pro Tips

1. **Always Use Dry Run First**:

   ```bash
   python file_organizer.py ~/Downloads --dry-run  # Preview
   python file_organizer.py ~/Downloads             # Execute
   ```
2. **Preview Organization Structure**:

   ```bash
   python file_organizer.py --preview
   ```
3. **Check Logs for Details**:
   Look in the `organization_logs` folder for detailed operation logs.
4. **Undo If Needed**:

   ```bash
   python file_organizer.py --undo
   ```

## 📄 License

This script is provided as-is for personal and educational use. Feel free to modify and distribute.

---

**Author**: Isaac Camilleri
**Date**: September 2025
**Version**: 2.0
