import axios from 'axios'
export const MOCK = true // set to false to call the real API
export const http = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || '/api' })
export const wait = (v, ms = 450) => new Promise(r => setTimeout(() => r(v), ms))
