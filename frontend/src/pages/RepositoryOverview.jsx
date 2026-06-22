import { useParams, useNavigate } from "react-router-dom";
import { BookOpen, Code, Database, FileText, Rocket, Layers, GitBranch, ChevronRight, ChevronDown, Server, Monitor, Settings, Brain, Clock, Gauge, ArrowRight, Lightbulb, Target, MessageSquare } from "lucide-react";
import { useState } from "react";
import { useRepositorySummary, useArchitectureTree } from "../hooks/useRepository";
import { AskAiSection } from "../components/AskAiSection"; // Add this import

function SummarySkeleton() {
  return (
    <div className="space-y-10 animate-pulse">
      <div className="space-y-4">
        <div className="h-7 w-56 bg-gray-100 rounded" />
        <div className="h-4 w-full bg-gray-100 rounded" />
        <div className="h-4 w-2/3 bg-gray-100 rounded" />
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="h-32 bg-gray-50 border border-gray-100 rounded" />
        <div className="h-32 bg-gray-50 border border-gray-100 rounded" />
      </div>
      <div className="h-48 bg-gray-50 border border-gray-100 rounded" />
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-24">
      <Database className="h-12 w-12 text-gray-200 mx-auto mb-4" />
      <h3 className="text-base font-medium text-gray-900 mb-1">No Summary Available</h3>
      <p className="text-sm text-gray-500">Import a repository to see its summary</p>
    </div>
  );
}

function ErrorState() {
  return (
    <div className="text-center py-24">
      <Database className="h-12 w-12 text-red-200 mx-auto mb-4" />
      <h3 className="text-base font-medium text-gray-900 mb-1">Failed to Load Summary</h3>
      <p className="text-sm text-gray-500">Something went wrong while loading the repository summary</p>
    </div>
  );
}

function getFileTypeLabel(path) {
  const lower = path.toLowerCase();
  if (lower.includes("readme") || lower.includes("docs")) return "Docs";
  if (lower.includes("test") || lower.includes("spec")) return "Test";
  if (lower.includes("config") || lower.includes("setup") || lower.includes("pyproject") || lower.includes("package")) return "Config";
  if (lower.endsWith(".py")) return "Python";
  if (lower.endsWith(".js") || lower.endsWith(".jsx")) return "JS";
  if (lower.endsWith(".ts") || lower.endsWith(".tsx")) return "TS";
  if (lower.endsWith(".md")) return "Markdown";
  if (lower.endsWith(".yml") || lower.endsWith(".yaml")) return "YAML";
  if (lower.endsWith(".toml")) return "TOML";
  return "File";
}

function getImportanceColor(importance) {
  switch (importance) {
    case "High": return "text-gray-900 bg-gray-100";
    case "Medium": return "text-gray-600 bg-gray-50";
    default: return "text-gray-400 bg-gray-50";
  }
}

function AiInsightBanner({ insight }) {
  if (!insight) return null;

  return (
    <div className="border border-gray-100 p-5 space-y-4">
      <div className="flex items-center gap-2">
        <Brain className="h-4 w-4 text-gray-400" />
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">AI Insight</h3>
      </div>
      <p className="text-sm text-gray-600 leading-relaxed">{insight.text}</p>
      <div className="grid grid-cols-3 gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5">
            <ArrowRight className="h-3 w-3 text-gray-400" />
            <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">Main Flow</p>
          </div>
          <p className="text-xs text-gray-700">{insight.main_flow}</p>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-1.5">
            <Clock className="h-3 w-3 text-gray-400" />
            <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">Onboarding</p>
          </div>
          <p className="text-xs text-gray-700">{insight.estimated_onboarding}</p>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-1.5">
            <Gauge className="h-3 w-3 text-gray-400" />
            <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">Complexity</p>
          </div>
          <p className="text-xs text-gray-700">{insight.complexity}</p>
        </div>
      </div>
    </div>
  );
}

function RecommendedStartFiles({ startingFiles, fileContext }) {
  if (!startingFiles || startingFiles.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Target className="h-4 w-4 text-gray-400" />
        <h4 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">Start Here</h4>
      </div>
      <div className="space-y-2">
        {startingFiles.slice(0, 5).map((file, i) => {
          const ctx = fileContext?.[file.path];
          return (
            <div key={i} className="flex items-center gap-4 p-3 bg-gray-50 border border-gray-100">
              <div className="w-7 h-7 bg-white border border-gray-200 flex items-center justify-center flex-shrink-0">
                <FileText className="h-3.5 w-3.5 text-gray-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-900 font-mono truncate">{file.path}</p>
                <p className="text-[10px] text-gray-500 mt-0.5">{file.reason}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                {ctx && (
                  <>
                    <span className="text-[9px] text-gray-400">{ctx.file_type}</span>
                    <span className={`text-[9px] px-1.5 py-0.5 ${getImportanceColor(ctx.importance)}`}>
                      {ctx.importance}
                    </span>
                  </>
                )}
                <span className="text-[10px] text-gray-500 bg-white border border-gray-200 px-2 py-0.5">
                  {i === 0 ? "Start here" : `Step ${i + 1}`}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ArchitectureSection({ archTree, summary }) {
  const [expanded, setExpanded] = useState({
    entry_points: true,
    frontend: true,
    backend: true,
  });

  const toggleExpand = (key) => {
    setExpanded(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const categories = [];
  const fileContext = archTree?.file_context || {};

  if (archTree) {
    if (archTree.entry_points?.length > 0) {
      categories.push({ key: "entry_points", label: "Entry Points", icon: Rocket, files: archTree.entry_points, description: "Application entry points" });
    }
    if (archTree.frontend?.length > 0) {
      categories.push({ key: "frontend", label: "Frontend", icon: Monitor, files: archTree.frontend, description: "Client-side code" });
    }
    if (archTree.backend?.length > 0) {
      categories.push({ key: "backend", label: "Backend", icon: Server, files: archTree.backend, description: "Server-side code" });
    }
    if (archTree.infrastructure?.length > 0) {
      categories.push({ key: "infrastructure", label: "Infrastructure", icon: Settings, files: archTree.infrastructure, description: "Deployment and config" });
    }
    if (archTree.documentation?.length > 0) {
      categories.push({ key: "documentation", label: "Documentation", icon: BookOpen, files: archTree.documentation, description: "Guides and references" });
    }
    if (archTree.configuration?.length > 0) {
      categories.push({ key: "configuration", label: "Configuration", icon: Database, files: archTree.configuration, description: "Project config files" });
    }
    if (archTree.tests?.length > 0) {
      categories.push({ key: "tests", label: "Tests", icon: FileText, files: archTree.tests, description: "Test files" });
    }
  } else if (summary?.architecture) {
    if (summary.architecture.entry_points?.length > 0) {
      categories.push({ key: "entry_points", label: "Entry Points", icon: Rocket, files: summary.architecture.entry_points, description: "Application entry points" });
    }
    if (summary.architecture.config_files?.length > 0) {
      categories.push({ key: "config_files", label: "Configuration", icon: Database, files: summary.architecture.config_files, description: "Project config files" });
    }
    if (summary.architecture.documentation?.length > 0) {
      categories.push({ key: "documentation", label: "Documentation", icon: BookOpen, files: summary.architecture.documentation, description: "Guides and references" });
    }
    if (summary.architecture.tests?.length > 0) {
      categories.push({ key: "tests", label: "Tests", icon: FileText, files: summary.architecture.tests, description: "Test files" });
    }
  }

  if (categories.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-sm text-gray-400">No architecture data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {categories.map(({ key, label, icon: Icon, files, description }) => {
        const isExpanded = expanded[key] !== false;

        return (
          <div key={key} className="border border-gray-100 overflow-hidden">
            <button
              onClick={() => toggleExpand(key)}
              className="w-full flex items-center gap-3 p-4 hover:bg-gray-50 transition-colors text-left"
            >
              <Icon className="h-4 w-4 text-gray-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{label}</p>
                <p className="text-[11px] text-gray-500 mt-0.5">{description}</p>
              </div>
              <span className="text-[11px] text-gray-400 bg-gray-100 px-2 py-0.5 rounded">
                {files.length}
              </span>
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-gray-400" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-400" />
              )}
            </button>
            {isExpanded && (
              <div className="border-t border-gray-50">
                {files.slice(0, 10).map((file, i) => {
                  const ctx = fileContext[file];
                  return (
                    <div key={i} className="flex items-center gap-3 px-4 py-3 pl-12 border-b border-gray-50 last:border-0">
                      <FileText className="h-3.5 w-3.5 text-gray-300 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <span className="text-xs text-gray-700 font-mono truncate block">{file}</span>
                        {ctx && (
                          <p className="text-[10px] text-gray-400 mt-0.5">{ctx.purpose}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        {ctx && (
                          <>
                            <span className="text-[9px] text-gray-400">{ctx.file_type}</span>
                            <span className={`text-[9px] px-1.5 py-0.5 ${getImportanceColor(ctx.importance)}`}>
                              {ctx.importance}
                            </span>
                          </>
                        )}
                        {!ctx && (
                          <span className="text-[10px] text-gray-400">{getFileTypeLabel(file)}</span>
                        )}
                      </div>
                    </div>
                  );
                })}
                {files.length > 10 && (
                  <div className="px-4 py-2 pl-12">
                    <p className="text-[10px] text-gray-400">+ {files.length - 10} more files</p>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function LearningPathSection({ learningPath }) {
  if (!learningPath || learningPath.length === 0) return null;

  return (
    <div className="space-y-4">
      <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">Learning Path</h3>
      <div className="relative">
        <div className="absolute left-5 top-0 bottom-0 w-px bg-gray-100 hidden md:block" />
        <div className="space-y-6">
          {learningPath.map((step, i) => (
            <div key={i} className="relative flex items-start gap-5">
              <div className="w-10 h-10 rounded-full bg-gray-900 text-white flex items-center justify-center flex-shrink-0 z-10 text-sm font-medium">
                {step.step}
              </div>
              <div className="flex-1 space-y-2">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">{step.title}</h4>
                  <p className="text-xs text-gray-500 mt-0.5">{step.description}</p>
                </div>
                {step.file && (
                  <div className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-100">
                    <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-900 font-mono truncate">{step.file}</p>
                    </div>
                    <span className="text-[10px] text-gray-400 flex-shrink-0">{step.file_type}</span>
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

function QuestionsToAskSection({ questions, onAskQuestion }) {
  const navigate = useNavigate();
  const { id } = useParams();

  if (!questions || questions.length === 0) return null;

  const handleAsk = (question) => {
    navigate(`/repository/${id}/chat`, { state: { initialQuestion: question } });
  };

  return (
    <div className="space-y-4">
      <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">Questions to Ask</h3>
      <div className="space-y-2">
        {questions.map((q, i) => (
          <button
            key={i}
            onClick={() => handleAsk(q.question)}
            className="w-full flex items-center gap-3 p-3 bg-gray-50 border border-gray-100 rounded-lg text-left hover:border-gray-300 transition-colors group"
          >
            <MessageSquare className="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <span className="text-xs text-gray-600 group-hover:text-gray-900 transition-colors">{q.question}</span>
            </div>
            <span className="text-[9px] text-gray-400 bg-white border border-gray-200 px-1.5 py-0.5 flex-shrink-0">{q.category}</span>
            <ChevronRight className="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 transition-colors flex-shrink-0" />
          </button>
        ))}
      </div>
    </div>
  );
}

export function OverviewPanel() {
  const { id } = useParams();
  const { data: summary, isLoading, error } = useRepositorySummary(id);
  const { data: archTree } = useArchitectureTree(id);

  if (isLoading) return <SummarySkeleton />;
  if (error) return <ErrorState />;
  if (!summary) return <EmptyState />;

  return (
    <div className="space-y-12">
      <div className="space-y-4">
        <h1 className="text-2xl font-serif text-gray-900">Repository Summary</h1>
        <p className="text-[15px] text-gray-600 leading-relaxed max-w-2xl">{summary.purpose}</p>
      </div>

      {summary.ai_insight && (
        <AiInsightBanner insight={summary.ai_insight} />
      )}

      <div className="grid gap-10 md:grid-cols-2">
        <div className="space-y-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">Tech Stack</h3>
          <div className="flex flex-wrap gap-2">
            {summary.tech_stack?.length > 0 ? (
              summary.tech_stack.map((tech, i) => (
                <span key={i} className="text-xs text-gray-700 bg-gray-100 px-3 py-1.5 rounded">
                  {tech}
                </span>
              ))
            ) : (
              <p className="text-sm text-gray-400">No tech stack detected</p>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">Frameworks</h3>
          <div className="flex flex-wrap gap-2">
            {summary.frameworks?.length > 0 ? (
              summary.frameworks.map((fw, i) => (
                <span key={i} className="text-xs text-gray-700 bg-gray-100 px-3 py-1.5 rounded">
                  {fw}
                </span>
              ))
            ) : (
              <p className="text-sm text-gray-400">No frameworks detected</p>
            )}
          </div>
        </div>
      </div>

      {summary.starting_files?.length > 0 && (
        <RecommendedStartFiles startingFiles={summary.starting_files} fileContext={archTree?.file_context} />
      )}

      <div className="space-y-4">
        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">Architecture</h3>
        <ArchitectureSection archTree={archTree} summary={summary} />
      </div>

      {summary.learning_path?.length > 0 && (
        <LearningPathSection learningPath={summary.learning_path} />
      )}

      {summary.questions_to_ask?.length > 0 && (
        <QuestionsToAskSection questions={summary.questions_to_ask} />
      )}

      {summary.stats && (
        <div className="space-y-4">
          <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider">Repository Stats</h3>
          <div className="grid grid-cols-3 gap-8">
            <div>
              <p className="text-4xl font-serif text-gray-900">{summary.stats.total_commits || 0}</p>
              <p className="text-xs text-gray-500 mt-1">Commits</p>
            </div>
            <div>
              <p className="text-4xl font-serif text-gray-900">{summary.stats.contributors || 0}</p>
              <p className="text-xs text-gray-500 mt-1">Contributors</p>
            </div>
            <div>
              <p className="text-4xl font-serif text-gray-900">{summary.stats.total_files || 0}</p>
              <p className="text-xs text-gray-500 mt-1">Files</p>
            </div>
          </div>
        </div>
      )}

      <AskAiSection repoId={id} />
    </div>
  );
}
