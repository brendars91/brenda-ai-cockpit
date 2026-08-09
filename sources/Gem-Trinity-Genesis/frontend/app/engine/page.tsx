"use client"
import Link from 'next/link'
import { ArrowLeft, Activity, Play, Cpu, MemoryStick, Zap, Trash2, HelpCircle, Wrench, Server, FileText } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, Suspense, useCallback } from 'react'
import { useSearchParams } from 'next/navigation'
import { IOViewerModal, IOViewerButton } from '@/components/IOViewerModal'
import { TransferredResourcesPanel, GitHubStatusBadge, ProcessingTracker } from '@/components/index'

function EngineContent() {
    const searchParams = useSearchParams()
    const preselectedAgent = searchParams.get('agent')

    const [agents, setAgents] = useState<any[]>([])
    const [projects, setProjects] = useState<any[]>([])
    const [selectedAgent, setSelectedAgent] = useState<string>(preselectedAgent || '')
    const [selectedProject, setSelectedProject] = useState<any>(null)
    const [isExecuting, setIsExecuting] = useState(false)
    const [isDeleting, setIsDeleting] = useState(false)
    const [logs, setLogs] = useState<string[]>([])
    const [telemetry, setTelemetry] = useState({ cpu: 0, memory: 0, tokens: 0, latency: 0 })
    const [showHelp, setShowHelp] = useState(false)
    
    // IO Viewer State
    const [showIOViewer, setShowIOViewer] = useState(false)
    const [ioData, setIOData] = useState<any>(null)

    const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const API_BASE = RAW_URL.replace(/\/api\/?$/, '') + '/api';

    const fetchData = useCallback(async () => {
        try {
            const [agentsRes, projectsRes] = await Promise.all([
                fetch(`${API_BASE}/builder/agents`),
                fetch(`${API_BASE}/projects`)
            ])
            const agentsData = await agentsRes.json()
            const projectsData = await projectsRes.json()
            setAgents(agentsData.agents || [])
            setProjects(projectsData.projects || [])
        } catch (err) {
            console.error(err)
        }
    }, [API_BASE])

    useEffect(() => {
        fetchData()
    }, [fetchData])

    useEffect(() => {
        if (preselectedAgent) {
            setSelectedAgent(preselectedAgent)
            // Find project details
            const agent = agents.find(a => a.id === preselectedAgent)
            if (agent) setSelectedProject(agent)
        }
    }, [preselectedAgent, agents])

    const handleAgentChange = (agentId: string) => {
        setSelectedAgent(agentId)
        const agent = agents.find(a => a.id === agentId)
        setSelectedProject(agent)
    }

    const handleExecute = async () => {
        if (!selectedAgent) return
        setIsExecuting(true)
        setLogs([])

        // Get task from the agent's context
        const task = selectedProject?.name || 'Execute assigned task'

        try {
            const res = await fetch(`${API_BASE}/engine/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent_id: selectedAgent, task, stream: true })
            })

            const reader = res.body?.getReader()
            const decoder = new TextDecoder()

            while (reader) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value)
                const lines = chunk.split('\n').filter(l => l.trim())

                lines.forEach(line => {
                    try {
                        const data = JSON.parse(line)
                        if (data.type === 'log') {
                            setLogs(prev => [...prev, data.message])
                        } else if (data.type === 'metric') {
                            setTelemetry({
                                cpu: data.cpu || 0,
                                memory: data.memory || 0,
                                tokens: data.tokens || 0,
                                latency: data.latency || 0
                            })
                        } else if (data.type === 'result') {
                            setLogs(prev => [...prev, '─'.repeat(40), data.output])
                            
                            // Set IO Data when result is ready
                            setIOData({
                                input: {
                                    agent_id: selectedAgent,
                                    task: task,
                                    context: selectedProject
                                },
                                output: {
                                    result: data.output,
                                },
                                metadata: {
                                    processingType: 'hybrid',
                                    tokensUsed: telemetry.tokens,
                                    processingTimeMs: telemetry.latency,
                                    phase: 'Engine (Execution)',
                                    model: selectedProject?.model
                                }
                            })
                        }
                    } catch (e) { }
                })
            }
        } catch (err) {
            console.error(err)
            setLogs(prev => [...prev, `Error: ${err}`])
        } finally {
            setIsExecuting(false)
        }
    }

    const handleDeleteProject = async () => {
        if (!selectedAgent || !confirm('¿Estás seguro de que quieres eliminar este proyecto? Esta acción no se puede deshacer.')) return

        setIsDeleting(true)
        try {
            const res = await fetch(`${API_BASE}/projects/${selectedAgent}`, { method: 'DELETE' })
            const data = await res.json()
            if (data.status === 'success' || data.deleted.length > 0) {
                setSelectedAgent('')
                setSelectedProject(null)
                await fetchData()
                setLogs(prev => [...prev, '✅ Proyecto eliminado correctamente'])
            }
        } catch (err) {
            console.error(err)
            setLogs(prev => [...prev, `Error al eliminar: ${err}`])
        } finally {
            setIsDeleting(false)
        }
    }

    return (
        <main className="min-h-screen p-8 lg:p-16 max-w-7xl mx-auto">
            {/* HEADER */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <Link href="/" className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-4 transition-colors">
                    <ArrowLeft className="w-4 h-4" />
                    Volver al Dashboard
                </Link>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                            <Activity className="w-6 h-6 text-emerald-600" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold font-heading text-foreground">Engine</h1>
                            <p className="text-muted-foreground text-sm flex items-center gap-2">
                                Ejecuta agentes de IA y monitorea telemetría en tiempo real
                                <span className="mx-2">|</span>
                                <GitHubStatusBadge />
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={() => setShowHelp(!showHelp)}
                        className="p-2 rounded-lg hover:bg-muted transition-colors"
                        title="Ayuda"
                    >
                        <HelpCircle className="w-6 h-6 text-muted-foreground" />
                    </button>
                </div>
            </motion.header>

            {/* HELP MODAL */}
            <AnimatePresence>
                {showHelp && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="mb-6 p-6 bg-card border border-border rounded-2xl shadow-lg"
                    >
                        <h3 className="text-lg font-semibold mb-3">¿Cómo funciona Engine?</h3>
                        <div className="space-y-3 text-sm text-muted-foreground">
                            <p><strong>Engine</strong> ejecuta los agentes compilados y muestra el resultado en tiempo real.</p>
                            <p><strong>Selecciona un Proyecto:</strong> Elige el proyecto que quieres ejecutar desde el dropdown.</p>
                            <p><strong>Skills en uso:</strong> Muestra qué habilidades usará el agente.</p>
                            <p><strong>MCPs activos:</strong> Protocolos de comunicación que se activarán.</p>
                            <p><strong>Eliminar Proyecto:</strong> Borra permanentemente el proyecto y todos sus artifacts.</p>
                            <p><strong>Logs:</strong> Salida en tiempo real de la ejecución del agente.</p>
                        </div>
                        <button onClick={() => setShowHelp(false)} className="mt-4 text-sm text-primary hover:underline">
                            Cerrar ayuda
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* LEFT: EXECUTION PANEL */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            <Play className="w-5 h-5 text-emerald-500" />
                            Panel de Ejecución
                        </h2>

                        <div className="space-y-4">
                            {/* Project Selector */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Selecciona Proyecto</label>
                                <select
                                    value={selectedAgent}
                                    onChange={(e) => handleAgentChange(e.target.value)}
                                    className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground"
                                >
                                    <option value="">Elige un proyecto...</option>
                                    {agents.map((agent) => (
                                        <option key={agent.id} value={agent.id}>
                                            {agent.name} ({agent.model})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {/* Project Summary */}
                            {selectedProject && (
                                <div className="p-4 bg-muted/50 rounded-xl">
                                    <h4 className="font-medium text-sm mb-2">Resumen del Proyecto</h4>
                                    <p className="text-xs text-muted-foreground mb-1">ID: {selectedProject.id?.slice(0, 16)}...</p>
                                    <p className="text-xs text-muted-foreground">Modelo: {selectedProject.model}</p>
                                </div>
                            )}

                            <div className="flex gap-3">
                                <button
                                    onClick={handleExecute}
                                    disabled={!selectedAgent || isExecuting}
                                    className="flex-1 px-6 py-3 rounded-lg bg-emerald-600 text-white font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
                                >
                                    {isExecuting ? 'Ejecutando...' : 'Ejecutar Agente'}
                                </button>
                                {selectedAgent && (
                                    <button
                                        onClick={handleDeleteProject}
                                        disabled={isDeleting}
                                        className="px-4 py-3 rounded-lg bg-red-500/10 text-red-600 font-semibold hover:bg-red-500/20 disabled:opacity-50 transition-colors flex items-center gap-2"
                                        title="Eliminar proyecto"
                                    >
                                        <Trash2 className="w-5 h-5" />
                                        {isDeleting ? '...' : 'Eliminar'}
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* LOG STREAM */}
                    <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold">Logs en Tiempo Real</h2>
                            
                            {/* IO Viewer Button */}
                            <IOViewerButton 
                                onClick={() => setShowIOViewer(true)} 
                                label="Ver I/O Ejecución"
                            />
                        </div>
                        <div className="h-64 overflow-auto bg-slate-950 text-green-400 rounded-lg p-4 font-mono text-xs">
                            {logs.length === 0 ? (
                                <span className="text-muted-foreground">Los logs aparecerán aquí durante la ejecución...</span>
                            ) : (
                                logs.map((log, idx) => (
                                    <div key={idx} className="mb-1">{log}</div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* RIGHT: TELEMETRY & CONTEXT */}
                <div className="space-y-4">
                    {/* Transferred Resources Panel - Only show if project selected */}
                    {selectedProject || selectedAgent ? (
                        <>
                            <TransferredResourcesPanel
                                projectName={selectedProject?.name || selectedAgent || 'Proyecto'}
                                skills={(selectedProject?.tools || selectedProject?.capabilities || []).map((s: string) => ({
                                    id: s,
                                    name: s,
                                    description: `Skill transferida: ${s}`,
                                    adapted: true,
                                    adaptedContext: selectedProject?.name
                                }))}
                                mcps={[
                                    { id: "filesystem", name: "Filesystem", description: "Acceso a sistema local" },
                                    { id: "context7", name: "Context7", description: "Documentación y contexto" },
                                    ...(selectedProject?.model?.includes('gemini') ? [{ id: "gemini-api", name: "Gemini API", description: "Modelo LLM backend" }] : [])
                                ]}
                            />
                            
                            {/* Processing Tracker - Visual Deterministic vs LLM */}
                            <ProcessingTracker 
                                compact={true}
                                processingType="hybrid"
                            />
                        </>
                    ) : (
                        <div className="bg-card border border-border rounded-2xl p-8 shadow-sm text-center">
                            <Server className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
                            <h3 className="text-lg font-semibold text-muted-foreground">Esperando Agente</h3>
                            <p className="text-sm text-muted-foreground/60 mt-1">
                                Selecciona un proyecto para ver sus recursos transferidos y métricas de procesamiento.
                            </p>
                        </div>
                    )}

                    {/* Telemetry */}
                    <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
                        <h2 className="text-lg font-semibold mb-4">Telemetría</h2>

                        <div className="space-y-4">
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm flex items-center gap-2">
                                        <Cpu className="w-4 h-4 text-blue-500" />
                                        CPU
                                    </span>
                                    <span className="text-sm font-mono">{telemetry.cpu.toFixed(1)}%</span>
                                </div>
                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                    <div className="h-full bg-blue-500 transition-all" style={{ width: `${telemetry.cpu}%` }} />
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm flex items-center gap-2">
                                        <MemoryStick className="w-4 h-4 text-purple-500" />
                                        Memory
                                    </span>
                                    <span className="text-sm font-mono">{telemetry.memory}MB</span>
                                </div>
                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                    <div className="h-full bg-purple-500 transition-all" style={{ width: `${Math.min((telemetry.memory / 2048) * 100, 100)}%` }} />
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm flex items-center gap-2">
                                        <Zap className="w-4 h-4 text-amber-500" />
                                        Tokens
                                    </span>
                                    <span className="text-sm font-mono">{telemetry.tokens}</span>
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm">Latency</span>
                                    <span className="text-sm font-mono">{telemetry.latency}ms</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* IO Viewer Modal */}
            <IOViewerModal
                isOpen={showIOViewer}
                onClose={() => setShowIOViewer(false)}
                title="Engine - Execution Process"
                data={ioData || { input: {}, output: {} }}
            />
        </main>
    )
}

// Wrapper with Suspense for useSearchParams
export default function EnginePage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            </div>
        }>
            <EngineContent />
        </Suspense>
    )
}
