export const DOMAINS = [
  { id: 'academic', label: 'Academic', question: 'I could manage my classes, coursework, and deadlines.' },
  { id: 'spiritual', label: 'Spiritual', question: 'I felt connected to what gives my life meaning, purpose, values, or inner grounding, with or without faith or religion.' },
  { id: 'social', label: 'Social', question: 'I felt connected to and supported by people I trust.' },
  { id: 'physical', label: 'Physical', question: 'I had the energy and physical wellbeing I needed for my daily activities.' },
  { id: 'psychological', label: 'Psychological', question: 'I could manage my emotions and cope with everyday stress.' },
]

export const AGGREGATION_THRESHOLD = 10
export const DOMAIN_SCALE = [
  'Strongly disagree',
  'Disagree',
  'Neither agree nor disagree',
  'Agree',
  'Strongly agree',
]

export function summarizeSession(responses, sessionId) {
  const eligible = responses.filter(row => row.sessionId === sessionId && row.researchEligible)
  const unique = [...new Map(eligible.map(row => [row.userId, row])).values()]
  const syntheticCount = unique.filter(row => row.synthetic).length
  if (unique.length < AGGREGATION_THRESHOLD) {
    return { count: unique.length, syntheticCount, released: false, means: null }
  }
  const means = Object.fromEntries(DOMAINS.map(({ id }) => [
    id,
    Number((unique.reduce((sum, row) => sum + row.ratings[id], 0) / unique.length).toFixed(1)),
  ]))
  return { count: unique.length, syntheticCount, released: true, means }
}
