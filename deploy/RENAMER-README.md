# Renamer - Desktop Media File Renaming Tool v2.0

## 🎉 What's New in Version 2.0

### 🐛 Bug Fixes
- **Fixed auto-loading issue** - Files from default folders now load reliably on startup
- **Improved path handling** - Better normalization and validation of folder paths
- **Enhanced error handling** - More robust network requests with timeouts
- **Fixed tree view selection** - Proper handling of file selection events

### ✨ New Features
- **🌙 Dark Theme** - Modern dark UI that's easy on the eyes
- **📊 Better status updates** - Real-time feedback on all operations
- **🔄 Improved threading** - Smoother UI during searches and loading
- **📁 Smart duplicate detection** - Prevents adding the same file twice
- **⚡ Optimized performance** - Faster file scanning and searching

### 🎨 UI Improvements
- **Emoji icons** - Visual indicators throughout the interface
- **Better color coding** - Clear visual feedback for actions
- **Enhanced preview** - Improved before/after folder structure display
- **Professional styling** - Consistent dark theme across all components

---

## Installation Instructions for Windows 11

### Step 1: Install Python
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"

### Step 2: Install Required Libraries
1. Open Command Prompt (press Win + R, type `cmd`, press Enter)
2. Run this command:
   ```
   pip install requests
   ```

### Step 3: Setup the App
1. Create a folder for the app (e.g., `C:\Renamer`)
2. Copy these files into that folder:
   - `renamer.py` (v2.0)
   - `run_renamer.bat`

### Step 4: Get API Keys
1. **TVDB API Key**:
   - Go to https://thetvdb.com/
   - Create a free account
   - Go to https://thetvdb.com/api-information
   - Generate an API key

2. **TMDB API Key**:
   - Go to https://www.themoviedb.org/
   - Create a free account
   - Go to https://www.themoviedb.org/settings/api
   - Request an API key (choose "Developer" option)

## How to Use

### Running the App
- Double-click `run_renamer.bat` in your Renamer folder
- OR open Command Prompt, navigate to the folder, and run: `python renamer.py`

### 🎯 Quick Start Guide

1. **First Time Setup**:
   - Click the **⚙️ Settings** tab
   - Enter your TVDB and TMDB API keys
   - Add your media folders to "Default Media Folders"
   - Check "✨ Automatically load files on startup"
   - Click **💾 Save All Settings**

2. **The app will now automatically**:
   - Load all media files from your default folders on startup
   - Scan all subfolders recursively
   - Display files ready for searching and renaming

### Using the App

1. **Configure API Keys** (First Time Only):
   - Click the **⚙️ Settings** tab
   - Enter your TVDB API key
   - Enter your TMDB API key
   - Click **💾 Save All Settings**

2. **Setup Default Folders** (Recommended):
   - In the **⚙️ Settings** tab, scroll to "📂 Default Media Folders"
   - Click **➕ Add Folder** and select folders containing your media files
   - The app will scan these folders AND all subfolders for media files
   - Check "✨ Automatically load files from default folders on startup"
   - Click **💾 Save All Settings**
   - Click **🔄 Load Now** to immediately load files
   - Files will auto-load every time you start the app!

3. **Add Files** (if not using auto-load):
   - Click the **📁 Files** tab
   - Click **📄 Select Files** for individual files
   - OR click **📁 Select Folder** to add all media from a folder

4. **Search for Matches**:
   - Click **🔍 Search Selected** to find matches only for checked files (faster!)
   - OR click **🔎 Search All** to find matches for all files
   - The app automatically selects the best match for each file

5. **Select Files to Rename**:
   - All files are selected by default (shown with ✓)
   - Double-click any file to toggle its selection
   - Use **✅ Select All** or **❌ Select None** buttons
   - Only selected files will be renamed

6. **Review Matches**:
   - Click on a file in the list
   - The bottom panel shows a **visual before/after preview**:
     - 📂 Folder structure with emojis
     - ❌ Items that will be deleted
     - ✅ Items that will be kept
     - ✨ Items that will be renamed

7. **Rename Files**:
   - Review the "New Filename" column
   - Click **✨ Rename Selected**
   - Confirm the action
   - The app will:
     - ✅ Rename selected files
     - ✅ Rename parent folders intelligently
     - 🗑️ Delete junk files (keeps subtitles)
     - 🗑️ Delete unnecessary subdirectories
     - ✅ Keep your library clean and organized!

## 🌙 Dark Theme

Version 2.0 features a modern dark theme that:
- Reduces eye strain during extended use
- Provides better contrast for file listings
- Uses color coding for different file states
- Includes visual feedback for all interactions

## Supported File Formats
- MKV
- MP4
- AVI
- MOV
- WMV
- FLV
- M4V

## File Naming Patterns

### TV Shows
Input: `The.Office.S02E03.720p.mkv`
Output: `The Office - S02E03 - The Carpet.mkv`

### Movies
Input: `Inception.2010.1080p.mp4`
Output: `Inception (2010).mp4`

### Smart Folder Renaming
Before:
```
📁 Jurassic.Park.1993.720p.BrRip.264.YIFY/
  ├── 🎬 Jurassic.Park.1993.720p.BrRip.264.YIFY.mp4
  ├── 📄 README.txt ❌
  ├── 🎬 sample.avi ❌
  ├── 📂 Proof/ ❌
  │   └── 📄 screenshots.jpg
  └── 📂 Subs/ ✅
      └── 📝 English.srt
```

After:
```
📁 Jurassic Park (1993)/
  ├── 🎬 Jurassic Park (1993).mp4 ✨
  └── 📂 Subs/ ✅
      └── 📝 English.srt
```

## Features
✅ **Automatic filename parsing** - Smart detection of TV shows and movies
✅ **API integration** - Search TVDB for TV shows, TMDB for movies
✅ **Multiple match selection** - Choose the best match from results
✅ **Visual file selection** - See which files will be renamed
✅ **Smart searching** - Search only selected files to save time
✅ **Beautiful previews** - Visual before/after with emoji indicators
✅ **Batch operations** - Rename multiple files at once
✅ **Smart folder renaming** - Automatically clean folder names
✅ **Aggressive cleanup** - Remove junk while preserving important files
✅ **Subtitle protection** - Never deletes .srt files or subtitle folders
✅ **Auto-loading** - Files ready when you open the app
✅ **Recursive scanning** - Finds all media in folders and subfolders
✅ **Dark theme** - Modern, eye-friendly interface
✅ **Real-time status** - Always know what the app is doing

## Troubleshooting

### "Files not auto-loading"
**Fixed in v2.0!** The auto-load feature now works reliably:
- Make sure you've saved settings after adding default paths
- Check that "Automatically load files" is enabled
- Verify the folders exist and contain media files
- The app will skip invalid paths and report them

### "Python not found"
- Make sure Python is installed and added to PATH
- Try restarting your computer after installing Python

### "API key error"
- Make sure you entered the correct API keys in Settings
- Check that your API keys are active and valid
- The app now shows better error messages for API issues

### "No matches found"
- Check that the filename follows a recognizable pattern
- Try manually searching on TVDB/TMDB to verify existence
- The file might be named incorrectly

### Permission errors
- Make sure you have write permissions to the folder
- Close any programs that might have the files open
- Try running as Administrator

## Safety Features
- ⚠️ Confirmation dialog before renaming
- 👁️ Visual preview of all changes
- ✅ Only renames explicitly selected files
- 🛡️ Preserves subtitle files and folders
- 📁 Smart folder detection prevents unwanted renames
- 🔒 Robust error handling prevents data loss

## Performance Tips
- Use **🔍 Search Selected** instead of Search All when possible
- Set up default paths for instant loading
- Keep media organized in main folders
- The app caches searches to avoid repeated API calls
- Dark theme reduces eye strain during long sessions

## Tips for Best Results
- Use descriptive filenames with season/episode or year info
- Organize files in folders by show/movie before processing
- Set up default paths for your Downloads, TV Shows, Movies folders
- Always review the preview before confirming rename
- The app saves all settings locally for convenience
- Take advantage of recursive scanning - just point to parent folders!

## Support
If you encounter issues:
1. Check that Python and requests library are installed
2. Verify your API keys are correct in Settings
3. Make sure files follow standard naming patterns
4. Check file permissions in the target folders
5. Review the status bar for error messages

## Version History
- **v2.0** (Current) - Fixed auto-loading, added dark theme, optimized performance
- **v1.0** - Initial release with basic renaming functionality

Enjoy organizing your media library with style! 🎬✨
