#!/usr/bin/env python3
"""
Local Repository to Claude Skill Converter

Converts local repositories into Claude AI skills by extracting:
- README and documentation files
- Code structure and signatures
- Configuration files and settings
- Usage examples from tests
- Directory structure

Usage:
    skill-seekers local --path ./my-project --name my-project
    skill-seekers local --config configs/local_project.json
"""

import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

try:
    from git import Repo, InvalidGitRepositoryError
except ImportError:
    print("Error: GitPython not installed. Run: pip install GitPython")
    sys.exit(1)

# Configure logging FIRST (before using logger)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import code analyzer for deep code analysis
try:
    from .code_analyzer import CodeAnalyzer
    CODE_ANALYZER_AVAILABLE = True
except ImportError:
    CODE_ANALYZER_AVAILABLE = False
    logger.warning("Code analyzer not available - deep analysis disabled")

# Import skill builder for automatic skill generation
try:
    from .build_local_skill import LocalSkillBuilder
    SKILL_BUILDER_AVAILABLE = True
except ImportError:
    SKILL_BUILDER_AVAILABLE = False
    logger.warning("Skill builder not available - automatic generation disabled")

# Directories to exclude from local repository analysis
EXCLUDED_DIRS = {
    'venv', 'env', '.venv', '.env',  # Virtual environments
    'node_modules', '__pycache__', '.pytest_cache',  # Dependencies and caches
    '.git', '.svn', '.hg',  # Version control
    'build', 'dist', '*.egg-info',  # Build artifacts
    'htmlcov', '.coverage',  # Coverage reports
    '.tox', '.nox',  # Testing environments
    '.mypy_cache', '.ruff_cache',  # Linter caches
    '.vscode', '.idea',  # IDE files
    'target', 'Cargo.lock',  # Rust build artifacts
    '.gradle', 'gradle', 'build',  # Gradle/Maven
}

# File extensions to include for analysis
INCLUDE_EXTENSIONS = {
    # Code files
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.dart',
    '.gd', '.gs',  # Godot
    '.lua', '.sh', '.bat', '.ps1',
    # Documentation
    '.md', '.rst', '.txt', '.adoc',
    # Config files
    '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    '.xml', '.plist', '.props', '.csproj', '.sln',
}

# README file patterns
README_PATTERNS = [
    'README.md', 'README.rst', 'README.txt', 'README',
    'readme.md', 'readme.rst', 'readme.txt', 'readme',
    'README.MD', 'README.TXT',
    'Docs/README.md', 'docs/README.md', 'doc/README.md',
    'DOCUMENTATION.md', 'DOCUMENTATION.txt',
    'INSTALL.md', 'INSTALL.txt',
    'SETUP.md', 'SETUP.txt',
]


class LocalScraper:
    """
    Local Repository Scraper

    Extracts repository information for skill generation:
    - Repository structure and files
    - README files at multiple levels
    - Code comments and docstrings
    - Programming language detection
    - Function/class signatures
    - Test examples
    - Configuration files
    - Git information
    """

    def __init__(self, config: Dict[str, Any], local_repo_path: Optional[str] = None):
        """Initialize local scraper with configuration."""
        self.config = config

        # Get repository path
        self.local_repo_path = local_repo_path or config.get('path') or config.get('local_repo_path')
        if not self.local_repo_path:
            raise ValueError("Local repository path is required")

        self.local_repo_path = os.path.expanduser(self.local_repo_path)
        if not os.path.exists(self.local_repo_path):
            raise ValueError(f"Repository path does not exist: {self.local_repo_path}")

        logger.info(f"Local repository mode: {self.local_repo_path}")

        # Skill metadata
        self.name = config.get('name', os.path.basename(self.local_repo_path.rstrip('/\\')))
        self.description = config.get('description', f'Skill for {self.name}')

        # Configure directory exclusions
        self.excluded_dirs = set(EXCLUDED_DIRS)
        if 'exclude_dirs' in config:
            self.excluded_dirs = set(config['exclude_dirs'])
            logger.warning(f"Using custom directory exclusions: {len(self.excluded_dirs)} dirs")
        elif 'exclude_dirs_additional' in config:
            additional = set(config['exclude_dirs_additional'])
            self.excluded_dirs = self.excluded_dirs.union(additional)
            logger.info(f"Added {len(additional)} custom directory exclusions")

        # Analysis options
        self.include_code = config.get('include_code', True)
        self.code_analysis_depth = config.get('code_analysis_depth', 'surface')  # 'surface', 'deep', 'full'
        self.file_patterns = config.get('file_patterns', [])
        self.max_file_size = config.get('max_file_size', 1024 * 1024)  # 1MB default
        self.include_tests = config.get('include_tests', True)
        self.include_configs = config.get('include_configs', True)

        # Initialize code analyzer if deep analysis requested
        self.code_analyzer = None
        if self.code_analysis_depth != 'surface' and CODE_ANALYZER_AVAILABLE:
            self.code_analyzer = CodeAnalyzer(depth=self.code_analysis_depth)
            logger.info(f"Code analysis depth: {self.code_analysis_depth}")

        # Output paths
        self.skill_dir = f"output/{self.name}"
        self.data_file = f"output/{self.name}_local_data.json"

        # Extracted data storage
        self.extracted_data = {
            'repo_info': {},
            'readme_files': [],  # Multiple README files at different levels
            'file_tree': [],
            'languages': {},
            'signatures': [],
            'test_examples': [],
            'config_files': [],
            'git_info': {},
            'documentation_files': []
        }

    def scrape(self) -> Dict[str, Any]:
        """
        Main scraping entry point.
        Executes all extraction tasks in sequence.
        """
        try:
            logger.info(f"Starting local repository scrape: {self.local_repo_path}")

            # Extract repository info
            self._extract_repository_info()

            # Find README files at multiple levels
            self._extract_readme_files()

            # Extract code structure
            self._extract_code_structure()

            # Extract configuration files
            if self.include_configs:
                self._extract_config_files()

            # Extract git information
            self._extract_git_info()

            # Save extracted data
            self._save_data()

            logger.info(f"✅ Local repository scraping complete! Data saved to: {self.data_file}")
            return self.extracted_data

        except Exception as e:
            logger.error(f"Unexpected error during local repository scraping: {e}")
            raise

    def _extract_repository_info(self):
        """Extract repository information."""
        logger.info("Extracting repository information...")

        repo_path = Path(self.local_repo_path)

        self.extracted_data['repo_info'] = {
            'name': self.name,
            'path': str(repo_path.absolute()),
            'description': self.description,
            'created_at': datetime.fromtimestamp(repo_path.stat().st_ctime).isoformat() if repo_path.exists() else None,
            'modified_at': datetime.fromtimestamp(repo_path.stat().st_mtime).isoformat() if repo_path.exists() else None,
        }

    def _extract_readme_files(self):
        """Extract README.md files from multiple levels of the repository."""
        logger.info("Searching for README files...")

        repo_path = Path(self.local_repo_path)
        found_readmes = []

        # Search for README files recursively
        for readme_pattern in README_PATTERNS:
            for readme_path in repo_path.rglob(readme_pattern):
                # Skip if in excluded directory
                if any(excluded in readme_path.parts for excluded in self.excluded_dirs):
                    continue

                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Get relative path from repo root
                    rel_path = str(readme_path.relative_to(repo_path))

                    found_readmes.append({
                        'path': rel_path,
                        'content': content,
                        'size': len(content),
                        'level': len(readme_path.relative_to(repo_path).parts)
                    })

                    logger.debug(f"README found: {rel_path} ({len(content)} chars)")

                except (OSError, UnicodeDecodeError) as e:
                    logger.warning(f"Could not read README {readme_path}: {e}")
                    continue

        # Sort by level (root level first) and size
        found_readmes.sort(key=lambda x: (x['level'], -x['size']))

        self.extracted_data['readme_files'] = found_readmes

        if found_readmes:
            logger.info(f"Found {len(found_readmes)} README file(s)")
            for readme in found_readmes[:3]:  # Log top 3
                logger.info(f"  - {readme['path']} ({readme['size']} chars)")
        else:
            logger.warning("No README files found in repository")

    def _extract_code_structure(self):
        """Extract code structure, languages, signatures, and test examples."""
        logger.info("Extracting code structure...")

        repo_path = Path(self.local_repo_path)

        # Collect file statistics
        language_stats = {}
        all_files = []

        # Walk through repository
        for file_path in repo_path.rglob('*'):
            if not file_path.is_file():
                continue

            # Skip if in excluded directory
            if any(excluded in file_path.parts for excluded in self.excluded_dirs):
                continue

            # Check file extension
            suffix = file_path.suffix.lower()
            if suffix not in INCLUDE_EXTENSIONS:
                continue

            # Skip if file too large
            try:
                if file_path.stat().st_size > self.max_file_size:
                    logger.debug(f"Skipping large file: {file_path}")
                    continue
            except OSError:
                continue

            # Get relative path
            rel_path = str(file_path.relative_to(repo_path))
            all_files.append(rel_path)

            # Update language statistics
            lang = self._get_language_from_extension(suffix)
            if lang:
                language_stats[lang] = language_stats.get(lang, 0) + 1

            # Extract content for analysis
            if self.include_code and suffix in {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.go', '.rs'}:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Extract signatures
                    if self.code_analyzer:
                        signatures = self.code_analyzer.extract_signatures(content, str(file_path))
                        self.extracted_data['signatures'].extend(signatures)

                    # Extract test examples
                    if self.include_tests and self._is_test_file(file_path):
                        examples = self._extract_test_examples(content, str(file_path))
                        self.extracted_data['test_examples'].extend(examples)

                except (OSError, UnicodeDecodeError):
                    continue

        # Store file tree and languages
        self.extracted_data['file_tree'] = sorted(all_files)
        self.extracted_data['languages'] = language_stats

        logger.info(f"Processed {len(all_files)} files")
        logger.info(f"Languages detected: {', '.join(language_stats.keys())}")

    def _extract_config_files(self):
        """Extract configuration files."""
        logger.info("Extracting configuration files...")

        repo_path = Path(self.local_repo_path)
        config_files = []

        config_patterns = [
            '*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.cfg', '*.conf',
            'package.json', 'requirements.txt', 'Pipfile', 'pyproject.toml',
            'Cargo.toml', 'composer.json', 'Gemfile', 'pom.xml', 'build.gradle',
            '.env.example', 'config.js', 'settings.py'
        ]

        for pattern in config_patterns:
            for config_path in repo_path.rglob(pattern):
                # Skip if in excluded directory
                if any(excluded in config_path.parts for excluded in self.excluded_dirs):
                    continue

                try:
                    with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    rel_path = str(config_path.relative_to(repo_path))

                    config_files.append({
                        'path': rel_path,
                        'content': content[:1000],  # First 1000 chars
                        'type': config_path.suffix.lower()
                    })

                except (OSError, UnicodeDecodeError):
                    continue

        self.extracted_data['config_files'] = config_files
        logger.info(f"Found {len(config_files)} configuration files")

    def _extract_git_info(self):
        """Extract git repository information."""
        logger.info("Extracting git information...")

        try:
            repo = Repo(self.local_repo_path)

            git_info = {
                'is_git_repo': True,
                'current_branch': repo.active_branch.name,
                'remote_url': None,
                'last_commit': {
                    'hash': repo.head.commit.hexsha,
                    'message': repo.head.commit.message.strip(),
                    'author': str(repo.head.commit.author),
                    'date': datetime.fromtimestamp(repo.head.commit.committed_date).isoformat()
                },
                'is_dirty': repo.is_dirty(),
                'untracked_files': len(repo.untracked_files)
            }

            # Get remote URL
            try:
                remote_url = repo.remotes.origin.url
                git_info['remote_url'] = remote_url
            except Exception:
                pass

            self.extracted_data['git_info'] = git_info
            logger.info(f"Git repository detected (branch: {git_info['current_branch']})")

        except InvalidGitRepositoryError:
            self.extracted_data['git_info'] = {'is_git_repo': False}
            logger.warning("Not a git repository")
        except Exception as e:
            self.extracted_data['git_info'] = {'is_git_repo': False, 'error': str(e)}
            logger.warning(f"Error reading git info: {e}")

    def _get_language_from_extension(self, extension: str) -> Optional[str]:
        """Map file extension to programming language."""
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React/JavaScript',
            '.tsx': 'React/TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.hpp': 'C++ Header',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.dart': 'Dart',
            '.gd': 'GDScript',
            '.gs': 'GDScript',
            '.lua': 'Lua',
            '.sh': 'Shell',
            '.bat': 'Batch',
            '.ps1': 'PowerShell',
            '.md': 'Markdown',
            '.rst': 'reStructuredText',
            '.txt': 'Plain Text',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.toml': 'TOML',
            '.ini': 'INI',
            '.xml': 'XML'
        }
        return extension_map.get(extension)

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is likely a test file."""
        name = file_path.name.lower()
        path_parts = [part.lower() for part in file_path.parts]

        # Check filename patterns
        test_patterns = [
            'test_', '_test.', 'tests.', '_spec.', 'spec_'
        ]

        if any(pattern in name for pattern in test_patterns):
            return True

        # Check directory patterns
        test_dirs = ['test', 'tests', 'spec', 'specs']
        if any(test_dir in path_parts for test_dir in test_dirs):
            return True

        return False

    def _extract_test_examples(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract test examples from test file content."""
        examples = []

        # Extract code blocks that look like test examples
        lines = content.split('\n')
        current_example = []
        in_example = False

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Detect test function/class definitions
            if any(keyword in line_stripped for keyword in ['def test_', 'def test', 'test(', 'describe(', 'it(']):
                if current_example:
                    # Save previous example
                    example_code = '\n'.join(current_example)
                    if len(example_code.strip()) > 20:  # Skip very short examples
                        examples.append({
                            'code': example_code,
                            'file': file_path,
                            'line_start': i - len(current_example) + 1
                        })

                current_example = [line]
                in_example = True

            elif in_example:
                current_example.append(line)

                # End example if we hit a blank line followed by another definition
                if not line_stripped and i < len(lines) - 1:
                    next_line = lines[i + 1].strip()
                    if any(keyword in next_line for keyword in ['def ', 'class ', 'function ', 'test(', 'describe(', 'it(']):
                        if current_example:
                            example_code = '\n'.join(current_example)
                            if len(example_code.strip()) > 20:
                                examples.append({
                                    'code': example_code,
                                    'file': file_path,
                                    'line_start': i - len(current_example) + 1
                                })
                        current_example = []
                        in_example = False

        # Add the last example if we have one
        if current_example and in_example:
            example_code = '\n'.join(current_example)
            if len(example_code.strip()) > 20:
                examples.append({
                    'code': example_code,
                    'file': file_path,
                    'line_start': len(lines) - len(current_example) + 1
                })

        return examples[:5]  # Limit to first 5 examples per file

    def _save_data(self):
        """Save extracted data to JSON file."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        # Prepare data for JSON serialization
        json_data = {
            'extracted_at': datetime.now().isoformat(),
            'repository': self.extracted_data['repo_info'],
            **self.extracted_data
        }

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)


def main():
    """Main entry point for local repository scraping."""
    parser = argparse.ArgumentParser(
        description="Convert local repository into Claude AI skill"
    )

    parser.add_argument("--config", help="Config JSON file")
    parser.add_argument("--path", help="Local repository path")
    parser.add_argument("--name", help="Skill name")
    parser.add_argument("--description", help="Skill description")
    parser.add_argument("--output", help="Output directory (default: output/)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load or create config
    config = {}

    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

    # Override config with command line arguments
    if args.path:
        config['path'] = args.path
    if args.name:
        config['name'] = args.name
    if args.description:
        config['description'] = args.description
    if args.output:
        config['output_dir'] = args.output

    try:
        # Step 1: Create scraper and scan
        scraper = LocalScraper(config)
        scraper.scrape()

        print(f"\n✅ Successfully scraped local repository: {scraper.name}")
        print(f"📁 Data file: {scraper.data_file}")

        # Step 2: Build skill automatically
        if SKILL_BUILDER_AVAILABLE:
            logger.info("Building skill from extracted data...")
            builder = LocalSkillBuilder(scraper.data_file, config.get('output_dir'))
            builder.build_skill()
            print(f"📁 Skill built at: {builder.output_dir}")
        else:
            logger.warning("Skill builder not available. Run manually:")
            print(f"   python -m skill_seekers.cli.build_local_skill {scraper.data_file}")
            print(f"🎯 Skill directory: {scraper.skill_dir}")

        return 0

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())