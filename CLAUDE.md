# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Renamer** is a desktop media file renaming tool (v2.0) built with Python/Tkinter. It automatically renames TV shows and movies using TVDB and TMDB APIs, with intelligent folder cleanup and dark theme UI.

### Core Functionality

The app performs three main operations when renaming:
1. **File renaming**: Renames media files using data from TVDB/TMDB APIs
2. **Folder renaming**: Intelligently renames parent folders to match content (when folder contains release info keywords or similar names)
3. **Aggressive cleanup**: Deletes junk files and subdirectories while preserving subtitles

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

### Building Executable (PyInstaller)
```bash
# Build standalone executable
pyinstaller Renamer.spec
```

The spec file is configured to create a windowed (non-console) executable with `icon.ico`.

## Architecture & Key Patterns

### Application Structure

The application follows a single-file monolithic architecture with two main classes:

1. **`DarkTheme`** (lines 21-136): Static theme configuration
   - Defines all color constants and ttk style configurations
   - `apply_theme(root)` method applies dark theme globally on startup

2. **`RenamerApp`** (lines 139-1396): Main application class
   - Manages all UI, state, and business logic
   - Uses threading for API calls and file operations to prevent UI freezing

### Critical Data Structures

```python
self.files = []                    # List of file info dicts with parsed metadata
self.search_results = {}           # {file_id: [api_results]}
self.selected_matches = {}         # {file_id: selected_match}
self.file_selected = {}            # {file_id: bool} - tracks rename selection
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
- Default test files location: `media-test-files/` and `example-files/`
- Old versions preserved in `old-app-versions/old/` for reference

## File Extensions

Media: `.mkv`, `.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.m4v`
Subtitles: `.srt`, `.sub`, `.idx`, `.ass`, `.ssa`, `.vtt`
