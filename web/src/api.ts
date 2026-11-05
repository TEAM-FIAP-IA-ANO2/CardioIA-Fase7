import type {Analysis,History,PatientData} from './types';
const BASE=(import.meta.env.VITE_API_URL||'http://localhost:8000').replace(/\/$/,'');
async function request<T>(path:string, options?:RequestInit):Promise<T>{const r=await fetch(BASE+path,{...options,headers:{'Content-Type':'application/json',...(options?.headers||{})}});if(!r.ok){let detail=`HTTP ${r.status}`;try{detail=(await r.json()).detail||detail}catch{}throw new Error(detail)}return r.json() as Promise<T>}
export const api={health:()=>request<{status:string;version:string}>('/health'),analyze:(p:PatientData)=>request<Analysis>('/api/v1/analyze',{method:'POST',body:JSON.stringify(p)}),history:(limit=30)=>request<History[]>(`/api/v1/readings?limit=${limit}`)};
