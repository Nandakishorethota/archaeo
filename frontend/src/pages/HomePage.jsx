import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, GitBranch } from "lucide-react";
import api from "../services/api";

const features = [
  {
    num: "01",
    title: "AI Summary",
    description: "Get an instant understanding of what the codebase does and how it works.",
  },
  {
    num: "02",
    title: "Learning Path",
    description: "Follow a guided sequence to understand any repository in under 10 minutes.",
  },
  {
    num: "03",
    title: "Architecture View",
    description: "See the file structure, entry points, and how modules connect.",
  },
  {
    num: "04",
    title: "Ask Questions",
    description: "Chat with an AI that has read the entire codebase.",
  },
];

export default function HomePage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function importRepo() {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.post("/repositories", { url });
      navigate(`/repository/${res.data.id}`);
    } catch (err) {
      setError("Failed to import repository. Please check the URL and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-56px)] flex flex-col">
      <div className="flex-1 flex items-center justify-center px-6 py-24">
        <div className="w-full max-w-2xl space-y-12">
          <div className="space-y-5">
            <p className="text-[11px] font-medium text-gray-400 uppercase tracking-[0.2em]">
              Software Archaeologist
            </p>
            <h1 className="text-[3.5rem] leading-[1.1] font-serif text-gray-900">
              Understand any codebase
            </h1>
            <p className="text-lg text-gray-500 leading-relaxed max-w-lg">
              Import a repository. Get an AI-powered summary, guided learning path, and the confidence to contribute.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-xl p-1.5 focus-within:border-gray-400 transition-colors">
            <div className="flex items-center gap-2.5 flex-1 px-4">
              <GitBranch className="h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && importRepo()}
                placeholder="https://github.com/owner/repo"
                className="flex-1 bg-transparent text-sm text-gray-900 placeholder-gray-400 focus:outline-none"
              />
            </div>
            <button
              onClick={importRepo}
              disabled={loading || !url.trim()}
              className="bg-gray-900 text-white text-sm font-medium px-6 py-2.5 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>Import <span className="text-gray-400">→</span></>
              )}
            </button>
          </div>

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}
        </div>
      </div>

      <div className="border-t border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="grid grid-cols-4 gap-8">
            {features.map((feature) => (
              <div key={feature.num} className="space-y-2.5">
                <p className="text-[11px] text-gray-300 font-mono">{feature.num}</p>
                <h3 className="text-sm font-semibold text-gray-900">{feature.title}</h3>
                <p className="text-[13px] text-gray-500 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
