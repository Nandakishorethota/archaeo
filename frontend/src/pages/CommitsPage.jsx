import { useState } from "react";
import { useParams } from "react-router-dom";
import { GitCommit, GitBranch, Calendar } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";

function formatDate(dateString) {
  if (!dateString) return "Unknown date";
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}

export function CommitsPage() {
  const { id } = useParams();
  const [page, setPage] = useState(1);

  const { data: commits, isLoading, error } = useQuery({
    queryKey: ["commits", id, page],
    queryFn: async () => {
      const res = await api.get(`/repositories/${id}/commits`, { params: { page, per_page: 20 } });
      return res.data;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <div className="space-y-3 animate-pulse">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="p-5 border border-gray-100 space-y-2">
            <div className="h-4 w-64 bg-gray-100 rounded" />
            <div className="h-3 w-48 bg-gray-100 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-24">
        <GitCommit className="h-12 w-12 text-gray-200 mx-auto mb-4" />
        <h3 className="text-base font-medium text-gray-900 mb-1">Error Loading Commits</h3>
        <p className="text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }

  if (!commits || commits.length === 0) {
    return (
      <div className="text-center py-24">
        <GitCommit className="h-12 w-12 text-gray-200 mx-auto mb-4" />
        <h3 className="text-base font-medium text-gray-900 mb-1">No Commits Found</h3>
        <p className="text-sm text-gray-500">This repository has no commits yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-serif text-gray-900">Commits</h1>
        <p className="text-sm text-gray-500">View the commit history of this repository</p>
      </div>

      <div className="space-y-2">
        {commits.map((commit, index) => (
          <div key={commit.sha || index} className="p-5 border border-gray-100">
            <p className="text-sm text-gray-900 font-medium mb-2">{commit.message || "No commit message"}</p>
            <div className="flex items-center gap-4 text-[11px] text-gray-500">
              {commit.author && (
                <span className="flex items-center gap-1.5"><GitBranch className="h-3.5 w-3.5" />{commit.author}</span>
              )}
              {commit.date && (
                <span className="flex items-center gap-1.5"><Calendar className="h-3.5 w-3.5" />{formatDate(commit.date)}</span>
              )}
              {commit.sha && <span className="font-mono text-gray-400">{commit.sha.substring(0, 7)}</span>}
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-center gap-6 pt-4">
        <button
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
          className="text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← Previous
        </button>
        <span className="text-sm text-gray-400">Page {page}</span>
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={commits.length < 20}
          className="text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next →
        </button>
      </div>
    </div>
  );
}
