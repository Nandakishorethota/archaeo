import { useQuery } from "@tanstack/react-query";
import api from "../services/api";

export function useRepositoryTree(repositoryId) {
  return useQuery({
    queryKey: ["repository", repositoryId, "tree"],
    queryFn: () => api.get(`/repositories/${repositoryId}/tree`).then(res => res.data),
    enabled: !!repositoryId,
    staleTime: 5 * 60 * 1000,
  });
}