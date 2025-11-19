# Renamer App - Product Roadmap

## Vision
Transform Renamer from a powerful file renaming tool into the definitive media library management solution with intelligent automation, comprehensive safety features, and seamless integration with popular media platforms.

---

## Phase 1: Safety & Confidence (Q1 2026)
**Theme**: Build user trust with reversibility and validation

### 1.1 Undo/Rollback System
- **Priority**: CRITICAL
- **Description**: Full operation history with one-click rollback
- **Features**:
  - Session-based undo stack (all operations since app launch)
  - Persistent rename history with timestamps
  - Multi-step rollback UI with preview
  - "Revert All" for entire batch operations
- **Value**: Eliminates fear of irreversible mistakes, encourages experimentation

### 1.2 Dry-Run Mode
- **Priority**: HIGH
- **Description**: Preview all changes without executing
- **Features**:
  - "Preview Only" mode that shows exact file operations
  - Detailed change report (files renamed, deleted, moved)
  - Export preview as text/CSV for review
  - Color-coded risk indicators (safe/warning/destructive)
- **Value**: Users can verify complex operations before committing

### 1.3 Smart Validation & Warnings
- **Priority**: MEDIUM
- **Description**: Intelligent pre-flight checks
- **Features**:
  - Detect potential filename conflicts
  - Warn about unusual patterns (very short names, missing metadata)
  - Flag files that couldn't be matched with high confidence
  - Suggest manual review for low-confidence matches (<80%)
- **Value**: Prevents common mistakes and improves rename accuracy

### 1.4 Enhanced Progress Tracking
- **Priority**: MEDIUM
- **Description**: Real-time operation visibility
- **Features**:
  - Progress bar with estimated time remaining
  - Current operation display (e.g., "Renaming 5/47 files...")
  - Pause/Resume capability for long operations
  - Error summary with actionable retry options
- **Value**: Better UX for large batch operations

---

## Phase 2: Customization & Flexibility (Q2 2026)
**Theme**: Adapt to diverse user workflows and preferences

### 2.1 Custom Naming Templates
- **Priority**: HIGH
- **Description**: User-defined rename patterns
- **Features**:
  - Template builder with variables: `{show} - S{season}E{episode} - {title}`
  - Separate templates for TV shows, movies, anime
  - Preview templates with sample data
  - Template library (import/export community templates)
  - Variables: show, season, episode, title, year, resolution, codec, audio, release_group
- **Value**: Supports different naming conventions (Plex, Kodi, Jellyfin standards)

### 2.2 Advanced Regex Pattern Editor
- **Priority**: MEDIUM
- **Description**: Customize filename parsing
- **Features**:
  - Visual regex builder for non-technical users
  - Test regex against sample filenames with live preview
  - Pattern library for anime, sports, documentaries
  - Priority ordering for patterns
  - Import/export pattern collections
- **Value**: Handles non-standard naming conventions and international content

### 2.3 Selective Cleanup Rules
- **Priority**: MEDIUM
- **Description**: Fine-grained control over cleanup behavior
- **Features**:
  - User-defined whitelist/blacklist for file extensions
  - Folder preservation rules (keep sample folders, extras)
  - Size-based rules (delete files < 10MB, keep files > 1GB)
  - Custom cleanup profiles (aggressive, conservative, custom)
- **Value**: Preserves valuable content like bonus features, extras

### 2.4 Multi-Language Support
- **Priority**: LOW
- **Description**: International content handling
- **Features**:
  - Language detection from filenames/metadata
  - Language tags in renamed files `{show} - S01E01 [EN]`
  - Multi-audio track detection
  - Preferred language settings for API searches
- **Value**: Better support for international users and multi-language libraries

---

## Phase 3: Automation & Intelligence (Q3 2026)
**Theme**: Reduce manual work with smart automation

### 3.1 Watch Folder Automation
- **Priority**: HIGH
- **Description**: Automatic processing of new files
- **Features**:
  - Monitor folders for new media files
  - Auto-search and rename on detection
  - Configurable auto-rename threshold (only if >90% confidence)
  - Move processed files to organized destination
  - Email/notification on completion or errors
- **Value**: Set-it-and-forget-it workflow for download automation

### 3.2 Intelligent Auto-Organization
- **Priority**: HIGH
- **Description**: Automatically organize files into folder structure
- **Features**:
  - Auto-create folder structure: `TV Shows/{Show Name}/Season {N}/`
  - Movie organization: `Movies/{Movie Name} ({Year})/`
  - Genre-based organization (action, comedy, etc.)
  - Custom folder structure templates
  - "Organize Library" bulk operation
- **Value**: Maintains clean, navigable media library structure

### 3.3 Duplicate Detection & Management
- **Priority**: MEDIUM
- **Description**: Find and handle duplicate content
- **Features**:
  - Hash-based duplicate detection (exact duplicates)
  - Metadata-based matching (same show/episode, different quality)
  - Comparison view (file size, resolution, codec)
  - Smart keep/delete suggestions (keep highest quality)
  - Archive duplicates instead of deleting
- **Value**: Saves storage space and eliminates library clutter

### 3.4 Batch Processing Profiles
- **Priority**: MEDIUM
- **Description**: Save and reuse operation configurations
- **Features**:
  - Named profiles (e.g., "TV Downloads", "4K Movies", "Anime")
  - Profile includes: naming template, cleanup rules, organization settings
  - Quick-apply profiles to folder selection
  - Profile sharing/import
- **Value**: Streamlines repetitive workflows

### 3.5 Season Pack Smart Handling
- **Priority**: LOW
- **Description**: Specialized handling for season packs
- **Features**:
  - Detect season pack folders (multiple episodes)
  - Bulk episode matching with single API call
  - Sequential episode numbering validation
  - Detect missing episodes in pack
  - Auto-organization into season folder
- **Value**: Efficient handling of common download scenario

---

## Phase 4: Metadata & Integration (Q4 2026)
**Theme**: Rich metadata and ecosystem connectivity

### 4.1 Enhanced Metadata Viewer/Editor
- **Priority**: MEDIUM
- **Description**: View and manually edit metadata
- **Features**:
  - Rich metadata display (poster, plot, cast, ratings)
  - Manual override for incorrect API matches
  - Fetch metadata from multiple sources (TVDB, TMDB, IMDB, OMDb)
  - Save metadata to NFO files (Kodi/Plex compatible)
  - Embedded metadata writing to MKV files
- **Value**: Ensures accurate metadata for media server integration

### 4.2 Media Server Integration
- **Priority**: HIGH
- **Description**: Direct integration with popular media servers
- **Features**:
  - Trigger Plex/Jellyfin/Emby library scan after renaming
  - Read existing library structure to match conventions
  - Validate renamed files against server requirements
  - API integration for metadata sync
- **Value**: Seamless workflow from download to media server

### 4.3 Additional API Provider Support
- **Priority**: MEDIUM
- **Description**: More metadata sources
- **Features**:
  - IMDb integration (official API or scraping)
  - OMDb API support
  - AniDB for anime content
  - TVmaze for TV shows
  - Trakt.tv integration
  - Provider priority/fallback configuration
- **Value**: Better coverage for niche content and international media

### 4.4 NFO File Generation
- **Priority**: LOW
- **Description**: Create Kodi/Plex compatible NFO files
- **Features**:
  - Auto-generate tvshow.nfo, movie.nfo, episodedetails.nfo
  - Include full metadata (plot, actors, ratings, artwork URLs)
  - Optional poster/fanart download
  - NFO template customization
- **Value**: Enhanced media server library richness

### 4.5 Cloud Storage Support
- **Priority**: LOW
- **Description**: Work with cloud-based media libraries
- **Features**:
  - Support for network shares (SMB/NFS)
  - Cloud provider integration (Google Drive, Dropbox, OneDrive)
  - Bandwidth-aware operations
  - Sync conflict detection
- **Value**: Enables remote library management

---

## Phase 5: Enterprise & Power Features (2027)
**Theme**: Advanced capabilities for power users

### 5.1 Command-Line Interface (CLI)
- **Priority**: MEDIUM
- **Description**: Scriptable headless operation
- **Features**:
  - Full CLI with same functionality as GUI
  - Batch processing from command line
  - JSON/CSV input for bulk operations
  - Exit codes and structured output for scripting
  - Docker container support
- **Value**: Automation and integration with existing workflows

### 5.2 Comprehensive Operation Logging
- **Priority**: MEDIUM
- **Description**: Detailed audit trail
- **Features**:
  - Persistent operation log with timestamps
  - Log levels (info, warning, error)
  - Export logs to file
  - Log viewer with filtering/search
  - Statistics dashboard (files renamed per day/week/month)
- **Value**: Troubleshooting and accountability

### 5.3 Plugin/Extension System
- **Priority**: LOW
- **Description**: Community extensibility
- **Features**:
  - Python-based plugin API
  - Custom API provider plugins
  - Custom naming template functions
  - Pre/post-processing hooks
  - Plugin marketplace/repository
- **Value**: Community-driven feature expansion

### 5.4 Multi-User Configuration
- **Priority**: LOW
- **Description**: Shared and user-specific settings
- **Features**:
  - Global configuration (shared API keys)
  - User profiles with individual preferences
  - Configuration sync across devices
  - Team/organization settings management
- **Value**: Family or team usage scenarios

### 5.5 Advanced Filtering & Search
- **Priority**: LOW
- **Description**: Powerful file management
- **Features**:
  - Filter files by type, year, resolution, codec
  - Search within loaded files
  - Smart collections (all files from 2020, all 1080p, etc.)
  - Save filter presets
  - Bulk operations on filtered results
- **Value**: Efficient management of large libraries

---

## Phase 6: Polish & Delight (Ongoing)
**Theme**: Refinement and user experience excellence

### 6.1 UI/UX Enhancements
- **Priority**: MEDIUM
- **Features**:
  - Light theme option (maintain dark as default)
  - Keyboard shortcuts for all operations
  - Drag-and-drop file/folder loading
  - Thumbnail previews for video files
  - Responsive design for different screen sizes
  - Tooltips and contextual help
  - Accessibility improvements (screen reader support)

### 6.2 Performance Optimization
- **Priority**: MEDIUM
- **Features**:
  - Parallel API requests for multiple files
  - Caching of API responses (session and persistent)
  - Lazy loading for large file lists
  - Optimized file operations (async I/O)
  - Memory usage optimization for 1000+ files

### 6.3 Error Handling & Recovery
- **Priority**: MEDIUM
- **Features**:
  - Graceful handling of API failures with retry
  - Partial operation recovery (continue after error)
  - Detailed error messages with suggested fixes
  - Automatic crash reporting (opt-in)
  - Safe mode for corrupted configurations

### 6.4 Documentation & Onboarding
- **Priority**: LOW
- **Features**:
  - Interactive tutorial on first launch
  - Video tutorials for common workflows
  - Comprehensive user guide
  - FAQ and troubleshooting section
  - Tooltips for every UI element
  - Sample file sets for testing

---

## Success Metrics

### User Engagement
- Daily active users growth
- Average files renamed per session
- Feature adoption rate
- User retention (30/60/90 day)

### Quality Metrics
- Rename accuracy rate (successful matches)
- Error rate (failed operations)
- Undo operation frequency (indicates mistakes)
- Average user session duration

### Performance Metrics
- API response time (< 2 seconds target)
- UI responsiveness (no freezing)
- Large batch operation time (1000 files)
- Memory footprint (< 200MB for typical usage)

### User Satisfaction
- Net Promoter Score (NPS)
- Support ticket volume
- User-reported bugs per release
- GitHub stars and community engagement

---

## Technical Debt & Maintenance

### Code Quality Improvements
- Refactor monolithic `renamer.py` into modular architecture
- Add comprehensive unit tests (target 80% coverage)
- Integration tests for API interactions
- Type hints throughout codebase
- Logging framework implementation

### Architecture Evolution
- Separate UI from business logic (MVC pattern)
- Database for operation history and cache (SQLite)
- Configuration management refactoring
- Plugin architecture foundation
- API abstraction layer

### Dependencies
- Regular dependency updates
- Security vulnerability scanning
- Minimize dependency footprint
- Pin versions for stability

---

## Community & Ecosystem

### Open Source Growth
- Contributor guidelines and code of conduct
- Issue templates and PR templates
- Regular release cadence (monthly minor, quarterly major)
- Changelog maintenance
- Roadmap transparency

### Community Features
- User forum or Discord server
- Template and pattern sharing platform
- User showcase (before/after library organization)
- Feature voting system
- Beta program for early access

### Documentation
- Developer documentation (API, architecture)
- Plugin development guide
- Contribution guide
- Translation guide for internationalization

---

## Release Strategy

### Version Numbering
- **Major (X.0.0)**: Breaking changes, major feature sets
- **Minor (2.X.0)**: New features, non-breaking changes
- **Patch (2.0.X)**: Bug fixes, minor improvements

### Proposed Timeline
- **v2.1** (Q1 2026): Phase 1 - Safety features (undo, dry-run)
- **v2.2** (Q2 2026): Phase 2 - Customization (templates, patterns)
- **v2.3** (Q3 2026): Phase 3 - Automation (watch folders, organization)
- **v2.4** (Q4 2026): Phase 4 - Integration (metadata, media servers)
- **v3.0** (2027): Phase 5 - Enterprise features (CLI, plugins)

### Release Channels
- **Stable**: Tested releases for general users
- **Beta**: Feature-complete but less tested
- **Nightly**: Latest development builds

---

## Competitive Analysis

### Current Landscape
- **FileBot**: Feature-rich but paid, complex UI
- **tinyMediaManager**: Java-based, heavy, comprehensive
- **MediaElch**: Good metadata editor, limited renaming
- **Radarr/Sonarr**: Automation-focused, not standalone renaming tools

### Renamer's Unique Value Propositions
1. **Simplicity**: Single-window UI, intuitive workflow
2. **Intelligence**: Smart folder detection, cleanup automation
3. **Free & Open Source**: No subscriptions, community-driven
4. **Lightweight**: Python/Tkinter, fast startup, low resources
5. **Safety**: Multi-file folder preservation, subtitle handling

### Strategic Positioning
- **Target Audience**: Home media enthusiasts, cord-cutters, Plex/Jellyfin users
- **Use Case**: Post-download organization and cleanup
- **Differentiator**: Balance of power and simplicity
- **Pricing**: Free forever, optional donation/sponsor model

---

## Risk Assessment

### Technical Risks
- **API Changes**: TVDB/TMDB API deprecation or changes
  - *Mitigation*: Multiple provider support, versioned API adapters
- **Platform Fragmentation**: Linux/macOS compatibility issues
  - *Mitigation*: Automated cross-platform testing, community testing
- **Performance Scaling**: Large libraries (10,000+ files)
  - *Mitigation*: Early performance testing, optimization sprints

### User Adoption Risks
- **Complexity Creep**: Too many features overwhelm users
  - *Mitigation*: Progressive disclosure, sensible defaults, power user mode
- **Breaking Changes**: Updates break existing workflows
  - *Mitigation*: Deprecation warnings, migration guides, configuration versioning

### Competitive Risks
- **Market Saturation**: Established tools with loyal users
  - *Mitigation*: Focus on unique value props, superior UX, community building
- **Resource Constraints**: Solo developer bandwidth
  - *Mitigation*: Open source contributions, prioritization, phased roadmap

---

## Conclusion

This roadmap transforms Renamer from a solid v2.0 foundation into a best-in-class media management solution. The phased approach ensures steady value delivery while maintaining code quality and user trust.

**Key Principles**:
1. **User trust first**: Safety features (Phase 1) before advanced automation
2. **Flexibility**: Customization (Phase 2) enables diverse use cases
3. **Automation**: Reduce manual work (Phase 3) for power users
4. **Integration**: Play well with ecosystem (Phase 4)
5. **Sustainability**: Enterprise features and architecture (Phase 5) ensure longevity

The roadmap is intentionally ambitious yet achievable with community contributions and focused execution. Prioritization will adapt based on user feedback and adoption metrics.

**Next Steps**:
1. Validate Phase 1 priorities with user survey
2. Set up project management (GitHub Projects/Issues)
3. Create detailed specification for v2.1 features
4. Recruit contributors for high-priority features
5. Establish regular release cadence

Let's build the future of media library management together.
