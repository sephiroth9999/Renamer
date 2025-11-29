# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Renamer** is a desktop media file renaming tool (v2.0) built with Python/Tkinter. It automatically renames TV shows and movies using TVDB and TMDB APIs, with intelligent folder cleanup and dark theme UI.

### Version Information
- **Current Version**: 2.0
- **Total Lines**: 1446 lines in renamer.py
- **Python Version**: Python 3.x
- **Main File**: `renamer.py` (single-file monolithic architecture)

### Core Functionality

The app performs three main operations when renaming:
1. **File renaming**: Renames media files using data from TVDB/TMDB APIs
2. **Folder renaming**: Intelligently renames parent folders to match content (when folder contains release info keywords or similar names)
3. **Aggressive cleanup**: Deletes junk files and subdirectories while preserving subtitles

### Repository Structure

```
Renamer/
├── renamer.py              # Main application (1446 lines)
├── requirements.txt        # Python dependencies
├── Renamer.spec            # PyInstaller build configuration
├── run_renamer.bat         # Windows launcher script
├── icon.ico                # Application icon
├── CLAUDE.md               # This file - AI assistant guidance
├── RENAMER-README.md       # User-facing documentation
├── .gitignore              # Git ignore rules
├── .claude/                # Claude Code settings
│   └── settings.local.json # Local Claude configuration
├── deploy/                 # Deployment files (copies for distribution)
│   ├── CLAUDE.md
│   ├── RENAMER-README.md
│   ├── Renamer.spec
│   ├── icon.ico
│   ├── renamer.py
│   ├── requirements.txt
│   └── run_renamer.bat
└── app-icon-image-files/   # Icon source files (PNG versions)
```

**Ignored Directories** (in .gitignore):
- `old-app-versions/` - Previous versions preserved for reference
- `media-test-files/` - Test media files
- `example-files/` - Example files for testing
- Python build artifacts (dist/, build/, __pycache__, etc.)

## Development Commands

### Running the Application
```bash
# Method 1: Direct Python execution
python renamer.py

# Method 2: Using batch file (Windows)
run_renamer.bat
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies:**
- `requests==2.31.0` - For API calls to TVDB and TMDB
- `tkinter-tooltip==2.1.0` - For UI tooltips
- `tkinter` - Built-in with Python (GUI framework)

### Building Executable (PyInstaller)
```bash
# Build standalone executable
pyinstaller Renamer.spec
```

The spec file is configured to create a windowed (non-console) executable with `icon.ico`.

**Build Configuration Details** (Renamer.spec):
- No console window (`console=False`)
- UPX compression enabled
- Icon: `icon.ico`
- Single-file executable
- All dependencies bundled

### Git Workflow

Current branch: `claude/claude-md-mi5o1fdzak7vvg9j-018Hu7cZMQPjVF8N7bjbd3Dx`

**When making changes:**
1. Work on the designated feature branch
2. Commit with clear, descriptive messages
3. Push to the specified branch when complete
4. Use `git push -u origin <branch-name>` for pushing

**Configuration:**
- User config stored at: `~/.renamer_config.json` (gitignored)
- Claude settings in: `.claude/settings.local.json`

## Architecture & Key Patterns

### Application Structure

The application follows a single-file monolithic architecture with clear separation of concerns:

**Main Components:**

1. **`DarkTheme`** (lines 21-136): Static theme configuration class
   - Defines all color constants (BG, FG, ACCENT, SUCCESS, ERROR, WARNING, etc.)
   - Configures ttk styles for all UI components
   - `apply_theme(root)` method applies dark theme globally on startup
   - Uses 'clam' theme as base and customizes all widget styles
   - Provides consistent look across Buttons, Entries, Notebooks, Treeviews, etc.

2. **`RenamerApp`** (lines 139-1430): Main application class
   - Manages all UI, state, and business logic
   - Uses threading for API calls and file operations to prevent UI freezing
   - Implements complete workflow: file loading → searching → renaming → cleanup
   - Handles all user interactions and state management

3. **`main()`** (lines 1432-1442): Entry point
   - Creates Tk root window
   - Sets application icon (icon.ico)
   - Instantiates RenamerApp
   - Starts main event loop

### Critical Data Structures

**State Management:**
```python
# File tracking
self.files = []                    # List of file info dicts with parsed metadata
                                   # Each dict: {id, path, original, type, name, season, episode, year}
self.file_id_counter = 0           # Unique ID generator for files

# Search and matching
self.search_results = {}           # {file_id: [api_results]} - all matches from API
self.selected_matches = {}         # {file_id: selected_match} - user's chosen match
self.file_selected = {}            # {file_id: bool} - checkbox state for renaming

# File extensions
self.media_extensions = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.m4v'}
self.subtitle_extensions = {'.srt', '.sub', '.idx', '.ass', '.ssa', '.vtt'}

# Configuration
self.config = {}                   # Loaded from ~/.renamer_config.json
                                   # Keys: tvdb, tmdb, default_paths, auto_load, dark_theme
```

**File Info Dictionary Structure:**
```python
{
    'id': int,                     # Unique identifier (used as Treeview item ID)
    'path': str,                   # Full absolute path to file
    'original': str,               # Original filename with extension
    'type': str,                   # 'tv' or 'movie'
    'name': str,                   # Parsed show/movie name
    'season': int,                 # Season number (TV shows only)
    'episode': int,                # Episode number (TV shows only)
    'year': int                    # Release year (movies, optional)
}
```

### Configuration Management

- Config stored at: `Path.home() / ".renamer_config.json"`
- Config keys: `tvdb`, `tmdb`, `default_paths`, `auto_load`, `dark_theme`
- Settings tab allows users to configure API keys and default media folders

### Filename Parsing Logic (lines 683-733)

The parser uses regex patterns in priority order:
1. **TV Shows**: `S01E01`, `1x01`, `Season 1 Episode 1` formats
2. **Movies**: `Movie.Name.2023` or `Movie Name (2023)` with year validation (1900-2030)
3. **Fallback**: Treats as movie without year

Returns dict with: `type`, `name`, `season`/`episode` (TV), `year` (movies), `path`, `id`

### Multi-File Folder Detection (lines 1314-1321)

**Critical feature**: Before renaming, the app detects if multiple files being renamed are in the same folder.

When 2+ files in the same folder are selected for renaming:
- **Folder name is preserved** (not renamed)
- **All media files are kept** (not deleted)
- **Junk files are still deleted** (txt, nfo, etc.)
- Confirmation dialog indicates how many multi-file folders detected

This handles common scenarios:
- Season folders with multiple episodes
- Themed collections (Christmas movies, Halloween films)
- Download folders with multiple items

### Smart Folder Renaming (lines 1218-1239)

Folders are renamed **only for single-file folders** when they contain:
- **Release info keywords**: `720p`, `1080p`, `brrip`, `webrip`, `yify`, `x264`, `hevc`, etc.
- **Similar names**: Jaccard similarity ≥ 0.7 threshold (lines 1199-1216)

New folder name matches the cleaned media filename (without extension).

### Cleanup Strategy (lines 1241-1299)

The `cleanup_folder()` method has a `preserve_media` parameter:
- `preserve_media=False` (single-file folders): Deletes other media files
- `preserve_media=True` (multi-file folders): Keeps all media files

Always protected:
- Main media file being renamed
- All subtitle files (`.srt`, `.sub`, `.idx`, `.ass`, `.ssa`, `.vtt`)
- Subtitle folders (`subtitles`, `subs`, `subtitle`, `sub` - case insensitive)
- **Other media files when `preserve_media=True`**

Always deleted:
- Non-media, non-subtitle files (txt, nfo, etc.)
- Non-protected subdirectories

### API Integration

**TVDB** (lines 813-879):
- Authenticates with apikey, receives bearer token
- Searches series by name
- Fetches episode details for first match (season/episode number)
- Returns up to 5 matches

**TMDB** (lines 881-916):
- Simpler API - uses API key in query params
- Searches movies by name and optional year
- Returns up to 5 matches

Both use 10-second timeouts and gracefully handle network errors.

### Threading Pattern

All long-running operations use daemon threads:
```python
threading.Thread(target=search_thread, daemon=True).start()
```

Used for:
- Auto-loading files on startup (line 168 with 500ms delay)
- Loading default paths (lines 596-632)
- Searching files (lines 949-987, 1000-1036)

### UI Organization

Two-tab notebook interface:
1. **Files Tab**: Treeview with columns (Selected, Filename, Type, Parsed Name, Status, New Name)
2. **Settings Tab**: Scrollable frame with API config and default paths

Preview panel shows before/after folder structure using `scrolledtext.ScrolledText` widgets with custom color tags.

## Important Implementation Details

### Auto-Load Timing
The auto-load feature (lines 166-168) uses `root.after(500, ...)` to ensure UI is fully initialized before loading files. This fixed a critical bug from v1.0.

### Path Normalization
All folder paths are normalized with `os.path.normpath()` to ensure consistent comparisons (line 565).

### Duplicate Prevention
Files are checked against existing `self.files` before adding (line 767) to prevent duplicates.

### Selection State Management
Files have two independent states:
- **Search selection**: Determines which files to search via "Search Selected" button
- **Rename selection**: `self.file_selected[file_id]` determines which files to rename

Double-click toggles rename selection (lines 657-681).

### Subtitle Renaming
When renaming media files, adjacent `.srt` files are renamed to match (lines 1116-1121).

## Testing Considerations

When testing, be aware:
- Rename operations are **irreversible** - test with copies
- API keys required for full functionality (get from TVDB/TMDB)
- Default test files location: `media-test-files/` and `example-files/` (gitignored)
- Old versions preserved in `old-app-versions/old/` (gitignored) for reference
- Use the deploy/ folder for creating distribution packages

**Testing Best Practices:**
1. Always test with copies of media files, never originals
2. Test both TV shows and movies
3. Test multi-file folders (season folders with multiple episodes)
4. Test single-file folders with junk files
5. Verify subtitle files are preserved
6. Check folder renaming logic with release keywords
7. Test network errors and missing API keys

## File Extensions

**Media Extensions:** `.mkv`, `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.m4v`

**Subtitle Extensions:** `.srt`, `.sub`, `.idx`, `.ass`, `.ssa`, `.vtt`

**Protected Subtitle Folder Names (case-insensitive):** `subtitles`, `subs`, `subtitle`, `sub`

## Key Methods Reference

Quick reference to important methods in RenamerApp (lines 139-1430):

**File Management:**
- `parse_filename(filename: str) -> Dict` (line 683) - Parses filename to extract metadata
- `select_files()` (line 735) - Opens file dialog to add individual files
- `select_folder()` (line 752) - Opens folder dialog and scans for media files
- `scan_folder_for_media(folder: str) -> List[str]` (line 772) - Recursively finds media files

**API Integration:**
- `search_tvdb(show_name: str, season: int, episode: int) -> List[Dict]` (line 813) - Search TVDB for TV episodes
- `search_tmdb(movie_name: str, year: Optional[int]) -> List[Dict]` (line 881) - Search TMDB for movies
- `search_selected()` (line 918) - Search API for selected files only
- `search_all()` (line 949) - Search API for all files

**Folder & Cleanup Logic:**
- `clean_name_for_comparison(name: str) -> str` (line 1191) - Normalize names for comparison
- `is_similar_name(name1: str, name2: str, threshold: float) -> bool` (line 1199) - Jaccard similarity check (≥0.7)
- `should_rename_parent_folder(file_path: str, new_filename: str) -> Tuple[bool, str]` (line 1218) - Determines if folder should be renamed
- `cleanup_folder(folder_path: str, keep_file: str, preserve_media: bool)` (line 1241) - Deletes junk files/folders

**Renaming:**
- `rename_files()` (line 1301) - Main rename orchestration method
  - Detects multi-file folders (lines 1314-1321)
  - Shows confirmation dialog
  - Performs renaming, folder renaming, and cleanup
  - Updates UI with results

**UI & Selection:**
- `on_file_double_click(event)` (line 657) - Toggles file selection for renaming
- `select_all_files()` / `select_none_files()` - Bulk selection management
- `update_preview(file_id)` - Shows before/after folder structure

**Configuration:**
- `load_config()` - Loads settings from ~/.renamer_config.json
- `save_config()` - Saves current settings
- `load_default_paths()` (lines 596-632) - Auto-loads files from default folders (threaded)

## Code Patterns & Conventions

**Threading Pattern:**
All long-running operations use daemon threads to prevent UI freezing:
```python
def operation():
    # Do work
    self.status_var.set("Status message")

thread = threading.Thread(target=operation, daemon=True)
thread.start()
```

**Error Handling:**
- All API calls wrapped in try/except with timeouts (10 seconds)
- File operations handle permission errors gracefully
- User feedback via messagebox for errors
- Status bar updates for real-time feedback

**UI Update Pattern:**
- Always update UI from main thread
- Use StringVar/IntVar for reactive updates
- Tree view item IDs match file IDs for easy lookup

**Naming Conventions:**
- Instance variables use `self.variable_name`
- Methods use `snake_case`
- Class names use `PascalCase`
- Constants in DarkTheme use `UPPER_CASE`

**Path Handling:**
- Always use `os.path.normpath()` for consistency (line 565)
- Store absolute paths, not relative
- Use `Path` from pathlib for config file location

## Common Development Tasks

**Adding a new file format:**
1. Add extension to `self.media_extensions` (around line 145)
2. Test parsing with the new format
3. Update documentation in RENAMER-README.md

**Modifying rename format:**
1. Locate format_new_filename() or similar method
2. Update for TV shows (S##E## format) or movies (Name (Year) format)
3. Test with various filename patterns

**Adding a new API source:**
1. Create new method like `search_newapi()`
2. Follow pattern of search_tvdb/search_tmdb (lines 813-916)
3. Add API key to config structure
4. Add UI elements in Settings tab
5. Integrate into search workflow

**Debugging tips:**
- Check console output - print statements throughout code
- Verify API keys in ~/.renamer_config.json
- Test with simple filenames first
- Use status_var.set() to add debug messages to UI

## Security Considerations

**API Keys:**
- Stored in ~/.renamer_config.json (gitignored)
- Never commit API keys to repository
- Keys sent in headers (TVDB) or query params (TMDB)

**File Operations:**
- No arbitrary command execution
- All file operations use Python's os/shutil modules
- User confirmation required before destructive operations
- Preview shown before any changes

**Network Requests:**
- 10-second timeout on all requests
- HTTPS only (TVDB and TMDB APIs)
- No user data sent to APIs beyond search terms

## Deployment Process

**For distribution:**
1. Update version number in docstring (line 5)
2. Test thoroughly with various file types
3. Copy latest files to `deploy/` folder:
   ```bash
   cp renamer.py deploy/
   cp requirements.txt deploy/
   cp *.md deploy/
   cp *.spec deploy/
   cp *.ico deploy/
   cp *.bat deploy/
   ```
4. Build executable: `pyinstaller Renamer.spec`
5. Test executable on clean system
6. Distribute deploy/ folder or dist/Renamer.exe

**Version control:**
- Commit to feature branch
- Clear commit messages describing changes
- Push when ready for review/merge

## Known Issues & Gotchas

**Auto-load timing issue (FIXED in v2.0):**
- v1.0 had issues with auto-loading files on startup
- Fixed by using `root.after(500, ...)` to delay auto-load until UI is ready (line 168)
- Never auto-load synchronously in `__init__`

**Multi-file folder detection is critical:**
- Without it, season folders would have all episodes deleted except one
- Always preserve media files when `len(files_in_folder) > 1`
- This is THE most important safety feature

**Jaccard similarity threshold:**
- Current threshold: 0.7 (70% word overlap)
- Too low: renames unrelated folders
- Too high: misses valid folder renames
- 0.7 balances precision and recall well

**API rate limiting:**
- TVDB and TMDB have rate limits
- No current rate limiting in code
- If issues arise, add delays between API calls

**Windows-specific issues:**
- Batch file only works on Windows
- Icon path handling differs on Linux/Mac
- File operations tested primarily on Windows

## AI Assistant Guidelines

**When analyzing this codebase:**
1. Always reference line numbers from renamer.py for accuracy
2. The file is 1446 lines - don't make assumptions about code not visible
3. Check RENAMER-README.md for user-facing documentation
4. Remember this is a single-file application - all logic is in renamer.py

**When making changes:**
1. **Safety first**: This app deletes files - test thoroughly
2. **Preserve the multi-file folder detection** - it's critical
3. **Update both CLAUDE.md and RENAMER-README.md** when adding features
4. **Test with real file scenarios** before committing
5. **Update line number references** in documentation after changes
6. **Keep the deploy/ folder in sync** for distribution

**When adding features:**
1. Follow existing patterns (threading, error handling, UI updates)
2. Update status_var for user feedback
3. Add emoji indicators for consistency with existing UI
4. Test both TV shows AND movies
5. Consider edge cases (missing API keys, network errors, permission issues)

**When debugging:**
1. Check console output first
2. Verify ~/.renamer_config.json exists and is valid JSON
3. Test API keys manually if search fails
4. Use simple, well-formatted filenames for initial testing
5. Check file permissions on test files/folders

**Code quality standards:**
1. Maintain type hints on function signatures
2. Add docstrings to new methods
3. Use descriptive variable names
4. Keep methods focused (single responsibility)
5. Handle errors gracefully with user-friendly messages

**Documentation updates required when:**
- Adding/removing methods (update Key Methods Reference)
- Changing line numbers significantly (update all line references)
- Adding new features (update both CLAUDE.md and RENAMER-README.md)
- Modifying data structures (update Critical Data Structures)
- Changing file extensions or protected folders (update File Extensions)
- Adding dependencies (update requirements.txt and Installing Dependencies)

## Quick Start for AI Assistants

**To understand the codebase:**
1. Read this CLAUDE.md completely
2. Skim RENAMER-README.md for user perspective
3. Read renamer.py focusing on:
   - DarkTheme class (lines 21-136)
   - RenamerApp.__init__ (lines 139-200)
   - parse_filename (line 683)
   - search_tvdb/search_tmdb (lines 813-916)
   - rename_files (line 1301)
   - cleanup_folder (line 1241)

**To make a simple change:**
1. Locate the relevant method using Key Methods Reference
2. Read the method and understand its context
3. Make the change following existing patterns
4. Test with appropriate file types
5. Update documentation if needed
6. Commit with clear message

**To add a major feature:**
1. Understand the full workflow first
2. Design the feature following existing patterns
3. Update data structures if needed
4. Add UI elements in appropriate tab
5. Implement business logic
6. Add error handling
7. Update configuration if needed
8. Test thoroughly (TV + movies, single + multi-file folders)
9. Update both CLAUDE.md and RENAMER-README.md
10. Commit and push to feature branch

## Related Files

- **RENAMER-README.md**: User-facing documentation with installation instructions, features, troubleshooting
- **requirements.txt**: Python dependencies
- **Renamer.spec**: PyInstaller build configuration
- **run_renamer.bat**: Windows launcher
- **.gitignore**: Defines ignored files/folders
- **deploy/**: Distribution folder (copies of all necessary files)

## Support & Resources

**External APIs:**
- TVDB API: https://thetvdb.com/api-information
- TMDB API: https://www.themoviedb.org/settings/api

**Python Documentation:**
- tkinter: https://docs.python.org/3/library/tkinter.html
- requests: https://requests.readthedocs.io/
- PyInstaller: https://pyinstaller.readthedocs.io/

**For users needing help:**
- Direct them to RENAMER-README.md
- Check Troubleshooting section first
- Verify API keys and Python installation
- Test with simple filenames before complex ones
