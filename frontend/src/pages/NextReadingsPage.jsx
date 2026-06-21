import { useParams } from "react-router-dom";
import { ChevronRight, FileText, Code, Database, BookOpen, MessageSquare, Brain } from "lucide-react";
import { useRepository, useArchitecture } from "../hooks/useRepository";

export function NextReadingsPage() {
  const { id } = useParams();
  const { data: repo, isLoading: repoLoading } = useRepository(id);
  const { data: arch, isLoading: archLoading } = useArchitecture(id);

  const loading = repoLoading || archLoading;

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-36 bg-gray-50 border border-gray-100" />
        ))}
      </div>
    );
  }

  if (!repo || !arch) {
    return (
      <div className="text-center py-24">
        <Brain className="h-12 w-12 text-gray-200 mx-auto mb-4" />
        <h3 className="text-base font-medium text-gray-900 mb-1">Reading List Not Available</h3>
        <p className="text-sm text-gray-500">Repository data not found</p>
      </div>
    );
  }

  const readingSteps = [
    { step: 1, title: "Start Here — Entry Points", description: "These files show where the application begins execution.", files: arch?.entry_points?.slice(0, 3) || [], icon: Code },
    { step: 2, title: "Configuration & Setup", description: "Configuration files reveal dependencies, build process, and project structure.", files: arch?.config_files?.slice(0, 3) || [], icon: Database },
    { step: 3, title: "Documentation & Guides", description: "Documentation provides context, usage instructions, and architectural decisions.", files: arch?.documentation?.slice(0, 3) || [], icon: BookOpen },
    { step: 4, title: "Tests — How It Works", description: "Tests show expected behavior and are often the best documentation.", files: arch?.tests?.slice(0, 3) || [], icon: MessageSquare },
  ];

  const getFileType = (file) => {
    const lower = file.toLowerCase();
    if (lower.includes("main") || lower.includes("app") || lower.includes("index")) return "Entry point";
    if (lower.includes("readme")) return "Documentation";
    if (lower.includes("config") || lower.includes("setup")) return "Configuration";
    if (lower.includes("pyproject") || lower.includes("package")) return "Dependencies";
    if (lower.includes("test")) return "Tests";
    return "Source code";
  };

  return (
    <div className="space-y-10">
      <div className="space-y-3">
        <h1 className="text-2xl font-serif text-gray-900">What Should I Read Next?</h1>
        <p className="text-sm text-gray-500 max-w-xl">Follow this guided reading sequence to understand {repo.name} in the most efficient order.</p>
      </div>

      <div className="space-y-4">
        {readingSteps.map((step, stepIndex) => (
          <div key={stepIndex} className="border border-gray-100 p-6 space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-gray-400">{String(step.step).padStart(2, "0")}</span>
              <h2 className="text-base font-medium text-gray-900">{step.title}</h2>
            </div>
            <p className="text-sm text-gray-500">{step.description}</p>
            <div className="space-y-2">
              {step.files.length > 0 ? (
                step.files.map((file, fileIndex) => (
                  <div key={fileIndex} className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-100 group">
                    <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 font-mono truncate">{file}</p>
                      <p className="text-[11px] text-gray-500 mt-0.5">{getFileType(file)}</p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-300 flex-shrink-0 group-hover:text-gray-600 transition-colors" />
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-400 italic">No files detected</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
