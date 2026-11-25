import { Phone } from 'lucide-react'
import { Card, Disclaimer } from '../../components/common/ui'
import { helpContacts } from '../../data/mock'

export function Help() {
  return (<><h1 className="h3">Support &amp; contacts</h1><Disclaimer>These options are here whenever you choose to use them; you do not need a particular check-in result to view them. Opening this page does not contact anyone. Hali is not an emergency service, and the numbers below are unverified placeholders.</Disclaimer>
    <Card title="Support contacts">
      {helpContacts.map(c => <div key={c.label} className="d-flex justify-content-between align-items-center border-top py-2"><div>{c.label}<br /><small className="muted">{c.tel}</small></div><a className="btn btn-outline-teal" href={`tel:${c.tel.replace(/ /g, '')}`}><Phone size={16} />Call</a></div>)}
    </Card></>)
}

export default Help
