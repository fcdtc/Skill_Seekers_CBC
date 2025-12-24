#!/usr/bin/env python3
"""
Build skill from local repository data

Converts extracted local repository data into Claude AI skill format.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class LocalSkillBuilder:
    """Build Claude skill from local repository data"""

    def __init__(self, data_file: str, output_dir: str = None):
        """
        Initialize skill builder

        Args:
            data_file: Path to extracted data JSON file
            output_dir: Output directory for skill (defaults to output/{name})
        """
        self.data_file = data_file

        # Load extracted data
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # Set output directory
        repo_name = self.data['repo_info']['name']
        self.output_dir = output_dir or f"output/{repo_name}"

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

    def build_skill(self):
        """Build complete skill structure"""
        print(f"Building skill for {self.data['repo_info']['name']}...")

        # Create main skill file
        self._create_skill_md()

        # Create references structure
        self._create_references()

        # Create assets if needed
        self._create_assets()

        print(f"✅ Skill built successfully at: {self.output_dir}")

    def _create_skill_md(self):
        """Create main SKILL.md file"""
        skill_path = os.path.join(self.output_dir, "SKILL.md")

        repo_info = self.data['repo_info']
        readme_files = self.data.get('readme_files', [])
        languages = self.data.get('languages', {})
        file_tree = self.data.get('file_tree', [])

        # Get main README content
        main_readme = ""
        if readme_files:
            main_readme = readme_files[0]['content']

        # Extract key code examples
        code_examples = self._extract_code_examples()

        # Extract configuration examples
        config_examples = self._extract_config_examples()

        skill_content = f"""# {repo_info['name']}

{repo_info['description']}

This skill provides comprehensive knowledge of the {repo_info['name']} project, including code examples, configurations, and usage patterns.

## Project Overview

{main_readme}

## Languages & Technologies

{', '.join(languages.keys()) if languages else 'Various'}

## Key Features & Code Examples

{code_examples}

## Configuration Examples

{config_examples}

## File Structure

The repository contains {len(file_tree)} files organized as follows:

```
{self._format_file_tree(file_tree[:50])}  # Show first 50 files
{'...' if len(file_tree) > 50 else ''}
```

## Common Usage Patterns

Based on the codebase analysis, here are common patterns:

### 1. Service implementation
Services typically follow client-server architecture with separate main.go files.

### 2. Protocol buffers
Protobuf files (`.pb.go`, `.trpc.go`) are auto-generated from proto definitions.

### 3. Configuration
YAML configuration files (`.yaml`, `yml`) are used for service settings.

## Getting Started

1. Explore the examples in the `helloworld` directory for basic usage
2. Check the `features` directory for specific functionality examples
3. Refer to individual feature READMEs for detailed setup instructions

---

*Generated from local repository analysis on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write(skill_content)

        print(f"✅ Created: SKILL.md")

    def _create_references(self):
        """Create references directory with categorized content"""
        refs_dir = os.path.join(self.output_dir, "references")
        os.makedirs(refs_dir, exist_ok=True)

        # Create index
        index_content = """# tRPC-Go Examples Reference Guide

This directory contains organized reference materials from the tRPC-Go examples repository.

## Available References

- [getting_started.md](getting_started.md) - Basic setup and first examples
- [configuration.md](configuration.md) - Configuration patterns and examples
- [features.md](features.md) - Feature documentation and examples
- [code_patterns.md](code_patterns.md) - Common code patterns and best practices

"""

        with open(os.path.join(refs_dir, "index.md"), 'w', encoding='utf-8') as f:
            f.write(index_content)

        # Create getting_started guide
        self._create_getting_started(refs_dir)

        # Create configuration guide
        self._create_configuration_guide(refs_dir)

        # Create features overview
        self._create_features_overview(refs_dir)

        # Create code patterns
        self._create_code_patterns(refs_dir)

        print(f"✅ Created: references/ directory")

    def _create_getting_started(self, refs_dir: Path):
        """Create getting started guide"""
        content = """# Getting Started with tRPC-Go Examples

## Quick Start

### 1. Basic Hello World

The `helloworld` directory contains the simplest example:

```bash
# Start server
cd helloworld
go run server/main.go

# In another terminal, start client
go run client/main.go
```

### 2. Explore Features

The `features/` directory contains 40+ examples demonstrating specific capabilities:

- `admin/` - Administrative features
- `compression/` - Compression
- `http/` - HTTP integration
- `stream/` - Streaming
- `timeout/` - Timeout handling

## Project Structure

Each feature follows this pattern:
```
feature-name/
├── README.md          # Feature documentation
├── client/
│   ├── main.go       # Client implementation
│   └── trpc_go.yaml  # Client config
├── server/
│   ├── main.go       # Server implementation
│   └── trpc_go.yaml  # Server config
└── shared/           # Optional shared code
"""

        with open(os.path.join(refs_dir, "getting_started.md"), 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_configuration_guide(self, refs_dir: Path):
        """Create configuration guide"""
        config_files = self.data.get('config_files', [])

        content = """# Configuration Guide

## Configuration Files

The project uses various configuration approaches:

### YAML Configuration

Most services use `trpc_go.yaml` for configuration:

```yaml
server:  # Server settings
client:  # Client settings
# Additional service-specific settings
```

### Go Modules

Dependencies are managed through `go.mod`:

```go
module git.code.oa.com/trpc-go/trpc-go/examples

go 1.21

require (
    git.code.oa.com/trpc-go/trpc-go v0.18.5
    # ... other dependencies
)
```

## Common Configuration Patterns

Based on the analyzed configuration files:

1. **Service Discovery**: Use naming services for service registration
2. **Transport**: Choose between HTTP, gRPC, or custom transport
3. **Filters**: Apply filters for logging, metrics, etc.
4. **Timeout**: Configure appropriate timeouts for services
"""

        # Add specific config examples
        if config_files:
            content += "\n\n## Example Configuration Files\n\n"
            for config in config_files[:5]:  # Show first 5
                content += f"### {config['path']}\n```\n{config['content'][:200]}...\n```\n\n"

        with open(os.path.join(refs_dir, "configuration.md"), 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_features_overview(self, refs_dir: Path):
        """Create features overview"""
        readme_files = self.data.get('readme_files', [])

        content = """# Features Overview

## Available Features

The examples demonstrate comprehensive tRPC-Go capabilities:

### Core Features
- **helloworld**: Basic client-server communication
- **config**: Configuration management
- **timeout**: Request timeout handling
- **compression**: Data compression

### Advanced Features
- **stream**: Streaming RPC
- **http**: HTTP integration and gateway
- **admin**: Administrative interfaces
- **robust**: Fault tolerance and reliability
- **discovery**: Service discovery mechanisms

### Transport Options
- **fasthttp**: High-performance HTTP
- **quic**: QUIC protocol support
- **http3**: HTTP/3 support

### Testing & Monitoring
- **filters**: Request/response filtering
- **rpcz**: RPC debugging and tracing
- **health**: Health check services

## Usage Guidelines

Each feature includes:
1. **README.md**: Feature description and usage steps
2. **client/main.go**: Working client example
3. **server/main.go**: Working server example
4. **Configuration files**: YAML configurations

## Feature Categories

Based on the analysis, features are categorized by functionality and use case.
"""

        with open(os.path.join(refs_dir, "features.md"), 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_code_patterns(self, refs_dir: Path):
        """Create code patterns documentation"""
        signatures = self.data.get('signatures', [])
        test_examples = self.data.get('test_examples', [])

        content = """# Code Patterns & Best Practices

## Common Patterns

### 1. Server Implementation

```go
package main

import (
    "context"
    "git.code.oa.com/trpc-go/trpc-go/trpc"
)

func main() {
    // Initialize service
    s := trpc.NewServer()

    // Register service
    // ... service registration

    // Start server
    s.Serve()
}
```

### 2. Client Implementation

```go
package main

import (
    "context"
    "git.code.oa.com/trpc-go/trpc-go/trpc"
)

func main() {
    // Create client connection
    client := trpc.NewClient()

    // Call service
    // ... service calls
}
```

## File Organization

- `proto/` - Protocol buffer definitions
- `client/` - Client implementations
- `server/` - Server implementations
- `shared/` - Shared utilities

## Key Go Patterns Observed

1. **Context-based operations**
2. **Error handling patterns**
3. **Service initialization**
4. **Resource management**
5. **Logging and monitoring**
"""

        with open(os.path.join(refs_dir, "code_patterns.md"), 'w', encoding='utf-8') as f:
            f.write(content)

    def _create_assets(self):
        """Create assets directory if needed"""
        assets_dir = os.path.join(self.output_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        # Could add images, diagrams etc. here if available
        print(f"✅ Created: assets/ directory")

    def _extract_code_examples(self) -> str:
        """Extract relevant code examples"""
        file_tree = self.data.get('file_tree', [])

        # Look for key Go files in helloworld and features
        go_examples = []

        for file_path in file_tree:
            if 'main.go' in file_path and ('helloworld' in file_path or ('features/' in file_path and len(go_examples) < 3)):
                try:
                    full_path = os.path.join(self.data['repo_info']['path'], file_path)
                    if os.path.exists(full_path):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract key parts
                            if len(content) < 2000:  # Only shorter files
                                go_examples.append(f"### {file_path}\n```go\n{content}\n```\n")
                except:
                    continue

        return '\n'.join(go_examples[:3])  # Limit to 3 examples

    def _extract_config_examples(self) -> str:
        """Extract configuration examples"""
        config_files = self.data.get('config_files', [])

        configs = []
        for config in config_files[:3]:  # Show first 3
            if config['content']:
                configs.append(f"### {config['path']}\n```yaml\n{config['content']}\n```\n")

        return '\n'.join(configs)

    def _format_file_tree(self, files: List[str], max_indent: int = 2) -> str:
        """Format file tree for display"""
        tree_lines = []

        for file_path in files:
            indent = '  ' * min(file_path.count('/'), max_indent)
            filename = file_path.split('/')[-1]
            tree_lines.append(f"{indent}├── {filename}")

        return '\n'.join(tree_lines)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Build skill from local repository data")
    parser.add_argument("data_file", help="Path to extracted data JSON file")
    parser.add_argument("--output", help="Output directory (optional)")

    args = parser.parse_args()

    if not os.path.exists(args.data_file):
        print(f"Error: Data file not found: {args.data_file}")
        return 1

    try:
        builder = LocalSkillBuilder(args.data_file, args.output)
        builder.build_skill()
        return 0
    except Exception as e:
        print(f"Error building skill: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())