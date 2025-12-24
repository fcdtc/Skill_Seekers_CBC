#!/usr/bin/env python3
"""
Skill Seekers - Unified CLI Entry Point

Provides a git-style unified command-line interface for all Skill Seekers tools.

Usage:
    skill-seekers <command> [options]

Commands:
    pdf           Extract from PDF file
    local         Scrape local repository
    unified       Multi-source scraping (PDF + local repo)
    enhance       AI-powered enhancement (local, no API key)
    package       Package skill into .zip file
    upload        Upload skill to Claude
    install-agent Install skill to AI agent directories

Examples:
    skill-seekers pdf --pdf docs.pdf --name my-docs
    skill-seekers local --path ./my-project --name my-project
    skill-seekers unified --config configs/project_unified.json
    skill-seekers package output/my-project/
    skill-seekers install-agent output/my-project/ --agent cursor
"""

import sys
import argparse
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="skill-seekers",
        description="Convert local repositories and PDFs into Claude AI skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from PDF
  skill-seekers pdf --pdf docs.pdf --name my-docs

  # Scrape local repository
  skill-seekers local --path ./my-project --name my-project

  # Multi-source scraping (unified)
  skill-seekers unified --config configs/project_unified.json

  # AI-powered enhancement
  skill-seekers enhance output/my-project/

  # Package and upload
  skill-seekers package output/my-project/
  skill-seekers upload output/my-project.zip

For more information: https://github.com/yusufkaraaslan/Skill_Seekers
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 2.3.0"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available Skill Seekers commands",
        help="Command to run"
    )

    # === local subcommand ===
    local_parser = subparsers.add_parser(
        "local",
        help="Scrape local repository",
        description="Scrape local repository and generate skill"
    )
    local_parser.add_argument("--config", help="Config JSON file")
    local_parser.add_argument("--path", help="Local repository path")
    local_parser.add_argument("--name", help="Skill name")
    local_parser.add_argument("--description", help="Skill description")

    # === pdf subcommand ===
    pdf_parser = subparsers.add_parser(
        "pdf",
        help="Extract from PDF file",
        description="Extract content from PDF and generate skill"
    )
    pdf_parser.add_argument("--config", help="Config JSON file")
    pdf_parser.add_argument("--pdf", help="PDF file path")
    pdf_parser.add_argument("--name", help="Skill name")
    pdf_parser.add_argument("--description", help="Skill description")
    pdf_parser.add_argument("--from-json", help="Build from extracted JSON")

    # === unified subcommand ===
    unified_parser = subparsers.add_parser(
        "unified",
        help="Multi-source scraping (PDF + local repo)",
        description="Combine PDF and local repository into one skill"
    )
    unified_parser.add_argument("--config", required=True, help="Unified config JSON file")
    unified_parser.add_argument("--merge-mode", help="Merge mode (rule-based, codebuddy-enhanced)")
    unified_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    # === enhance subcommand ===
    enhance_parser = subparsers.add_parser(
        "enhance",
        help="AI-powered enhancement (local, no API key)",
        description="Enhance SKILL.md using CodeBuddy Code (local)"
    )
    enhance_parser.add_argument("skill_directory", help="Skill directory path")
    enhance_parser.add_argument(
        '--interactive-enhancement',
        action='store_true',
        help='Open terminal window for enhancement (default: headless mode)'
    )
    enhance_parser.add_argument(
        '--timeout',
        type=int,
        default=3600,
        help='Timeout in seconds for headless mode (default: 3600 = 1 hour)'
    )

    # === package subcommand ===
    package_parser = subparsers.add_parser(
        "package",
        help="Package skill into .zip file",
        description="Package skill directory into uploadable .zip"
    )
    package_parser.add_argument("skill_directory", help="Skill directory path")
    package_parser.add_argument("--no-open", action="store_true", help="Don't open output folder")
    package_parser.add_argument("--upload", action="store_true", help="Auto-upload after packaging")

    # === upload subcommand ===
    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload skill to Claude",
        description="Upload .zip file to Claude via Anthropic API"
    )
    upload_parser.add_argument("zip_file", help=".zip file to upload")
    upload_parser.add_argument("--api-key", help="Anthropic API key")

    
    # === install-agent subcommand ===
    install_agent_parser = subparsers.add_parser(
        "install-agent",
        help="Install skill to AI agent directories",
        description="Copy skill to agent-specific installation directories"
    )
    install_agent_parser.add_argument(
        "skill_directory",
        help="Skill directory path (e.g., output/react/)"
    )
    install_agent_parser.add_argument(
        "--agent",
        required=True,
        help="Agent name (claude, cursor, vscode, amp, goose, opencode, all)"
    )
    install_agent_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing installation without asking"
    )
    install_agent_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview installation without making changes"
    )

    # === install subcommand ===
    install_parser = subparsers.add_parser(
        "install",
        help="Complete workflow: fetch → scrape → enhance → package → upload",
        description="One-command skill installation (AI enhancement MANDATORY)"
    )
    install_parser.add_argument(
        "--config",
        required=True,
        help="Config name (e.g., 'react') or path (e.g., 'configs/custom.json')"
    )
    install_parser.add_argument(
        "--destination",
        default="output",
        help="Output directory (default: output/)"
    )
    install_parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip automatic upload to Claude"
    )
    install_parser.add_argument(
        "--unlimited",
        action="store_true",
        help="Remove page limits during scraping"
    )
    install_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview workflow without executing"
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the unified CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Delegate to the appropriate tool
    try:
        if args.command == "local":
            from skill_seekers.cli.local_scraper import main as local_main
            sys.argv = ["local_scraper.py"]
            if args.config:
                sys.argv.extend(["--config", args.config])
            if args.path:
                sys.argv.extend(["--path", args.path])
            if args.name:
                sys.argv.extend(["--name", args.name])
            if args.description:
                sys.argv.extend(["--description", args.description])
            return local_main() or 0

        elif args.command == "pdf":
            from skill_seekers.cli.pdf_scraper import main as pdf_main
            sys.argv = ["pdf_scraper.py"]
            if args.config:
                sys.argv.extend(["--config", args.config])
            if args.pdf:
                sys.argv.extend(["--pdf", args.pdf])
            if args.name:
                sys.argv.extend(["--name", args.name])
            if args.description:
                sys.argv.extend(["--description", args.description])
            if args.from_json:
                sys.argv.extend(["--from-json", args.from_json])
            return pdf_main() or 0

        elif args.command == "unified":
            from skill_seekers.cli.unified_scraper import main as unified_main
            sys.argv = ["unified_scraper.py", "--config", args.config]
            if args.merge_mode:
                sys.argv.extend(["--merge-mode", args.merge_mode])
            if args.dry_run:
                sys.argv.append("--dry-run")
            return unified_main() or 0

        elif args.command == "enhance":
            from skill_seekers.cli.enhance_skill_local import main as enhance_main
            sys.argv = ["enhance_skill_local.py", args.skill_directory]
            if args.interactive_enhancement:
                sys.argv.append("--interactive-enhancement")
            if args.timeout:
                sys.argv.extend(["--timeout", str(args.timeout)])
            return enhance_main() or 0

        elif args.command == "package":
            from skill_seekers.cli.package_skill import main as package_main
            sys.argv = ["package_skill.py", args.skill_directory]
            if args.no_open:
                sys.argv.append("--no-open")
            if args.upload:
                sys.argv.append("--upload")
            return package_main() or 0

        elif args.command == "upload":
            from skill_seekers.cli.upload_skill import main as upload_main
            sys.argv = ["upload_skill.py", args.zip_file]
            if args.api_key:
                sys.argv.extend(["--api-key", args.api_key])
            return upload_main() or 0

        
        elif args.command == "install-agent":
            from skill_seekers.cli.install_agent import main as install_agent_main
            sys.argv = ["install_agent.py", args.skill_directory, "--agent", args.agent]
            if args.force:
                sys.argv.append("--force")
            if args.dry_run:
                sys.argv.append("--dry-run")
            return install_agent_main() or 0

        elif args.command == "install":
            from skill_seekers.cli.install_skill import main as install_main
            sys.argv = ["install_skill.py"]
            if args.config:
                sys.argv.extend(["--config", args.config])
            if args.destination:
                sys.argv.extend(["--destination", args.destination])
            if args.no_upload:
                sys.argv.append("--no-upload")
            if args.unlimited:
                sys.argv.append("--unlimited")
            if args.dry_run:
                sys.argv.append("--dry-run")
            return install_main() or 0

        else:
            print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
