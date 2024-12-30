"""Tests for the PromptPlugin."""
import pytest
import logging
import os
from unittest.mock import patch, mock_open
from llmfs.content.plugins.prompt import PromptPlugin
from llmfs.models.filesystem import FileNode
from llmfs.config.settings import get_global_prompt, _read_template

def create_file_node(content=None):
    """Helper to create a FileNode instance"""
    return FileNode(
        type="file",
        content=content,
        attrs={"st_mode": "33188"},  # 644 permissions
        xattrs={}
    )

def test_prompt_plugin_handles_prompt_files(caplog):
    """Test that prompt plugin correctly handles prompt files with logging"""
    plugin = PromptPlugin()
    caplog.set_level(logging.DEBUG)
    
    # Mock the template read to return a known value
    template_content = "Default template content for testing"
    with patch('llmfs.config.settings._read_template', return_value=template_content):
        # Test with raw text
        test_prompt = "Generate {path} as a Python script"
        node = create_file_node(content=test_prompt)
        content = plugin.generate("/.llmfs.prompt", node, {})
        assert content.strip() == test_prompt
        assert "Using raw prompt input" in caplog.text
        
        # Test with JSON
        test_prompt = "Create {path} with these rules"
        node = create_file_node(content=f'{{"prompt": "{test_prompt}"}}')
        content = plugin.generate("/.llmfs.prompt", node, {})
        assert content.strip() == test_prompt
        assert "Parsed prompt from JSON" in caplog.text
        
        # Test default
        node = create_file_node()
        content = plugin.generate("/.llmfs.prompt", node, {})
        assert content.strip() == template_content
        assert "Using default prompt template" in caplog.text

def test_nearest_prompt_lookup():
    """Test that prompt plugin correctly uses nearest prompt file with proper precedence"""
    plugin = PromptPlugin()
    
    # Mock the template read to return a known value
    template_content = "Default template content for testing"
    with patch('llmfs.config.settings._read_template', return_value=template_content):
        # Create filesystem structure with multiple prompt files
        fs_structure = {
            "/project/.llmfs.prompt": create_file_node(
                content='{"prompt": "Project llmfs prompt"}'
            ),
            "/project/.prompt": create_file_node(
                content='{"prompt": "Project prompt"}'
            ),
            "/project/subdir/.llmfs.prompt": create_file_node(
                content='{"prompt": "Subdir llmfs prompt"}'
            ),
            "/project/subdir/.prompt": create_file_node(
                content='{"prompt": "Subdir prompt"}'
            ),
            "/project/subdir/file.py": create_file_node(),
            "/project/other/file.txt": create_file_node(),
            "/project/other/.prompt": create_file_node(
                content='{"prompt": "Other prompt"}'
            ),
        }
        
        # Test subdir file uses nearest .llmfs.prompt
        content = plugin.generate(
            "/project/subdir/file.py", 
            fs_structure["/project/subdir/file.py"],
            fs_structure
        )
        assert content.strip() == "Subdir llmfs prompt"
        
        # Test other file uses .prompt when no .llmfs.prompt exists
        content = plugin.generate(
            "/project/other/file.txt",
            fs_structure["/project/other/file.txt"],
            fs_structure
        )
        assert content.strip() == "Other prompt"
        
        # Test local .prompt is used when no .llmfs.prompt exists at same level
        fs_structure_2 = {
            "/project/.llmfs.prompt": create_file_node(
                content='{"prompt": "Project llmfs prompt"}'
            ),
            "/project/subdir/.prompt": create_file_node(
                content='{"prompt": "Subdir prompt"}'
            ),
            "/project/subdir/file.py": create_file_node(),
        }
        content = plugin.generate(
            "/project/subdir/file.py",
            fs_structure_2["/project/subdir/file.py"],
            fs_structure_2
        )
        assert content.strip() == "Subdir prompt"  # Should use local .prompt since no .llmfs.prompt at same level
        
        # Test prompt file doesn't reference itself
        content = plugin.generate(
            "/project/subdir/.llmfs.prompt",
            fs_structure["/project/subdir/.llmfs.prompt"],
            fs_structure
        )
        assert content.strip() == "Subdir llmfs prompt"
        

def test_prompt_format_variables():
    """Test that prompt templates preserve format variables"""
    plugin = PromptPlugin()
    
    # Mock the template read to return a known value
    template_content = "Default template content for testing"
    with patch('llmfs.config.settings._read_template', return_value=template_content):
        # Test path variable preservation
        test_prompt = "Generate {path} with specific requirements"
        node = create_file_node(content=test_prompt)
        content = plugin.generate("/.llmfs.prompt", node, {})
        assert content.strip() == test_prompt
        assert "{path}" in content
        
        # Test filesystem structure variable preservation
        test_prompt = "Structure: {json.dumps({p: n.model_dump() for p, n in fs_structure.items()}, indent=2)}"
        node = create_file_node(content=test_prompt)
        content = plugin.generate("/.llmfs.prompt", node, {})
        assert content.strip() == test_prompt
        assert "{json.dumps" in content
        assert "fs_structure" in content
