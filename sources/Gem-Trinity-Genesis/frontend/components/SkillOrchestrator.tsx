"use client"
import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wrench, Server, Eye, ChevronDown, ChevronUp, CheckCircle, Plus, Sparkles } from 'lucide-react'

interface Skill {
    id: string
    name: string
    description: string
    source: 'existing' | 'created' | 'adapted'
    adaptedFor?: string
}

interface MCP {
    id: string
    name: string
    description: string
    status: 'active' | 'pending' | 'unavailable'
    transferrable: boolean
}

interface SkillOrchestratorProps {
    projectContext: {
        domain: string
        complexity: string
        objectives: string[]
        useCase: string
    }
    onSkillsSelected?: (skills: Skill[], mcps: MCP[]) => void
}

// Deterministic fallback skill selection based on context
const getFallbackSkills = (ctx: SkillOrchestratorProps['projectContext']): Skill[] => {
    const baseSkills: Skill[] = [
        { id: 'core-reasoning', name: 'Core Reasoning', description: 'Razonamiento lógico base', source: 'existing' },
        { id: 'error-handling', name: 'Error Handling', description: 'Manejo robusto de errores', source: 'existing' }
    ]

    if (ctx.domain === 'sap') {
        baseSkills.push(
            { id: 'sap-knowledge-base', name: 'SAP Knowledge Base', description: 'Base de conocimiento SAP FI/CO/ABAP', source: 'existing' },
            { id: 'abap-syntax', name: 'ABAP Syntax', description: 'Parser y generador de código ABAP', source: 'existing' },
            { id: 'financial-calculations', name: 'Financial Calculations', description: 'Cálculos financieros IFRS', source: 'existing' }
        )
    } else if (ctx.domain === 'devops') {
        baseSkills.push(
            { id: 'ci-cd-pipeline', name: 'CI/CD Pipeline', description: 'Gestión de pipelines', source: 'existing' },
            { id: 'container-management', name: 'Container Management', description: 'Docker y Kubernetes', source: 'existing' }
        )
    } else if (ctx.domain === 'marketing') {
        baseSkills.push(
            { id: 'analytics-interpreter', name: 'Analytics Interpreter', description: 'Interpretación de métricas', source: 'existing' },
            { id: 'content-generator', name: 'Content Generator', description: 'Generación de contenido', source: 'existing' }
        )
    }

    if (ctx.complexity === 'medium' || ctx.complexity === 'difficult') {
        baseSkills.push(
            { id: 'rag-pipeline', name: 'RAG Pipeline', description: 'Retrieval Augmented Generation', source: 'existing' }
        )
    }

    if (ctx.complexity === 'difficult') {
        baseSkills.push(
            { id: 'multi-agent-coordination', name: 'Multi-Agent Coordination', description: 'Orquestación de múltiples agentes', source: 'existing' },
            { id: 'security-audit', name: 'Security Audit', description: 'Auditoría de seguridad', source: 'existing' }
        )
    }

    return baseSkills
}

// Deterministic fallback MCP selection
const getFallbackMCPs = (ctx: SkillOrchestratorProps['projectContext']): MCP[] => {
    const baseMCPs: MCP[] = [
        { id: 'filesystem', name: 'Filesystem', description: 'Acceso a sistema de archivos', status: 'active', transferrable: true },
        { id: 'context7', name: 'Context7', description: 'Documentación en tiempo real', status: 'active', transferrable: true }
    ]

    if (ctx.domain === 'sap') {
        baseMCPs.push(
            { id: 'database', name: 'Database', description: 'Conexión a bases de datos', status: 'active', transferrable: true },
            { id: 'sap-connector', name: 'SAP Connector', description: 'RFC/BAPI connections', status: 'pending', transferrable: true }
        )
    } else if (ctx.domain === 'devops') {
        baseMCPs.push(
            { id: 'github', name: 'GitHub', description: 'GitHub API integration', status: 'active', transferrable: true },
            { id: 'docker', name: 'Docker', description: 'Docker management', status: 'active', transferrable: true }
        )
    }

    if (ctx.complexity === 'difficult') {
        baseMCPs.push(
            { id: 'snyk', name: 'Snyk', description: 'Security scanning', status: 'active', transferrable: true },
            { id: 'monitoring', name: 'Monitoring', description: 'Telemetry and monitoring', status: 'active', transferrable: true }
        )
    }

    return baseMCPs
}

export function SkillOrchestrator({ projectContext, onSkillsSelected }: SkillOrchestratorProps) {
    const [skills, setSkills] = useState<Skill[]>([])
    const [mcps, setMCPs] = useState<MCP[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [showSkillDetails, setShowSkillDetails] = useState(false)
    const [showMCPDetails, setShowMCPDetails] = useState(false)
    const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)

    const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const API_BASE = RAW_URL.replace(/\/api\/?$/, '') + '/api'

    const orchestrateResources = useCallback(async () => {
        setIsLoading(true)
        try {
            const res = await fetch(`${API_BASE}/skills/orchestrate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(projectContext)
            })
            const data = await res.json()
            setSkills(data.skills || [])
            setMCPs(data.mcps || [])
            onSkillsSelected?.(data.skills || [], data.mcps || [])
        } catch (err) {
            console.error('Error orchestrating resources:', err)
            // Fallback to deterministic selection
            const fallbackSkills = getFallbackSkills(projectContext)
            const fallbackMCPs = getFallbackMCPs(projectContext)
            setSkills(fallbackSkills)
            setMCPs(fallbackMCPs)
            onSkillsSelected?.(fallbackSkills, fallbackMCPs)
        } finally {
            setIsLoading(false)
        }
    }, [API_BASE, onSkillsSelected, projectContext])

    useEffect(() => {
        orchestrateResources()
    }, [orchestrateResources])

    const getSourceBadge = (source: Skill['source']) => {
        switch (source) {
            case 'existing':
                return <span className="px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px]">Existente</span>
            case 'adapted':
                return <span className="px-1.5 py-0.5 bg-amber-500/20 text-amber-400 rounded text-[10px]">Adaptada</span>
            case 'created':
                return <span className="px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded text-[10px]">Nueva</span>
        }
    }

    const getStatusBadge = (status: MCP['status']) => {
        switch (status) {
            case 'active':
                return <span className="px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px]">Activo</span>
            case 'pending':
                return <span className="px-1.5 py-0.5 bg-amber-500/20 text-amber-400 rounded text-[10px]">Pendiente</span>
            case 'unavailable':
                return <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-[10px]">No disponible</span>
        }
    }

    if (isLoading) {
        return (
            <div className="bg-card border border-border rounded-xl p-4">
                <div className="flex items-center gap-3">
                    <div className="w-5 h-5 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                    <span className="text-sm text-muted-foreground">Orquestando recursos para el contexto...</span>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-4">
            {/* Skills Panel */}
            <div className="bg-card border border-border rounded-xl overflow-hidden">
                <button
                    onClick={() => setShowSkillDetails(!showSkillDetails)}
                    className="w-full flex items-center justify-between p-4 hover:bg-muted/30 transition-colors"
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-purple-500/20">
                            <Wrench className="w-4 h-4 text-purple-500" />
                        </div>
                        <div className="text-left">
                            <h3 className="font-semibold text-sm">Skills Seleccionadas</h3>
                            <p className="text-xs text-muted-foreground">{skills.length} skills 100% adaptadas al contexto</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="flex items-center gap-1 text-xs text-emerald-500">
                            <CheckCircle className="w-3 h-3" /> Orquestadas
                        </span>
                        {showSkillDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                </button>

                <AnimatePresence>
                    {showSkillDetails && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="border-t border-border"
                        >
                            <div className="p-4 space-y-2 max-h-64 overflow-y-auto">
                                {skills.map((skill) => (
                                    <div
                                        key={skill.id}
                                        className="flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors"
                                    >
                                        <div className="flex items-center gap-3">
                                            <Sparkles className="w-4 h-4 text-purple-400" />
                                            <div>
                                                <p className="text-sm font-medium">{skill.name}</p>
                                                <p className="text-xs text-muted-foreground">{skill.description}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {getSourceBadge(skill.source)}
                                            <button
                                                onClick={() => setSelectedSkill(skill)}
                                                className="p-1.5 rounded hover:bg-muted transition-colors"
                                            >
                                                <Eye className="w-3 h-3 text-muted-foreground" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* MCPs Panel */}
            <div className="bg-card border border-border rounded-xl overflow-hidden">
                <button
                    onClick={() => setShowMCPDetails(!showMCPDetails)}
                    className="w-full flex items-center justify-between p-4 hover:bg-muted/30 transition-colors"
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-500/20">
                            <Server className="w-4 h-4 text-blue-500" />
                        </div>
                        <div className="text-left">
                            <h3 className="font-semibold text-sm">MCPs Requeridos</h3>
                            <p className="text-xs text-muted-foreground">
                                {mcps.filter(m => m.transferrable).length} MCPs se transferirán al proyecto
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="flex items-center gap-1 text-xs text-blue-500">
                            <CheckCircle className="w-3 h-3" /> Configurados
                        </span>
                        {showMCPDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                </button>

                <AnimatePresence>
                    {showMCPDetails && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="border-t border-border"
                        >
                            <div className="p-4 space-y-2 max-h-64 overflow-y-auto">
                                {mcps.map((mcp) => (
                                    <div
                                        key={mcp.id}
                                        className="flex items-center justify-between p-3 bg-muted/30 rounded-lg"
                                    >
                                        <div className="flex items-center gap-3">
                                            <Server className="w-4 h-4 text-blue-400" />
                                            <div>
                                                <p className="text-sm font-medium">{mcp.name}</p>
                                                <p className="text-xs text-muted-foreground">{mcp.description}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {getStatusBadge(mcp.status)}
                                            {mcp.transferrable && (
                                                <span className="px-1.5 py-0.5 bg-cyan-500/20 text-cyan-400 rounded text-[10px]">
                                                    Transferible
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Compact Summary */}
            <div className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg border border-purple-500/20">
                <span className="text-xs text-muted-foreground">
                    Total: {skills.length} skills + {mcps.length} MCPs configurados para {projectContext.domain}
                </span>
                <span className="text-xs text-emerald-500 flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" /> 100% adaptados
                </span>
            </div>
        </div>
    )
}
