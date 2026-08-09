"use client"
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wrench, Server, Eye, Package, CheckCircle, ChevronDown, ChevronUp, Copy, Check, ExternalLink } from 'lucide-react'

interface TransferredSkill {
    id: string
    name: string
    description: string
    adapted: boolean
    adaptedContext?: string
    code?: string
}

interface TransferredMCP {
    id: string
    name: string
    description: string
    config?: Record<string, any>
    documentation?: string
}

interface TransferredResourcesPanelProps {
    skills: TransferredSkill[]
    mcps: TransferredMCP[]
    projectName: string
}

export function TransferredResourcesPanel({ skills, mcps, projectName }: TransferredResourcesPanelProps) {
    const [showSkills, setShowSkills] = useState(false)
    const [showMCPs, setShowMCPs] = useState(false)
    const [selectedResource, setSelectedResource] = useState<TransferredSkill | TransferredMCP | null>(null)
    const [copied, setCopied] = useState(false)

    const copyConfig = async (config: any) => {
        await navigator.clipboard.writeText(JSON.stringify(config, null, 2))
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className="space-y-4">
            {/* Header Summary */}
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 rounded-xl border border-purple-500/20">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-white/10">
                        <Package className="w-5 h-5 text-cyan-500" />
                    </div>
                    <div>
                        <h3 className="font-semibold">Recursos Transferidos</h3>
                        <p className="text-xs text-muted-foreground">
                            {skills.length} skills + {mcps.length} MCPs para {projectName}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-1">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    <span className="text-xs text-emerald-500">100% adaptados</span>
                </div>
            </div>

            {/* Skills Section */}
            <div className="bg-card border border-border rounded-xl overflow-hidden">
                <button
                    onClick={() => setShowSkills(!showSkills)}
                    className="w-full flex items-center justify-between p-4 hover:bg-muted/30 transition-colors"
                >
                    <div className="flex items-center gap-3">
                        <Wrench className="w-5 h-5 text-purple-500" />
                        <div className="text-left">
                            <h4 className="font-medium text-sm">Skills Transferidas</h4>
                            <p className="text-xs text-muted-foreground">
                                {skills.filter(s => s.adapted).length} adaptadas al contexto
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">
                            {skills.length}
                        </span>
                        {showSkills ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                </button>

                <AnimatePresence>
                    {showSkills && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="border-t border-border"
                        >
                            <div className="p-4 space-y-3">
                                {skills.map((skill) => (
                                    <div
                                        key={skill.id}
                                        className="p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className="font-medium text-sm">{skill.name}</span>
                                                {skill.adapted && (
                                                    <span className="px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px]">
                                                        Adaptada
                                                    </span>
                                                )}
                                            </div>
                                            <button
                                                onClick={() => setSelectedResource(skill)}
                                                className="p-1.5 hover:bg-muted rounded transition-colors"
                                            >
                                                <Eye className="w-3 h-3" />
                                            </button>
                                        </div>
                                        <p className="text-xs text-muted-foreground">{skill.description}</p>
                                        {skill.adaptedContext && (
                                            <p className="text-xs text-cyan-400 mt-1">
                                                → {skill.adaptedContext}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* MCPs Section */}
            <div className="bg-card border border-border rounded-xl overflow-hidden">
                <button
                    onClick={() => setShowMCPs(!showMCPs)}
                    className="w-full flex items-center justify-between p-4 hover:bg-muted/30 transition-colors"
                >
                    <div className="flex items-center gap-3">
                        <Server className="w-5 h-5 text-blue-500" />
                        <div className="text-left">
                            <h4 className="font-medium text-sm">MCPs Transferidos</h4>
                            <p className="text-xs text-muted-foreground">
                                Configurados para producción
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                            {mcps.length}
                        </span>
                        {showMCPs ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                </button>

                <AnimatePresence>
                    {showMCPs && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="border-t border-border"
                        >
                            <div className="p-4 space-y-3">
                                {mcps.map((mcp) => (
                                    <div
                                        key={mcp.id}
                                        className="p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                                <span className="font-medium text-sm">{mcp.name}</span>
                                                <span className="px-1.5 py-0.5 bg-blue-500/20 text-blue-400 rounded text-[10px]">
                                                    MCP
                                                </span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                {mcp.config && (
                                                    <button
                                                        onClick={() => copyConfig(mcp.config)}
                                                        className="p-1.5 hover:bg-muted rounded transition-colors"
                                                        title="Copiar configuración"
                                                    >
                                                        {copied ? (
                                                            <Check className="w-3 h-3 text-emerald-500" />
                                                        ) : (
                                                            <Copy className="w-3 h-3" />
                                                        )}
                                                    </button>
                                                )}
                                                {mcp.documentation && (
                                                    <a
                                                        href={mcp.documentation}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="p-1.5 hover:bg-muted rounded transition-colors"
                                                        title="Documentación"
                                                    >
                                                        <ExternalLink className="w-3 h-3" />
                                                    </a>
                                                )}
                                            </div>
                                        </div>
                                        <p className="text-xs text-muted-foreground">{mcp.description}</p>
                                        {mcp.config && (
                                            <details className="mt-2">
                                                <summary className="text-xs text-cyan-400 cursor-pointer hover:text-cyan-300">
                                                    Ver configuración
                                                </summary>
                                                <pre className="mt-2 p-2 bg-slate-950 rounded text-[10px] font-mono text-slate-400 overflow-x-auto">
                                                    {JSON.stringify(mcp.config, null, 2)}
                                                </pre>
                                            </details>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Usage Instructions */}
            <div className="p-4 bg-muted/20 rounded-xl border border-border">
                <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    Instrucciones de Uso
                </h4>
                <ul className="text-xs text-muted-foreground space-y-1">
                    <li>• Las skills están en <code className="text-cyan-400">/skills</code> de tu proyecto</li>
                    <li>• La configuración de MCPs está en <code className="text-cyan-400">/config/mcps.json</code></li>
                    <li>• Todas las adaptaciones son específicas para tu contexto</li>
                </ul>
            </div>
        </div>
    )
}
