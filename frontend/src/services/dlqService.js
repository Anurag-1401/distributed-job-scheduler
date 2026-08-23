import { api } from "./api";
export async function listDeadLetterJobs(params) { const { data } = await api.get("/api/v1/dlq", { params }); return data; }
export async function getDeadLetterJob(id) { const { data } = await api.get(`/api/v1/dlq/${id}`); return data; }
export async function retryDeadLetterJob(id) { const { data } = await api.post(`/api/v1/dlq/${id}/retry`); return data; }
export async function deleteDeadLetterJob(id) { const { data } = await api.delete(`/api/v1/dlq/${id}`); return data; }
