import { useQuery } from "@tanstack/react-query";
import api from "../services/api";

export function useSummary(repoId) {
  return useQuery({
    queryKey: ["summary", repoId],
    queryFn: async () => {
      const res = await api.get(
        `/repositories/${repoId}/summary`
      );
      return res.data;
    },
    enabled: !!repoId,
    staleTime: 1000 * 60 * 60,
  });
}