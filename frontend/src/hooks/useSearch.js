import { useQuery } from "@tanstack/react-query";
import api from "../services/api";

export function useSearch(repoId, keyword) {
  return useQuery({
    queryKey: ["search", repoId, keyword],
    queryFn: async () => {
      const res = await api.get(
        `/repositories/${repoId}/search-content`,
        {
          params: {
            keyword,
          },
        }
      );

      return res.data;
    },
    enabled: !!repoId && !!keyword,
  });
}