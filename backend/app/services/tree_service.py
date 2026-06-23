from sqlalchemy.orm import Session
from typing import List, Dict


class TreeService:

    @staticmethod
    def build_tree_structure(files):
        root = {"name": "root", "type": "directory", "children": []}
        
        for file_data in files:
            path_parts = file_data["path"].split("/")
            current_level = root
            
            for i, part in enumerate(path_parts):
                is_last = i == len(path_parts) - 1
                node_type = "file" if is_last else "directory"
                
                if node_type == "directory":
                    existing_child = next(
                        (child for child in current_level["children"] if child["name"] == part),
                        None
                    )
                    if existing_child:
                        current_level = existing_child
                    else:
                        new_child = {"name": part, "type": "directory", "children": []}
                        current_level["children"].append(new_child)
                        current_level = new_child
                else:
                    current_level["children"].append({"name": part, "type": "file"})
        
        return root