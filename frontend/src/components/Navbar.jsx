import { Link, useLocation } from "react-router-dom";
import { Search } from "lucide-react";
import { useState } from "react";

export function Navbar() {
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 h-14 bg-white border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-6 h-full flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-sm font-semibold text-gray-900">
          <span className="font-bold">SA</span>
          <span>Software Archaeologist</span>
        </Link>

        <button
          onClick={() => setSearchOpen(!searchOpen)}
          className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors"
        >
          <Search className="h-4 w-4" />
          <span>Search</span>
          <kbd className="text-[10px] text-gray-400 bg-gray-50 border border-gray-200 rounded px-1.5 py-0.5 font-mono">/</kbd>
        </button>
      </div>
    </header>
  );
}

export default Navbar;
