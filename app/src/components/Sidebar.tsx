import { useState } from 'react'
import {
  LayoutDashboard, MessageSquare, Activity, Cpu, Network,
  Package, BookOpen, PlaySquare, Globe2, Brain, CreditCard,
  MapPin, GitMerge, Database, Fingerprint, Target, Settings,
  ChevronLeft, ChevronRight, Sun, Moon,
} from 'lucide-react'

export type PageId =
  | 'overview' | 'chat' | 'live' | 'runtime' | 'architecture'
  | 'modules' | 'knowledge' | 'demos' | 'sphere' | 'noema'
  | 'cards' | 'sites' | 'orbital'
  | 'pamiec' | 'tozsamosc' | 'plany' | 'ustawienia'

interface NavItem {
  id: PageId
  label: string
  icon: React.ComponentType<{ className?: string }>
  section?: string
}

const NAV: NavItem[] = [
  // System
  { id: 'overview',     label: 'Overview',       icon: LayoutDashboard, section: 'system' },
  { id: 'chat',         label: 'Chat',            icon: MessageSquare,   section: 'system' },
  { id: 'live',         label: 'CIEL Live',       icon: Activity,        section: 'system' },
  { id: 'runtime',      label: 'Runtime',         icon: Cpu,             section: 'system' },
  // Architecture
  { id: 'architecture', label: 'Architecture',    icon: Network,         section: 'arch' },
  { id: 'modules',      label: 'Modules',         icon: Package,         section: 'arch' },
  { id: 'knowledge',    label: 'Knowledge',       icon: BookOpen,        section: 'arch' },
  { id: 'demos',        label: 'Demos',           icon: PlaySquare,      section: 'arch' },
  // Orbital / Consciousness
  { id: 'sphere',       label: 'Sphere',          icon: Globe2,          section: 'orbital' },
  { id: 'noema',        label: 'Noema',           icon: Brain,           section: 'orbital' },
  { id: 'cards',        label: 'Cards',           icon: CreditCard,      section: 'orbital' },
  { id: 'sites',        label: 'Sites',           icon: MapPin,          section: 'orbital' },
  { id: 'orbital',      label: 'Orbital',         icon: GitMerge,        section: 'orbital' },
  // Operational
  { id: 'pamiec',       label: 'Pamięć',          icon: Database,        section: 'ops' },
  { id: 'tozsamosc',    label: 'Tożsamość',       icon: Fingerprint,     section: 'ops' },
  { id: 'plany',        label: 'Plany',           icon: Target,          section: 'ops' },
  { id: 'ustawienia',   label: 'Ustawienia',      icon: Settings,        section: 'ops' },
]

const SECTION_LABELS: Record<string, string> = {
  system:  'System',
  arch:    'Architektura',
  orbital: 'Orbital · Świadomość',
  ops:     'Operacyjne',
}

interface SidebarProps {
  active: PageId
  onNavigate: (id: PageId) => void
  theme: 'dark' | 'light'
  onThemeToggle: () => void
}

export function Sidebar({ active, onNavigate, theme, onThemeToggle }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)

  const sections = Array.from(new Set(NAV.map((n) => n.section!)))

  return (
    <aside
      className={`flex flex-col h-screen bg-card border-r border-border transition-all duration-200 shrink-0 ${
        collapsed ? 'w-14' : 'w-52'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-4 border-b border-border">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-cyan-400 font-mono">Ω</span>
            <span className="text-sm font-bold tracking-wide">CIEL/Ω</span>
          </div>
        )}
        {collapsed && <span className="text-lg font-bold text-cyan-400 font-mono mx-auto">Ω</span>}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded hover:bg-muted text-muted-foreground ml-auto"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-2">
        {sections.map((section) => (
          <div key={section} className="mb-1">
            {!collapsed && (
              <div className="px-3 py-1.5 text-[9px] font-mono font-bold text-muted-foreground/50 uppercase tracking-widest">
                {SECTION_LABELS[section]}
              </div>
            )}
            {NAV.filter((n) => n.section === section).map((item) => {
              const isActive = active === item.id
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  title={collapsed ? item.label : undefined}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm transition-colors ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-300 border-r-2 border-cyan-500'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-cyan-400' : ''}`} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </button>
              )
            })}
            {!collapsed && <div className="mx-3 my-1 h-px bg-border/50" />}
          </div>
        ))}
      </nav>

      {/* Theme toggle at bottom */}
      <div className="border-t border-border p-2">
        <button
          onClick={onThemeToggle}
          className="w-full flex items-center gap-2 px-2 py-2 rounded hover:bg-muted text-muted-foreground text-xs transition-colors"
          title="Przełącz motyw"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 shrink-0" /> : <Moon className="w-4 h-4 shrink-0" />}
          {!collapsed && <span>{theme === 'dark' ? 'Jasny motyw' : 'Ciemny motyw'}</span>}
        </button>
      </div>
    </aside>
  )
}
