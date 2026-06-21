import { useState } from "react";
import { useParams } from "react-router-dom";
import { Search, FileText, Loader2, Brain } from "lucide-react";
import { useSearch } from "../hooks/useSearch";

export function SearchPage() {
  const { id } = useParams();
  const [keyword, setKeyword] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const { data: results, isLoading, error } = useSearch(id, searchQuery);

  function handleSearch(e) {
    e.preventDefault();
    if (keyword.trim()) setSearchQuery(keyword.trim());
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-serif text-gray-900">Search</h1>
        <p className="text-sm text-gray-500">Search across all files in the repository</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Search for keywords, functions, classes..."
            className="w-full bg-gray-50 border border-gray-200 pl-10 pr-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-gray-400 transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={!keyword.trim() || isLoading}
          className="bg-gray-900 text-white px-5 py-2.5 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 hover:bg-gray-800"
        >
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          Search
        </button>
      </form>

      {isLoading && (
        <div className="space-y-3 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="p-5 border border-gray-100 space-y-2">
              <div className="h-4 w-48 bg-gray-100 rounded" />
              <div className="h-3 w-full bg-gray-100 rounded" />
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="text-center py-24">
          <Brain className="h-12 w-12 text-gray-200 mx-auto mb-4" />
          <h3 className="text-base font-medium text-gray-900 mb-1">Search Error</h3>
          <p className="text-sm text-gray-500">{error.message}</p>
        </div>
      )}

      {!isLoading && !error && searchQuery && results?.length === 0 && (
        <div className="text-center py-24">
          <Search className="h-12 w-12 text-gray-200 mx-auto mb-4" />
          <h3 className="text-base font-medium text-gray-900 mb-1">No Results Found</h3>
          <p className="text-sm text-gray-500">No files contain "{searchQuery}"</p>
        </div>
      )}

      {!isLoading && !error && results?.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-gray-500">Found {results.length} result{results.length !== 1 ? 's' : ''} for "{searchQuery}"</p>
          {results.map((result, index) => (
            <div key={index} className="p-5 border border-gray-100">
              <div className="flex items-start gap-3">
                <FileText className="h-4 w-4 text-gray-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{result.file || result.path}</p>
                  {result.line && <p className="text-[11px] text-gray-400 mt-1">Line {result.line}</p>}
                  {result.content && (
                    <p className="text-xs text-gray-600 mt-3 font-mono bg-gray-50 border border-gray-100 p-4 overflow-x-auto">
                      {result.content}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!isLoading && !error && !searchQuery && (
        <div className="text-center py-24">
          <Search className="h-12 w-12 text-gray-200 mx-auto mb-4" />
          <h3 className="text-base font-medium text-gray-900 mb-1">Search the Repository</h3>
          <p className="text-sm text-gray-500">Enter a keyword to search across all files</p>
        </div>
      )}
    </div>
  );
}
