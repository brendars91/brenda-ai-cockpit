"use client"
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Eye, EyeOff, Copy, Check, Cpu, Zap, Clock, FileJson, ChevronDown, ChevronUp } from 'lucide-react'

interface IOData {
    input: any
    output: any
    metadata?: {
        processingType: 'llm' | 'deterministic' | 'hybrid'
        tokensUsed?: number
        processingTimeMs?: number
        model?: string
        phase?: string
    }
}

interface IOViewerModalProps {
    isOpen: boolean
    onClose: () => void
    title: string
    data: IOData
}

export function IOViewerModal({ isOpen, onClose, title, data }: IOViewerModalProps) {
    const [showInput, setShowInput] = useState(true)
    const [showOutput, setShowOutput] = useState(true)
    const [copiedSection, setCopiedSection] = useState<string | null>(null)

    const copyToClipboard = (content: any, section: string) => {
        navigator.clipboard.writeText(JSON.stringify(content, null, 2))
        setCopiedSection(section)
        setTimeout(() => setCopiedSection(null), 2000)
    }

    const getProcessingBadge = (type: string) => {
        switch (type) {
            case 'llm':
                return (
                    <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded-lg text-xs flex items-center gap-1">
                        <Cpu className="w-3 h-3" /> LLM
                    </span>
                )
            case 'deterministic':
                return (
                    <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-lg text-xs flex items-center gap-1">
                        <Zap className="w-3 h-3" /> Determinístico
                    </span>
                )
            case 'hybrid':
                return (
                    <span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded-lg text-xs flex items-center gap-1">
                        <Zap className="w-3 h-3" /> Híbrido
                    </span>
                )
            default:
                return null
        }
    }

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="bg-card border border-border rounded-2xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-border bg-muted/30">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-cyan-500/20">
                                    <FileJson className="w-5 h-5 text-cyan-500" />
                                </div>
                                <div>
                                    <h2 className="text-lg font-semibold">{title}</h2>
                                    <p className="text-xs text-muted-foreground">Transparencia de Input/Output</p>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 rounded-lg hover:bg-muted transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Metadata Bar */}
                        {data.metadata && (
                            <div className="flex items-center gap-4 px-4 py-3 bg-muted/20 border-b border-border">
                                {getProcessingBadge(data.metadata.processingType)}

                                {data.metadata.model && (
                                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                                        <Cpu className="w-3 h-3" /> {data.metadata.model}
                                    </span>
                                )}

                                {data.metadata.tokensUsed && (
                                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                                        <Zap className="w-3 h-3" /> {data.metadata.tokensUsed} tokens
                                    </span>
                                )}

                                {data.metadata.processingTimeMs && (
                                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                                        <Clock className="w-3 h-3" /> {data.metadata.processingTimeMs}ms
                                    </span>
                                )}

                                {data.metadata.phase && (
                                    <span className="text-xs text-cyan-500 ml-auto">
                                        Fase: {data.metadata.phase}
                                    </span>
                                )}
                            </div>
                        )}

                        {/* Content */}
                        <div className="p-4 overflow-y-auto max-h-[60vh] space-y-4">
                            {/* Input Section */}
                            <div className="border border-border rounded-xl overflow-hidden">
                                <button
                                    onClick={() => setShowInput(!showInput)}
                                    className="w-full flex items-center justify-between p-3 bg-blue-500/10 hover:bg-blue-500/15 transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        <Eye className="w-4 h-4 text-blue-500" />
                                        <span className="font-medium text-sm">INPUT</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                copyToClipboard(data.input, 'input')
                                            }}
                                            className="p-1.5 rounded-lg hover:bg-blue-500/20 transition-colors"
                                            title="Copiar"
                                        >
                                            {copiedSection === 'input' ? (
                                                <Check className="w-4 h-4 text-emerald-500" />
                                            ) : (
                                                <Copy className="w-4 h-4 text-muted-foreground" />
                                            )}
                                        </button>
                                        {showInput ? (
                                            <ChevronUp className="w-4 h-4" />
                                        ) : (
                                            <ChevronDown className="w-4 h-4" />
                                        )}
                                    </div>
                                </button>
                                <AnimatePresence>
                                    {showInput && (
                                        <motion.div
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: 'auto', opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            className="overflow-hidden"
                                        >
                                            <pre className="p-4 bg-slate-950 text-green-400 text-xs font-mono overflow-x-auto max-h-48">
                                                {typeof data.input === 'string'
                                                    ? data.input
                                                    : JSON.stringify(data.input, null, 2)}
                                            </pre>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>

                            {/* Output Section */}
                            <div className="border border-border rounded-xl overflow-hidden">
                                <button
                                    onClick={() => setShowOutput(!showOutput)}
                                    className="w-full flex items-center justify-between p-3 bg-emerald-500/10 hover:bg-emerald-500/15 transition-colors"
                                >
                                    <div className="flex items-center gap-2">
                                        <EyeOff className="w-4 h-4 text-emerald-500" />
                                        <span className="font-medium text-sm">OUTPUT</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                copyToClipboard(data.output, 'output')
                                            }}
                                            className="p-1.5 rounded-lg hover:bg-emerald-500/20 transition-colors"
                                            title="Copiar"
                                        >
                                            {copiedSection === 'output' ? (
                                                <Check className="w-4 h-4 text-emerald-500" />
                                            ) : (
                                                <Copy className="w-4 h-4 text-muted-foreground" />
                                            )}
                                        </button>
                                        {showOutput ? (
                                            <ChevronUp className="w-4 h-4" />
                                        ) : (
                                            <ChevronDown className="w-4 h-4" />
                                        )}
                                    </div>
                                </button>
                                <AnimatePresence>
                                    {showOutput && (
                                        <motion.div
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: 'auto', opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            className="overflow-hidden"
                                        >
                                            <pre className="p-4 bg-slate-950 text-cyan-400 text-xs font-mono overflow-x-auto max-h-64">
                                                {typeof data.output === 'string'
                                                    ? data.output
                                                    : JSON.stringify(data.output, null, 2)}
                                            </pre>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-end gap-3 p-4 border-t border-border bg-muted/20">
                            <button
                                onClick={onClose}
                                className="px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm"
                            >
                                Cerrar
                            </button>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}

// Compact toggle button to open I/O viewer
interface IOViewerButtonProps {
    onClick: () => void
    label?: string
    size?: 'sm' | 'md'
}

export function IOViewerButton({ onClick, label = "Ver I/O", size = 'sm' }: IOViewerButtonProps) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-1.5 rounded-lg bg-cyan-500/10 text-cyan-600 hover:bg-cyan-500/20 transition-colors ${size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1.5 text-sm'
                }`}
            title="Ver Input/Output"
        >
            <Eye className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />
            {label}
        </button>
    )
}
