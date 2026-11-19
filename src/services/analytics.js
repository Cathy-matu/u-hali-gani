import { http, MOCK, wait } from './http'
import { adminSeries } from '../data/mock'
export const analyticsApi = { overview: () => (MOCK ? wait(adminSeries) : http.get('/analytics/overview')) }
