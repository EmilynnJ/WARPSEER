import axios from 'axios';
import type { AxiosInstance } from 'axios';
import { env } from './env';
import { getAuthToken } from './auth';

const api: AxiosInstance = axios.create({ baseURL: env.backendBase, withCredentials: false });

export async function authHeaders() {
  const token = await getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

api.interceptors.request.use(async (config) => {
  const token = await getAuthToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export { api };