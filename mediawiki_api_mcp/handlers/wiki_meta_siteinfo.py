"""MediaWiki siteinfo metadata handlers for MCP server."""

import json
import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_meta_siteinfo(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_meta_siteinfo tool calls for getting site information."""

    # Extract siteinfo parameters
    siprop = arguments.get("siprop")
    sifilteriw = arguments.get("sifilteriw")
    sishowalldb = arguments.get("sishowalldb", False)
    sinumberingroup = arguments.get("sinumberingroup", False)
    siinlanguagecode = arguments.get("siinlanguagecode")

    try:
        result = await client.get_siteinfo(
            siprop=siprop,
            sifilteriw=sifilteriw,
            sishowalldb=sishowalldb,
            sinumberingroup=sinumberingroup,
            siinlanguagecode=siinlanguagecode
        )

        if "query" not in result:
            return [types.TextContent(
                type="text",
                text=f"Unexpected response format: {result}"
            )]

        query_data = result["query"]

        # Format the response based on what information was requested
        response_text = "MediaWiki Site Information\n"
        response_text += "=" * 29 + "\n\n"

        # Process each type of information
        for info_type, info_data in query_data.items():
            response_text += format_siteinfo_section(info_type, info_data)
            response_text += "\n"

        return [types.TextContent(
            type="text",
            text=response_text
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error getting site information: {str(e)}"
        )]


def format_siteinfo_section(section_name: str, data: Any) -> str:
    """Format a specific section of site information."""
    output = ""

    if section_name == "general":
        output += "General Information:\n"
        output += "-" * 21 + "\n"

        # Key general information
        key_fields = [
            ("sitename", "Site name"),
            ("mainpage", "Main page"),
            ("base", "Base URL"),
            ("server", "Server"),
            ("wikiid", "Wiki ID"),
            ("generator", "MediaWiki version"),
            ("phpversion", "PHP version"),
            ("dbtype", "Database type"),
            ("dbversion", "Database version"),
            ("lang", "Language"),
            ("fallback", "Language fallback"),
            ("legaltitlechars", "Legal title characters"),
            ("case", "Case sensitivity"),
            ("timezone", "Timezone"),
            ("timeoffset", "Time offset"),
            ("articlepath", "Article path"),
            ("scriptpath", "Script path"),
            ("script", "Script"),
            ("variantarticlepath", "Variant article path"),
            ("favicon", "Favicon"),
            ("logo", "Logo"),
        ]

        for field, label in key_fields:
            if field in data:
                value = data[field]
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, indent=2)
                output += f"  {label}: {value}\n"

        # Rights information
        if "rights" in data:
            output += f"  Rights: {data['rights']}\n"
        if "rightsurl" in data:
            output += f"  Rights URL: {data['rightsurl']}\n"

    elif section_name == "namespaces":
        output += "Namespaces:\n"
        output += "-" * 11 + "\n"

        for ns_id, ns_data in data.items():
            if isinstance(ns_data, dict):
                name = ns_data.get("*", f"Namespace {ns_id}")
                canonical = ns_data.get("canonical", "")
                case = ns_data.get("case", "")

                output += f"  {ns_id}: {name}"
                if canonical and canonical != name:
                    output += f" (canonical: {canonical})"
                if case:
                    output += f" [{case}]"
                output += "\n"

    elif section_name == "namespacealiases":
        output += "Namespace Aliases:\n"
        output += "-" * 18 + "\n"

        for alias in data:
            if isinstance(alias, dict):
                alias_name = alias.get("*", "")
                ns_id = alias.get("id", "")
                output += f"  {alias_name} -> Namespace {ns_id}\n"

    elif section_name == "statistics":
        output += "Site Statistics:\n"
        output += "-" * 16 + "\n"

        stats_fields = [
            ("pages", "Total pages"),
            ("articles", "Content pages"),
            ("edits", "Total edits"),
            ("images", "Uploaded files"),
            ("users", "Registered users"),
            ("activeusers", "Active users"),
            ("admins", "Administrators"),
            ("jobs", "Job queue length"),
        ]

        for field, label in stats_fields:
            if field in data:
                output += f"  {label}: {data[field]:,}\n"

    elif section_name == "usergroups":
        output += "User Groups:\n"
        output += "-" * 12 + "\n"

        for group in data:
            if isinstance(group, dict):
                name = group.get("name", "")
                rights = group.get("rights", [])
                output += f"  {name}:\n"
                if rights:
                    output += f"    Rights: {', '.join(rights[:5])}"
                    if len(rights) > 5:
                        output += f" (and {len(rights) - 5} more)"
                    output += "\n"

    elif section_name == "extensions":
        output += "Extensions:\n"
        output += "-" * 11 + "\n"

        for ext in data:
            if isinstance(ext, dict):
                name = ext.get("name", "")
                version = ext.get("version", "")
                output += f"  {name}"
                if version:
                    output += f" (v{version})"
                output += "\n"

    elif section_name == "skins":
        output += "Skins:\n"
        output += "-" * 6 + "\n"

        for skin_key, skin_data in data.items():
            if isinstance(skin_data, dict):
                name = skin_data.get("*", skin_key)
                output += f"  {name}\n"

    elif section_name == "languages":
        output += "Supported Languages:\n"
        output += "-" * 20 + "\n"

        for lang_code, lang_name in data.items():
            if isinstance(lang_name, str):
                output += f"  {lang_code}: {lang_name}\n"

    elif section_name == "interwikimap":
        output += "Interwiki Map:\n"
        output += "-" * 14 + "\n"

        for iw in data:
            if isinstance(iw, dict):
                prefix = iw.get("prefix", "")
                url = iw.get("url", "")
                local = " (local)" if iw.get("local") else ""
                output += f"  {prefix}: {url}{local}\n"

    elif section_name == "dbrepllag":
        output += "Database Replication Lag:\n"
        output += "-" * 26 + "\n"

        for db in data:
            if isinstance(db, dict):
                host = db.get("host", "")
                lag = db.get("lag", "")
                output += f"  {host}: {lag} seconds\n"

    elif section_name == "fileextensions":
        output += "Allowed File Extensions:\n"
        output += "-" * 25 + "\n"

        extensions = [ext.get("ext", "") for ext in data if isinstance(ext, dict)]
        # Group extensions for better readability
        for i in range(0, len(extensions), 10):
            group = extensions[i:i+10]
            output += f"  {', '.join(group)}\n"

    else:
        # Generic formatting for other sections
        section_title = section_name.replace("_", " ").title()
        output += f"{section_title}:\n"
        output += "-" * len(section_title) + "\n"

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, indent=2)
                output += f"  {key}: {value}\n"
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # Try to find a meaningful field to display
                    display_value = (
                        item.get("name") or
                        item.get("*") or
                        item.get("title") or
                        str(item)
                    )
                    output += f"  {display_value}\n"
                else:
                    output += f"  {item}\n"
        else:
            output += f"  {data}\n"

    return output
