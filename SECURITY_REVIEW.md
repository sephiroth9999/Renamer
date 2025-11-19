# Security Code Review - Renamer v2.0

**Review Date:** 2025-11-19
**Reviewer:** Security Code Review
**Application:** Renamer - Media File Renaming Tool v2.0

## Executive Summary

This security review identified **12 critical and high-severity vulnerabilities** in the Renamer application that could lead to:
- Arbitrary file system access and manipulation
- Data loss through uncontrolled deletion
- API key exposure and credential leakage
- Race conditions and data corruption
- Potential for path traversal attacks

**Risk Level: HIGH** - Immediate remediation recommended before production use.

---

## Critical Vulnerabilities

### 1. Path Traversal Vulnerability (CRITICAL)
**Location:** Lines 562-565, 747-758, 220-228, 602-610
**CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)

**Description:**
The application allows users to select arbitrary directories without validating paths or restricting access to specific directories. An attacker could:
- Access sensitive system directories (`/etc`, `/root`, `C:\Windows\System32`)
- Process files in protected locations
- Traverse to parent directories using `..` sequences

**Vulnerable Code:**
```python
# renamer.py:562-565
def add_default_path(self):
    folder = filedialog.askdirectory(title='Select default media folder')
    if folder:
        folder = os.path.normpath(folder)  # Normalization alone is insufficient
        # No validation that folder is within allowed boundaries
```

**Impact:**
- **Severity: CRITICAL**
- Attackers can read/rename/delete files anywhere on the filesystem
- Could target system files, configuration files, or other users' data
- `os.path.normpath()` does NOT prevent path traversal attacks

**Proof of Concept:**
```python
# User could provide paths like:
/home/user/../../../etc/
C:\Users\User\..\Administrator\Documents
```

**Recommendation:**
```python
import os
from pathlib import Path

ALLOWED_BASE_PATHS = [
    Path.home() / "Videos",
    Path.home() / "Downloads",
    Path.home() / "Documents" / "Media"
]

def is_safe_path(user_path: str) -> bool:
    """Validate path is within allowed directories"""
    try:
        resolved = Path(user_path).resolve()
        return any(
            resolved == base or base in resolved.parents
            for base in ALLOWED_BASE_PATHS
        )
    except (ValueError, RuntimeError):
        return False

def add_default_path(self):
    folder = filedialog.askdirectory(title='Select default media folder')
    if folder and is_safe_path(folder):
        # Safe to proceed
        pass
    else:
        messagebox.showerror("Invalid Path", "Please select a path within allowed directories")
```

---

### 2. Arbitrary File Deletion (CRITICAL)
**Location:** Lines 1241-1299, 1274-1276, 1290-1292
**CWE:** CWE-732 (Incorrect Permission Assignment for Critical Resource)

**Description:**
The `cleanup_folder()` function recursively deletes directories and files with minimal validation. Combined with the path traversal vulnerability, this could result in catastrophic data loss.

**Vulnerable Code:**
```python
# renamer.py:1274-1276
try:
    shutil.rmtree(item_path)  # Recursively deletes entire directory tree
    deleted_dirs += 1
except Exception as e:
    print(f"Failed to delete directory {item}: {e}")
```

**Attack Scenario:**
1. Attacker selects `/home/user/` as media folder
2. Places a malicious media file in `/home/user/important_project/`
3. Triggers rename operation
4. `cleanup_folder()` deletes all non-media files in `important_project/`
5. User loses all project files (code, documents, etc.)

**Impact:**
- **Severity: CRITICAL**
- Permanent data loss
- No confirmation dialog for individual deletions
- No recycle bin / trash integration
- Affects files user may not be aware of

**Recommendation:**
```python
def cleanup_folder(self, folder_path: str, keep_file: str, preserve_media: bool = False):
    """Delete non-media files with safety checks"""

    # 1. Validate folder path is within allowed directories
    if not is_safe_path(folder_path):
        raise ValueError("Folder path outside allowed directories")

    # 2. Create a preview of what will be deleted
    files_to_delete = []
    dirs_to_delete = []

    # ... build lists ...

    # 3. Require explicit confirmation with preview
    confirmation = messagebox.askyesno(
        "Confirm Deletion",
        f"About to delete:\n{len(files_to_delete)} files\n{len(dirs_to_delete)} directories\n\n"
        f"Preview: {', '.join(files_to_delete[:5])}\n\n"
        "This cannot be undone. Continue?"
    )

    if not confirmation:
        return 0, 0

    # 4. Use send2trash instead of permanent deletion
    import send2trash
    for item in files_to_delete:
        send2trash.send2trash(item)  # Moves to recycle bin instead
```

---

### 3. Insecure Credential Storage (HIGH)
**Location:** Lines 149-150, 182-198, 545-558
**CWE:** CWE-522 (Insufficiently Protected Credentials)

**Description:**
API keys are stored in plaintext in `~/.renamer_config.json` without any encryption or access controls beyond default file permissions.

**Vulnerable Code:**
```python
# renamer.py:196-198
def save_config(self):
    with open(self.config_file, 'w') as f:
        json.dump(self.api_keys, f, indent=2)  # Plaintext storage
```

**Example Config File:**
```json
{
  "tvdb": "actual-api-key-12345",
  "tmdb": "actual-tmdb-key-67890",
  "default_paths": ["/home/user/Videos"],
  "auto_load": true
}
```

**Impact:**
- **Severity: HIGH**
- API keys accessible to malware or other users
- Keys could be logged, backed up to cloud, or included in system snapshots
- No key rotation mechanism
- Violates OWASP A02:2021 - Cryptographic Failures

**Recommendation:**
```python
from cryptography.fernet import Fernet
import keyring  # Use system keyring for encryption key

def save_config(self):
    """Save config with encrypted API keys"""
    # Get or create encryption key from system keyring
    key = keyring.get_password("renamer", "encryption_key")
    if not key:
        key = Fernet.generate_key().decode()
        keyring.set_password("renamer", "encryption_key", key)

    cipher = Fernet(key.encode())

    # Encrypt sensitive fields
    safe_config = self.api_keys.copy()
    if safe_config.get('tvdb'):
        safe_config['tvdb'] = cipher.encrypt(safe_config['tvdb'].encode()).decode()
    if safe_config.get('tmdb'):
        safe_config['tmdb'] = cipher.encrypt(safe_config['tmdb'].encode()).decode()

    # Set restrictive permissions (0600)
    with open(self.config_file, 'w') as f:
        json.dump(safe_config, f, indent=2)
    os.chmod(self.config_file, 0o600)
```

---

### 4. API Key Exposure in URL Parameters (HIGH)
**Location:** Lines 887-896
**CWE:** CWE-598 (Use of GET Request Method With Sensitive Query Strings)

**Description:**
TMDB API key is passed in URL query parameters, which can be logged by proxies, web servers, browser history, and monitoring tools.

**Vulnerable Code:**
```python
# renamer.py:887-896
def search_tmdb(self, movie_name: str, year: Optional[int] = None) -> List[Dict]:
    params = {
        'api_key': self.api_keys['tmdb'],  # Exposed in URL
        'query': movie_name
    }
    response = requests.get('https://api.themoviedb.org/3/search/movie',
                           params=params,  # Key visible in logs
                           timeout=10)
```

**Where Keys Can Leak:**
- HTTP proxy logs
- Browser network inspector
- System network monitoring tools
- Reverse proxy logs (nginx, Apache)
- Request tracing tools

**Impact:**
- **Severity: HIGH**
- API key compromise
- Unauthorized API usage
- Account suspension

**Recommendation:**
```python
def search_tmdb(self, movie_name: str, year: Optional[int] = None) -> List[Dict]:
    """Search TMDB using header-based authentication"""
    # Use Authorization header instead of query params
    headers = {
        'Authorization': f'Bearer {self.api_keys["tmdb"]}',
        'Content-Type': 'application/json'
    }

    params = {'query': movie_name}
    if year:
        params['year'] = year

    response = requests.get(
        'https://api.themoviedb.org/3/search/movie',
        params=params,
        headers=headers,
        timeout=10
    )
```

---

### 5. Race Conditions / TOCTOU (HIGH)
**Location:** Lines 1367-1386, multiple threading operations
**CWE:** CWE-362 (Concurrent Execution using Shared Resource with Improper Synchronization)

**Description:**
The application has multiple race conditions between checking file state and performing operations, especially during rename operations and when multiple threads access shared state.

**Vulnerable Code:**
```python
# renamer.py:1367-1386
# No file locking mechanism
temp_new_path = os.path.join(old_dir, new_filename)
if old_path != temp_new_path:  # Check
    os.rename(old_path, temp_new_path)  # Use - file could change in between

# Later...
if old_dir != new_dir:  # Check
    if not os.path.exists(new_dir):  # Additional check
        os.rename(old_dir, new_dir)  # Use - directory could be created by another process
```

**Thread Safety Issues:**
```python
# Multiple threads access without locks:
self.files = []                # Lines 949-987 (search_thread)
self.search_results = {}       # Lines 1000-1036 (search_thread)
self.selected_matches = {}     # Lines 204-254 (auto_load_files)
self.file_selected = {}        # Lines 596-632 (load_thread)
```

**Attack Scenario:**
1. User starts rename operation on folder A
2. Another process/user creates a file with the target name
3. `os.rename()` fails, but cleanup has already deleted files
4. Data loss occurs

**Impact:**
- **Severity: HIGH**
- Data corruption
- Unexpected application behavior
- Partial operations leaving filesystem in inconsistent state
- Potential for data loss

**Recommendation:**
```python
import threading
import fcntl  # Unix file locking
import contextlib

class RenamerApp:
    def __init__(self, root):
        # Add thread locks
        self.file_lock = threading.Lock()
        self.search_lock = threading.Lock()

    @contextlib.contextmanager
    def atomic_file_operation(self, file_path):
        """Ensure exclusive access during file operations"""
        with open(file_path, 'r') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def rename_files(self):
        """Thread-safe rename operation"""
        with self.file_lock:
            # Perform all file operations atomically
            for file_id, match in files_to_rename.items():
                # Use atomic operations
                try:
                    # Use os.replace() instead of os.rename() for atomic operation
                    os.replace(old_path, new_path)
                except FileExistsError:
                    # Handle collision gracefully
                    pass
```

---

### 6. Insufficient Input Validation (MEDIUM)
**Location:** Lines 1045-1046, 1049, 683-733
**CWE:** CWE-20 (Improper Input Validation)

**Description:**
File and folder names are sanitized but with incomplete validation. This could lead to filesystem issues or unexpected behavior.

**Vulnerable Code:**
```python
# renamer.py:1045-1046
clean_name = re.sub(r'[:<>"/\\|?*]', '', match['name'])
clean_episode = re.sub(r'[:<>"/\\|?*]', '', match.get('episodeName', ''))
# Missing: length validation, reserved names, unicode issues, trailing dots/spaces
```

**Missing Validations:**
1. **Filename length limits** (255 bytes on most systems, less for some)
2. **Reserved names** (CON, PRN, AUX, NUL on Windows)
3. **Leading/trailing spaces or dots** (problematic on Windows)
4. **Unicode normalization** (could create duplicate names)
5. **Empty filenames** after sanitization
6. **Path length limits** (260 chars on Windows, 4096 on Linux)

**Impact:**
- **Severity: MEDIUM**
- File operations could fail silently
- Could create files that are difficult to delete (trailing dots)
- Platform-specific issues

**Recommendation:**
```python
import unicodedata
import re

class FilenameValidator:
    # Windows reserved names
    RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }

    MAX_FILENAME_LENGTH = 255
    MAX_PATH_LENGTH = 4096  # Conservative limit

    @staticmethod
    def sanitize_filename(name: str, extension: str = '') -> str:
        """Comprehensive filename sanitization"""
        # 1. Unicode normalization
        name = unicodedata.normalize('NFKD', name)

        # 2. Remove invalid characters
        name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)

        # 3. Remove leading/trailing spaces and dots
        name = name.strip('. ')

        # 4. Check for reserved names
        base_name = name.split('.')[0].upper()
        if base_name in FilenameValidator.RESERVED_NAMES:
            name = f"_{name}"

        # 5. Ensure not empty
        if not name:
            name = "unnamed"

        # 6. Check length (accounting for extension)
        full_name = f"{name}{extension}"
        if len(full_name.encode('utf-8')) > FilenameValidator.MAX_FILENAME_LENGTH:
            # Truncate while preserving extension
            max_name_bytes = FilenameValidator.MAX_FILENAME_LENGTH - len(extension.encode('utf-8'))
            name = name.encode('utf-8')[:max_name_bytes].decode('utf-8', errors='ignore')

        return name

def generate_new_filename(self, file_info: Dict, match: Dict) -> str:
    """Generate validated filename"""
    extension = os.path.splitext(file_info['original'])[1]

    if file_info['type'] == 'tv' and 'episodeName' in match:
        season_str = f"{match.get('season', file_info['season']):02d}"
        episode_str = f"{match.get('episode', file_info['episode']):02d}"

        # Use validator
        clean_name = FilenameValidator.sanitize_filename(match['name'])
        clean_episode = FilenameValidator.sanitize_filename(match.get('episodeName', ''))

        return f"{clean_name} - S{season_str}E{episode_str} - {clean_episode}{extension}"
    else:
        clean_name = FilenameValidator.sanitize_filename(match['name'])
        return f"{clean_name} ({match['year']}){extension}"
```

---

### 7. Information Disclosure (MEDIUM)
**Location:** Lines 190, 201, 232, 253, 874-879, 911-916, 1137, 1409
**CWE:** CWE-209 (Generation of Error Message Containing Sensitive Information)

**Description:**
Detailed error messages with full file paths and system information are printed to console and displayed to users.

**Vulnerable Code:**
```python
# renamer.py:190
except Exception as e:
    print(f"Error loading config: {e}")  # Could expose path info

# renamer.py:1137
except Exception as e:
    structure.append(f"  ⚠️ Error reading directory: {e}")  # Shown to user

# renamer.py:1409
except Exception as e:
    error_count += 1
    errors.append(f"{file_info.get('original', 'unknown')}: {str(e)}")  # Detailed error
```

**Information Leaked:**
- Full filesystem paths
- User directory structure
- System configuration details
- Python stack traces
- Library versions (in exceptions)

**Impact:**
- **Severity: MEDIUM**
- Aids reconnaissance for attackers
- Leaks directory structure
- Could expose sensitive paths
- Violates principle of least information

**Recommendation:**
```python
import logging
import sys

# Configure proper logging
logging.basicConfig(
    filename=Path.home() / '.renamer_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Use different messages for users vs logs
def handle_error(operation: str, error: Exception, user_message: str = None):
    """Centralized error handling"""
    # Log detailed error for debugging
    logging.error(f"{operation} failed: {type(error).__name__}: {error}", exc_info=True)

    # Show generic message to user
    if user_message is None:
        user_message = f"An error occurred during {operation}. Please check the log file."

    return user_message

# Usage:
try:
    with open(self.config_file, 'r') as f:
        loaded_config = json.load(f)
except Exception as e:
    message = handle_error("configuration loading", e, "Failed to load settings")
    messagebox.showerror("Error", message)
```

---

### 8. No Certificate Validation (MEDIUM)
**Location:** Lines 820-826, 831-838, 894-896
**CWE:** CWE-295 (Improper Certificate Validation)

**Description:**
While HTTPS is used for API calls, there's no explicit certificate validation configuration, and no certificate pinning for known services.

**Vulnerable Code:**
```python
# renamer.py:820-826
auth_response = requests.post(
    'https://api4.thetvdb.com/v4/login',
    json={'apikey': self.api_keys['tvdb']},
    timeout=10
    # No cert verification specified
)
```

**Impact:**
- **Severity: MEDIUM**
- Man-in-the-middle attacks possible
- API keys could be intercepted
- API responses could be tampered with

**Recommendation:**
```python
import certifi
import requests

class SecureAPIClient:
    """Wrapper for secure API calls"""

    # Certificate pins for known services (public keys)
    CERT_PINS = {
        'api4.thetvdb.com': 'sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
        'api.themoviedb.org': 'sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB='
    }

    @staticmethod
    def make_request(method: str, url: str, **kwargs):
        """Make secure HTTP request with validation"""
        # Use certifi for updated CA bundle
        kwargs['verify'] = certifi.where()

        # Enforce TLS 1.2+
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_connections=10,
            pool_maxsize=10
        )
        session.mount('https://', adapter)

        # Make request
        response = session.request(method, url, **kwargs)

        # Verify response
        response.raise_for_status()
        return response

# Usage:
response = SecureAPIClient.make_request(
    'POST',
    'https://api4.thetvdb.com/v4/login',
    json={'apikey': self.api_keys['tvdb']},
    timeout=10
)
```

---

### 9. Regular Expression Denial of Service (ReDoS) (LOW)
**Location:** Lines 689-696, 710-716
**CWE:** CWE-1333 (Inefficient Regular Expression Complexity)

**Description:**
Regex patterns for parsing filenames could be exploited with crafted input causing exponential backtracking.

**Vulnerable Code:**
```python
# renamer.py:689-692
tv_patterns = [
    r'^(.+?)[\s._-]+[Ss](\d+)[Ee](\d+)',  # Potential backtracking on (.+?)
    r'^(.+?)[\s._-]+(\d+)[xX](\d+)',
    # ...
]
```

**Attack Scenario:**
```python
# Malicious filename designed to cause ReDoS
malicious = "A" * 10000 + "SSSSSSSSSSSSSSSS1E1.mkv"
# The (.+?) with multiple possible matches causes excessive backtracking
```

**Impact:**
- **Severity: LOW**
- CPU exhaustion
- Application hang/freeze
- Denial of service (local)

**Recommendation:**
```python
import re
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    """Timeout context manager"""
    def timeout_handler(signum, frame):
        raise TimeoutError()

    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def parse_filename(self, filename: str) -> Dict:
    """Parse filename with timeout protection"""
    try:
        with timeout(1):  # 1 second max for regex
            # Use more specific patterns to reduce backtracking
            tv_patterns = [
                r'^([^/]+?)[\s._-]+[Ss](\d{1,3})[Ee](\d{1,3})',  # Limit digit length
                r'^([^/]+?)[\s._-]+(\d{1,3})[xX](\d{1,3})',
                # More specific patterns
            ]

            for pattern in tv_patterns:
                match = re.match(pattern, filename)
                if match:
                    return self._extract_tv_info(match)
    except TimeoutError:
        logging.warning(f"Regex timeout on filename: {filename[:50]}")
        # Return default parse

    return self._default_parse(filename)
```

---

### 10. No API Rate Limiting (LOW)
**Location:** Lines 813-916 (API functions)
**CWE:** CWE-770 (Allocation of Resources Without Limits or Throttling)

**Description:**
No rate limiting on API calls could lead to account suspension or service blocks.

**Impact:**
- **Severity: LOW**
- API key suspension
- IP address blocking
- Service degradation

**Recommendation:**
```python
import time
from collections import deque
from threading import Lock

class RateLimiter:
    """Token bucket rate limiter"""
    def __init__(self, calls_per_second: float):
        self.calls_per_second = calls_per_second
        self.timestamps = deque()
        self.lock = Lock()

    def wait_if_needed(self):
        """Block if rate limit exceeded"""
        with self.lock:
            now = time.time()

            # Remove old timestamps
            while self.timestamps and self.timestamps[0] < now - 1:
                self.timestamps.popleft()

            if len(self.timestamps) >= self.calls_per_second:
                sleep_time = 1 - (now - self.timestamps[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.timestamps.clear()

            self.timestamps.append(time.time())

class RenamerApp:
    def __init__(self, root):
        # Rate limiters for each API
        self.tvdb_limiter = RateLimiter(calls_per_second=2)
        self.tmdb_limiter = RateLimiter(calls_per_second=4)

    def search_tvdb(self, show_name: str, season: int, episode: int):
        self.tvdb_limiter.wait_if_needed()
        # ... make API call
```

---

### 11. Auto-Load Security Risk (MEDIUM)
**Location:** Lines 166-168, 204-254
**CWE:** CWE-434 (Unrestricted Upload of File with Dangerous Type)

**Description:**
The auto-load feature automatically scans and processes files on startup without user interaction, which could process malicious files.

**Vulnerable Code:**
```python
# renamer.py:166-168
if self.api_keys.get('auto_load', False) and self.api_keys.get('default_paths'):
    self.root.after(500, self.auto_load_files)  # Automatic processing
```

**Attack Scenario:**
1. Attacker places malicious media file with crafted name in monitored directory
2. Application auto-loads on startup
3. Malicious filename exploits parsing vulnerabilities
4. Could trigger ReDoS, path traversal, or other attacks

**Impact:**
- **Severity: MEDIUM**
- Automatic processing of untrusted input
- No user confirmation
- Could trigger other vulnerabilities automatically

**Recommendation:**
```python
def auto_load_files(self):
    """Auto-load with safety checks"""
    # 1. Require explicit user consent every session
    if not self.api_keys.get('auto_load_confirmed'):
        response = messagebox.askyesno(
            "Auto-Load Confirmation",
            "Auto-load will scan default folders for media files.\n\n"
            "Only enable this if you trust all files in these folders.\n\n"
            "Continue?"
        )
        if not response:
            return

    # 2. Implement file count and size limits
    MAX_AUTO_LOAD_FILES = 100
    MAX_FILE_SIZE = 50 * 1024 * 1024 * 1024  # 50GB

    all_files = []
    total_size = 0

    for folder in default_paths:
        for ext in self.media_extensions:
            found = list(Path(folder).glob(f'**/*{ext}'))
            for f in found:
                if len(all_files) >= MAX_AUTO_LOAD_FILES:
                    messagebox.showwarning(
                        "Auto-Load Limit",
                        f"Auto-load limited to {MAX_AUTO_LOAD_FILES} files"
                    )
                    break

                file_size = f.stat().st_size
                if total_size + file_size > MAX_FILE_SIZE:
                    break

                total_size += file_size
                all_files.append(f)

    # 3. Show summary before processing
    response = messagebox.askyesno(
        "Confirm Auto-Load",
        f"Found {len(all_files)} files ({total_size / 1024**3:.1f} GB)\n\n"
        "Process these files?"
    )

    if response:
        self.add_files([str(f) for f in all_files])
```

---

### 12. Unsafe File Extension Checking (LOW)
**Location:** Lines 159-160, 1282, 1289
**CWE:** CWE-434 (Unrestricted Upload of File with Dangerous Type)

**Description:**
File type checking relies solely on extensions, which can be spoofed. No magic number/MIME type validation.

**Vulnerable Code:**
```python
# renamer.py:159-160
self.media_extensions = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.m4v'}
self.subtitle_extensions = {'.srt', '.sub', '.idx', '.ass', '.ssa', '.vtt'}

# renamer.py:1282-1289
_, ext = os.path.splitext(item)
if preserve_media and ext.lower() in self.media_extensions:
    continue  # Keep based solely on extension
```

**Attack Scenario:**
```bash
# Create malicious file disguised as media
mv malicious_script.py fake_movie.mkv
# Application treats it as media file, may not delete it
```

**Impact:**
- **Severity: LOW**
- Could preserve malicious files
- Incorrect file type detection
- Bypass of cleanup logic

**Recommendation:**
```python
import magic  # python-magic library

class FileValidator:
    # Expected MIME types for media files
    MEDIA_MIMES = {
        'video/mp4', 'video/x-matroska', 'video/x-msvideo',
        'video/quicktime', 'video/x-ms-wmv', 'video/x-flv'
    }

    SUBTITLE_MIMES = {
        'text/plain', 'application/x-subrip'
    }

    @staticmethod
    def is_valid_media_file(file_path: str) -> bool:
        """Validate file is actually a media file"""
        try:
            # Check extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in RenamerApp.media_extensions:
                return False

            # Check magic number/MIME type
            mime = magic.from_file(file_path, mime=True)
            if mime not in FileValidator.MEDIA_MIMES:
                logging.warning(f"Extension/MIME mismatch: {file_path} is {mime}")
                return False

            # Check file size (media files should be substantial)
            size = os.path.getsize(file_path)
            if size < 1024 * 1024:  # Less than 1MB is suspicious
                return False

            return True
        except Exception as e:
            logging.error(f"File validation error: {e}")
            return False

# Usage in cleanup_folder:
if preserve_media and ext.lower() in self.media_extensions:
    # Validate it's actually a media file
    if FileValidator.is_valid_media_file(item_path):
        continue
    else:
        logging.warning(f"Fake media file detected: {item_path}")
```

---

## Additional Security Concerns

### 13. No Audit Logging
**Severity: MEDIUM**

The application performs destructive operations (rename, delete) but doesn't maintain an audit log of actions taken.

**Recommendation:**
```python
import logging
from datetime import datetime

class AuditLogger:
    def __init__(self, log_file: Path):
        self.logger = logging.getLogger('audit')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_rename(self, old_path: str, new_path: str):
        self.logger.info(f"RENAME: {old_path} -> {new_path}")

    def log_delete(self, path: str, item_type: str):
        self.logger.info(f"DELETE: {item_type} {path}")

    def log_cleanup(self, folder: str, files_deleted: int, dirs_deleted: int):
        self.logger.info(
            f"CLEANUP: {folder} - {files_deleted} files, {dirs_deleted} dirs deleted"
        )
```

### 14. No Undo Functionality
**Severity: MEDIUM**

All operations are irreversible. Consider implementing:
- Transaction log for undo operations
- Backup before rename
- Preview mode

### 15. Dependency Vulnerabilities
**Severity: VARIES**

**Current Dependencies:**
- `requests==2.31.0` - Check for known CVEs
- `tkinter-tooltip==2.1.0` - Check for updates

**Recommendation:**
```bash
# Add security scanning to CI/CD
pip install safety bandit
safety check --file requirements.txt
bandit -r renamer.py

# Keep dependencies updated
pip-audit
```

### 16. No Code Signing
**Severity: LOW**

The PyInstaller executable is not code-signed, making it easier for malware to impersonate the application.

**Recommendation:**
- Implement code signing for Windows executables
- Provide checksums (SHA256) for releases
- Use trusted distribution channels

---

## Security Testing Recommendations

### Automated Testing
```bash
# Static analysis
bandit -r renamer.py -f json -o bandit_report.json

# Dependency scanning
safety check --file requirements.txt

# Secrets scanning
truffleHog filesystem . --only-verified

# SAST scanning
semgrep --config=auto renamer.py
```

### Manual Testing Checklist
- [ ] Path traversal with `../` sequences
- [ ] Long filename attacks (>255 chars)
- [ ] Reserved filename attacks (CON, PRN, etc.)
- [ ] Unicode normalization issues
- [ ] Symlink following attacks
- [ ] Race condition testing with concurrent operations
- [ ] ReDoS with crafted filenames
- [ ] API key extraction from memory dumps
- [ ] Config file permission testing
- [ ] Network interception (MITM testing)

---

## Remediation Priority

### CRITICAL (Fix Immediately)
1. ✅ Path traversal vulnerability - Implement path validation
2. ✅ Arbitrary file deletion - Add safety checks and confirmations
3. ✅ API key storage - Implement encryption

### HIGH (Fix Before Release)
4. ✅ API key exposure in URLs - Use header authentication
5. ✅ Race conditions - Implement file locking
6. ✅ Auto-load security - Add explicit confirmations

### MEDIUM (Fix Soon)
7. ✅ Input validation - Comprehensive filename sanitization
8. ✅ Information disclosure - Sanitize error messages
9. ✅ Certificate validation - Implement cert pinning
10. ✅ No audit logging - Add operation logging

### LOW (Address When Possible)
11. ✅ ReDoS vulnerabilities - Add regex timeouts
12. ✅ API rate limiting - Implement rate limiters
13. ✅ File type validation - Use magic numbers
14. ✅ Code signing - Sign executables

---

## Secure Development Recommendations

### 1. Security by Design
- Implement principle of least privilege
- Use allowlists instead of denylists
- Fail securely (deny by default)
- Defense in depth approach

### 2. Code Review Process
- Require security review for file operation code
- Use SAST tools in CI/CD pipeline
- Regular dependency updates and scanning

### 3. User Education
- Document security features
- Warn about risks of auto-load
- Provide secure configuration guidelines

### 4. Incident Response
- Implement logging and monitoring
- Create security contact/disclosure policy
- Maintain security changelog

---

## References

- **OWASP Top 10 2021**: https://owasp.org/Top10/
- **CWE Top 25**: https://cwe.mitre.org/top25/
- **NIST Secure Software Development Framework**: https://csrc.nist.gov/Projects/ssdf
- **Python Security Best Practices**: https://python.readthedocs.io/en/stable/library/security_warnings.html

---

## Conclusion

The Renamer application contains multiple **critical security vulnerabilities** that could lead to:
- **Data loss** through uncontrolled file deletion
- **Credential theft** via plaintext API key storage
- **System compromise** through path traversal attacks

**Immediate action required** before any production deployment. All CRITICAL and HIGH severity issues must be addressed.

**Estimated Remediation Time:**
- Critical fixes: 16-24 hours
- High priority fixes: 8-16 hours
- Medium priority fixes: 16-24 hours
- Total: 40-64 hours of development time

**Risk Assessment:**
- **Current State:** HIGH RISK - Not suitable for production use
- **After Critical Fixes:** MEDIUM RISK - Suitable for cautious personal use
- **After All Fixes:** LOW RISK - Suitable for general distribution

---

**Report Completed:** 2025-11-19
**Next Review Date:** After critical fixes implemented
