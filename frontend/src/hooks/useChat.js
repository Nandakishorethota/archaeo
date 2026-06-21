import { useMutation } from "@tanstack/react-query";
import api from "../services/api";

export function useChat(repoId) {
  const mutation = useMutation({
    mutationFn: async (question) => {
      const response = await api.post(
        `/repositories/${repoId}/ask`,
        { question }
      );
      return response.data;
    },
  });

  return {
    askQuestion: mutation.mutateAsync,
    loading: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
  };
}
