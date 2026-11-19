// Screening only. Not a diagnosis.
export const scoreAll = a => {
  const sum = p => Object.entries(a).filter(([k]) => k.startsWith(p)).reduce((s, [, v]) => s + v, 0)
  return { phq: sum('phq'), gad: sum('gad'), who: sum('who'), item9: a.phq9 || 0, phq2: (a.phq1 || 0) + (a.phq2 || 0), gad2: (a.gad1 || 0) + (a.gad2 || 0) }
}
export const routeRisk = (mode, s) => {
  if (s.item9 > 0) return 'red'
  const amber = mode === 'full' ? s.phq >= 10 || s.gad >= 10 || s.who < 13 : s.phq2 >= 3 || s.gad2 >= 3
  return amber ? 'amber' : 'green'
}
