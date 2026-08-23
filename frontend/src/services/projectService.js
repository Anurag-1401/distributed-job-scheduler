import { api } from "./api";

export async function listProjects(params) {
  const { data } = await api.get("/api/v1/projects", { params });
  return data;
}

export async function getProject(id) {
  const { data } = await api.get(`/api/v1/projects/${id}`);
  return data;
}

export async function createProject(payload) {
  const { data } = await api.post("/api/v1/projects", payload);
  return data;
}

export async function updateProject(id, payload) {
  const { data } = await api.patch(`/api/v1/projects/${id}`, payload);
  return data;
}

export async function deleteProject(id) {
  const { data } = await api.delete(`/api/v1/projects/${id}`);
  return data;
}
