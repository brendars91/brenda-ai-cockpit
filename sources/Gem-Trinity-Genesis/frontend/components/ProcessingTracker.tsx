"use client"
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Cpu, Zap, TrendingUp, DollarSign, BarChart3 } from 'lucide-react'

interface ProcessingStats {
    llmCalls: number
    deterministicCalls: number
    totalTokens: number
    estimatedCostUSD: number
    breakdown: {
        phase: string
        llm: number
        deterministic: number
    }[]
}

interface ProcessingTrackerProps {
    stats?: ProcessingStats
    compact?: boolean
    processingType?: string
}

export function ProcessingTracker({ stats, compact = false, processingType }: ProcessingTrackerProps) {
    const [animatedStats, setAnimatedStats] = useState<ProcessingStats>({
        llmCalls: 0,
        deterministicCalls: 0,
        totalTokens: 0,
        estimatedCostUSD: 0,
        breakdown: []
    })

    useEffect(() => {
        if (stats) {
            setAnimatedStats(stats)
        }
    }, [stats])

    const totalCalls = animatedStats.llmCalls + animatedStats.deterministicCalls
    const llmPercentage = totalCalls > 0 ? (animatedStats.llmCalls / totalCalls) * 100 : 0
    const deterministicPercentage = totalCalls > 0 ? (animatedStats.deterministicCalls / totalCalls) * 100 : 0

    // Compact version for inline display
    if (compact) {
        return (
            <div className="flex items-center gap-4 px-3 py-2 bg-muted/30 rounded-lg">
                <div className="flex items-center gap-2">
                    <Zap className="w-3 h-3 text-emerald-500" />
                    <span className="text-xs font-medium">{deterministicPercentage.toFixed(0)}% Determinístico</span>
                </div>
                <div className="flex items-center gap-2">
                    <Cpu className="w-3 h-3 text-purple-500" />
                    <span className="text-xs font-medium">{llmPercentage.toFixed(0)}% LLM</span>
                </div>
                {animatedStats.totalTokens > 0 && (
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <span className="text-amber-500">{animatedStats.totalTokens.toLocaleString()}</span> tokens
                    </div>
                )}
            </div>
        )
    }

    return (
        <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-purple-500/20">
                        <BarChart3 className="w-5 h-5 text-cyan-500" />
                    </div>
                    <div>
                        <h3 className="font-semibold">Tracking de Procesamiento</h3>
                        <p className="text-xs text-muted-foreground">Determinístico vs LLM</p>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-2xl font-bold text-emerald-500">{deterministicPercentage.toFixed(0)}%</p>
                    <p className="text-xs text-muted-foreground">Eficiencia Determinística</p>
                </div>
            </div>

            {/* Main Progress Bar */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-muted-foreground">Distribución de procesamiento</span>
                    <span className="text-xs text-muted-foreground">{totalCalls} operaciones totales</span>
                </div>
                <div className="h-4 bg-muted rounded-full overflow-hidden flex">
                    <motion.div
                        className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400"
                        initial={{ width: 0 }}
                        animate={{ width: `${deterministicPercentage}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                    />
                    <motion.div
                        className="h-full bg-gradient-to-r from-purple-500 to-purple-400"
                        initial={{ width: 0 }}
                        animate={{ width: `${llmPercentage}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut', delay: 0.2 }}
                    />
                </div>
                <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-emerald-500" />
                        <span className="text-xs">Determinístico ({animatedStats.deterministicCalls})</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-purple-500" />
                        <span className="text-xs">LLM ({animatedStats.llmCalls})</span>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-muted/30 rounded-xl">
                    <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-4 h-4 text-amber-500" />
                        <span className="text-xs text-muted-foreground">Tokens Usados</span>
                    </div>
                    <p className="text-xl font-bold">{animatedStats.totalTokens.toLocaleString()}</p>
                </div>
                <div className="p-4 bg-muted/30 rounded-xl">
                    <div className="flex items-center gap-2 mb-2">
                        <DollarSign className="w-4 h-4 text-emerald-500" />
                        <span className="text-xs text-muted-foreground">Costo Estimado</span>
                    </div>
                    <p className="text-xl font-bold">${animatedStats.estimatedCostUSD.toFixed(4)}</p>
                </div>
            </div>

            {/* Breakdown by Phase */}
            {animatedStats.breakdown.length > 0 && (
                <div>
                    <h4 className="text-sm font-medium mb-3">Desglose por Fase</h4>
                    <div className="space-y-2">
                        {animatedStats.breakdown.map((item, idx) => {
                            const phaseTotal = item.llm + item.deterministic
                            const phaseDetermPct = phaseTotal > 0 ? (item.deterministic / phaseTotal) * 100 : 0
                            return (
                                <div key={idx} className="flex items-center gap-3">
                                    <span className="text-xs text-muted-foreground w-20 truncate">{item.phase}</span>
                                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden flex">
                                        <div
                                            className="h-full bg-emerald-500"
                                            style={{ width: `${phaseDetermPct}%` }}
                                        />
                                        <div
                                            className="h-full bg-purple-500"
                                            style={{ width: `${100 - phaseDetermPct}%` }}
                                        />
                                    </div>
                                    <span className="text-xs w-12 text-right">{phaseDetermPct.toFixed(0)}%</span>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* Savings Indicator */}
            <div className="mt-6 p-4 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 rounded-xl border border-emerald-500/20">
                <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-emerald-500" />
                    <div>
                        <p className="text-sm font-medium text-emerald-400">
                            Ahorro estimado: ${(animatedStats.estimatedCostUSD * (deterministicPercentage / 100) * 2).toFixed(4)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                            Comparado con 100% procesamiento LLM
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

// Hook for tracking processing in components
export function useProcessingTracker() {
    const [stats, setStats] = useState<ProcessingStats>({
        llmCalls: 0,
        deterministicCalls: 0,
        totalTokens: 0,
        estimatedCostUSD: 0,
        breakdown: []
    })

    const trackLLMCall = (tokens: number, phase: string) => {
        const costPerToken = 0.000001 // Approximate cost per token
        setStats(prev => {
            const existingPhase = prev.breakdown.find(b => b.phase === phase)
            const newBreakdown = existingPhase
                ? prev.breakdown.map(b => b.phase === phase ? { ...b, llm: b.llm + 1 } : b)
                : [...prev.breakdown, { phase, llm: 1, deterministic: 0 }]

            return {
                ...prev,
                llmCalls: prev.llmCalls + 1,
                totalTokens: prev.totalTokens + tokens,
                estimatedCostUSD: prev.estimatedCostUSD + (tokens * costPerToken),
                breakdown: newBreakdown
            }
        })
    }

    const trackDeterministicCall = (phase: string) => {
        setStats(prev => {
            const existingPhase = prev.breakdown.find(b => b.phase === phase)
            const newBreakdown = existingPhase
                ? prev.breakdown.map(b => b.phase === phase ? { ...b, deterministic: b.deterministic + 1 } : b)
                : [...prev.breakdown, { phase, llm: 0, deterministic: 1 }]

            return {
                ...prev,
                deterministicCalls: prev.deterministicCalls + 1,
                breakdown: newBreakdown
            }
        })
    }

    const resetStats = () => {
        setStats({
            llmCalls: 0,
            deterministicCalls: 0,
            totalTokens: 0,
            estimatedCostUSD: 0,
            breakdown: []
        })
    }

    return { stats, trackLLMCall, trackDeterministicCall, resetStats }
}
