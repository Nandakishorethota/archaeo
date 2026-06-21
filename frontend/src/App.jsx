import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Layout from "./components/Layout";
import RepositoryLayout from "./components/RepositoryLayout";

import HomePage from "./pages/HomePage";
import { OverviewPanel } from "./pages/RepositoryOverview";
import { LearningPathPage } from "./pages/LearningPathPage";
import { NextReadingsPage } from "./pages/NextReadingsPage";
import { FilesPage } from "./pages/FilesPage";
import { CommitsPage } from "./pages/CommitsPage";
import { SearchPage } from "./pages/SearchPage";
import { ChatPage } from "./pages/ChatPage";

function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          element={<Layout />}
        >

          <Route
            path="/"
            element={<HomePage />}
          />

        </Route>

        <Route
          element={<RepositoryLayout />}
        >

          <Route
            path="/repository/:id"
            element={<OverviewPanel />}
          />
          <Route
            path="/repository/:id/overview"
            element={<OverviewPanel />}
          />
          <Route
            path="/repository/:id/learning-path"
            element={<LearningPathPage />}
          />
          <Route
            path="/repository/:id/next-readings"
            element={<NextReadingsPage />}
          />
          <Route
            path="/repository/:id/files"
            element={<FilesPage />}
          />
          <Route
            path="/repository/:id/commits"
            element={<CommitsPage />}
          />
          <Route
            path="/repository/:id/search"
            element={<SearchPage />}
          />
          <Route
            path="/repository/:id/chat"
            element={<ChatPage />}
          />

        </Route>

      </Routes>

    </BrowserRouter>
  );
}

export default App;
