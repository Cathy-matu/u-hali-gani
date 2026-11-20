import { useMemo, useState } from 'react'
import { ArrowDownRight, ArrowUpRight, Facebook, Instagram, Search, Users, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'
import { communityCategories, communities, getCommunitySocialLinks } from '../../data/communities'
import { useApp } from '../../context/AuthContext'

const getSavedCommunities = key => {
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '[]')
    return Array.isArray(saved) ? saved : []
  } catch (error) {
    console.error('Unable to read saved communities.', error)
    return []
  }
}

const scrollToDirectory = event => {
  event.preventDefault()
  document.getElementById('community-list')?.scrollIntoView({ behavior: 'instant', block: 'start' })
}

export function Communities() {
  const { user } = useApp()
  const storageKey = `hali-community-saves:${user?.id}`
  const [category, setCategory] = useState('All')
  const [query, setQuery] = useState('')
  const [joined, setJoined] = useState(() => getSavedCommunities(storageKey))
  const [showJoined, setShowJoined] = useState(false)

  const filteredCommunities = useMemo(() => communities.filter(community => {
    const matchesCategory = category === 'All' || community.category === category
    const matchesQuery = `${community.name} ${community.description} ${community.category}`
      .toLowerCase()
      .includes(query.trim().toLowerCase())
    const matchesMembership = !showJoined || joined.includes(community.id)
    return matchesCategory && matchesQuery && matchesMembership
  }), [category, joined, query, showJoined])

  const toggleJoin = community => {
    const nextJoined = joined.includes(community.id)
      ? joined.filter(id => id !== community.id)
      : [...joined, community.id]
    try {
      localStorage.setItem(storageKey, JSON.stringify(nextJoined))
      setJoined(nextJoined)
      toast.success(nextJoined.includes(community.id) ? `Joined ${community.name}. This is saved to your local list.` : `Left ${community.name}.`)
    } catch (error) {
      console.error('Unable to save community preferences.', error)
      toast.error('We could not save that change. Please check your browser storage and try again.')
    }
  }

  return (
    <div className="community-page">
      <header className="community-page-heading">
        <div>
          <span className="dashboard-kicker">CAMPUS LIFE</span>
          <h1>Find your people</h1>
          <p>Shared interests are a lovely place to start. Explore a group, save the ones you like, and find their public community pages.</p>
        </div>
        <span className="community-count"><Users size={17} /> {communities.length} places to start</span>
      </header>

      <section className="community-feature" aria-label="Community welcome">
        <img src="/images/campus-friends-high-five.jpg" alt="University friends greeting each other on campus" />
        <div className="community-feature-shade" />
        <div className="community-feature-content">
          <span>YOU DON’T HAVE TO DO CAMPUS ALONE</span>
          <h2>Show up as you are.<br />There’s room for you here.</h2>
          <p>Teams, societies, creative spaces and people who get it—all good places to begin.</p>
          <a className="community-feature-link" href="#community-list" onClick={scrollToDirectory}>Explore communities <ArrowDownRight size={17} /></a>
        </div>
      </section>

      <section className="community-directory" id="community-list">
        <div className="community-directory-heading">
          <div>
            <span className="dashboard-kicker">YOUR NEXT HELLO</span>
            <h2>Explore campus communities</h2>
          </div>
          <button type="button" className={`community-saved-toggle${showJoined ? ' active' : ''}`} onClick={() => setShowJoined(value => !value)}>
            <Users size={16} /> {showJoined ? 'All communities' : `Your groups (${joined.length})`}
          </button>
        </div>

        <div className="community-filters">
          <label className="community-search">
            <Search size={18} />
            <input aria-label="Search communities" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search a sport, society or interest" />
            {query && <button type="button" aria-label="Clear search" onClick={() => setQuery('')}><X size={15} /></button>}
          </label>
          <div className="community-category-list" aria-label="Filter by category">
            {communityCategories.map(item => (
              <button type="button" key={item} className={`community-category-chip${category === item ? ' active' : ''}`} aria-pressed={category === item} onClick={() => setCategory(item)}>{item}</button>
            ))}
          </div>
        </div>

        {filteredCommunities.length ? (
          <div className="community-grid">
            {filteredCommunities.map(community => {
              const isJoined = joined.includes(community.id)
              return (
                <article className="community-card" key={community.id}>
                  <div className="community-card-image">
                    <img src={community.image} alt={community.imageAlt} loading="lazy" />
                    <span className="community-category-label">{community.category}</span>
                  </div>
                  <div className="community-card-body">
                    <div className="community-card-title">
                      <h3>{community.name}</h3>
                      {isJoined && <span className="community-joined-mark">Saved</span>}
                    </div>
                    <p>{community.description}</p>
                    <div className="community-activity"><Users size={15} /><span>{community.activity}</span></div>
                    <div className="community-card-actions">
                      <button type="button" className={isJoined ? 'community-join-button joined' : 'community-join-button'} onClick={() => toggleJoin(community)}>
                        {isJoined ? 'Leave group' : 'Join group'} {isJoined ? <X size={15} /> : <ArrowUpRight size={15} />}
                      </button>
                      <div className="community-socials" aria-label={`${community.name} social searches`}>
                        {getCommunitySocialLinks(community).map(({ label, href }) => {
                          const Icon = label === 'Instagram' ? Instagram : Facebook
                          return <a key={label} href={href} target="_blank" rel="noopener noreferrer" aria-label={`Search ${community.name} on ${label}`} title={`Search ${label}`}><Icon size={17} /></a>
                        })}
                      </div>
                    </div>
                    <p className="community-social-note">Social links open public searches. Sign in on the social platform if you choose.</p>
                  </div>
                </article>
              )
            })}
          </div>
        ) : (
          <div className="community-empty">
            <Search size={24} />
            <h3>No groups found</h3>
            <p>Try a different search or category—or browse all communities.</p>
            <button type="button" className="community-category-chip active" onClick={() => { setQuery(''); setCategory('All'); setShowJoined(false) }}>Show all communities</button>
          </div>
        )}
      </section>

      <section className="community-real-life-note">
        <div><span className="dashboard-kicker">START SMALL</span><h2>New to a group? That’s the whole point.</h2><p>You can message a group before going, bring a friend, or just see what feels right. No pressure to join everything.</p></div>
        <Link to="/student/help">Need a person to talk to? <ArrowUpRight size={16} /></Link>
      </section>
      <p className="community-disclaimer">Starter directory for a campus wellbeing prototype. Confirm group availability and official accounts with your university. Group membership is saved in this browser only; Hali does not notify or enroll you with a real campus group.</p>
    </div>
  )
}

export default Communities
