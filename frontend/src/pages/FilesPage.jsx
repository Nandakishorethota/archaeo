import { useParams } from "react-router-dom";
import { FileText, Folder, FolderOpen, Brain } from "lucide-react";
import { useFileTree } from "../hooks/useRepository";

function FileTreeItem({ item, depth = 0 }) {
  const isDir = item.type === "directory";

  return (
    <div>
      <div
        className="flex items-center gap-2.5 py-2 px-3 hover:bg-gray-50 transition-colors"
        style={{ paddingLeft: `${depth * 16 + 12}px` }}
      >
        {isDir ? (
          <FolderOpen className="h-4 w-4 text-gray-400 flex-shrink-0" />
        ) : (
          <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
        )}
        <span className="text-sm text-gray-700 truncate">{item.name}</span>
        {isDir && item.children && (
          <span className="text-[11px] text-gray-400 ml-auto">{item.children.length} items</span>
        )}
      </div>
      {isDir && item.children && (
        <div>
          {item.children.map((child, index) => (
            <FileTreeItem key={index} item={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export function FilesPage() {
  const { id } = useParams();
  const { data: fileTree, isLoading, error } = useFileTree(id);

  if (isLoading) {
    return (
      <div className="space-y-2 animate-pulse">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center gap-2 p-2">
            <div className="w-4 h-4 bg-gray-100 rounded" />
            <div className="h-4 w-48 bg-gray-100 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-24">
        <Brain className="h-12 w-12 text-gray-200 mx-auto mb-4" />
        <h3 className="text-base font-medium text-gray-900 mb-1">Error Loading Files</h3>
        <p className="text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }

  if (!fileTree || fileTree.length === 0) {
    return (
      <div className="text-center py-24">
        <FileText className="h-12 w-12 text-gray-200 mx-auto mb-4" />
        <h3 className="text-base font-medium text-gray-900 mb-1">No Files Found</h3>
        <p className="text-sm text-gray-500">This repository appears to be empty</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-serif text-gray-900">Files</h1>
        <p className="text-sm text-gray-500">Browse the repository file structure</p>
      </div>

      <div className="border border-gray-100">
        <div className="divide-y divide-gray-50">
          {fileTree.map((item, index) => (
            <FileTreeItem key={index} item={item} />
          ))}
        </div>
      </div>
    </div>
  );
}
