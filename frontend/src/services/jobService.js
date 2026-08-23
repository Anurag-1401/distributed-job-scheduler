import { api } from "./api";
import { buildJobQuery } from "../utils/format";

export async function listJobs(filters) {
  const { data } = await api.get("/api/v1/jobs", { params: buildJobQuery(filters) });
  return data;
}

export async function getJob(id) {
  const { data } = await api.get(`/api/v1/jobs/${id}`);
  return data;
}

export async function createJob(payload, idempotencyKey) {
  const headers = {};
  if (idempotencyKey) {
    headers["Idempotency-Key"] = idempotencyKey;
  }
  const { data } = await api.post("/api/v1/jobs", payload, { headers });
  return data;
}

export async function createJobBatch(payload) {
  const { data } = await api.post("/api/v1/jobs/batch", payload);
  return data;
}

export async function retryJob(id) {
  const { data } = await api.post(`/api/v1/jobs/${id}/retry`);
  return data;
}

export async function cancelJob(id) {
  const { data } = await api.post(`/api/v1/jobs/${id}/cancel`);
  return data;
}

export async function listJobExecutions(id, params) {
  const { data } = await api.get(`/api/v1/jobs/${id}/executions`, { params });
  return data;
}

export async function listJobLogs(id, params) {
  const { data } = await api.get(`/api/v1/jobs/${id}/logs`, { params });
  return data;
}
