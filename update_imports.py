#!/usr/bin/env python3
"""Script to update imports in server_tools files."""

import os

files_to_update = [
    "/usr/local/var/www/entanglr/mediawiki-api-mcp/mediawiki_api_mcp/server_tools/wiki_meta_siteinfo.py",
    "/usr/local/var/www/entanglr/mediawiki-api-mcp/mediawiki_api_mcp/server_tools/wiki_page_delete.py",
    "/usr/local/var/www/entanglr/mediawiki-api-mcp/mediawiki_api_mcp/server_tools/wiki_page_move.py",
    "/usr/local/var/www/entanglr/mediawiki-api-mcp/mediawiki_api_mcp/server_tools/wiki_page_undelete.py"
]

for file_path in files_to_update:
    with open(file_path, 'r') as f:
        content = f.read()

    # Replace the import line
    content = content.replace(
        "from ..client import MediaWikiClient, MediaWikiConfig",
        "from ..client import MediaWikiClient\nfrom ..config import MediaWikiConfig"
    )

    with open(file_path, 'w') as f:
        f.write(content)

    print(f"Updated {file_path}")

print("All files updated!")
