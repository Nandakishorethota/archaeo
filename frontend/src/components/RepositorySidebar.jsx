import { Link, useLocation } from "react-router-dom";
import { GitBranch, MessageSquare, Code, BookOpen, Lightbulb } from "lucide-react";
import { useRepository } from "../hooks/useRepository";
import { useRepositoryTree } from "../hooks/useRepositoryTree";
import { RepositoryTree } from "./RepositoryTree";
import { cn } from "../lib/utils";

const primaryTabs = [
  { id: "overview", label: "Overview", icon: Code, path: "" },
  { id: "learning-path", label: "Learning Path", icon: BookOpen, path: "learning-path" },
  { id: "next-readings", label: "What to Read Next", icon: Lightbulb, path: "next-readings" },
  { id: "chat", label: "Ask Repository", icon: MessageSquare, path: "chat" },
];

export function RepositorySidebar({ repoId }) {
  const location = useLocation();
  const currentTab = primaryTabs.find(t => location.pathname.endsWith(t.path) || (t.path === "" && location.pathname === `/repository/${repoId}`)) || primaryTabs[0];
  const { data: repo } = useRepository(repoId);
  const { data: tree } = useRepositoryTree(repoId);

  const handleFileClick = (file) => {
    console.log("File clicked:", file);
  };

  return (
    <aside className="w-56 flex-shrink-0 border-r border-gray-100 bg-gray-50/50 h-[calc(100vh-56px)] flex flex-col">
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-gray-400" />
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{repo?.name || "repository"}</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-6">
        <nav className="space-y-0.5">
          {primaryTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentTab.id === tab.id;
            const href = `/repository/${repoId}${tab.path ? `/${tab.path}` : ""}`;

            return (
              <Link
                key={tab.id}
                to={href}
                className={cn(
                  "flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors",
                  isActive
                    ? "bg-gray-900 text-white"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                )}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </Link>
            );
          })}
          </nav>

        <div>
          <p className="px-3 mb-2 text-[10px] font-medium text-gray-400 uppercase tracking-wider">Repository</p>
          <div className="max-h-64 overflow-y-auto">
            {tree && (
              <RepositoryTree
                tree={tree}
                onFileClick={handleFileClick}
                depth={0}
              />
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}

export default RepositorySidebar;
