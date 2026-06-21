import { useParams } from "react-router-dom";
import { BookOpen, FileText, Code, Database, MessageSquare, Brain, Target, Lightbulb } from "lucide-react";
import { useRepository, useArchitecture } from "../hooks/useRepository";

export function LearningPathPage() {
  const { id } = useParams();
  const { data: repo, isLoading: repoLoading } = useRepository(id);
  const { data: arch, isLoading: archLoading } = useArchitecture(id);

  const loading = repoLoading || archLoading;

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-start gap-5">
            <div className="w-10 h-10 rounded-full bg-gray-100" />
            <div className="flex-1 space-y-3">
              <div className="h-5 w-56 bg-gray-100 rounded" />
              <div className="h-4 w-full bg-gray-100 rounded" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!repo || !arch) {
    return (
      <div className="text-center py-24">
        <Brain className="h-12 w-12 text-gray-200 mx-auto mb-4" />
        <h3 className="text-base font-medium text-gray-900 mb-1">Learning Path Not Available</h3>
        <p className="text-sm text-gray-500">Repository data not found</p>
      </div>
    );
  }

  const learningSteps = [
    {
      step: 1,
      title: "Understand the Purpose",
      description: "Read the project description and understand what this codebase is supposed to do.",
      icon: Target,
      content: (
        <div className="p-5 bg-gray-50 border border-gray-100">
          <p className="text-sm text-gray-700 mb-4">{repo.description || "No description available"}</p>
          <div className="flex flex-wrap gap-2">
            {repo.language && <span className="text-xs text-gray-600 bg-white border border-gray-200 px-3 py-1">{repo.language}</span>}
            <span className="text-xs text-gray-600 bg-white border border-gray-200 px-3 py-1">{Number(repo?.commit_count || 0).toLocaleString()} commits</span>
            <span className="text-xs text-gray-600 bg-white border border-gray-200 px-3 py-1">{Number(repo?.file_count || 0)} files</span>
          </div>
        </div>
      ),
    },
    {
      step: 2,
      title: "Read the Entry Points",
      description: "Entry points show where the application starts. Understanding the entry point gives you the big picture.",
      icon: Code,
      files: arch?.entry_points?.slice(0, 3) || [],
    },
    {
      step: 3,
      title: "Review Configuration",
      description: "Configuration files reveal dependencies, build process, and project structure.",
      icon: Database,
      files: arch?.config_files?.slice(0, 3) || [],
    },
    {
      step: 4,
      title: "Scan Documentation",
      description: "Documentation provides context, usage instructions, and architectural decisions.",
      icon: BookOpen,
      files: arch?.documentation?.slice(0, 3) || [],
    },
    {
      step: 5,
      title: "Ask Smart Questions",
      description: "Now that you have context, ask specific questions to fill in the gaps.",
      icon: Lightbulb,
      questions: [
        "How does this application handle [specific feature]?",
        "What is the main data flow in this codebase?",
        "Where are the critical business logic components?",
        "How do different modules communicate with each other?",
      ],
    },
  ];

  const getFileLabel = (file) => {
    const lower = file.toLowerCase();
    if (lower.includes("main") || lower.includes("app") || lower.includes("index")) return "Entry point";
    if (lower.includes("readme")) return "Documentation";
    if (lower.includes("config") || lower.includes("pyproject") || lower.includes("package")) return "Configuration";
    return "Source code";
  };

  return (
    <div className="space-y-10">
      <div className="space-y-3">
        <h1 className="text-2xl font-serif text-gray-900">AI Learning Path</h1>
        <p className="text-sm text-gray-500 max-w-xl">Follow this guided journey to understand {repo.name} in under 10 minutes.</p>
      </div>

      <div className="relative">
        <div className="absolute left-5 top-0 bottom-0 w-px bg-gray-100 hidden md:block" />

        <div className="space-y-8">
          {learningSteps.map((step, stepIndex) => (
            <div key={stepIndex} className="relative flex items-start gap-5">
              <div className="w-10 h-10 rounded-full bg-gray-900 text-white flex items-center justify-center flex-shrink-0 z-10 text-sm font-medium">
                {step.step}
              </div>
              <div className="flex-1 space-y-3">
                <div>
                  <h2 className="text-base font-medium text-gray-900">{step.title}</h2>
                  <p className="text-sm text-gray-500 mt-1">{step.description}</p>
                </div>

                {step.content && step.content}

                {step.files && step.files.length > 0 && (
                  <div className="space-y-2">
                    {step.files.map((file, fileIndex) => (
                      <div key={fileIndex} className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-100">
                        <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-900 font-mono truncate">{file}</p>
                        </div>
                        <span className="text-[11px] text-gray-400">{getFileLabel(file)}</span>
                      </div>
                    ))}
                  </div>
                )}

                {step.files && step.files.length === 0 && (
                  <p className="text-sm text-gray-400 italic">No files detected</p>
                )}

                {step.questions && (
                  <div className="space-y-2">
                    {step.questions.map((q, qIndex) => (
                      <div key={qIndex} className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-100">
                        <MessageSquare className="h-4 w-4 text-gray-400 flex-shrink-0" />
                        <p className="text-sm text-gray-600">{q}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
