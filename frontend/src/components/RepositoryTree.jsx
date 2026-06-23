import { useState } from "react";
import { Folder, FolderOpen } from "lucide-react";

export function RepositoryTree({ tree, onFileClick, depth = 0 }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const hasChildren = tree.children && tree.children.length > 0;
  
  const handleToggle = () => {
    if (hasChildren) {
      setIsExpanded(!isExpanded);
    }
  };
  
  const handleFileClick = () => {
    if (tree.type === "file" && onFileClick) {
      onFileClick(tree);
    }
  };
  
  return (
    <div style={{ paddingLeft: `${depth * 16}px` }}>
      <div
        className="flex items-center gap-2 py-1 px-2 rounded cursor-pointer hover:bg-gray-100"
        onClick={handleToggle}
      >
        {hasChildren ? (
          isExpanded ? (
            <FolderOpen className="h-4 w-4 text-gray-400" />
          ) : (
            <Folder className="h-4 w-4 text-gray-400" />
          )
        ) : (
          <div className="w-4" />
        )}
        <span
          className={`text-sm ${tree.type === "file" ? "text-gray-700 font-medium" : "text-gray-900"}`}
          onClick={tree.type === "file" ? handleFileClick : undefined}
        >
          {tree.name}
        </span>
      </div>
      {hasChildren && isExpanded && (
        <div>
          {tree.children.map((child, index) => (
            <RepositoryTree
              key={index}
              tree={child}
              onFileClick={onFileClick}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}