import { useQuery } from "@tanstack/react-query";
import api from "../services/api";

export function useRepository(id) {
  return useQuery({
    queryKey: ["repository", id],
    queryFn: () => api.get(`/repositories/${id}`).then(res => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useRepositoryStats(id) {
  return useQuery({
    queryKey: ["repository", id, "stats"],
    queryFn: () => api.get(`/repositories/${id}/stats`).then(res => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useArchitecture(id) {
  return useQuery({
    queryKey: ["repository", id, "architecture"],
    queryFn: () => api.get(`/repositories/${id}/architecture`).then(res => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFileTree(id) {
  return useQuery({
    queryKey: ["repository", id, "file-tree"],
    queryFn: () => api.get(`/repositories/${id}/file-tree`).then(res => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useRepositorySummary(id) {
  return useQuery({
    queryKey: ["repository", id, "summary"],
    queryFn: () => api.get(`/repositories/${id}/summary`).then(res => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useArchitectureTree(id) {
  return useQuery({
    queryKey: ["repository", id, "architecture-tree"],
    queryFn: () => api.get(`/repositories/${id}/architecture-tree`).then(res => res.data),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}