import { ResponsiveContainer } from 'recharts'
export default function ChartBox({ children, h = 250 }) {
  return <div style={{ height: h }}><ResponsiveContainer>{children}</ResponsiveContainer></div>
}
