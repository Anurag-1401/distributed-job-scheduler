import { api } from "./api";
export async function listWorkers(params) { 
    const { data } = await 
            api.get("/api/v1/workers",
             { params }
            ); 
    return data; }

export async function getWorker(id) {
     const { data } = await 
        api.get(`/api/v1/workers/${id}`); 
        return data; 
    }

export async function listWorkerJobs(id, params) { 
    const { data } = await api.get(`/api/v1/workers/${id}/jobs`, 
        { params }); return data; 
    }
