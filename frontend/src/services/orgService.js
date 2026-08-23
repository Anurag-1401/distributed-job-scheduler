import { api } from "./api";

export async function listOrganizations() {
  const { data } = await api.get("/api/v1/organizations");
  return data;
}

export async function createOrganization(payload) {
  const { data } = await api.post("/api/v1/organizations", payload);
  return data;
}
