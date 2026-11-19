import { http, MOCK, wait } from './http'
export const messagingApi = { send: m => (MOCK ? wait(m, 200) : http.post('/messages', m)) }
