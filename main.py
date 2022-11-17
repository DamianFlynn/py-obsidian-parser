"""
Obsidian Parser CLI
"""

# Import Multiplication from your library
from obsidian_parser import ObsidianParser
import argparse
import os

__version__ = "0.2.0"

parser = argparse.ArgumentParser()

parser.add_argument(
    "--hugo-content-dir",
    help="Directory of your Hugo content directory, the obsidian notes should be processed into.",
    type=str,
)

parser.add_argument(
    "--obsidian-vault-dir",
    help="Directory of the Obsidian vault",
    type=str,
)

parser.add_argument(
    "--export-dir",
    help="The Obsidian vault folder the notes should be processed from.",
    type=str
)

parser.add_argument(
    "--version",
    action="version",
    version="%(prog)s " + __version__,
)

def main():
    """Run the CLI."""
    args = parser.parse_args()
    print("Obsidian Parser CLI")
    if not args.hugo_content_dir or not os.path.isdir(args.hugo_content_dir):
        parser.error("The hugo content directory does not exist.")
    if not args.obsidian_vault_dir or not os.path.isdir(args.obsidian_vault_dir):
        parser.error("The obsidian vault directory does not exist.")
    if not args.export_dir or not os.path.isdir(os.path.join(args.obsidian_vault_dir, args.export_dir)):
        parser.error("The obsidian vault directory to export does not exist.")

    obsidian_parser = ObsidianParser(
        obsidian_vault_dir=args.obsidian_vault_dir,
        vault_content_dir=args.export_dir,
        hugo_content_dir=args.hugo_content_dir,
    )
    obsidian_parser.process(erase_hugo_content=True)

if __name__ == "__main__":
    main()