"""Test suite for MediaWiki MCP tool definitions."""

import pytest
from mediawiki_api_mcp.tools.wiki_page_edit import get_edit_tools
from mediawiki_api_mcp.tools.wiki_search import get_search_tools


class TestToolDefinitions:
    """Test cases for MCP tool definitions."""

    def test_get_edit_tools(self):
        """Test that edit tools are properly defined."""
        tools = get_edit_tools()

        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "wiki_page_edit" in tool_names
        assert "wiki_page_get" in tool_names

    def test_wiki_edit_page_tool_definition(self):
        """Test wiki_page_edit tool definition."""
        tools = get_edit_tools()
        edit_tool = next(tool for tool in tools if tool.name == "wiki_page_edit")

        assert edit_tool.name == "wiki_page_edit"
        assert edit_tool.description == "Edit or create a MediaWiki page"
        assert edit_tool.inputSchema["type"] == "object"

        # Check required properties exist
        properties = edit_tool.inputSchema["properties"]
        assert "title" in properties
        assert "pageid" in properties
        assert "text" in properties
        assert "summary" in properties
        assert "bot" in properties

        # Check property types
        assert properties["title"]["type"] == "string"
        assert properties["pageid"]["type"] == "integer"
        assert properties["bot"]["type"] == "boolean"
        assert properties["bot"]["default"] is True

    def test_wiki_get_page_tool_definition(self):
        """Test wiki_page_get tool definition."""
        tools = get_edit_tools()
        get_tool = next(tool for tool in tools if tool.name == "wiki_page_get")

        assert get_tool.name == "wiki_page_get"
        assert get_tool.description == "Get information and content of a MediaWiki page"
        assert get_tool.inputSchema["type"] == "object"

        # Check properties
        properties = get_tool.inputSchema["properties"]
        assert "title" in properties
        assert "pageid" in properties
        assert properties["title"]["type"] == "string"
        assert properties["pageid"]["type"] == "integer"

    def test_get_search_tools(self):
        """Test that search tools are properly defined."""
        tools = get_search_tools()

        assert len(tools) == 1
        assert tools[0].name == "wiki_search"

    def test_wiki_search_tool_definition(self):
        """Test wiki_search tool definition."""
        tools = get_search_tools()
        search_tool = tools[0]

        assert search_tool.name == "wiki_search"
        assert search_tool.description == "Search for wiki pages by title or content using MediaWiki's search API"
        assert search_tool.inputSchema["type"] == "object"

        # Check required field
        assert search_tool.inputSchema["required"] == ["query"]

        # Check properties
        properties = search_tool.inputSchema["properties"]
        assert "query" in properties
        assert "namespaces" in properties
        assert "limit" in properties
        assert "offset" in properties
        assert "what" in properties
        assert "sort" in properties

        # Check property types and constraints
        assert properties["query"]["type"] == "string"
        assert properties["namespaces"]["type"] == "array"
        assert properties["limit"]["type"] == "integer"
        assert properties["limit"]["minimum"] == 1
        assert properties["limit"]["maximum"] == 500
        assert properties["limit"]["default"] == 10

        # Check enum values
        assert "text" in properties["what"]["enum"]
        assert "title" in properties["what"]["enum"]
        assert "nearmatch" in properties["what"]["enum"]

        # Check sort options
        sort_options = properties["sort"]["enum"]
        assert "relevance" in sort_options
        assert "create_timestamp_asc" in sort_options
        assert "last_edit_desc" in sort_options

    def test_tool_schema_validation(self):
        """Test that all tool schemas are valid."""
        edit_tools = get_edit_tools()
        search_tools = get_search_tools()
        all_tools = edit_tools + search_tools

        for tool in all_tools:
            # Check that tool has required attributes
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')

            # Check that schema has required structure
            schema = tool.inputSchema
            assert schema["type"] == "object"
            assert "properties" in schema

            # Check that all properties have types
            for prop_name, prop_def in schema["properties"].items():
                assert "type" in prop_def or "enum" in prop_def
                assert "description" in prop_def

    def test_tool_names_have_wiki_prefix(self):
        """Test that all tool names have the 'wiki_' prefix."""
        edit_tools = get_edit_tools()
        search_tools = get_search_tools()
        all_tools = edit_tools + search_tools

        for tool in all_tools:
            assert tool.name.startswith("wiki_"), f"Tool {tool.name} does not have 'wiki_' prefix"

    def test_no_duplicate_tool_names(self):
        """Test that there are no duplicate tool names."""
        edit_tools = get_edit_tools()
        search_tools = get_search_tools()
        all_tools = edit_tools + search_tools

        tool_names = [tool.name for tool in all_tools]
        assert len(tool_names) == len(set(tool_names)), "Duplicate tool names found"
