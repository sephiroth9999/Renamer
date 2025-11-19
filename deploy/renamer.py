#!/usr/bin/env python3
"""
Renamer - Media File Renaming Tool
Automatically renames TV shows and movies using TVDB and TMDB APIs
Version 2.0 - Fixed auto-loading and added dark theme
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import re
import requests
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import threading
import time


class DarkTheme:
    """Dark theme colors and styles"""
    BG = "#1e1e1e"
    BG_SECONDARY = "#252525"
    BG_TERTIARY = "#2d2d2d"
    FG = "#e0e0e0"
    FG_SECONDARY = "#b0b0b0"
    ACCENT = "#4a9eff"
    ACCENT_HOVER = "#6bb1ff"
    SUCCESS = "#4caf50"
    ERROR = "#f44336"
    WARNING = "#ff9800"
    BORDER = "#3a3a3a"
    ENTRY_BG = "#2a2a2a"
    TREE_BG = "#252525"
    TREE_SELECTED = "#3a5f8a"
    
    @staticmethod
    def apply_theme(root):
        """Apply dark theme to the application"""
        style = ttk.Style(root)
        
        # Configure root window
        root.configure(bg=DarkTheme.BG)
        
        # Configure ttk styles
        style.theme_use('clam')
        
        # General configurations
        style.configure('TFrame', background=DarkTheme.BG)
        style.configure('TLabel', background=DarkTheme.BG, foreground=DarkTheme.FG)
        style.configure('TButton', 
                       background=DarkTheme.BG_SECONDARY,
                       foreground=DarkTheme.FG,
                       bordercolor=DarkTheme.BORDER,
                       darkcolor=DarkTheme.BG,
                       lightcolor=DarkTheme.BG,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', DarkTheme.BG_TERTIARY)],
                 foreground=[('active', DarkTheme.FG)])
        
        # Accent button style
        style.configure('Accent.TButton',
                       background=DarkTheme.ACCENT,
                       foreground='white',
                       bordercolor=DarkTheme.ACCENT)
        style.map('Accent.TButton',
                 background=[('active', DarkTheme.ACCENT_HOVER)])
        
        # Entry style
        style.configure('TEntry',
                       fieldbackground=DarkTheme.ENTRY_BG,
                       background=DarkTheme.ENTRY_BG,
                       foreground=DarkTheme.FG,
                       bordercolor=DarkTheme.BORDER,
                       insertcolor=DarkTheme.FG)
        
        # Notebook style
        style.configure('TNotebook', 
                       background=DarkTheme.BG,
                       bordercolor=DarkTheme.BORDER)
        style.configure('TNotebook.Tab',
                       background=DarkTheme.BG_SECONDARY,
                       foreground=DarkTheme.FG,
                       padding=[20, 8])
        style.map('TNotebook.Tab',
                 background=[('selected', DarkTheme.BG_TERTIARY)],
                 foreground=[('selected', DarkTheme.ACCENT)])
        
        # LabelFrame style
        style.configure('TLabelframe', 
                       background=DarkTheme.BG,
                       foreground=DarkTheme.FG,
                       bordercolor=DarkTheme.BORDER)
        style.configure('TLabelframe.Label',
                       background=DarkTheme.BG,
                       foreground=DarkTheme.ACCENT)
        
        # Checkbutton style
        style.configure('TCheckbutton',
                       background=DarkTheme.BG,
                       foreground=DarkTheme.FG,
                       focuscolor='none')
        style.map('TCheckbutton',
                 background=[('active', DarkTheme.BG)])
        
        # Separator style
        style.configure('TSeparator',
                       background=DarkTheme.BORDER)
        
        # Treeview style
        style.configure('Treeview',
                       background=DarkTheme.TREE_BG,
                       foreground=DarkTheme.FG,
                       fieldbackground=DarkTheme.TREE_BG,
                       bordercolor=DarkTheme.BORDER)
        style.configure('Treeview.Heading',
                       background=DarkTheme.BG_SECONDARY,
                       foreground=DarkTheme.FG,
                       bordercolor=DarkTheme.BORDER)
        style.map('Treeview',
                 background=[('selected', DarkTheme.TREE_SELECTED)],
                 foreground=[('selected', 'white')])
        
        # Scrollbar style
        style.configure('Vertical.TScrollbar',
                       background=DarkTheme.BG_SECONDARY,
                       bordercolor=DarkTheme.BORDER,
                       arrowcolor=DarkTheme.FG,
                       troughcolor=DarkTheme.BG)
        style.configure('Horizontal.TScrollbar',
                       background=DarkTheme.BG_SECONDARY,
                       bordercolor=DarkTheme.BORDER,
                       arrowcolor=DarkTheme.FG,
                       troughcolor=DarkTheme.BG)


class RenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer - Media File Renaming Tool v2.0")
        self.root.geometry("1300x850")
        
        # Apply dark theme
        DarkTheme.apply_theme(self.root)
        
        # Configuration
        self.config_file = Path.home() / ".renamer_config.json"
        self.api_keys = self.load_config()
        
        # Data
        self.files = []
        self.search_results = {}
        self.selected_matches = {}
        self.file_selected = {}  # Track which files are selected for renaming
        
        # Media extensions
        self.media_extensions = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.m4v'}
        self.subtitle_extensions = {'.srt', '.sub', '.idx', '.ass', '.ssa', '.vtt'}
        
        # Setup UI
        self.setup_ui()
        
        # Auto-load default paths if enabled (with better timing)
        if self.api_keys.get('auto_load', False) and self.api_keys.get('default_paths'):
            # Schedule auto-load after UI is fully initialized
            self.root.after(500, self.auto_load_files)
    
    def load_config(self) -> Dict:
        """Load API keys and settings from config file"""
        default_config = {
            'tvdb': '', 
            'tmdb': '', 
            'default_paths': [], 
            'auto_load': False,
            'dark_theme': True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key in default_config:
                        if key not in loaded_config:
                            loaded_config[key] = default_config[key]
                    return loaded_config
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save API keys to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.api_keys, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def auto_load_files(self):
        """Auto-load files from default paths with proper error handling"""
        try:
            default_paths = self.api_keys.get('default_paths', [])
            
            if not default_paths:
                return
            
            # Update status
            self.status_var.set("Auto-loading files from default folders...")
            self.root.update_idletasks()
            
            all_files = []
            valid_paths = []
            invalid_paths = []
            
            for folder in default_paths:
                if os.path.exists(folder) and os.path.isdir(folder):
                    valid_paths.append(folder)
                    # Recursively search for media files
                    for ext in self.media_extensions:
                        found = list(Path(folder).glob(f'**/*{ext}'))
                        all_files.extend(found)
                else:
                    invalid_paths.append(folder)
            
            # Report invalid paths
            if invalid_paths:
                print(f"Warning: Invalid default paths: {invalid_paths}")
            
            if all_files:
                # Clear existing files
                self.clear_files(silent=True)
                
                # Add new files
                self.add_files([str(f) for f in all_files])
                
                # Update status
                status_msg = f"Auto-loaded {len(all_files)} file(s) from {len(valid_paths)} folder(s)"
                if invalid_paths:
                    status_msg += f" ({len(invalid_paths)} invalid path(s) skipped)"
                self.status_var.set(status_msg)
                
                # Switch to Files tab
                self.notebook.select(self.files_frame)
            else:
                self.status_var.set(f"No media files found in default folders")
                
        except Exception as e:
            print(f"Error in auto_load_files: {e}")
            self.status_var.set("Error loading default files")
    
    def setup_ui(self):
        """Setup the user interface with dark theme"""
        # Create main container with padding
        main_container = ttk.Frame(self.root, padding="5")
        main_container.pack(fill='both', expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Files tab
        self.files_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.files_frame, text='📁 Files')
        self.setup_files_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text='⚙️ Settings')
        self.setup_settings_tab()
        
        # Status bar with dark theme
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(status_frame, 
                                  textvariable=self.status_var, 
                                  relief=tk.SUNKEN,
                                  bg=DarkTheme.BG_SECONDARY,
                                  fg=DarkTheme.FG,
                                  pady=5,
                                  padx=10,
                                  anchor='w')
        self.status_bar.pack(fill=tk.X)
    
    def setup_settings_tab(self):
        """Setup the settings tab with dark theme"""
        # Create scrollable container
        canvas = tk.Canvas(self.settings_frame, 
                          bg=DarkTheme.BG,
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.settings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title
        title_label = tk.Label(scrollable_frame, 
                              text="⚙️ API Configuration", 
                              font=('Arial', 18, 'bold'),
                              bg=DarkTheme.BG,
                              fg=DarkTheme.ACCENT)
        title_label.pack(pady=(10, 20))
        
        # TVDB API Key
        tvdb_frame = ttk.LabelFrame(scrollable_frame, text="📺 TVDB API Key", padding=15)
        tvdb_frame.pack(fill='x', padx=20, pady=10)
        
        self.tvdb_entry = ttk.Entry(tvdb_frame, show='*', width=50, font=('Arial', 10))
        self.tvdb_entry.pack(fill='x', pady=5)
        self.tvdb_entry.insert(0, self.api_keys.get('tvdb', ''))
        
        tvdb_link = tk.Label(tvdb_frame, 
                            text="Get your API key from: https://thetvdb.com/api-information",
                            fg=DarkTheme.ACCENT,
                            bg=DarkTheme.BG,
                            cursor="hand2")
        tvdb_link.pack(anchor='w')
        
        # TMDB API Key
        tmdb_frame = ttk.LabelFrame(scrollable_frame, text="🎬 TMDB API Key", padding=15)
        tmdb_frame.pack(fill='x', padx=20, pady=10)
        
        self.tmdb_entry = ttk.Entry(tmdb_frame, show='*', width=50, font=('Arial', 10))
        self.tmdb_entry.pack(fill='x', pady=5)
        self.tmdb_entry.insert(0, self.api_keys.get('tmdb', ''))
        
        tmdb_link = tk.Label(tmdb_frame,
                            text="Get your API key from: https://www.themoviedb.org/settings/api",
                            fg=DarkTheme.ACCENT,
                            bg=DarkTheme.BG,
                            cursor="hand2")
        tmdb_link.pack(anchor='w')
        
        # Default Paths Section
        paths_frame = ttk.LabelFrame(scrollable_frame, text="📂 Default Media Folders", padding=15)
        paths_frame.pack(fill='x', padx=20, pady=10)
        
        info_label = tk.Label(paths_frame,
                             text="Add folders to automatically scan for media files (including all subfolders):",
                             wraplength=500,
                             bg=DarkTheme.BG,
                             fg=DarkTheme.FG_SECONDARY)
        info_label.pack(anchor='w', pady=5)
        
        # Auto-load checkbox
        self.auto_load_var = tk.BooleanVar(value=self.api_keys.get('auto_load', False))
        auto_check = ttk.Checkbutton(paths_frame, 
                                     text="✨ Automatically load files from default folders on startup",
                                     variable=self.auto_load_var)
        auto_check.pack(anchor='w', pady=5)
        
        # Paths list with dark theme
        paths_list_frame = ttk.Frame(paths_frame)
        paths_list_frame.pack(fill='both', expand=True, pady=5)
        
        self.paths_listbox = tk.Listbox(paths_list_frame, 
                                        height=6,
                                        bg=DarkTheme.ENTRY_BG,
                                        fg=DarkTheme.FG,
                                        selectbackground=DarkTheme.TREE_SELECTED,
                                        selectforeground='white',
                                        font=('Arial', 10))
        paths_scrollbar = ttk.Scrollbar(paths_list_frame, orient="vertical", 
                                       command=self.paths_listbox.yview)
        self.paths_listbox.configure(yscrollcommand=paths_scrollbar.set)
        
        self.paths_listbox.pack(side='left', fill='both', expand=True)
        paths_scrollbar.pack(side='right', fill='y')
        
        # Load existing paths
        for path in self.api_keys.get('default_paths', []):
            self.paths_listbox.insert(tk.END, path)
        
        # Buttons for path management
        paths_buttons = ttk.Frame(paths_frame)
        paths_buttons.pack(fill='x', pady=10)
        
        ttk.Button(paths_buttons, text="➕ Add Folder", 
                  command=self.add_default_path).pack(side='left', padx=2)
        ttk.Button(paths_buttons, text="➖ Remove Selected", 
                  command=self.remove_default_path).pack(side='left', padx=2)
        ttk.Button(paths_buttons, text="🔄 Load Now", 
                  command=self.load_default_paths).pack(side='left', padx=2)
        
        # Save button
        save_btn = ttk.Button(scrollable_frame, text="💾 Save All Settings", 
                             command=self.save_api_keys, 
                             style='Accent.TButton')
        save_btn.pack(pady=20)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_files_tab(self):
        """Setup the files tab with dark theme"""
        # Top button frame
        button_frame = ttk.Frame(self.files_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        # File selection buttons
        ttk.Button(button_frame, text="📄 Select Files", 
                  command=self.select_files).pack(side='left', padx=3)
        ttk.Button(button_frame, text="📁 Select Folder", 
                  command=self.select_folder).pack(side='left', padx=3)
        
        # Separator
        ttk.Separator(button_frame, orient='vertical').pack(side='left', padx=10, fill='y')
        
        # Selection management buttons
        ttk.Button(button_frame, text="✅ Select All", 
                  command=self.select_all_files).pack(side='left', padx=3)
        ttk.Button(button_frame, text="❌ Select None", 
                  command=self.select_none_files).pack(side='left', padx=3)
        
        # Separator
        ttk.Separator(button_frame, orient='vertical').pack(side='left', padx=10, fill='y')
        
        # Action buttons
        ttk.Button(button_frame, text="🔍 Search Selected", 
                  command=self.search_selected_files,
                  style='Accent.TButton').pack(side='left', padx=3)
        ttk.Button(button_frame, text="🔎 Search All", 
                  command=self.search_all_files).pack(side='left', padx=3)
        ttk.Button(button_frame, text="✨ Rename Selected", 
                  command=self.rename_files,
                  style='Accent.TButton').pack(side='left', padx=3)
        ttk.Button(button_frame, text="🗑️ Clear All", 
                  command=self.clear_files).pack(side='left', padx=3)
        
        # Files list with scrollbar
        list_frame = ttk.Frame(self.files_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create Treeview with dark theme
        columns = ('Selected', 'Filename', 'Type', 'Parsed Name', 'Status', 'New Name')
        self.files_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', selectmode='browse')
        
        # Configure columns
        self.files_tree.heading('#0', text='')
        self.files_tree.column('#0', width=30)
        self.files_tree.heading('Selected', text='✓')
        self.files_tree.column('Selected', width=40, anchor='center')
        self.files_tree.heading('Filename', text='Original Filename')
        self.files_tree.column('Filename', width=300)
        self.files_tree.heading('Type', text='Type')
        self.files_tree.column('Type', width=60)
        self.files_tree.heading('Parsed Name', text='Parsed Name')
        self.files_tree.column('Parsed Name', width=200)
        self.files_tree.heading('Status', text='Status')
        self.files_tree.column('Status', width=120)
        self.files_tree.heading('New Name', text='New Filename')
        self.files_tree.column('New Name', width=350)
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.files_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.files_tree.xview)
        self.files_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.files_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.files_tree.bind('<Double-Button-1>', self.toggle_file_selection)
        
        # Details frame - Before/After folder structure
        details_frame = ttk.LabelFrame(self.files_frame, text="📋 Folder Structure Preview", padding=10)
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create two columns for before/after
        before_after_frame = ttk.Frame(details_frame)
        before_after_frame.pack(fill='both', expand=True)
        
        # Before column
        before_frame = ttk.Frame(before_after_frame)
        before_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        before_label = tk.Label(before_frame, text="📂 BEFORE", 
                               font=('Arial', 12, 'bold'),
                               bg=DarkTheme.BG,
                               fg='#ff6b6b')
        before_label.pack(pady=(0, 5))
        
        self.before_text = scrolledtext.ScrolledText(before_frame, 
                                                      height=12, 
                                                      wrap=tk.WORD, 
                                                      font=('Courier New', 10),
                                                      bg='#2b2b2b',
                                                      fg='#e0e0e0',
                                                      insertbackground='white')
        self.before_text.pack(fill='both', expand=True)
        
        # Separator
        separator = ttk.Separator(before_after_frame, orient='vertical')
        separator.pack(side='left', fill='y', padx=10)
        
        # After column
        after_frame = ttk.Frame(before_after_frame)
        after_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        after_label = tk.Label(after_frame, text="✨ AFTER", 
                              font=('Arial', 12, 'bold'),
                              bg=DarkTheme.BG,
                              fg='#4caf50')
        after_label.pack(pady=(0, 5))
        
        self.after_text = scrolledtext.ScrolledText(after_frame, 
                                                     height=12,
                                                     wrap=tk.WORD,
                                                     font=('Courier New', 10),
                                                     bg='#1e3a1e',
                                                     fg='#90ee90',
                                                     insertbackground='white')
        self.after_text.pack(fill='both', expand=True)
        
        # Configure text tags for styling
        for text_widget in [self.before_text, self.after_text]:
            text_widget.tag_configure('folder', foreground='#87ceeb', font=('Courier New', 10, 'bold'))
            text_widget.tag_configure('file', foreground='#98fb98')
            text_widget.tag_configure('deleted', foreground='#ff6b6b', overstrike=True)
            text_widget.tag_configure('kept', foreground='#ffd700')
            text_widget.tag_configure('new', foreground='#90ee90', font=('Courier New', 10, 'bold'))
            text_widget.tag_configure('tree', foreground='#888888')
    
    def save_api_keys(self):
        """Save API keys and settings"""
        self.api_keys['tvdb'] = self.tvdb_entry.get().strip()
        self.api_keys['tmdb'] = self.tmdb_entry.get().strip()
        self.api_keys['auto_load'] = self.auto_load_var.get()
        
        # Get paths from listbox
        paths = []
        for i in range(self.paths_listbox.size()):
            paths.append(self.paths_listbox.get(i))
        self.api_keys['default_paths'] = paths
        
        if self.save_config():
            messagebox.showinfo("Success", "✅ All settings saved successfully!")
        else:
            messagebox.showerror("Error", "❌ Failed to save settings!")
    
    def add_default_path(self):
        """Add a folder to default paths"""
        folder = filedialog.askdirectory(title='Select default media folder')
        if folder:
            # Normalize path
            folder = os.path.normpath(folder)
            
            # Check if already exists
            existing_paths = [self.paths_listbox.get(i) for i in range(self.paths_listbox.size())]
            if folder not in existing_paths:
                self.paths_listbox.insert(tk.END, folder)
                self.status_var.set(f"Added: {folder}")
            else:
                messagebox.showinfo("Already Added", "This folder is already in the default paths list.")
    
    def remove_default_path(self):
        """Remove selected path from default paths"""
        selection = self.paths_listbox.curselection()
        if selection:
            path = self.paths_listbox.get(selection[0])
            self.paths_listbox.delete(selection[0])
            self.status_var.set(f"Removed: {path}")
        else:
            messagebox.showwarning("No Selection", "Please select a path to remove.")
    
    def load_default_paths(self, silent=False):
        """Load files from all default paths including subfolders"""
        default_paths = self.api_keys.get('default_paths', [])
        
        if not default_paths:
            if not silent:
                messagebox.showinfo("No Default Paths", 
                                  "No default paths configured. Add them in Settings.")
            return
        
        # Run in thread to prevent UI freezing
        def load_thread():
            self.status_var.set("Loading files from default folders...")
            all_files = []
            valid_paths = []
            invalid_paths = []
            
            for folder in default_paths:
                if os.path.exists(folder) and os.path.isdir(folder):
                    valid_paths.append(folder)
                    # Recursively search for media files
                    for ext in self.media_extensions:
                        found = list(Path(folder).glob(f'**/*{ext}'))
                        all_files.extend(found)
                else:
                    invalid_paths.append(folder)
            
            if all_files:
                # Clear existing files
                self.clear_files(silent=True)
                # Add new files
                self.add_files([str(f) for f in all_files])
                
                status_msg = f"Loaded {len(all_files)} file(s) from {len(valid_paths)} folder(s)"
                if invalid_paths:
                    status_msg += f" ({len(invalid_paths)} invalid)"
                self.status_var.set(status_msg)
                
                # Switch to Files tab
                self.notebook.select(self.files_frame)
            else:
                if not silent:
                    messagebox.showinfo("No Files Found", 
                                      f"No media files found in {len(valid_paths)} folder(s).")
                else:
                    self.status_var.set("No media files found in default folders")
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def select_all_files(self):
        """Select all files for renaming"""
        for file_id in range(len(self.files)):
            self.file_selected[file_id] = True
            # Update tree display
            current_values = list(self.files_tree.item(file_id)['values'])
            current_values[0] = '✓'
            self.files_tree.item(file_id, values=current_values)
        
        selected_count = sum(1 for v in self.file_selected.values() if v)
        self.status_var.set(f"Selected all {selected_count} file(s)")
    
    def select_none_files(self):
        """Deselect all files"""
        for file_id in range(len(self.files)):
            self.file_selected[file_id] = False
            # Update tree display
            current_values = list(self.files_tree.item(file_id)['values'])
            current_values[0] = ''
            self.files_tree.item(file_id, values=current_values)
        
        self.status_var.set("Deselected all files")
    
    def toggle_file_selection(self, event):
        """Toggle selection of a file when double-clicked"""
        region = self.files_tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        
        item = self.files_tree.identify_row(event.y)
        if not item:
            return
        
        try:
            file_id = int(item)
        except:
            return
        
        # Toggle selection
        self.file_selected[file_id] = not self.file_selected.get(file_id, True)
        
        # Update display
        current_values = list(self.files_tree.item(file_id)['values'])
        current_values[0] = '✓' if self.file_selected[file_id] else ''
        self.files_tree.item(file_id, values=current_values)
        
        selected_count = sum(1 for v in self.file_selected.values() if v)
        self.status_var.set(f"{selected_count} file(s) selected for renaming")
    
    def parse_filename(self, filename: str) -> Dict:
        """Parse filename to extract show/movie information"""
        # Remove extension
        name_without_ext = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|m4v)$', '', filename, flags=re.IGNORECASE)
        
        # Try TV show patterns
        tv_patterns = [
            r'^(.+?)[\s._-]+[Ss](\d+)[Ee](\d+)',  # S01E01
            r'^(.+?)[\s._-]+(\d+)[xX](\d+)',       # 1x01
            r'^(.+?)[\s._-]+[Ss]eason[\s._-]*(\d+)[\s._-]+[Ee]pisode[\s._-]*(\d+)',  # Season 1 Episode 1
        ]
        
        for pattern in tv_patterns:
            tv_match = re.match(pattern, name_without_ext)
            if tv_match:
                show_name = tv_match.group(1).replace('.', ' ').replace('_', ' ').strip()
                season = int(tv_match.group(2))
                episode = int(tv_match.group(3))
                return {
                    'type': 'tv',
                    'name': show_name,
                    'season': season,
                    'episode': episode,
                    'original': filename
                }
        
        # Try movie patterns
        movie_patterns = [
            r'^(.+?)[\s._-]+[\(\[]?(\d{4})[\)\]]?',  # Movie.Name.2023 or (2023)
            r'^(.+?)[\s._-]+(\d{4})',                 # Movie Name 2023
        ]
        
        for pattern in movie_patterns:
            movie_match = re.match(pattern, name_without_ext)
            if movie_match:
                movie_name = movie_match.group(1).replace('.', ' ').replace('_', ' ').strip()
                year = int(movie_match.group(2))
                if 1900 <= year <= 2030:  # Reasonable year range
                    return {
                        'type': 'movie',
                        'name': movie_name,
                        'year': year,
                        'original': filename
                    }
        
        # Default to movie without year
        return {
            'type': 'movie',
            'name': name_without_ext.replace('.', ' ').replace('_', ' ').strip(),
            'original': filename
        }
    
    def select_files(self):
        """Select individual files"""
        filetypes = (
            ('Media files', '*.mkv *.mp4 *.avi *.mov *.wmv *.flv *.m4v'),
            ('All files', '*.*')
        )
        filenames = filedialog.askopenfilenames(title='Select media files', filetypes=filetypes)
        
        if filenames:
            self.add_files(filenames)
    
    def select_folder(self):
        """Select a folder and add all media files including subfolders"""
        folder = filedialog.askdirectory(title='Select folder containing media files')
        
        if folder:
            files = []
            # Recursively search for media files
            for ext in self.media_extensions:
                files.extend(Path(folder).glob(f'**/*{ext}'))
            
            if files:
                self.add_files([str(f) for f in files])
                self.status_var.set(f"Added {len(files)} file(s) from {folder}")
            else:
                messagebox.showwarning("No Files", "No media files found in the selected folder.")
    
    def add_files(self, file_paths: List[str]):
        """Add files to the list"""
        added_count = 0
        for file_path in file_paths:
            # Skip if file already added
            if any(f['path'] == file_path for f in self.files):
                continue
                
            file_info = self.parse_filename(os.path.basename(file_path))
            file_info['path'] = file_path
            file_info['id'] = len(self.files)
            self.files.append(file_info)
            
            # Mark file as selected by default
            self.file_selected[file_info['id']] = True
            
            # Add to tree
            parsed_name = file_info['name']
            if file_info['type'] == 'tv':
                parsed_name += f" S{file_info['season']:02d}E{file_info['episode']:02d}"
            elif 'year' in file_info:
                parsed_name += f" ({file_info['year']})"
            
            self.files_tree.insert('', 'end', iid=file_info['id'],
                                   values=('✓',
                                          os.path.basename(file_path), 
                                          file_info['type'].upper(),
                                          parsed_name,
                                          'Not searched',
                                          ''))
            added_count += 1
        
        if added_count > 0:
            self.status_var.set(f"Added {added_count} new file(s). Total: {len(self.files)}")
    
    def clear_files(self, silent=False):
        """Clear all files"""
        self.files = []
        self.search_results = {}
        self.selected_matches = {}
        self.file_selected = {}
        
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        self.before_text.delete(1.0, tk.END)
        self.after_text.delete(1.0, tk.END)
        
        if not silent:
            self.status_var.set("Cleared all files")
    
    def search_tvdb(self, show_name: str, season: int, episode: int) -> List[Dict]:
        """Search TVDB for TV show"""
        if not self.api_keys.get('tvdb'):
            raise Exception('TVDB API key not set')
        
        try:
            # Authenticate
            auth_response = requests.post(
                'https://api4.thetvdb.com/v4/login',
                json={'apikey': self.api_keys['tvdb']},
                timeout=10
            )
            auth_response.raise_for_status()
            token = auth_response.json()['data']['token']
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # Search for series
            search_response = requests.get(
                f'https://api4.thetvdb.com/v4/search',
                params={'query': show_name, 'type': 'series'},
                headers=headers,
                timeout=10
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if not search_data.get('data'):
                return []
            
            results = []
            for show in search_data['data'][:5]:  # Top 5 matches
                result = {
                    'id': show['tvdb_id'],
                    'name': show['name'],
                    'year': show.get('year', ''),
                    'overview': show.get('overview', '')
                }
                
                # Try to get episode details for first match
                if show == search_data['data'][0]:
                    try:
                        episode_response = requests.get(
                            f"https://api4.thetvdb.com/v4/series/{show['tvdb_id']}/episodes/default",
                            params={'season': season, 'episodeNumber': episode},
                            headers=headers,
                            timeout=10
                        )
                        if episode_response.ok:
                            episode_data = episode_response.json()
                            if episode_data.get('data', {}).get('episodes'):
                                result['episodeName'] = episode_data['data']['episodes'][0].get('name', 'Unknown')
                                result['season'] = season
                                result['episode'] = episode
                    except:
                        pass
                
                results.append(result)
            
            return results
            
        except requests.RequestException as e:
            print(f"Network error searching TVDB: {e}")
            return []
        except Exception as e:
            print(f"Error searching TVDB: {e}")
            return []
    
    def search_tmdb(self, movie_name: str, year: Optional[int] = None) -> List[Dict]:
        """Search TMDB for movie"""
        if not self.api_keys.get('tmdb'):
            raise Exception('TMDB API key not set')
        
        try:
            params = {
                'api_key': self.api_keys['tmdb'],
                'query': movie_name
            }
            if year:
                params['year'] = year
            
            response = requests.get('https://api.themoviedb.org/3/search/movie', 
                                   params=params,
                                   timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for movie in data.get('results', [])[:5]:  # Top 5 matches
                results.append({
                    'id': movie['id'],
                    'name': movie['title'],
                    'year': movie.get('release_date', '')[:4] if movie.get('release_date') else 'Unknown',
                    'overview': movie.get('overview', '')
                })
            
            return results
            
        except requests.RequestException as e:
            print(f"Network error searching TMDB: {e}")
            return []
        except Exception as e:
            print(f"Error searching TMDB: {e}")
            return []
    
    def search_file(self, file_info: Dict) -> List[Dict]:
        """Search for a single file"""
        try:
            if file_info['type'] == 'tv':
                return self.search_tvdb(file_info['name'], file_info['season'], file_info['episode'])
            else:
                return self.search_tmdb(file_info['name'], file_info.get('year'))
        except Exception as e:
            print(f"Error searching for {file_info['name']}: {e}")
            return []
    
    def search_selected_files(self):
        """Search only for selected files"""
        if not self.api_keys.get('tvdb') or not self.api_keys.get('tmdb'):
            messagebox.showerror("Error", "Please configure API keys in Settings first!")
            return
        
        if not self.files:
            messagebox.showwarning("No Files", "Please select files first!")
            return
        
        # Get only selected files
        selected_files = [f for f in self.files if self.file_selected.get(f['id'], False)]
        
        if not selected_files:
            messagebox.showwarning("No Files Selected", 
                                 "No files are selected for searching!\n\n"
                                 "Double-click files to select them, or use 'Select All' button.")
            return
        
        # Run search in thread
        def search_thread():
            self.status_var.set("Searching selected files...")
            
            for i, file_info in enumerate(selected_files):
                results = self.search_file(file_info)
                self.search_results[file_info['id']] = results
                
                # Update tree
                status = f"Found {len(results)} matches" if results else "No matches"
                current_values = list(self.files_tree.item(file_info['id'])['values'])
                
                self.files_tree.item(file_info['id'], values=(
                    current_values[0],  # Keep selection
                    current_values[1],
                    current_values[2],
                    current_values[3],
                    status,
                    ''
                ))
                
                # Auto-select first match if available
                if results:
                    self.selected_matches[file_info['id']] = results[0]
                    new_name = self.generate_new_filename(file_info, results[0])
                    current_values[5] = new_name
                    self.files_tree.item(file_info['id'], values=current_values)
                
                self.status_var.set(f"Searching... {i+1}/{len(selected_files)}")
            
            matches_found = len([r for fid, r in self.search_results.items() 
                               if r and fid in [f['id'] for f in selected_files]])
            self.status_var.set(f"Search complete! Found matches for {matches_found}/{len(selected_files)} selected file(s)")
            
            # Update preview if a file is selected
            selection = self.files_tree.selection()
            if selection:
                self.update_folder_preview(int(selection[0]))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def search_all_files(self):
        """Search for all files"""
        if not self.api_keys.get('tvdb') or not self.api_keys.get('tmdb'):
            messagebox.showerror("Error", "Please configure API keys in Settings first!")
            return
        
        if not self.files:
            messagebox.showwarning("No Files", "Please select files first!")
            return
        
        # Run search in thread
        def search_thread():
            self.status_var.set("Searching all files...")
            
            for i, file_info in enumerate(self.files):
                results = self.search_file(file_info)
                self.search_results[file_info['id']] = results
                
                # Update tree
                status = f"Found {len(results)} matches" if results else "No matches"
                current_values = list(self.files_tree.item(file_info['id'])['values'])
                
                self.files_tree.item(file_info['id'], values=(
                    current_values[0],  # Keep selection
                    current_values[1],
                    current_values[2],
                    current_values[3],
                    status,
                    ''
                ))
                
                # Auto-select first match if available
                if results:
                    self.selected_matches[file_info['id']] = results[0]
                    new_name = self.generate_new_filename(file_info, results[0])
                    current_values[5] = new_name
                    self.files_tree.item(file_info['id'], values=current_values)
                
                self.status_var.set(f"Searching... {i+1}/{len(self.files)}")
            
            self.status_var.set(f"Search complete! Found matches for {len(self.selected_matches)}/{len(self.files)} file(s)")
            
            # Update preview if a file is selected
            selection = self.files_tree.selection()
            if selection:
                self.update_folder_preview(int(selection[0]))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def generate_new_filename(self, file_info: Dict, match: Dict) -> str:
        """Generate new filename from match"""
        extension = os.path.splitext(file_info['original'])[1]
        
        if file_info['type'] == 'tv' and 'episodeName' in match:
            season_str = f"{match.get('season', file_info['season']):02d}"
            episode_str = f"{match.get('episode', file_info['episode']):02d}"
            clean_name = re.sub(r'[:<>"/\\|?*]', '', match['name'])
            clean_episode = re.sub(r'[:<>"/\\|?*]', '', match.get('episodeName', ''))
            return f"{clean_name} - S{season_str}E{episode_str} - {clean_episode}{extension}"
        else:
            clean_name = re.sub(r'[:<>"/\\|?*]', '', match['name'])
            return f"{clean_name} ({match['year']}){extension}"
    
    def build_folder_structure(self, file_path: str, new_filename: str = None, is_after: bool = False) -> str:
        """Build a visual representation of the folder structure"""
        parent_dir = os.path.dirname(file_path)
        folder_name = os.path.basename(parent_dir)
        file_basename = os.path.basename(file_path)
        
        structure = []
        
        # Determine folder name for display
        if is_after and new_filename:
            should_rename, new_folder_name = self.should_rename_parent_folder(file_path, new_filename)
            if should_rename:
                folder_name = new_folder_name
            display_filename = new_filename
        else:
            display_filename = file_basename
        
        # Add folder header
        structure.append(f"📁 {folder_name}/")
        
        # Get all items in the directory
        try:
            items = sorted(os.listdir(parent_dir))
            
            protected_subfolders = {'subtitles', 'subs', 'subtitle', 'sub'}
            
            for i, item in enumerate(items):
                item_path = os.path.join(parent_dir, item)
                is_last = (i == len(items) - 1)
                prefix = "└── " if is_last else "├── "
                
                if os.path.isdir(item_path):
                    # Check if it's a subtitle folder
                    if item.lower() in protected_subfolders:
                        structure.append(f"  {prefix}📂 {item}/ ✅")
                        # Show subtitle files inside
                        try:
                            sub_items = sorted(os.listdir(item_path))
                            for j, sub_item in enumerate(sub_items):
                                sub_is_last = (j == len(sub_items) - 1)
                                sub_prefix = "    └── " if sub_is_last else "    ├── "
                                if is_last:
                                    sub_prefix = "    " + sub_prefix
                                structure.append(f"{sub_prefix}📄 {sub_item}")
                        except:
                            pass
                    else:
                        # This folder will be deleted in AFTER view
                        if is_after:
                            continue  # Don't show deleted folders
                        else:
                            structure.append(f"  {prefix}📂 {item}/ ❌")
                else:
                    # It's a file
                    _, ext = os.path.splitext(item)
                    
                    # Current media file
                    if item == file_basename:
                        if is_after:
                            structure.append(f"  {prefix}🎬 {display_filename} ✨")
                        else:
                            structure.append(f"  {prefix}🎬 {item}")
                    # Subtitle files - kept
                    elif ext.lower() in self.subtitle_extensions:
                        if is_after and new_filename:
                            # Rename .srt to match the new filename
                            base_without_ext = os.path.splitext(new_filename)[0]
                            structure.append(f"  {prefix}📝 {base_without_ext}{ext} ✅")
                        else:
                            structure.append(f"  {prefix}📝 {item} ✅")
                    # Media files - kept
                    elif ext.lower() in self.media_extensions:
                        if item != file_basename:  # Other media files
                            if is_after:
                                continue  # Deleted in cleanup
                            else:
                                structure.append(f"  {prefix}🎬 {item} ❌")
                    # Other files - deleted
                    else:
                        if is_after:
                            continue  # Don't show deleted files
                        else:
                            structure.append(f"  {prefix}📄 {item} ❌")
        
        except Exception as e:
            structure.append(f"  ⚠️ Error reading directory: {e}")
        
        return "\n".join(structure)
    
    def update_folder_preview(self, file_id: int):
        """Update the before/after folder structure preview"""
        if file_id >= len(self.files):
            return
            
        file_info = self.files[file_id]
        
        # Clear both text widgets
        self.before_text.delete(1.0, tk.END)
        self.after_text.delete(1.0, tk.END)
        
        # Check if we have a match selected
        match = self.selected_matches.get(file_id)
        
        if not match:
            # No match yet
            self.before_text.insert(tk.END, "📋 No match selected yet.\n\n")
            self.before_text.insert(tk.END, "Click '🔍 Search Selected' or '🔎 Search All' to find matches.")
            self.after_text.insert(tk.END, "✨ Preview will appear here after searching.")
            return
        
        # Generate new filename
        new_filename = self.generate_new_filename(file_info, match)
        
        # Build BEFORE structure
        before_structure = self.build_folder_structure(file_info['path'], new_filename, is_after=False)
        
        # Build AFTER structure
        after_structure = self.build_folder_structure(file_info['path'], new_filename, is_after=True)
        
        # Display structures
        self.before_text.insert(tk.END, before_structure)
        self.after_text.insert(tk.END, after_structure)
        
        # Add legend
        self.before_text.insert(tk.END, "\n\n❌ = Will be deleted\n✅ = Will be kept")
        self.after_text.insert(tk.END, "\n\n✨ = Renamed\n✅ = Kept as-is")
    
    def on_file_select(self, event):
        """Handle file selection in tree"""
        selection = self.files_tree.selection()
        if not selection:
            return
        
        try:
            file_id = int(selection[0])
            self.update_folder_preview(file_id)
        except:
            pass
    
    def clean_name_for_comparison(self, name: str) -> str:
        """Clean a name for similarity comparison"""
        # Remove year, special chars, make lowercase
        cleaned = re.sub(r'\d{4}', '', name)  # Remove year
        cleaned = re.sub(r'[^a-z0-9\s]', '', cleaned.lower())  # Remove special chars
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize spaces
        return cleaned
    
    def is_similar_name(self, name1: str, name2: str, threshold: float = 0.7) -> bool:
        """Check if two names are similar enough"""
        clean1 = self.clean_name_for_comparison(name1)
        clean2 = self.clean_name_for_comparison(name2)
        
        # Simple similarity check - what percentage of words match
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        
        if not words1 or not words2:
            return False
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold
    
    def should_rename_parent_folder(self, file_path: str, new_filename: str) -> Tuple[bool, str]:
        """Determine if the parent folder should be renamed"""
        parent_dir = os.path.dirname(file_path)
        parent_name = os.path.basename(parent_dir)
        
        # Get the new name without extension for folder naming
        new_name_without_ext = os.path.splitext(new_filename)[0]
        
        # Release info keywords
        release_keywords = ['720p', '1080p', '480p', '2160p', '4k', 'brrip', 'webrip', 
                           'hdtv', 'bluray', 'dvdrip', 'yify', 'x264', 'x265', 'hevc',
                           'web-dl', 'webdl', 'hdrip', 'hdcam', 'cam', 'ts', 'tc']
        
        folder_lower = parent_name.lower()
        has_release_info = any(keyword in folder_lower for keyword in release_keywords)
        
        # Also check if names are similar
        is_similar = self.is_similar_name(parent_name, new_name_without_ext)
        
        should_rename = has_release_info or is_similar
        
        return should_rename, new_name_without_ext
    
    def cleanup_folder(self, folder_path: str, keep_file: str, preserve_media: bool = False):
        """Delete non-media files and non-subtitle folders

        Args:
            folder_path: Path to folder to clean
            keep_file: Path to the main file being renamed
            preserve_media: If True, keeps all media files (for multi-file folders)
        """
        keep_extensions = self.media_extensions.union(self.subtitle_extensions)

        # Protected subfolder names (case-insensitive)
        protected_subfolders = {'subtitles', 'subs', 'subtitle', 'sub'}

        deleted_files = 0
        deleted_dirs = 0

        try:
            items_to_check = list(os.listdir(folder_path))

            for item in items_to_check:
                item_path = os.path.join(folder_path, item)

                # Skip the file we're keeping
                if item_path == keep_file:
                    continue

                # If it's a directory
                if os.path.isdir(item_path):
                    # Check if it's a protected subtitle folder
                    if item.lower() in protected_subfolders:
                        continue

                    # Delete non-protected directories
                    try:
                        shutil.rmtree(item_path)
                        deleted_dirs += 1
                    except Exception as e:
                        print(f"Failed to delete directory {item}: {e}")

                # If it's a file
                elif os.path.isfile(item_path):
                    _, ext = os.path.splitext(item)

                    # If preserve_media is True, keep all media files
                    if preserve_media and ext.lower() in self.media_extensions:
                        continue

                    # Delete if it's not a media or subtitle file
                    if ext.lower() not in keep_extensions:
                        try:
                            os.remove(item_path)
                            deleted_files += 1
                        except Exception as e:
                            print(f"Failed to delete file {item}: {e}")

        except Exception as e:
            print(f"Error cleaning folder {folder_path}: {e}")

        return deleted_files, deleted_dirs
    
    def rename_files(self):
        """Rename selected files with smart folder renaming and cleanup"""
        # Get only selected files that have matches
        files_to_rename = {fid: match for fid, match in self.selected_matches.items()
                          if self.file_selected.get(fid, False)}

        if not files_to_rename:
            messagebox.showwarning("No Files Selected",
                                 "No files are selected for renaming!\n\n"
                                 "✓ = Selected for renaming\n"
                                 "Double-click files to select/deselect")
            return

        # Detect multi-file folders (2+ files being renamed in same folder)
        folder_file_counts = {}
        for file_id in files_to_rename.keys():
            file_info = self.files[file_id]
            folder = os.path.dirname(file_info['path'])
            folder_file_counts[folder] = folder_file_counts.get(folder, 0) + 1

        multi_file_folders = {folder for folder, count in folder_file_counts.items() if count > 1}

        # Confirm
        confirm_message = f"Are you sure you want to rename {len(files_to_rename)} selected file(s)?\n\n"
        confirm_message += "This will:\n"
        confirm_message += "✅ Rename the files\n"

        if multi_file_folders:
            confirm_message += f"📂 Preserve {len(multi_file_folders)} folder(s) with multiple files\n"
            confirm_message += "🗑️ Delete junk files (txt, nfo, etc.)\n"
        else:
            confirm_message += "✅ Rename parent folders to match content\n"
            confirm_message += "🗑️ Delete non-media files (except subtitles)\n"
            confirm_message += "🗑️ Delete subdirectories (except Subtitles/Subs)\n"

        confirm_message += "\n⚠️ This action cannot be undone!"

        response = messagebox.askyesno("🚀 Confirm Rename", confirm_message)

        if not response:
            return

        success_count = 0
        error_count = 0
        folders_renamed = 0
        folders_preserved = set()
        total_files_cleaned = 0
        total_dirs_cleaned = 0
        errors = []

        for file_id, match in files_to_rename.items():
            try:
                file_info = self.files[file_id]
                old_path = file_info['path']
                old_dir = os.path.dirname(old_path)

                # Check if this is a multi-file folder
                is_multi_file_folder = old_dir in multi_file_folders

                new_filename = self.generate_new_filename(file_info, match)

                # Step 1: Cleanup folder (preserve media files if multi-file folder)
                deleted_files, deleted_dirs = self.cleanup_folder(old_dir, old_path, preserve_media=is_multi_file_folder)
                total_files_cleaned += deleted_files
                total_dirs_cleaned += deleted_dirs

                # Step 2: Rename the file
                temp_new_path = os.path.join(old_dir, new_filename)
                if old_path != temp_new_path:
                    os.rename(old_path, temp_new_path)

                final_path = temp_new_path

                # Step 3: Check if we should rename the parent folder (skip for multi-file folders)
                if not is_multi_file_folder:
                    should_rename, new_folder_name = self.should_rename_parent_folder(temp_new_path, new_filename)

                    if should_rename:
                        parent_of_old_dir = os.path.dirname(old_dir)
                        new_dir = os.path.join(parent_of_old_dir, new_folder_name)

                        if old_dir != new_dir:
                            if not os.path.exists(new_dir):
                                os.rename(old_dir, new_dir)
                                folders_renamed += 1
                                final_path = os.path.join(new_dir, new_filename)
                else:
                    folders_preserved.add(old_dir)

                # Update file info
                file_info['path'] = final_path
                file_info['original'] = new_filename

                # Update tree
                current_values = list(self.files_tree.item(file_id)['values'])
                self.files_tree.item(file_id, values=(
                    current_values[0],
                    new_filename,
                    file_info['type'].upper(),
                    current_values[3],
                    '✅ Renamed',
                    ''
                ))

                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"{file_info.get('original', 'unknown')}: {str(e)}")
                print(f"Error renaming: {e}")

        # Show results
        message = f"✅ Successfully renamed {success_count} file(s)"
        if folders_renamed > 0:
            message += f"\n📁 Renamed {folders_renamed} folder(s)"
        if len(folders_preserved) > 0:
            message += f"\n📂 Preserved {len(folders_preserved)} multi-file folder(s)"
        if total_files_cleaned > 0:
            message += f"\n🗑️ Deleted {total_files_cleaned} junk file(s)"
        if total_dirs_cleaned > 0:
            message += f"\n🗑️ Deleted {total_dirs_cleaned} directory(ies)"
        if error_count > 0:
            message += f"\n\n❌ Errors: {error_count}"
            if errors:
                message += f"\n{chr(10).join(errors[:3])}"  # Show first 3 errors

        messagebox.showinfo("✨ Rename Complete", message)

        self.status_var.set(f"✅ Renamed {success_count} file(s), {folders_renamed} folder(s)")


def main():
    root = tk.Tk()
    
    # Set window icon if possible
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    app = RenamerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
