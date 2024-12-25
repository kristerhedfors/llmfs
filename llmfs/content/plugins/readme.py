"""README generator that creates filesystem tree documentation."""
from typing import Dict, List
from ...models.filesystem import FileNode
from .base import BaseContentGenerator

class ReadmeGenerator(BaseContentGenerator):
    """Generator that creates README.md with filesystem tree structure."""
    
    def generator_name(self) -> str:
        return "readme"
    
    def _build_tree(self, path: str, structure: Dict[str, FileNode], indent: str = "") -> List[str]:
        """Build a tree representation of the filesystem structure."""
        result = []
        
        # Get all child paths for this directory
        children = structure[path].children or {}
        sorted_names = sorted(children.keys())
        
        for i, name in enumerate(sorted_names):
            child_path = children[name]
            is_last = i == len(sorted_names) - 1
            
            # Choose the appropriate symbols
            prefix = "└── " if is_last else "├── "
            child_indent = indent + ("    " if is_last else "│   ")
            
            # Add this node
            result.append(f"{indent}{prefix}{name}")
            
            # Recursively add children if this is a directory
            child_node = structure[child_path]
            if child_node.type == "directory":
                result.extend(self._build_tree(child_path, structure, child_indent))
            elif child_node.xattrs and "generator" in child_node.xattrs:
                # Add note about auto-generation
                result.append(f"{child_indent}    (Content will be auto-generated by {child_node.xattrs['generator']} plugin)")
        
        return result
    
    def generate(self, path: str, node: FileNode, fs_structure: Dict[str, FileNode]) -> str:
        """Generate a README with filesystem structure visualization."""
        tree_lines = self._build_tree("/", fs_structure)
        tree_str = "\n".join(tree_lines)
        
        return f"""# Project Structure

This directory contains the following structure:

```
{tree_str}
```

Files marked with "(Content will be auto-generated...)" are dynamically generated when read.
Their content is created based on the specified plugin and the current state of the filesystem.
"""