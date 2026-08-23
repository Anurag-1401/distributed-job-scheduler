import { api } from "./api";

export async function listQueues(params) {
  const { data } = await api.get("/api/v1/queues", { params });
  return data;
}

export async function getQueue(id) {
  const { data } = await api.get(`/api/v1/queues/${id}`);
  return data;
}

export async function createQueue(payload) {
  const { data } = await api.post("/api/v1/queues", payload);
  return data;
}

export async function updateQueue(id, payload) {
  const { data } = await api.patch(`/api/v1/queues/${id}`, payload);
  return data;
}

export async function pauseQueue(id) {
  const { data } = await api.post(`/api/v1/queues/${id}/pause`);
  return data;
}

export async function resumeQueue(id) {
  const { data } = await api.post(`/api/v1/queues/${id}/resume`);
  return data;
}
