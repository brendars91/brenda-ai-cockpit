"use client"
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Trash2, AlertTriangle, X, Check, Archive } from 'lucide-react'

interface DoubleConfirmDeleteProps {
    isOpen: boolean
    onClose: () => void
    onConfirm: () => Promise<void>
    projectName: string
    itemType?: 'project' | 'agent' | 'payload'
}

export function DoubleConfirmDelete({ isOpen, onClose, onConfirm, projectName, itemType = 'project' }: DoubleConfirmDeleteProps) {
    const [step, setStep] = useState<1 | 2>(1)
    const [confirmText, setConfirmText] = useState('')
    const [isDeleting, setIsDeleting] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const expectedText = 'ELIMINAR'
    const canProceedStep2 = confirmText.toUpperCase() === expectedText

    // Reset when modal opens/closes
    useEffect(() => {
        if (isOpen) {
            setStep(1)
            setConfirmText('')
            setError(null)
        }
    }, [isOpen])

    const handleStep1Confirm = () => {
        setStep(2)
    }

    const handleFinalConfirm = async () => {
        if (!canProceedStep2) return

        setIsDeleting(true)
        setError(null)

        try {
            await onConfirm()
            onClose()
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error al eliminar')
        } finally {
            setIsDeleting(false)
        }
    }

    const getItemLabel = () => {
        switch (itemType) {
            case 'agent': return 'agente'
            case 'payload': return 'payload'
            default: return 'proyecto'
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
                        className="bg-card border border-red-500/30 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-border bg-red-500/10">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-red-500/20">
                                    <AlertTriangle className="w-5 h-5 text-red-500" />
                                </div>
                                <div>
                                    <h2 className="font-semibold text-red-400">Confirmar Eliminación</h2>
                                    <p className="text-xs text-muted-foreground">Paso {step} de 2</p>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 rounded-lg hover:bg-muted transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Progress Bar */}
                        <div className="h-1 bg-muted">
                            <motion.div
                                className="h-full bg-red-500"
                                initial={{ width: '50%' }}
                                animate={{ width: step === 1 ? '50%' : '100%' }}
                            />
                        </div>

                        {/* Content */}
                        <div className="p-6">
                            <AnimatePresence mode="wait">
                                {step === 1 ? (
                                    <motion.div
                                        key="step1"
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 20 }}
                                        className="space-y-4"
                                    >
                                        <div className="text-center">
                                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                                                <Trash2 className="w-8 h-8 text-red-500" />
                                            </div>
                                            <h3 className="text-lg font-semibold mb-2">¿Eliminar {getItemLabel()}?</h3>
                                            <p className="text-sm text-muted-foreground mb-4">
                                                Estás a punto de eliminar:
                                            </p>
                                            <div className="p-3 bg-muted/50 rounded-lg">
                                                <p className="font-mono text-sm font-medium">{projectName}</p>
                                            </div>
                                        </div>

                                        <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                                            <p className="text-xs text-amber-400">
                                                ⚠️ Esta acción eliminará todos los artefactos asociados:
                                            </p>
                                            <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                                                <li>• Payloads de Architect</li>
                                                <li>• Agentes compilados</li>
                                                <li>• Registros de ejecución</li>
                                                <li>• Documentación generada</li>
                                            </ul>
                                        </div>
                                    </motion.div>
                                ) : (
                                    <motion.div
                                        key="step2"
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -20 }}
                                        className="space-y-4"
                                    >
                                        <div className="text-center">
                                            <h3 className="text-lg font-semibold mb-2">Confirmación Final</h3>
                                            <p className="text-sm text-muted-foreground">
                                                Escribe <span className="font-mono font-bold text-red-400">ELIMINAR</span> para confirmar
                                            </p>
                                        </div>

                                        <input
                                            type="text"
                                            value={confirmText}
                                            onChange={(e) => setConfirmText(e.target.value)}
                                            placeholder="Escribe ELIMINAR"
                                            className="w-full px-4 py-3 rounded-lg border-2 border-red-500/30 bg-background text-center font-mono text-lg focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
                                            autoFocus
                                        />

                                        {error && (
                                            <div className="p-3 bg-red-500/20 border border-red-500/40 rounded-lg">
                                                <p className="text-sm text-red-400">{error}</p>
                                            </div>
                                        )}

                                        <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                                            <p className="text-xs text-red-300 text-center">
                                                🚫 Esta acción NO se puede deshacer
                                            </p>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-between p-4 border-t border-border bg-muted/20">
                            <button
                                onClick={step === 1 ? onClose : () => setStep(1)}
                                className="px-4 py-2 rounded-lg hover:bg-muted transition-colors text-sm"
                            >
                                {step === 1 ? 'Cancelar' : 'Volver'}
                            </button>

                            {step === 1 ? (
                                <button
                                    onClick={handleStep1Confirm}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors text-sm font-medium"
                                >
                                    Continuar
                                    <Check className="w-4 h-4" />
                                </button>
                            ) : (
                                <button
                                    onClick={handleFinalConfirm}
                                    disabled={!canProceedStep2 || isDeleting}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
                                >
                                    {isDeleting ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                            Eliminando...
                                        </>
                                    ) : (
                                        <>
                                            <Trash2 className="w-4 h-4" />
                                            Eliminar Definitivamente
                                        </>
                                    )}
                                </button>
                            )}
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}

// Simple delete button that triggers the modal
interface DeleteButtonProps {
    onClick: () => void
    disabled?: boolean
    size?: 'sm' | 'md'
    label?: string
}

export function DeleteButton({ onClick, disabled = false, size = 'sm', label }: DeleteButtonProps) {
    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`flex items-center gap-1.5 rounded-lg bg-red-500/10 text-red-600 hover:bg-red-500/20 disabled:opacity-50 transition-colors ${size === 'sm' ? 'p-1.5' : 'px-3 py-2 text-sm'
                }`}
            title="Eliminar"
        >
            <Trash2 className={size === 'sm' ? 'w-4 h-4' : 'w-5 h-5'} />
            {label && <span>{label}</span>}
        </button>
    )
}
