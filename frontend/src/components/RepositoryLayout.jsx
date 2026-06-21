import { Outlet, useParams } from "react-router-dom";
import RepositorySidebar from "./RepositorySidebar";

function RepositoryLayout() {
  const { id } = useParams();

  return (
    <div className="flex h-[calc(100vh-56px)]">
      <RepositorySidebar repoId={id} />
      <main className="flex-1 overflow-y-auto bg-white">
        <div className="max-w-4xl mx-auto px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default RepositoryLayout;
