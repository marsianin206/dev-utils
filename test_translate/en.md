# DevUtils - Developer Utilities

A comprehensive set of CLI tools for developers.

## Features

### File Tools
- **list** - List files in directory
- **hash** - Calculate file hash
- **find** - Find files by pattern
- **size** - Check file/folder size
- **diff** - Compare two files

### Data Tools
- **validate** - Validate JSON
- **format** - Format JSON
- **minify** - Minify JSON
- **convert** - Convert JSON <-> YAML
- **query** - Query JSON data

### Network Tools
- **ip** - Get public IP address
- **info** - Get IP information
- **headers** - Get URL headers
- **test** - Test URL
- **status** - Check redirect status

### Text Tools
- **wc** - Word count
- **grep** - Search text
- **replace** - Replace text
- **encode** - Encode text (base64, url, hex)
- **decode** - Decode text

### Crypto Tools
- **hash** - Hash text
- **generate-password** - Generate secure password
- **generate-token** - Generate random token
- **uuid** - Generate UUID

### System Tools
- **ps** - List processes
- **top** - Top processes
- **info** - System information
- **memory** - Memory usage
- **disk** - Disk usage

## Installation

```bash
pip install dev-utils
```

## Usage

```bash
# Show help
dev-utils --help

# Show version
dev-utils version

# Use file tools
dev-utils file list
dev-utils file hash file.txt

# Use network tools
dev-utils net ip
```