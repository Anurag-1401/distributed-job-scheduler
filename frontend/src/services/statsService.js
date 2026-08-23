import { api } from "./api";

export async function getStats() {
  const { data } = await api.get("/api/v1/metrics/overview");
  return data;
}
export async function getHealth() { const { data } = await api.get("/health"); return data; }
export async function getReady() { const { data } = await api.get("/ready"); return data; }
