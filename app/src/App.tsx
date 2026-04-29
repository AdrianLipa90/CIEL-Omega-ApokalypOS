import { useState, useEffect, useRef, useCallback } from 'react'
import { useCIELStatus } from '@/hooks/useCIELStatus'
import { useCIELChat } from '@/hooks/useCIELChat'
import { 
  Atom, Brain, Code, Sparkles, 
  Play, Pause, RotateCcw, Timer,
  Target, Shield, Layers, Orbit, GitBranch, Database,
  Microscope, Waves, Infinity, Eye,
  FileText, BarChart3, Network, Compass, Star, Download, FileCode, FileType, ScrollText, BookMarked
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'

// ============================================
// TYPES
// ============================================
interface SimulationConfig {
  gridSize: number
  dt: number
  steps: number
  lambda1: number
  lambda2: number
  lambda3: number
}

interface FieldState {
  I: number[][]
  tau: number[][]
  R: number[][]
  mass: number[][]
}

// ============================================
// HERO SECTION WITH ORBITAL ANIMATION
// ============================================
function HeroSection() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isPlaying, setIsPlaying] = useState(true)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio
      canvas.height = canvas.offsetHeight * window.devicePixelRatio
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    }
    resize()
    window.addEventListener('resize', resize)

    let animationId: number
    let time = 0
    const orbits: { radius: number; speed: number; particles: number; offset: number }[] = [
      { radius: 80, speed: 0.008, particles: 3, offset: 0 },
      { radius: 140, speed: 0.005, particles: 5, offset: 1 },
      { radius: 200, speed: 0.003, particles: 7, offset: 2 },
      { radius: 260, speed: 0.002, particles: 9, offset: 3 },
    ]

    function draw() {
      if (!ctx || !canvas) return
      const width = canvas.offsetWidth
      const height = canvas.offsetHeight
      const centerX = width / 2
      const centerY = height / 2

      ctx.fillStyle = 'rgba(10, 22, 40, 0.15)'
      ctx.fillRect(0, 0, width, height)

      // Draw orbital rings
      orbits.forEach((orbit, i) => {
        ctx.beginPath()
        ctx.arc(centerX, centerY, orbit.radius, 0, Math.PI * 2)
        ctx.strokeStyle = `rgba(93, 173, 226, ${0.1 + i * 0.05})`
        ctx.lineWidth = 1
        ctx.stroke()

        // Draw particles
        for (let p = 0; p < orbit.particles; p++) {
          const angle = time * orbit.speed + (p * Math.PI * 2) / orbit.particles + orbit.offset
          const x = centerX + Math.cos(angle) * orbit.radius
          const y = centerY + Math.sin(angle) * orbit.radius

          // Particle glow
          const gradient = ctx.createRadialGradient(x, y, 0, x, y, 12)
          gradient.addColorStop(0, i % 2 === 0 ? 'rgba(212, 175, 55, 0.8)' : 'rgba(93, 173, 226, 0.8)')
          gradient.addColorStop(0.5, i % 2 === 0 ? 'rgba(212, 175, 55, 0.3)' : 'rgba(93, 173, 226, 0.3)')
          gradient.addColorStop(1, 'transparent')
          
          ctx.beginPath()
          ctx.arc(x, y, 12, 0, Math.PI * 2)
          ctx.fillStyle = gradient
          ctx.fill()

          // Core
          ctx.beginPath()
          ctx.arc(x, y, 3, 0, Math.PI * 2)
          ctx.fillStyle = i % 2 === 0 ? '#f4d03f' : '#85c1e9'
          ctx.fill()
        }
      })

      // Central nucleus
      const nucleusGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 40)
      nucleusGradient.addColorStop(0, 'rgba(212, 175, 55, 0.6)')
      nucleusGradient.addColorStop(0.5, 'rgba(93, 173, 226, 0.3)')
      nucleusGradient.addColorStop(1, 'transparent')
      
      ctx.beginPath()
      ctx.arc(centerX, centerY, 40, 0, Math.PI * 2)
      ctx.fillStyle = nucleusGradient
      ctx.fill()

      ctx.beginPath()
      ctx.arc(centerX, centerY, 8, 0, Math.PI * 2)
      ctx.fillStyle = '#d4af37'
      ctx.shadowColor = '#f4d03f'
      ctx.shadowBlur = 20
      ctx.fill()
      ctx.shadowBlur = 0

      if (isPlaying) time += 1
      animationId = requestAnimationFrame(draw)
    }

    draw()
    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', resize)
    }
  }, [isPlaying])

  return (
    <section className="relative min-h-[90vh] flex flex-col items-center justify-center overflow-hidden">
      <div className="absolute inset-0 canvas-container">
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>
      
      <div className="relative z-10 text-center px-4 max-w-5xl mx-auto">
        <Badge className="mb-6 bg-amber-500/20 text-amber-300 border-amber-500/40 backdrop-blur-sm">
          <Sparkles className="w-3 h-3 mr-1" />
          Adrian Lipa's Unified Framework
        </Badge>
        
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6">
          <span className="gradient-text-gold">CIEL</span>
          <span className="text-sky-400">/</span>
          <span className="gradient-text-sky">0</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-sky-200/80 mb-4 font-light">
          Consciousness-Integrated Evolutionary Lambda
        </p>
        
        <p className="text-lg text-sky-300/60 mb-8 max-w-2xl mx-auto">
          A unified framework bridging quantum mechanics, consciousness, and cosmology 
          through the resonance of symbolic and intentional fields.
        </p>

        <div className="flex flex-wrap justify-center gap-4 mb-12">
          <Button 
            size="lg" 
            className="btn-gold"
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
            {isPlaying ? 'Pause Orbitals' : 'Resume Orbitals'}
          </Button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="glass-navy rounded-lg p-4 card-hover">
            <div className="text-2xl font-bold text-amber-400">8</div>
            <div className="text-sky-300/60">Fundamental Fields</div>
          </div>
          <div className="glass-navy rounded-lg p-4 card-hover">
            <div className="text-2xl font-bold text-sky-400">6</div>
            <div className="text-sky-300/60">Core Axioms</div>
          </div>
          <div className="glass-navy rounded-lg p-4 card-hover">
            <div className="text-2xl font-bold text-amber-400">3+1D</div>
            <div className="text-sky-300/60">Spacetime</div>
          </div>
          <div className="glass-navy rounded-lg p-4 card-hover">
            <div className="text-2xl font-bold text-sky-400">∞</div>
            <div className="text-sky-300/60">Possibilities</div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ============================================
// FIELD SIMULATION ENGINE
// ============================================
function FieldSimulationEngine() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [config, setConfig] = useState<SimulationConfig>({
    gridSize: 64,
    dt: 0.01,
    steps: 0,
    lambda1: 0.1,
    lambda2: 0.05,
    lambda3: 0.2
  })
  const fieldState = useRef<FieldState | null>(null)
  const animationRef = useRef<number | undefined>(undefined)

  const initializeFields = useCallback(() => {
    const N = config.gridSize
    const I: number[][] = Array(N).fill(null).map(() => Array(N).fill(0))
    const tau: number[][] = Array(N).fill(null).map(() => Array(N).fill(0))
    const R: number[][] = Array(N).fill(null).map(() => Array(N).fill(0))
    const mass: number[][] = Array(N).fill(null).map(() => Array(N).fill(0))

    // Initialize with Gaussian pulse
    const center = N / 2
    for (let i = 0; i < N; i++) {
      for (let j = 0; j < N; j++) {
        const dx = i - center
        const dy = j - center
        const r2 = (dx * dx + dy * dy) / (N * N / 8)
        I[i][j] = 0.5 * Math.exp(-r2)
        tau[i][j] = 0.1 * Math.exp(-r2)
      }
    }

    fieldState.current = { I, tau, R, mass }
  }, [config.gridSize])

  const step = useCallback(() => {
    if (!fieldState.current) return
    const { I, tau, R, mass } = fieldState.current
    const N = config.gridSize
    const dt = config.dt

    const newI = I.map(row => [...row])
    const newTau = tau.map(row => [...row])

    for (let i = 1; i < N - 1; i++) {
      for (let j = 1; j < N - 1; j++) {
        // Laplacian
        const lapI = I[i+1][j] + I[i-1][j] + I[i][j+1] + I[i][j-1] - 4 * I[i][j]
        
        // Nonlinear term
        const nonlin = 2 * config.lambda1 * I[i][j] ** 2 * I[i][j]
        
        // Phase term
        const phase = config.lambda3 * Math.sin(tau[i][j]) * I[i][j]
        
        newI[i][j] = I[i][j] + dt * (-lapI - nonlin - phase)
        
        // Tau evolution
        const gradTau = (tau[i+1][j] - tau[i-1][j]) ** 2 + (tau[i][j+1] - tau[i][j-1]) ** 2
        const f = 1 / (2 * (1 + gradTau ** 2))
        const div = f * ((tau[i+1][j] - tau[i][j]) - (tau[i][j] - tau[i-1][j])) +
                    f * ((tau[i][j+1] - tau[i][j]) - (tau[i][j] - tau[i][j-1]))
        newTau[i][j] = tau[i][j] + dt * (div - config.lambda3 * Math.sin(tau[i][j] - Math.atan2(I[i][j], I[i][j])))
      }
    }

    // Update resonance and mass
    for (let i = 0; i < N; i++) {
      for (let j = 0; j < N; j++) {
        R[i][j] = newI[i][j] ** 2
        mass[i][j] = Math.sqrt(Math.max(0, 1 - R[i][j]))
      }
    }

    fieldState.current.I = newI
    fieldState.current.tau = newTau
  }, [config])

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas || !fieldState.current) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const N = config.gridSize
    const cellW = canvas.width / N
    const cellH = canvas.height / N
    const { I, tau } = fieldState.current

    const imageData = ctx.createImageData(N, N)
    for (let i = 0; i < N; i++) {
      for (let j = 0; j < N; j++) {
        const idx = (i * N + j) * 4
        const intensity = Math.min(1, I[i][j] * 2)
        const phase = (Math.atan2(tau[i][j], I[i][j]) + Math.PI) / (2 * Math.PI)
        
        // Color based on phase, intensity based on |I|
        imageData.data[idx] = Math.floor(intensity * (100 + 155 * Math.sin(phase * Math.PI * 2)))
        imageData.data[idx + 1] = Math.floor(intensity * (150 + 105 * Math.cos(phase * Math.PI * 2)))
        imageData.data[idx + 2] = Math.floor(intensity * (200 + 55 * Math.sin(phase * Math.PI)))
        imageData.data[idx + 3] = 255
      }
    }
    
    ctx.putImageData(imageData, 0, 0)
    ctx.scale(cellW, cellH)
    ctx.drawImage(canvas, 0, 0, N, N, 0, 0, N, N)
    ctx.setTransform(1, 0, 0, 1, 0, 0)
  }, [config.gridSize])

  useEffect(() => {
    initializeFields()
    draw()
  }, [initializeFields, draw])

  useEffect(() => {
    if (isRunning) {
      const loop = () => {
        step()
        draw()
        animationRef.current = requestAnimationFrame(loop)
      }
      loop()
    } else {
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
  }, [isRunning, step, draw])

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 items-center">
        <Button 
          onClick={() => setIsRunning(!isRunning)}
          className={isRunning ? "btn-sky" : "btn-gold"}
        >
          {isRunning ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
          {isRunning ? 'Stop' : 'Start'}
        </Button>
        <Button 
          onClick={() => { initializeFields(); draw(); }}
          variant="outline"
          className="border-sky-500/40 text-sky-300"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Reset
        </Button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <Label className="text-sky-300/70 text-xs">λ₁ (Intention Coupling)</Label>
          <Slider 
            value={[config.lambda1]} 
            onValueChange={([v]) => setConfig(c => ({ ...c, lambda1: v }))}
            min={0} max={0.5} step={0.01}
            className="mt-2"
          />
          <span className="text-amber-400 text-sm">{config.lambda1.toFixed(2)}</span>
        </div>
        <div>
          <Label className="text-sky-300/70 text-xs">λ₂ (Lambda Coupling)</Label>
          <Slider 
            value={[config.lambda2]} 
            onValueChange={([v]) => setConfig(c => ({ ...c, lambda2: v }))}
            min={0} max={0.2} step={0.01}
            className="mt-2"
          />
          <span className="text-amber-400 text-sm">{config.lambda2.toFixed(2)}</span>
        </div>
        <div>
          <Label className="text-sky-300/70 text-xs">λ₃ (Phase Coupling)</Label>
          <Slider 
            value={[config.lambda3]} 
            onValueChange={([v]) => setConfig(c => ({ ...c, lambda3: v }))}
            min={0} max={0.5} step={0.01}
            className="mt-2"
          />
          <span className="text-amber-400 text-sm">{config.lambda3.toFixed(2)}</span>
        </div>
        <div>
          <Label className="text-sky-300/70 text-xs">Time Step (dt)</Label>
          <Slider 
            value={[config.dt]} 
            onValueChange={([v]) => setConfig(c => ({ ...c, dt: v }))}
            min={0.001} max={0.05} step={0.001}
            className="mt-2"
          />
          <span className="text-amber-400 text-sm">{config.dt.toFixed(3)}</span>
        </div>
      </div>

      <div className="canvas-container" style={{ height: '400px' }}>
        <canvas 
          ref={canvasRef} 
          width={config.gridSize} 
          height={config.gridSize}
          className="w-full h-full object-contain"
        />
      </div>
      
      <div className="flex justify-between text-xs text-sky-400/60">
        <span>Field: Intention I(x,t)</span>
        <span>Color = Phase | Brightness = Amplitude</span>
      </div>
    </div>
  )
}

// ============================================
// ORBITAL VISUALIZATION ENGINE
// ============================================
function OrbitalEngine() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [entities, setEntities] = useState(12)
  const [showConnections, setShowConnections] = useState(true)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio
      canvas.height = canvas.offsetHeight * window.devicePixelRatio
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    }
    resize()

    let time = 0
    let animationId: number

    const orbitalEntities = Array.from({ length: entities }, (_, i) => ({
      id: i,
      orbitRadius: 60 + (i % 4) * 50,
      angle: (i / entities) * Math.PI * 2,
      speed: 0.002 + (i % 3) * 0.001,
      mass: 0.5 + Math.random() * 0.5,
      phase: Math.random() * Math.PI * 2
    }))

    function draw() {
      if (!ctx || !canvas) return
      const width = canvas.offsetWidth
      const height = canvas.offsetHeight
      const cx = width / 2
      const cy = height / 2

      ctx.fillStyle = 'rgba(10, 22, 40, 0.1)'
      ctx.fillRect(0, 0, width, height)

      // Update positions
      orbitalEntities.forEach(e => {
        e.angle += e.speed
      })

      // Draw connections
      if (showConnections) {
        ctx.strokeStyle = 'rgba(93, 173, 226, 0.15)'
        ctx.lineWidth = 0.5
        for (let i = 0; i < orbitalEntities.length; i++) {
          for (let j = i + 1; j < orbitalEntities.length; j++) {
            const e1 = orbitalEntities[i]
            const e2 = orbitalEntities[j]
            const x1 = cx + Math.cos(e1.angle) * e1.orbitRadius
            const y1 = cy + Math.sin(e1.angle) * e1.orbitRadius
            const x2 = cx + Math.cos(e2.angle) * e2.orbitRadius
            const y2 = cy + Math.sin(e2.angle) * e2.orbitRadius
            
            const dist = Math.sqrt((x2-x1)**2 + (y2-y1)**2)
            if (dist < 120) {
              ctx.globalAlpha = 1 - dist / 120
              ctx.beginPath()
              ctx.moveTo(x1, y1)
              ctx.lineTo(x2, y2)
              ctx.stroke()
            }
          }
        }
        ctx.globalAlpha = 1
      }

      // Draw entities
      orbitalEntities.forEach(e => {
        const x = cx + Math.cos(e.angle) * e.orbitRadius
        const y = cy + Math.sin(e.angle) * e.orbitRadius
        
        // Glow
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 15 * e.mass)
        gradient.addColorStop(0, 'rgba(212, 175, 55, 0.6)')
        gradient.addColorStop(0.5, 'rgba(93, 173, 226, 0.3)')
        gradient.addColorStop(1, 'transparent')
        
        ctx.beginPath()
        ctx.arc(x, y, 15 * e.mass, 0, Math.PI * 2)
        ctx.fillStyle = gradient
        ctx.fill()

        // Core
        ctx.beginPath()
        ctx.arc(x, y, 4 * e.mass, 0, Math.PI * 2)
        ctx.fillStyle = '#f4d03f'
        ctx.fill()
      })

      // Central attractor
      const attractorGradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, 30)
      attractorGradient.addColorStop(0, 'rgba(212, 175, 55, 0.4)')
      attractorGradient.addColorStop(1, 'transparent')
      ctx.beginPath()
      ctx.arc(cx, cy, 30, 0, Math.PI * 2)
      ctx.fillStyle = attractorGradient
      ctx.fill()

      time++
      animationId = requestAnimationFrame(draw)
    }

    draw()
    return () => cancelAnimationFrame(animationId)
  }, [entities, showConnections])

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2">
          <Label className="text-sky-300/70">Entities:</Label>
          <Slider 
            value={[entities]} 
            onValueChange={([v]) => setEntities(v)}
            min={3} max={24} step={1}
            className="w-32"
          />
          <span className="text-amber-400 w-8">{entities}</span>
        </div>
        <div className="flex items-center gap-2">
          <Switch 
            checked={showConnections} 
            onCheckedChange={setShowConnections}
          />
          <Label className="text-sky-300/70">Show Couplings</Label>
        </div>
      </div>

      <div className="canvas-container" style={{ height: '350px' }}>
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>
      
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="glass-navy rounded p-2">
          <div className="text-amber-400 font-bold">Σ e^(iγ) = 0</div>
          <div className="text-sky-400/60">Euler-Berry</div>
        </div>
        <div className="glass-navy rounded p-2">
          <div className="text-amber-400 font-bold">W_ij = ωe^(iδ)</div>
          <div className="text-sky-400/60">Coupling</div>
        </div>
        <div className="glass-navy rounded p-2">
          <div className="text-amber-400 font-bold">T² ∝ a³/A</div>
          <div className="text-sky-400/60">Orbit Law</div>
        </div>
      </div>
    </div>
  )
}

// ============================================
// LIVE STATUS BAR
// ============================================
function CIELStatusBar() {
  const { status, connected, mode } = useCIELStatus(30_000)

  const modeColor = mode === 'deep' ? 'text-amber-400' : mode === 'standard' ? 'text-sky-400' : 'text-red-400'
  const dot = connected ? 'bg-emerald-400' : 'bg-red-500'

  return (
    <div className="flex items-center gap-4 px-6 py-2 bg-slate-950/70 border-b border-sky-500/10 flex-wrap text-xs font-mono">
      <span className="flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full ${dot} animate-pulse`} />
        <span className={connected ? 'text-emerald-400' : 'text-red-400'}>
          {connected ? 'CIEL online' : 'offline'}
        </span>
      </span>
      {connected && (
        <>
          <span className="text-sky-500/40">|</span>
          <span className={modeColor}>mode: {mode}</span>
          <span className="text-sky-500/40">|</span>
          <span className="text-sky-300/70">health: <span className={status.system_health >= 0.5 ? 'text-sky-300' : 'text-orange-400'}>{status.system_health.toFixed(3)}</span></span>
          <span className="text-sky-500/40">|</span>
          <span className="text-sky-300/70">coherence: <span className="text-sky-300">{status.coherence_index.toFixed(3)}</span></span>
          <span className="text-sky-500/40">|</span>
          <span className="text-sky-300/70">ethical: <span className={status.ethical_score >= 0.7 ? 'text-emerald-400' : 'text-orange-400'}>{status.ethical_score.toFixed(3)}</span></span>
          <span className="text-sky-500/40">|</span>
          <span className="text-amber-400/80">emotion: {status.dominant_emotion}</span>
          <span className="text-sky-500/40">|</span>
          <span className="text-sky-300/70">soul: {status.soul_invariant.toFixed(3)}</span>
          <a href="http://localhost:5050/portal" target="_blank" rel="noopener noreferrer"
            className="ml-auto text-amber-400/60 hover:text-amber-400 transition-colors">
            CIELweb →
          </a>
        </>
      )}
    </div>
  )
}

// ============================================
// LIVE CHAT TAB
// ============================================
function CIELChatPanel() {
  const { messages, sending, send, reset } = useCIELChat()
  const [input, setInput] = useState('')
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = async () => {
    if (!input.trim() || sending) return
    const text = input; setInput('')
    await send(text)
  }

  return (
    <div className="flex flex-col h-[480px]">
      <div className="flex-1 overflow-y-auto space-y-3 pr-2 mb-3">
        {messages.length === 0 && (
          <p className="text-sky-400/40 text-sm text-center mt-8">
            Czat z CIEL — RAG + metryki live + GGUF model
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === 'assistant' ? '' : 'flex-row-reverse'}`}>
            <div className={`text-xs font-bold font-mono mt-1 w-16 flex-shrink-0 ${m.role === 'assistant' ? 'text-sky-400' : 'text-amber-400 text-right'}`}>
              {m.role === 'assistant' ? 'CIEL' : 'Adrian'}
            </div>
            <div className={`rounded-lg p-3 text-sm max-w-[80%] ${m.role === 'assistant' ? 'glass-navy text-sky-100/90' : 'bg-amber-500/10 border border-amber-500/20 text-amber-100/90'}`}>
              {m.content}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex gap-3">
            <div className="text-xs font-bold font-mono mt-1 w-16 text-sky-400">CIEL</div>
            <div className="glass-navy rounded-lg p-3 text-sm text-sky-400/50 animate-pulse">…</div>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="Wiadomość do CIEL…"
          className="flex-1 bg-slate-800/50 border border-sky-500/20 rounded-lg px-4 py-2 text-sm text-sky-100 placeholder:text-sky-500/30 focus:outline-none focus:border-sky-500/50"
        />
        <Button onClick={handleSend} disabled={sending} size="sm"
          className="bg-amber-500/20 border border-amber-500/30 text-amber-300 hover:bg-amber-500/30">
          Wyślij
        </Button>
        <Button onClick={reset} variant="ghost" size="sm" className="text-sky-500/40 hover:text-sky-400">
          <RotateCcw className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}

// ============================================
// MAIN APP WITH TABS
// ============================================
// ============================================
// LIVE METRICS CARD
// ============================================
function LiveMetricsCard() {
  const { status, mode } = useCIELStatus(30_000)
  const bars = [
    { label: 'Health',    value: status.system_health,   warn: status.system_health < 0.5 },
    { label: 'Coherence', value: status.coherence_index, warn: status.coherence_index < 0.767 },
    { label: 'Ethical',   value: status.ethical_score,   warn: status.ethical_score < 0.7 },
    { label: 'Soul',      value: status.soul_invariant,  warn: false },
  ]
  return (
    <Card className="glass-navy border-sky-500/20 p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-mono text-sky-400/60">Metryki orbitalne — live</span>
        <span className={`text-xs font-mono font-bold ${mode === 'deep' ? 'text-amber-400' : mode === 'standard' ? 'text-sky-400' : 'text-red-400'}`}>{mode}</span>
      </div>
      <div className="space-y-2">
        {bars.map(b => (
          <div key={b.label}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-sky-300/60">{b.label}</span>
              <span className={b.warn ? 'text-orange-400' : 'text-sky-300'}>{b.value.toFixed(3)}</span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all duration-500 ${b.warn ? 'bg-orange-500' : 'bg-gradient-to-r from-sky-500 to-amber-400'}`}
                style={{ width: `${Math.min(b.value * 100, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-2 text-xs">
        <span className="text-sky-300/60">Emotion:</span>
        <span className="text-amber-400 font-medium">{status.dominant_emotion}</span>
        <span className="ml-auto text-sky-300/40">closure: {status.closure_penalty.toFixed(3)}</span>
      </div>
    </Card>
  )
}

function App() {
  const [activeTab, setActiveTab] = useState('ciel_live')

  const tabs = [
    { id: 'ciel_live', label: 'CIEL Live', icon: Brain },
    { id: 'overview', label: 'Overview', icon: Eye },
    { id: 'fields', label: 'Field Engine', icon: Waves },
    { id: 'orbital', label: 'Orbital System', icon: Orbit },
    { id: 'metatime', label: 'Metatime', icon: Timer },
    { id: 'axioms', label: 'Axioms', icon: Shield },
    { id: 'hyperref', label: 'Hyperref', icon: Network },
    { id: 'code', label: 'Implementation', icon: Code },
    { id: 'downloads', label: 'Downloads', icon: Download },
  ]

  return (
    <div className="min-h-screen bg-navy-gradient">
      <CIELStatusBar />
      <HeroSection />

      <section className="py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid grid-cols-5 md:grid-cols-9 gap-1 bg-slate-900/50 p-1 rounded-xl mb-8">
              {tabs.map(tab => (
                <TabsTrigger
                  key={tab.id}
                  value={tab.id}
                  className="data-[state=active]:bg-gradient-to-b data-[state=active]:from-amber-500/20 data-[state=active]:to-amber-500/5 data-[state=active]:border-b-2 data-[state=active]:border-amber-400 data-[state=active]:text-amber-300 text-sky-400/70 text-xs md:text-sm py-3"
                >
                  <tab.icon className="w-4 h-4 mr-1 hidden md:inline" />
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>

            {/* CIEL LIVE TAB */}
            <TabsContent value="ciel_live" className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="glass-navy border-sky-500/20">
                  <CardHeader>
                    <CardTitle className="gradient-text-sky flex items-center gap-2">
                      <Brain className="w-5 h-5" /> Czat z CIEL
                    </CardTitle>
                    <CardDescription className="text-sky-300/60">
                      GGUF model + RAG pamięci + metryki orbitalne
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <CIELChatPanel />
                  </CardContent>
                </Card>

                <div className="space-y-4">
                  <LiveMetricsCard />
                  <Card className="glass-navy border-sky-500/20 p-4">
                    <div className="text-xs font-mono text-sky-400/60 mb-3">Szybkie akcje</div>
                    <div className="flex flex-wrap gap-2">
                      {[
                        { label: '→ Archiwum', href: 'http://localhost:5050/portal/archive' },
                        { label: '→ Pamięć', href: 'http://localhost:5050/portal/memory' },
                        { label: '→ Plany', href: 'http://localhost:5050/portal/plans' },
                        { label: '→ Hunchy', href: 'http://localhost:5050/portal/hunches' },
                        { label: '→ Projekty', href: 'http://localhost:5050/portal/projects' },
                        { label: '→ Rutyny', href: 'http://localhost:5050/portal/routines' },
                      ].map(l => (
                        <a key={l.href} href={l.href} target="_blank" rel="noopener noreferrer"
                          className="px-3 py-1.5 rounded-lg text-xs font-mono bg-sky-500/10 border border-sky-500/20 text-sky-300 hover:bg-sky-500/20 transition-colors">
                          {l.label}
                        </a>
                      ))}
                    </div>
                  </Card>
                </div>
              </div>
            </TabsContent>

            {/* OVERVIEW TAB */}
            <TabsContent value="overview" className="space-y-6">
              <Card className="glass-navy border-sky-500/20">
                <CardHeader>
                  <CardTitle className="gradient-text-gold text-2xl">CIEL/0 Framework Overview</CardTitle>
                  <CardDescription className="text-sky-300/60">
                    Consciousness-Integrated Evolutionary Lambda — Theory of Everything
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-sky-300">Core Philosophy</h3>
                      <p className="text-sky-200/70 text-sm leading-relaxed">
                        CIEL/0 proposes that reality emerges from the resonance between symbolic possibility 
                        (S) and intentional actualization (I). The framework unifies quantum mechanics, 
                        consciousness studies, and cosmology through a single mathematical formalism.
                      </p>
                      <div className="code-block text-xs">
                        <span className="text-amber-400">R(S,I)</span> = |⟨S|I⟩|² — The Resonance Function
                      </div>
                    </div>
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-sky-300">Key Innovations</h3>
                      <ul className="space-y-2 text-sm text-sky-200/70">
                        <li className="flex items-start gap-2">
                          <Star className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                          <span>Emergent mass from symbolic misalignment</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Star className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                          <span>Time as entropy gradient, not fundamental dimension</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Star className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                          <span>Dynamic Lambda0 operator coupling consciousness to cosmology</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Star className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                          <span>Zeta-Riemann modulation of quantum phases</span>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <Separator className="bg-sky-500/20" />

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <Card className="glass-navy p-4 text-center card-hover">
                      <Brain className="w-8 h-8 text-sky-400 mx-auto mb-2" />
                      <div className="text-amber-400 font-bold">I(x,t)</div>
                      <div className="text-xs text-sky-300/60">Intention Field</div>
                    </Card>
                    <Card className="glass-navy p-4 text-center card-hover">
                      <Timer className="w-8 h-8 text-sky-400 mx-auto mb-2" />
                      <div className="text-amber-400 font-bold">τ(x,t)</div>
                      <div className="text-xs text-sky-300/60">Temporal Field</div>
                    </Card>
                    <Card className="glass-navy p-4 text-center card-hover">
                      <Target className="w-8 h-8 text-sky-400 mx-auto mb-2" />
                      <div className="text-amber-400 font-bold">R(S,I)</div>
                      <div className="text-xs text-sky-300/60">Resonance</div>
                    </Card>
                    <Card className="glass-navy p-4 text-center card-hover">
                      <Atom className="w-8 h-8 text-sky-400 mx-auto mb-2" />
                      <div className="text-amber-400 font-bold">m(S,I)</div>
                      <div className="text-xs text-sky-300/60">Emergent Mass</div>
                    </Card>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* FIELD ENGINE TAB */}
            <TabsContent value="fields" className="space-y-6">
              <Card className="glass-navy border-sky-500/20">
                <CardHeader>
                  <CardTitle className="gradient-text-gold text-2xl flex items-center gap-2">
                    <Waves className="w-6 h-6" />
                    Field Simulation Engine
                  </CardTitle>
                  <CardDescription className="text-sky-300/60">
                    Interactive visualization of CIEL/0 field dynamics
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <FieldSimulationEngine />
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-3 gap-4">
                <Card className="glass-navy p-4">
                  <h4 className="text-amber-400 font-semibold mb-2">Intention Field I(x,t)</h4>
                  <p className="text-xs text-sky-200/60">
                    Complex scalar field representing conscious intent. Evolves through nonlinear 
                    dynamics with phase-coupled temporal interactions.
                  </p>
                </Card>
                <Card className="glass-navy p-4">
                  <h4 className="text-amber-400 font-semibold mb-2">Resonance R(S,I)</h4>
                  <p className="text-xs text-sky-200/60">
                    Inner product between symbolic and intention states. Quantifies the coherence 
                    of reality. Bounded in (0,1).
                  </p>
                </Card>
                <Card className="glass-navy p-4">
                  <h4 className="text-amber-400 font-semibold mb-2">Emergent Mass</h4>
                  <p className="text-xs text-sky-200/60">
                    Mass arises from misalignment: m² = μ₀[1 - R(S,I)]. No Higgs mechanism required 
                    at fundamental level.
                  </p>
                </Card>
              </div>
            </TabsContent>

            {/* ORBITAL TAB */}
            <TabsContent value="orbital" className="space-y-6">
              <Card className="glass-navy border-sky-500/20">
                <CardHeader>
                  <CardTitle className="gradient-text-gold text-2xl flex items-center gap-2">
                    <Orbit className="w-6 h-6" />
                    Orbital System Visualization
                  </CardTitle>
                  <CardDescription className="text-sky-300/60">
                    OORP: Orbital Orchestrated Reduction Pipeline
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <OrbitalEngine />
                </CardContent>
              </Card>

              <Card className="glass-navy p-6">
                <h3 className="text-lg font-semibold text-amber-400 mb-4">Orbital Methodology</h3>
                <div className="grid md:grid-cols-2 gap-6 text-sm">
                  <div className="space-y-3">
                    <p className="text-sky-200/70">
                      The Orbital System provides a framework for organizing entities in 
                      hyperspace with semantic mass, subjective time, and orbital assignment.
                    </p>
                    <div className="code-block text-xs">
                      <div className="text-sky-400">relation → orbital superposition</div>
                      <div className="text-sky-400">  → orchestration → reduction</div>
                      <div className="text-sky-400">  → memory update</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sky-300/70">
                      <span>Semantic Mass:</span>
                      <span className="text-amber-400">M_sem = αM_EC + βM_ZS + χC_dep</span>
                    </div>
                    <div className="flex justify-between text-sky-300/70">
                      <span>Subjective Time:</span>
                      <span className="text-amber-400">Δτ = Δt · g(r, C, Δ, m, A)</span>
                    </div>
                    <div className="flex justify-between text-sky-300/70">
                      <span>Winding:</span>
                      <span className="text-amber-400">w(N) = (1/2π) Σ Δφ · (Δt/Δτ)</span>
                    </div>
                    <div className="flex justify-between text-sky-300/70">
                      <span>Orbit Law:</span>
                      <span className="text-amber-400">T² ∝ a³/A_eff</span>
                    </div>
                  </div>
                </div>
              </Card>
            </TabsContent>

            {/* METATIME TAB */}
            <TabsContent value="metatime" className="space-y-6">
              <Card className="glass-navy border-sky-500/20">
                <CardHeader>
                  <CardTitle className="gradient-text-gold text-2xl flex items-center gap-2">
                    <Infinity className="w-6 h-6" />
                    Metatime Unified Framework
                  </CardTitle>
                  <CardDescription className="text-sky-300/60">
                    Time as a topological field on Kähler manifold M_time ≅ S²
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-sky-300">Core Insight</h3>
                      <p className="text-sky-200/70 text-sm leading-relaxed">
                        Time itself is a topological field whose geometric structure generates 
                        the fermion spectrum through iterative Collatz dynamics seeded by twin-prime 
                        arithmetic—while simultaneously solving the cosmological constant problem 
                        through Berry phase quantization.
                      </p>
                      <div className="code-block text-xs space-y-1">
                        <div className="text-amber-400">Twin Primes → Collatz → τᵢ eigenvalues</div>
                        <div className="text-sky-400">  → Berry Phases → Topological Corrections</div>
                        <div className="text-amber-400">  → Fermion Masses mᵢ = κ·τᵢ^α·Fᵢ</div>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-sky-300">Precision Results</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center p-2 glass-navy rounded">
                          <span className="text-sky-300/70 text-sm">Charged Leptons (e,μ,τ)</span>
                          <Badge className="badge-strict">0.0% Error</Badge>
                        </div>
                        <div className="flex justify-between items-center p-2 glass-navy rounded">
                          <span className="text-sky-300/70 text-sm">Light Quarks (u,d,s)</span>
                          <Badge className="badge-strict">0.04% Error</Badge>
                        </div>
                        <div className="flex justify-between items-center p-2 glass-navy rounded">
                          <span className="text-sky-300/70 text-sm">Heavy Quarks (c,b,t)</span>
                          <Badge className="badge-strict">0.1% Error</Badge>
                        </div>
                        <div className="flex justify-between items-center p-2 glass-navy rounded">
                          <span className="text-sky-300/70 text-sm">Neutrino Δm²₃₁</span>
                          <Badge className="badge-strict">Exact Match</Badge>
                        </div>
                      </div>
                    </div>
                  </div>

                  <Separator className="bg-sky-500/20" />

                  <div>
                    <h3 className="text-lg font-semibold text-amber-400 mb-4">Falsifiable Predictions (2026-2030)</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      <Card className="glass-navy p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Microscope className="w-5 h-5 text-sky-400" />
                          <span className="text-amber-400 font-semibold">DUNE (2027-28)</span>
                        </div>
                        <p className="text-xs text-sky-200/60">
                          CP resonance at E₀ = 0.63 GeV (±5%). Discrete resonance ladder 
                          from linking numbers k = 0,1,2.
                        </p>
                      </Card>
                      <Card className="glass-navy p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Compass className="w-5 h-5 text-sky-400" />
                          <span className="text-amber-400 font-semibold">Simons Obs (2026-27)</span>
                        </div>
                        <p className="text-xs text-sky-200/60">
                          CMB low-ℓ power enhancement: 2.7× over ΛCDM at ℓ ~ 50-100.
                        </p>
                      </Card>
                      <Card className="glass-navy p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Layers className="w-5 h-5 text-sky-400" />
                          <span className="text-amber-400 font-semibold">Accordion BEC (2026-27)</span>
                        </div>
                        <p className="text-xs text-sky-200/60">
                          Multi-site soliton phase sum: |Σ e^(iϕⱼ)| &lt; 0.11 (topology constraint).
                        </p>
                      </Card>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* AXIOMS TAB */}
            <TabsContent value="axioms" className="space-y-6">
              <Card className="glass-navy border-sky-500/20">
                <CardHeader>
                  <CardTitle className="gradient-text-gold text-2xl flex items-center gap-2">
                    <Shield className="w-6 h-6" />
                    The Six Axioms of CIEL
                  </CardTitle>
                  <CardDescription className="text-sky-300/60">
                    Constitutional principles governing the framework
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { id: 'L0', name: 'Perfect Coherence Forbidden', desc: 'R(S,I) < 1 — Complete alignment is prohibited, ensuring dynamic evolution.', status: 'strict' },
                      { id: 'L1', name: 'Resonance Boundedness', desc: 'R(S,I) ∈ (0,1) — Strictly bounded, maintaining information conservation.', status: 'strict' },
                      { id: 'L2', name: 'Intention-Symbolic Coupling', desc: '∂_tS ∝ I — Symbolic states evolve in response to intention fields.', status: 'strict' },
                      { id: 'L3', name: 'Time as Entropy Gradient', desc: 'T^μ = −∇^μS_res — Temporal flow emerges from symbolic entropy.', status: 'strict' },
                      { id: 'L4', name: 'Life Integrity Preservation', desc: '∮_C R(S,I) ≥ R_min — Coherence must be maintained above threshold.', status: 'strict' },
                      { id: 'L5', name: 'Mass from Misalignment', desc: 'm² ∝ (1 − R) — Mass emerges from misalignment between S and I.', status: 'strict' },
                    ].map((axiom) => (
                      <Card key={axiom.id} className="glass-navy p-4 card-hover">
                        <div className="flex items-start gap-4">
                          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-500/30 to-amber-600/10 flex items-center justify-center flex-shrink-0 border border-amber-500/30">
                            <span className="text-amber-400 font-bold">{axiom.id}</span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-1">
                              <h4 className="text-lg font-semibold text-sky-200">{axiom.name}</h4>
                              <Badge className={axiom.status === 'strict' ? 'badge-strict' : 'badge-candidate'}>
                                {axiom.status === 'strict' ? '✓ STRICTE' : 'Candidate'}
                              </Badge>
                            </div>
                            <p className="text-sky-300/60 text-sm">{axiom.desc}</p>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* HYPERREF TAB */}
            <TabsContent value="hyperref" className="space-y-6">
              <Card className="glass-navy border-sky-500/20">
                <CardHeader>
                  <CardTitle className="gradient-text-gold text-2xl flex items-center gap-2">
                    <Network className="w-6 h-6" />
                    Hyperref Nonlocal Indexing System
                  </CardTitle>
                  <CardDescription className="text-sky-300/60">
                    ID + Cards + Catalogs + Graphs + Anchors + Crossref + Audit
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid md:grid-cols-4 gap-4">
                    {[
                      { title: 'Inventory Layer', desc: 'Physical repo mapping: files, folders, hashes, types', icon: Database },
                      { title: 'Card Layer', desc: 'Object cards: ID, path, type, dependencies, provenance', icon: FileText },
                      { title: 'Hyperref Layer', desc: 'Relation graphs: defines, depends_on, uses, inherits', icon: GitBranch },
                      { title: 'Audit Layer', desc: 'Defect detection: orphans, dead links, inconsistencies', icon: BarChart3 },
                    ].map((layer) => (
                      <Card key={layer.title} className="glass-navy p-4 text-center card-hover">
                        <layer.icon className="w-8 h-8 text-sky-400 mx-auto mb-3" />
                        <h4 className="text-amber-400 font-semibold text-sm mb-2">{layer.title}</h4>
                        <p className="text-xs text-sky-300/60">{layer.desc}</p>
                      </Card>
                    ))}
                  </div>

                  <div className="glass-navy rounded-lg p-4">
                    <h4 className="text-amber-400 font-semibold mb-3">Core Principle</h4>
                    <p className="text-sky-200/70 text-sm">
                      <span className="text-amber-400 font-mono">Without ID there is no holonomy.</span> Names may change. 
                      IDs do not. The system transforms a loose collection of files into a field of entities with 
                      persistent IDs, local and non-local anchoring, provenance trails, dependency relations, 
                      and measurable cross-reference state.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* CODE TAB */}
            <TabsContent value="code" className="space-y-6">
              <Card className="glass-navy border-sky-500/20">
                <CardHeader>
                  <CardTitle className="gradient-text-gold text-2xl flex items-center gap-2">
                    <Code className="w-6 h-6" />
                    Implementation
                  </CardTitle>
                  <CardDescription className="text-sky-300/60">
                    Python framework with full SI unit consistency
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="code-block text-sm overflow-x-auto">
                    <pre className="text-sky-200/80">
{`class CIEL0Framework:
    """Complete implementation of Adrian Lipa's CIEL/0 Theory of Everything"""
    
    def __init__(self, params: CIELParameters, grid_size: int = 64):
        self.params = params
        self.grid_size = grid_size
        self._initialize_fields()
    
    def compute_resonance(self, S: np.ndarray, I: np.ndarray) -> np.ndarray:
        """R(S,I) = |⟨S|I⟩|² - The coherence of reality"""
        inner_product = np.conj(S) * I
        return np.abs(inner_product) ** 2
    
    def compute_symbolic_mass(self, S: np.ndarray, I: np.ndarray) -> np.ndarray:
        """m²(S,I) = μ₀[1 - R(S,I)] - Mass from misalignment"""
        R = self.compute_resonance(S, I)
        mass_squared = self.params.m_planck**2 * (1 - R)
        return np.sqrt(np.maximum(mass_squared, 0))
    
    def evolution_step(self, dt: float = 0.1):
        """One step of unified field evolution"""
        self.R_field = self.compute_resonance(self.S_field, self.I_field)
        self.mass_field = self.compute_symbolic_mass(self.S_field, self.I_field)
        self.I_field = self.compute_intention_dynamics(self.I_field, self.tau_field, dt)
        self.tau_field = self.compute_temporal_dynamics(self.tau_field, self.I_field, dt)`}
                    </pre>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mt-6">
                    <div className="glass-navy rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-amber-400">1000+</div>
                      <div className="text-sky-300/60 text-sm">Lines of Code</div>
                    </div>
                    <div className="glass-navy rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-sky-400">15+</div>
                      <div className="text-sky-300/60 text-sm">Core Functions</div>
                    </div>
                    <div className="glass-navy rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-amber-400">8</div>
                      <div className="text-sky-300/60 text-sm">Field Types</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* DOWNLOADS TAB */}
            <TabsContent value="downloads" className="space-y-6">
              <Card className="glass-navy border-sky-500/20">
                <CardHeader>
                  <CardTitle className="gradient-text-gold text-2xl flex items-center gap-2">
                    <Download className="w-6 h-6" />
                    Project Files
                  </CardTitle>
                  <CardDescription className="text-sky-300/60">
                    All source files, documentation and papers — download freely
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Python Scripts */}
                  <div>
                    <h3 className="text-lg font-semibold text-amber-400 mb-3 flex items-center gap-2">
                      <FileCode className="w-5 h-5" />
                      Python Scripts
                    </h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      {[
                        { name: 'cielnofft.py', desc: 'CIEL/0 Complete Framework — Full field simulation', icon: FileCode },
                        { name: 'cielquantum.py', desc: 'Quantum-Relativistic Kernel — Quantized reality', icon: FileCode },
                        { name: 'originsphaseholoext.py', desc: 'Universal Origin-of-Life Simulator — 5 scenarios', icon: FileCode },
                        { name: 'originsHolo2.py', desc: 'Holographic origins simulator v2', icon: FileCode },
                        { name: 'Proof-of-concept2.py', desc: 'Merged sweep + 5-scenario topo simulator', icon: FileCode },
                        { name: 'gluons.py', desc: 'Gluon dynamics simulation', icon: FileCode },
                        { name: 'Solver.py', desc: 'Equation solver component', icon: FileCode },
                      ].map((file) => (
                        <a key={file.name} href={`/files/${file.name}`} download className="no-underline">
                          <Card className="glass-navy p-3 card-hover flex items-center gap-3 cursor-pointer">
                            <file.icon className="w-8 h-8 text-amber-400 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="text-sky-200 font-medium text-sm truncate">{file.name}</div>
                              <div className="text-sky-400/50 text-xs truncate">{file.desc}</div>
                            </div>
                            <Download className="w-5 h-5 text-sky-500/50 flex-shrink-0" />
                          </Card>
                        </a>
                      ))}
                    </div>
                  </div>

                  <Separator className="bg-sky-500/20" />

                  {/* Documentation */}
                  <div>
                    <h3 className="text-lg font-semibold text-amber-400 mb-3 flex items-center gap-2">
                      <ScrollText className="w-5 h-5" />
                      Documentation (Markdown)
                    </h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      {[
                        { name: 'HYPERREF_NONLOCAL_INDEXING_SYSTEM.md', desc: 'Hyperref nonlocal indexing system spec', icon: ScrollText },
                        { name: 'KONSTYTUCJA_ROBOCZA_CIEL.md', desc: 'Working Constitution of CIEL', icon: BookMarked },
                        { name: 'PELNA_METODOLOGIA_SYSTEMU_ORBITALNEGO.md', desc: 'Full Orbital System Methodology', icon: ScrollText },
                        { name: 'TFIR_optimization_pass_4.md', desc: 'TFIR Optimization Pass 4', icon: ScrollText },
                        { name: 'METATIME_UNIFIED_THEORY_SYNTHESIS.md', desc: 'Metatime Unified Theory Synthesis', icon: ScrollText },
                      ].map((file) => (
                        <a key={file.name} href={`/files/${file.name}`} download className="no-underline">
                          <Card className="glass-navy p-3 card-hover flex items-center gap-3 cursor-pointer">
                            <file.icon className="w-8 h-8 text-sky-400 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="text-sky-200 font-medium text-sm truncate">{file.name}</div>
                              <div className="text-sky-400/50 text-xs truncate">{file.desc}</div>
                            </div>
                            <Download className="w-5 h-5 text-sky-500/50 flex-shrink-0" />
                          </Card>
                        </a>
                      ))}
                    </div>
                  </div>

                  <Separator className="bg-sky-500/20" />

                  {/* Papers & PDFs */}
                  <div>
                    <h3 className="text-lg font-semibold text-amber-400 mb-3 flex items-center gap-2">
                      <FileType className="w-5 h-5" />
                      Papers & PDFs
                    </h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      {[
                        { name: 'TheFundamentalTheory.pdf', desc: 'The Fundamental Theory paper', icon: FileType },
                        { name: 'Metatimenew.pdf', desc: 'Metatime theory paper', icon: FileType },
                        { name: 'NoparamSM1.pdf', desc: 'No-Param Standard Model v1', icon: FileType },
                        { name: 'NoparamSM2.pdf', desc: 'No-Param Standard Model v2', icon: FileType },
                        { name: 'mentalism6.pdf', desc: 'Mentalism framework paper', icon: FileType },
                      ].map((file) => (
                        <a key={file.name} href={`/files/${file.name}`} download className="no-underline">
                          <Card className="glass-navy p-3 card-hover flex items-center gap-3 cursor-pointer">
                            <file.icon className="w-8 h-8 text-rose-400 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="text-sky-200 font-medium text-sm truncate">{file.name}</div>
                              <div className="text-sky-400/50 text-xs truncate">{file.desc}</div>
                            </div>
                            <Download className="w-5 h-5 text-sky-500/50 flex-shrink-0" />
                          </Card>
                        </a>
                      ))}
                    </div>
                  </div>

                  <Separator className="bg-sky-500/20" />

                  {/* Text Files */}
                  <div>
                    <h3 className="text-lg font-semibold text-amber-400 mb-3 flex items-center gap-2">
                      <FileText className="w-5 h-5" />
                      Text Files
                    </h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      {[
                        { name: 'gluonsfull.txt', desc: 'Full gluon specification', icon: FileText },
                        { name: 'noparamSMsolver.txt', desc: 'No-Param SM solver specification', icon: FileText },
                      ].map((file) => (
                        <a key={file.name} href={`/files/${file.name}`} download className="no-underline">
                          <Card className="glass-navy p-3 card-hover flex items-center gap-3 cursor-pointer">
                            <file.icon className="w-8 h-8 text-emerald-400 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="text-sky-200 font-medium text-sm truncate">{file.name}</div>
                              <div className="text-sky-400/50 text-xs truncate">{file.desc}</div>
                            </div>
                            <Download className="w-5 h-5 text-sky-500/50 flex-shrink-0" />
                          </Card>
                        </a>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-12 px-4 border-t border-sky-500/20">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="text-3xl font-bold gradient-text-gold">CIEL</span>
            <span className="text-3xl font-bold text-sky-400">/</span>
            <span className="text-3xl font-bold gradient-text-sky">0</span>
          </div>
          <p className="text-sky-300/50 mb-6">
            Consciousness-Integrated Evolutionary Lambda — Theory of Everything
          </p>
          <Separator className="bg-sky-500/20 mb-6" />
          <div className="flex flex-wrap justify-center gap-6 text-sm text-sky-400/50">
            <span>© 2025 Adrian Lipa</span>
            <span>MIT License</span>
            <span>Python 3.12+</span>
            <span>NumPy & SciPy</span>
          </div>
          <p className="mt-6 text-xs text-sky-500/40 italic">
            "Reality is the resonance between what is symbolically possible and intentionally desired."
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
