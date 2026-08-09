"use client"
import Link from 'next/link'
import { ArrowLeft, Layers, Clock, CheckCircle, XCircle, Loader, Eye, ChevronRight, HelpCircle, Wrench, Server, FileText } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { IOViewerModal, IOViewerButton } from '@/components/IOViewerModal'
import { GitHubStatusBadge } from '@/components/index'

export default function BuilderPage() {
    const router = useRouter()
    const [queue, setQueue] = useState<any[]>([])
    const [agents, setAgents] = useState<any[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [selectedAgent, setSelectedAgent] = useState<any>(null)
    const [showHelp, setShowHelp] = useState(false)
    
    // IO Viewer State
    const [showIOViewer, setShowIOViewer] = useState(false)
    const [ioData, setIOData] = useState<any>(null)

    const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const API_BASE = RAW_URL.replace(/\/api\/?$/, '') + '/api';

    const fetchData = useCallback(async () => {
        try {
            const [queueRes, agentsRes] = await Promise.all([
                fetch(`${API_BASE}/builder/queue`),
                fetch(`${API_BASE}/builder/agents`)
            ])
            const queueData = await queueRes.json()
            const agentsData = await agentsRes.json()
            setQueue(queueData.queue || [])
            setAgents(agentsData.agents || [])
            setIsLoading(false)
        } catch (err) {
            console.error(err)
            setIsLoading(false)
        }
    }, [API_BASE])

    useEffect(() => {
        fetchData()
        const interval = setInterval(fetchData, 3000)
        return () => clearInterval(interval)
    }, [fetchData])

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'READY': return <CheckCircle className="w-5 h-5 text-emerald-500" />
            case 'BUILDING': return <Loader className="w-5 h-5 text-blue-500 animate-spin" />
            case 'FAILED': return <XCircle className="w-5 h-5 text-red-500" />
            default: return <Clock className="w-5 h-5 text-amber-500" />
        }
    }

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'READY': return 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
            case 'BUILDING': return 'bg-blue-500/10 text-blue-600 border-blue-500/20'
            case 'FAILED': return 'bg-red-500/10 text-red-600 border-red-500/20'
            default: return 'bg-amber-500/10 text-amber-600 border-amber-500/20'
        }
    }

    const handleViewResult = async (buildId: string) => {
        try {
            const res = await fetch(`${API_BASE}/builder/agent/${buildId}`)
            const data = await res.json()
            setSelectedAgent(data)
            
            // Set IO Data for transparency
            setIOData({
                input: {
                    payload_id: data.payload_id,
                    llm_config: data.llm_config,
                    tools: data.tools
                },
                output: {
                    id: data.id,
                    status: data.status,
                    code: data.code_snippet || "(Código no disponible en vista previa)",
                    compiled_at: data.compiled_at
                },
                metadata: {
                    processingType: data.processing_type || 'hybrid',
                    tokensUsed: data.tokens_used || 0,
                    processingTimeMs: data.build_time_ms || 2500,
                    phase: 'Builder (Compilation)'
                }
            })
        } catch (err) {
            console.error(err)
        }
    }

    const handlePassToEngine = (agentId: string) => {
        router.push(`/engine?agent=${agentId}`)
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
                        <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
                            <Layers className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold font-heading text-foreground">Builder</h1>
                            <p className="text-muted-foreground text-sm flex items-center gap-2">
                                Compila agentes de IA desde payloads de contexto
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
                        <h3 className="text-lg font-semibold mb-3">¿Cómo funciona Builder?</h3>
                        <div className="space-y-3 text-sm text-muted-foreground">
                            <p><strong>Builder</strong> compila agentes de IA ejecutables desde los payloads generados en Architect.</p>
                            <p><strong>Cola de Builds:</strong> Muestra los agentes en proceso de compilación.</p>
                            <p><strong>Ver Resultado:</strong> Inspecciona el agente compilado (código, skills, configuración).</p>
                            <p><strong>Pasar a Engine:</strong> Envía el agente listo para ejecución.</p>
                            <p><strong>Skills Detectadas:</strong> Skills que el agente usará según el contexto.</p>
                            <p><strong>MCPs Requeridos:</strong> Protocolos de comunicación necesarios.</p>
                        </div>
                        <button onClick={() => setShowHelp(false)} className="mt-4 text-sm text-primary hover:underline">
                            Cerrar ayuda
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* LEFT: BUILD QUEUE */}
                <div className="lg:col-span-2">
                    <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-semibold">Cola de Compilación</h2>
                            <span className="text-sm text-muted-foreground">{queue.length} agente(s) en cola</span>
                        </div>

                        {isLoading ? (
                            <div className="h-64 flex items-center justify-center">
                                <Loader className="w-8 h-8 animate-spin text-muted-foreground" />
                            </div>
                        ) : queue.length === 0 ? (
                            <div className="h-64 flex flex-col items-center justify-center text-muted-foreground">
                                <Layers className="w-12 h-12 mb-4 opacity-50" />
                                <p>No hay agentes en cola</p>
                                <p className="text-sm mt-2">Genera un payload en Architect para comenzar</p>
                                <Link href="/architect" className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm">
                                    Ir a Architect
                                </Link>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {queue.map((agent, idx) => (
                                    <motion.div
                                        key={agent.build_id || idx}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                        className="border border-border rounded-xl p-4 bg-background/50"
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                {getStatusIcon(agent.status)}
                                                <div>
                                                    <h3 className="font-semibold">{agent.agent_name || `Agent ${idx + 1}`}</h3>
                                                    <p className="text-sm text-muted-foreground">
                                                        {agent.model || 'Gemini 2.0'} • {agent.tools?.length || 0} tools
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(agent.status)}`}>
                                                    {agent.status}
                                                </span>
                                                {agent.status === 'READY' && (
                                                    <>
                                                        <button
                                                            onClick={() => handleViewResult(agent.build_id)}
                                                            className="p-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
                                                            title="Ver Resultado"
                                                        >
                                                            <Eye className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={() => handlePassToEngine(agent.build_id)}
                                                            className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors flex items-center gap-1"
                                                        >
                                                            Engine <ChevronRight className="w-4 h-4" />
                                                        </button>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                        {agent.status === 'BUILDING' && (
                                            <div className="mt-4">
                                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                                    <div className="h-full bg-blue-500 animate-pulse" style={{ width: `${agent.progress || 45}%` }} />
                                                </div>
                                                <p className="text-xs text-muted-foreground mt-2">ETA: {agent.eta_seconds || 30}s</p>
                                            </div>
                                        )}

                                        {/* Skills & MCPs Preview */}
                                        {agent.tools && agent.tools.length > 0 && (
                                            <div className="mt-3 pt-3 border-t border-border">
                                                <div className="flex flex-wrap gap-1">
                                                    {agent.tools.map((tool: string) => (
                                                        <span key={tool} className="px-2 py-0.5 bg-purple-500/10 text-purple-600 rounded text-xs">
                                                            {tool}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* RIGHT: AGENT DETAILS */}
                <div className="space-y-4">
                    {/* Skills Panel */}
                    <div className="bg-card border border-border rounded-2xl p-4 shadow-sm">
                        <h3 className="font-semibold mb-3 flex items-center gap-2">
                            <Wrench className="w-4 h-4 text-purple-500" />
                            Skills Detectadas
                        </h3>
                        {selectedAgent?.capabilities?.length > 0 ? (
                            <div className="flex flex-wrap gap-1">
                                {selectedAgent.capabilities.map((cap: string) => (
                                    <span key={cap} className="px-2 py-1 bg-purple-500/10 text-purple-600 rounded-lg text-xs">
                                        {cap}
                                    </span>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-muted-foreground">Selecciona un agente para ver sus skills</p>
                        )}
                    </div>

                    {/* MCPs Panel */}
                    <div className="bg-card border border-border rounded-2xl p-4 shadow-sm">
                        <h3 className="font-semibold mb-3 flex items-center gap-2">
                            <Server className="w-4 h-4 text-blue-500" />
                            MCPs Requeridos
                        </h3>
                        {selectedAgent ? (
                            <div className="flex flex-wrap gap-1">
                                <span className="px-2 py-1 bg-blue-500/10 text-blue-600 rounded-lg text-xs">filesystem</span>
                                {selectedAgent.model?.includes('gemini') && (
                                    <span className="px-2 py-1 bg-blue-500/10 text-blue-600 rounded-lg text-xs">context7</span>
                                )}
                            </div>
                        ) : (
                            <p className="text-sm text-muted-foreground">Selecciona un agente para ver sus MCPs</p>
                        )}
                    </div>

                    {/* Agent Details */}
                    {selectedAgent && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-card border border-border rounded-2xl p-4 shadow-sm"
                        >
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="font-semibold">Detalle del Agente</h3>
                                <IOViewerButton 
                                    onClick={() => setShowIOViewer(true)} 
                                    label="Ver I/O Compilation"
                                />
                            </div>
                            <div className="space-y-2 text-sm">
                                <p><span className="text-muted-foreground">ID:</span> {selectedAgent.id?.slice(0, 8)}...</p>
                                <p><span className="text-muted-foreground">Nombre:</span> {selectedAgent.name}</p>
                                <p><span className="text-muted-foreground">Modelo:</span> {selectedAgent.model}</p>
                                <p><span className="text-muted-foreground">Versión:</span> {selectedAgent.version}</p>
                            </div>
                            <button
                                onClick={() => handlePassToEngine(selectedAgent.id)}
                                className="w-full mt-4 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-emerald-600 text-white font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                            >
                                Pasar a Engine <ChevronRight className="w-4 h-4" />
                            </button>
                        </motion.div>
                    )}
                </div>
            </div>
            
            {/* IO Viewer Modal */}
            <IOViewerModal
                isOpen={showIOViewer}
                onClose={() => setShowIOViewer(false)}
                title="Builder - Compilation Process"
                data={ioData || { input: {}, output: {} }}
            />
        </main>
    )
}
