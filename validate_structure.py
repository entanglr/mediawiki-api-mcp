#!/usr/bin/env python3
"""Validation script to test the organized MediaWiki MCP server structure."""

import asyncio
import sys

# Test imports
try:
    from mediawiki_api_mcp.server import app
    from mediawiki_api_mcp.tools import get_edit_tools, get_search_tools
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


async def validate_tools():
    """Validate that tools are properly defined."""
    try:
        # Test tool definitions
        edit_tools = get_edit_tools()
        search_tools = get_search_tools()

        assert len(edit_tools) == 2, f"Expected 2 edit tools, got {len(edit_tools)}"
        assert len(search_tools) == 1, f"Expected 1 search tool, got {len(search_tools)}"

        all_tools = edit_tools + search_tools
        tool_names = [tool.name for tool in all_tools]

        expected_tools = ["wiki_edit_page", "wiki_get_page", "wiki_search"]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Missing tool: {expected_tool}"

        # Verify all tools have wiki_ prefix
        for tool in all_tools:
            assert tool.name.startswith("wiki_"), f"Tool {tool.name} missing wiki_ prefix"

        print("✓ Tool definitions valid")

        # Test server integration
        server_tools = await app.list_tools()
        server_tool_names = [tool.name for tool in server_tools]

        for expected_tool in expected_tools:
            assert expected_tool in server_tool_names, f"Missing server tool: {expected_tool}"

        print("✓ Server tool integration valid")

    except Exception as e:
        print(f"✗ Tool validation error: {e}")
        return False

    return True


def validate_structure():
    """Validate the modular structure."""
    try:
        # Test that handlers are properly organized
        import mediawiki_api_mcp.handlers.edit
        import mediawiki_api_mcp.handlers.search
        import mediawiki_api_mcp.tools.edit
        import mediawiki_api_mcp.tools.search

        # Check that handler functions exist
        assert hasattr(mediawiki_api_mcp.handlers.edit, 'handle_edit_page')
        assert hasattr(mediawiki_api_mcp.handlers.edit, 'handle_get_page')
        assert hasattr(mediawiki_api_mcp.handlers.search, 'handle_search')

        # Check that tool functions exist
        assert hasattr(mediawiki_api_mcp.tools.edit, 'get_edit_tools')
        assert hasattr(mediawiki_api_mcp.tools.search, 'get_search_tools')

        print("✓ Modular structure valid")
        return True

    except Exception as e:
        print(f"✗ Structure validation error: {e}")
        return False


async def main():
    """Run all validations."""
    print("Validating MediaWiki MCP Server organized structure...")
    print("=" * 50)

    # Test structure
    structure_valid = validate_structure()

    # Test tools
    tools_valid = await validate_tools()

    print("=" * 50)
    if structure_valid and tools_valid:
        print("✓ All validations passed! The organized structure is working correctly.")
        return 0
    else:
        print("✗ Some validations failed.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
