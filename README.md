# 🌳 TouchFS - LLM-powered Memory Filesystem

TouchFS represents a novel approach to integrating large language model capabilities directly into the filesystem layer. By leveraging the inherently hierarchical nature of filesystems, TouchFS provides an intuitive and powerful way to organize and generate content using LLMs.

The project's core ambition is to seamlessly blend AI capabilities with the familiar tree-like structure of filesystems, enabling new ways of organizing and interacting with files that go beyond traditional static storage. Through a sophisticated system of hierarchical inheritance and granular controls, TouchFS allows for context-aware content generation that respects and utilizes the natural relationships between files and directories.

## ✨ Key Features

- **Hierarchical Intelligence**: Leverages the filesystem's tree structure to provide context-aware content generation, where parent directories influence the behavior of their children
- **Granular Control**: Fine-grained control over LLM behavior at any level of the filesystem through hierarchical configuration inheritance
- **Dynamic Content**: Intelligent content generation for tagged files, with support for both initial structure creation and on-demand updates via touch commands
- **Flexible Architecture**: 
  - In-memory filesystem with JSON serialization
  - Extended attribute (xattr) support for metadata
  - Symlink support for flexible organization
  - Plugin system for custom content generation strategies
- **Context Awareness**: Each file operation considers its position in the filesystem hierarchy, enabling sophisticated inheritance of prompts, models, and generation behavior

## 🔄 Content Generation

TouchFS uses a safe and predictable content generation strategy:

1. **Generation Trigger**: Content is only generated when:
   - A file is marked with the `generate_content` extended attribute (xattr)
   - AND the file is empty (0 bytes)
   - This happens during size calculation (stat) operations

2. **Safety First**: This approach ensures:
   - No accidental overwrites of existing content
   - Predictable generation behavior
   - Clear separation between marked and unmarked files

3. **File Marking Methods**:
   - Initial filesystem generation: All created files are automatically marked
   - New files: Must be explicitly marked using the touch command
   - Manual marking: Can use setfattr to mark existing files

## 🚀 Getting Started

### Installation

```bash
pip install touchfs
```

### Quick Start

Let's create a Python project structure using TouchFS:

```bash
# Mount a new filesystem
touchfs_mount ~/python_project --prompt "Create a modern Python project with tests and CI"

# Explore the generated structure
cd ~/python_project
ls -la

# You'll see a complete project structure:
src/
tests/
.github/workflows/
requirements.txt
setup.py
README.md
```

All files in the initial structure are tagged for generation, and new files can be tagged using touch:

```bash
# Initial structure files are pre-tagged
cat src/main.py        # Generates and shows content
cat tests/test_main.py # Generates and shows content

# New files need touch to tag them
touch src/utils.py     # Creates and tags new file
cat src/utils.py      # Generates and shows content
```

### Customizing Your Environment

When you mount a TouchFS filesystem, you'll find a `.touchfs` directory that helps you control and monitor the system. For a complete guide to all customization options, see our [Plugins Guide](touchfs/content/plugins/README.md).

Here are some common operations:

```bash
# View the current filesystem structure
cat .touchfs/tree

# Read the auto-generated documentation
cat .touchfs/README

# Monitor system logs
tail -f .touchfs/log

# Change the AI model (must support structured output)
echo "gpt-4o-2024-08-06" > .touchfs/model.default

# Customize generation prompts
echo "Focus on security best practices" > .touchfs/prompt.default
```

### Improving Performance

TouchFS includes a caching system to speed up repeated operations:

```bash
# Enable caching
echo 1 > .touchfs/cache_enabled

# Monitor cache performance
watch -n1 cat .touchfs/cache_stats

# Clear cache if needed
echo 1 > .touchfs/cache_clear
```

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `TOUCHFS_PROMPT`: Default generation prompt
- `TOUCHFS_CACHE_FOLDER`: Custom cache location (default: ~/.touchfs.cache)

### Fun Examples: Creating Different Project Types

```bash
# Create a Windows 95 structure
touchfs_mount win95_fs --prompt "Create an authentic Windows 95 filesystem structure with Program Files, Windows folder, and system files"

# Generated structure:
C:\
├── WINDOWS\
│   ├── SYSTEM\
│   └── COMMAND\
├── PROGRA~1\
└── AUTOEXEC.BAT

# Create a classic Unix system
touchfs_mount unix_fs --prompt "Generate a classic Unix filesystem with standard directories and period-accurate system files"

# Generated structure:
/
├── bin/
├── etc/
├── usr/
│   └── local/
└── var/
```

## 🔌 Plugin System

TouchFS includes several built-in plugins:

1. **DefaultGenerator**
   - Primary content generator using OpenAI
   - Context-aware content generation
   - Uses hierarchical prompt system

2. **ModelPlugin**
   - Controls model selection via model.default
   - Supports JSON or raw model name
   - Default: gpt-4o-2024-08-06

3. **PromptPlugin & ModelPlugin**
   - Both plugins use the same hierarchical lookup pattern:
     1. `.touchfs/<name>` in current directory (e.g., prompt or model)
     2. `.touchfs/<name>.default` in current directory
     3. Repeat steps 1-2 in each parent directory
     4. Root `.touchfs/<name>.default` proc file
   - First non-empty file found in this chain is used
   - Allows for increasingly specific settings deeper in the directory tree
   - Supports both raw text and JSON input formats
   - Example:
     ```
     project/
     ├── .touchfs/
     │   ├── model.default  # Project-wide model (gpt-4o-2024-08-06)
     │   └── prompt.default # Project-wide prompt
     ├── src/
     │   ├── .touchfs/
     │   │   ├── model     # Override model if needed
     │   │   └── prompt    # Override prompt for src/
     │   └── components/
     │       └── .touchfs/
     │           ├── model # Specific model settings
     │           └── prompt # Specific prompt for components
     ```
   - Empty files are skipped in the lookup chain
   - Detailed debug logging of lookup process

4. **LogSymlinkPlugin**
   - Creates symlink at .touchfs/log pointing to /var/log/touchfs/touchfs.log
   - Atomic logging with file locking for consistent output
   - Automatic log rotation with numbered suffixes (e.g. touchfs.log.1, touchfs.log.2)
   - Safe for concurrent access and real-time monitoring

5. **TreeGenerator**
   - Structured tree visualization
   - Shows generator assignments and configuration
   - Greppable output format
   - Example output:
     ```
     # Filesystem Tree Structure
     # Files marked with 🔄 will be generated on next read
     # For default generator shows relative paths to prompt and model files
     #
     # File Tree                                    Generator Info
     ├── WindowsVistaBestOf
     │   ├── features.txt                                🔄 default (prompt: ../.prompt model: ../.model)
     │   ├── wallpapers
     │   │   ├── img1.jpg                                🔄 default (prompt: ../../.prompt model: ../../.model)
     │   │   └── img2.jpg                                🔄 default (prompt: ../../.prompt model: ../../.model)
     │   └── symlink_to_features
     ├── .touchfs
     │   ├── readme                                      🔄 readme
     │   ├── tree                                        🔄 tree
     │   ├── prompt.default                              🔄 prompt
     │   ├── model.default                               🔄 model
     │   ├── log
     │   ├── cache_enabled                               🔄 cache_control
     │   ├── cache_stats                                 🔄 cache_control
     │   ├── cache_clear                                 🔄 cache_control
     │   └── cache_list                                  🔄 cache_control
     ├── .model
     ├── .prompt
     └── song.txt
     ```
   - For files using the default generator, shows relative paths to:
     - The prompt file that will be used (e.g., ../.prompt)
     - The model file that will be used (e.g., ../.model)
   - Paths are shown relative to each file's location
   - If no custom prompt/model files are found, defaults to .touchfs/prompt.default and .touchfs/model.default

6. **ReadmeGenerator**
   - Dynamic README in .touchfs
   - Shows filesystem structure
   - Includes generation status

7. **CacheControlPlugin**
   - Provides cache control through proc-like files in .touchfs/
   - Enables/disables caching globally via cache_enabled
   - Monitors cache performance via cache_stats
   - Manages cache content via cache_clear and cache_list
   - Real-time cache statistics tracking
   - Example usage:
     ```bash
     # Enable/disable caching
     echo 1 > .touchfs/cache_enabled
     echo 0 > .touchfs/cache_enabled
     
     # Monitor cache performance
     watch -n1 cat .touchfs/cache_stats
     
     # Clear cache when needed
     echo 1 > .touchfs/cache_clear
     
     # List cached content
     cat .touchfs/cache_list
     ```

### Creating Custom Plugins

```python
from touchfs.content.plugins.base import BaseContentGenerator

class CustomPlugin(BaseContentGenerator):
    def generator_name(self) -> str:
        return "custom"
        
    def generate(self, path: str, node: FileNode, fs_structure: Dict[str, FileNode]) -> str:
        return "Generated content based on filesystem context"
```

## 🔍 Context System

TouchFS includes a sophisticated context retrieval system that follows Model Context Protocol (MCP) principles:

### Context Generation

The system provides two main ways to work with context:

1. **Built-in Context Management**
   - Hierarchical context inheritance through filesystem structure
   - Automatic context collection during content generation
   - Token-aware content inclusion
   - Smart file ordering (e.g., __init__.py files first)

2. **Command Line Tool**
   ```bash
   # Generate context from current directory
   touchfs_context .
   
   # Specify maximum tokens
   touchfs_context . --max-tokens 4000
   
   # Exclude specific patterns
   touchfs_context . --exclude "*.pyc" --exclude "*/__pycache__/*"
   ```

### Context Features

- **Token Management**
  - Automatic token counting using tiktoken
  - Configurable token limits
  - Smart content truncation when limits are reached

- **MCP-Compliant Output**
  - Structured file content as resources
  - Rich metadata for each file
  - URI-based resource identification
  - Organized by module/directory structure

- **Smart File Organization**
  - Priority ordering for important files (__init__.py, __main__.py)
  - Grouping by module/directory
  - Clear separation with headers and markers
  - Formatted for readability with syntax highlighting

## 🔧 Technical Details

TouchFS uses FUSE (Filesystem in USErspace) to create a virtual filesystem:

```
User Programs (ls, cat, etc.)
           ↓
    VFS (Kernel Space)
           ↓
     FUSE Kernel Module
           ↓
     FUSE Userspace Lib
           ↓
         TouchFS
```

### Key Components

1. **Memory Management**
   - In-memory file storage
   - JSON serialization support
   - Efficient content generation

2. **LLM Integration**
   - OpenAI API integration
   - Context-aware generation
   - Structured outputs using Pydantic

3. **Plugin Architecture**
   - Custom content generators
   - Dynamic file overlays
   - Extended attribute support

### Caching System

TouchFS includes a robust caching system to improve performance and reduce API calls:

1. **Cache Control Files**
   Located in the `.touchfs` directory:
   ```
   .touchfs/
   ├── cache_enabled   # Write 0/1 to disable/enable caching
   ├── cache_stats     # Read-only cache statistics
   ├── cache_clear     # Write 1 to clear cache
   └── cache_list      # List of cached request hashes
   ```

2. **Enabling/Disabling Cache**
   ```bash
   # Enable caching
   echo 1 > .touchfs/cache_enabled

   # Disable caching
   echo 0 > .touchfs/cache_enabled

   # Check current status
   cat .touchfs/cache_enabled
   ```

3. **Cache Statistics**
   Monitor cache performance:
   ```bash
   cat .touchfs/cache_stats
   # Output:
   # Hits: 42
   # Misses: 7
   # Size: 128000 bytes
   # Enabled: True
   ```

4. **Managing Cache**
   ```bash
   # Clear all cached content
   echo 1 > .touchfs/cache_clear

   # List cached requests
   cat .touchfs/cache_list
   ```

5. **Cache Location**
   - Default: `~/.touchfs.cache/`
   - Override with `TOUCHFS_CACHE_FOLDER` environment variable

6. **What Gets Cached**
   - Filesystem structure generation results
   - Individual file content generation
   - Each cache entry is keyed by a hash of the request parameters
   - Cache entries are JSON files containing the generated content

7. **Cache Behavior**
   - Cache is checked before making API calls
   - Cache hits return immediately with stored content
   - Cache misses trigger normal content generation
   - Generated content is automatically cached if caching is enabled
   - Cache settings have immediate global effect
   - Cache statistics track hits and misses for performance monitoring

### Performance Considerations

- Operates in userspace via FUSE
- Memory-bound rather than I/O-bound
- Ideal for development and prototyping
- Caching significantly reduces API calls and improves response times

## 📝 Logging System

### Overview
TouchFS implements a robust logging system that provides detailed context for debugging, monitoring, and software engineering tasks. The logging system is designed to maintain a comprehensive history while preventing unbounded growth through automatic rotation.

### Log File Location
- Primary log file: `/var/log/touchfs/touchfs.log`
- Accessible via symlink: `/.touchfs/log` -> `/var/log/touchfs/touchfs.log`
- Rotated logs: `/var/log/touchfs/touchfs.log.{N}` where N is an incrementing number

### Debug Mode
For development and troubleshooting, TouchFS supports directing debug logs to stderr:
```bash
# Enable debug logging to stderr
touchfs_mount ~/project --debug-stderr

# Debug logs will now print to stderr in addition to the log file
```

### Log Rotation
- Automatic rotation occurs on each filesystem mount
- Previous log file is renamed with an incrementing suffix (e.g., touchfs.log.1, touchfs.log.2)
- Ensures logs don't grow unbounded while preserving historical context
- Atomic operations with file locking prevent data loss during rotation

### Log Format
Each log entry contains rich contextual information:
```
timestamp - name - level - filename:line - function - process_id - thread_id - message
```

### Using Logs for Software Engineering
The logging system is particularly valuable for software engineering tasks when used with LLM prompts:

1. **Debugging Context**
   - Log entries provide full stack traces and execution paths
   - Process and thread IDs help track concurrent operations
   - Timestamps enable temporal analysis of operations

2. **System Understanding**
   - Function names and line numbers reveal code structure
   - Log patterns show common operation sequences
   - Error messages highlight potential failure points

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
