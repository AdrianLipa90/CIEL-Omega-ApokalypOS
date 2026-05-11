import { useState, useEffect } from 'react'
import { Sidebar, type PageId } from '@/components/Sidebar'

import Overview      from '@/pages/Overview'
import Chat          from '@/pages/Chat'
import CielLive      from '@/pages/CielLive'
import Runtime       from '@/pages/Runtime'
import Architecture  from '@/pages/Architecture'
import Modules       from '@/pages/Modules'
import Knowledge     from '@/pages/Knowledge'
import Demos         from '@/pages/Demos'
import Sphere        from '@/pages/Sphere'
import Noema         from '@/pages/Noema'
import Cards         from '@/pages/Cards'
import Sites         from '@/pages/Sites'
import Orbital       from '@/pages/Orbital'
import Pamiec        from '@/pages/Pamiec'
import Tozsamosc     from '@/pages/Tozsamosc'
import Plany         from '@/pages/Plany'
import Ustawienia    from '@/pages/Ustawienia'

const PAGES: Record<PageId, React.ComponentType> = {
  overview:     Overview,
  chat:         Chat,
  live:         CielLive,
  runtime:      Runtime,
  architecture: Architecture,
  modules:      Modules,
  knowledge:    Knowledge,
  demos:        Demos,
  sphere:       Sphere,
  noema:        Noema,
  cards:        Cards,
  sites:        Sites,
  orbital:      Orbital,
  pamiec:       Pamiec,
  tozsamosc:    Tozsamosc,
  plany:        Plany,
  ustawienia:   Ustawienia,
}

function getInitialPage(): PageId {
  const stored = localStorage.getItem('ciel_active_page')
  if (stored && stored in PAGES) return stored as PageId
  return 'overview'
}

function getInitialTheme(): 'dark' | 'light' {
  const stored = localStorage.getItem('ciel_theme')
  return stored === 'light' ? 'light' : 'dark'
}

export default function App() {
  const [page, setPage] = useState<PageId>(getInitialPage)
  const [theme, setTheme] = useState<'dark' | 'light'>(getInitialTheme)

  // Apply theme on mount and change
  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
      root.classList.remove('light')
    } else {
      root.classList.remove('dark')
      root.classList.add('light')
    }
    localStorage.setItem('ciel_theme', theme)
  }, [theme])

  const navigate = (id: PageId) => {
    setPage(id)
    localStorage.setItem('ciel_active_page', id)
  }

  const toggleTheme = () => {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
  }

  const PageComponent = PAGES[page]

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar
        active={page}
        onNavigate={navigate}
        theme={theme}
        onThemeToggle={toggleTheme}
      />
      <main className="flex-1 overflow-y-auto">
        <PageComponent />
      </main>
    </div>
  )
}
