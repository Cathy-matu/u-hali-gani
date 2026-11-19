import { http, MOCK, wait } from './http'
import { cases } from '../data/mock'
export const counsellorApi = { cases: () => (MOCK ? wait(cases) : http.get('/counsellor/cases')) }
