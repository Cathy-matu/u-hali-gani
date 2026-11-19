import { useEffect } from 'react'
export default function useDocumentTitle(t) { useEffect(() => { document.title = t ? `${t} · Hali` : 'Hali' }, [t]) }
