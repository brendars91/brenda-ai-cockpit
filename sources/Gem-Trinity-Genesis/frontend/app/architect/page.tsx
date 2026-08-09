"use client"
import Link from 'next/link'
import { ArrowLeft, Code, FileJson, Sparkles, HelpCircle, ChevronRight, FileText, Settings, Eye, MessageSquare } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { IOViewerModal, IOViewerButton } from '@/components/IOViewerModal'
import { QuestionnaireFlow } from '@/components/QuestionnaireFlow'
import { SkillOrchestrator } from '@/components/SkillOrchestrator'
import { ProcessingTracker, useProcessingTracker } from '@/components/ProcessingTracker'
import { GitHubStatusBadge } from '@/components/index'

export default function ArchitectPage() {
    const router = useRouter()
    const [projectName, setProjectName] = useState('')
    const [useCase, setUseCase] = useState('')
    const [domain, setDomain] = useState('custom')
    const [complexity, setComplexity] = useState<'simple' | 'medium' | 'difficult'>('medium')
    const [isGenerating, setIsGenerating] = useState(false)
    const [payload, setPayload] = useState<any>(null)
    const [showHelp, setShowHelp] = useState(false)
    const [activeStep, setActiveStep] = useState(0)
    
    // New state for enhanced features
    const [showQuestionnaire, setShowQuestionnaire] = useState(false)
    const [questionnaireAnswers, setQuestionnaireAnswers] = useState<Record<string, string>>({})
    const [showIOViewer, setShowIOViewer] = useState(false)
    const [ioData, setIOData] = useState<any>(null)
    const { stats, trackLLMCall, trackDeterministicCall } = useProcessingTracker()

    const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const API_BASE = RAW_URL.replace(/\/api\/?$/, '') + '/api';

    const complexityOptions = [
        { value: 'simple', label: 'Sencillo', desc: 'PRD básico, 1-2 Skills', color: 'emerald' },
        { value: 'medium', label: 'Medio', desc: 'PRD detallado, 3-5 Skills', color: 'amber' },
        { value: 'difficult', label: 'Difícil', desc: 'PRD exhaustivo, 5+ Skills', color: 'red' }
    ]

    const workflowSteps = [
        { icon: Sparkles, title: 'Optimizador de Prompt', desc: 'Mejora y estructura tu idea' },
        { icon: FileText, title: 'Generador PRD', desc: 'Documento de requisitos según complejidad' },
        { icon: Settings, title: 'Spec Contract', desc: 'Skills y MCPs necesarios' }
    ]

    const handleGenerate = async () => {
        setIsGenerating(true)
        setActiveStep(1)

        const inputData = {
            use_case: useCase,
            domain,
            complexity,
            model: 'gemini-2.0',
            project_name: projectName,
            questionnaire_answers: questionnaireAnswers
        }

        try {
            // Step 1: Optimizing
            trackDeterministicCall('Optimizer')
            await new Promise(r => setTimeout(r, 500))
            setActiveStep(2)

            // Step 2: Generate
            const res = await fetch(`${API_BASE}/architect/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(inputData)
            })
            const data = await res.json()
            
            // Track based on response
            if (data.context_payload) {
                // Check if LLM was used (tokens_estimated > 0 usually means LLM)
                if (data.tokens_estimated > 500) {
                    trackLLMCall(data.tokens_estimated, 'PRD Generator')
                } else {
                    trackDeterministicCall('PRD Generator')
                }
            }
            trackDeterministicCall('Spec Contract')
            
            setActiveStep(3)
            await new Promise(r => setTimeout(r, 300))
            setPayload(data)
            
            // Store I/O data for viewer
            setIOData({
                input: inputData,
                output: data,
                metadata: {
                    processingType: data.tokens_estimated > 500 ? 'hybrid' : 'deterministic',
                    tokensUsed: data.tokens_estimated || 0,
                    processingTimeMs: 1500,
                    model: data.model,
                    phase: 'Architect'
                }
            })
        } catch (err) {
            console.error(err)
        } finally {
            setIsGenerating(false)
            setActiveStep(0)
        }
    }

    const handleQuestionnaireComplete = (answers: Record<string, string>) => {
        setQuestionnaireAnswers(answers)
        // Build use case from answers
        const problemAnswer = answers.problem || ''
        const ioAnswer = answers.io || ''
        const enhancedUseCase = `${problemAnswer}\n\nInput/Output: ${ioAnswer}\n\nRestricciones: ${answers.constraints || 'N/A'}\n\nMétricas de éxito: ${answers.success || 'N/A'}`
        setUseCase(enhancedUseCase)
        setShowQuestionnaire(false)
    }

    const handleSendToBuilder = async () => {
        try {
            await fetch(`${API_BASE}/builder/compile`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    payload_id: payload.payload_id,
                    agent_name: projectName || payload.domain === 'sap' ? 'SAP_Specialist' : 'Genesis_Agent',
                    llm_config: { model: payload.model || 'gemini-2.0-flash' },
                    tools: payload.spec_contract?.skills_required || []
                })
            })
            router.push('/builder')
        } catch (err) {
            console.error(err)
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
                        <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20">
                            <Code className="w-6 h-6 text-purple-600" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold font-heading text-foreground">Architect</h1>
                            <p className="text-muted-foreground text-sm flex items-center gap-2">
                                Diseña agentes de IA con contexto optimizado
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
                        <h3 className="text-lg font-semibold mb-3">¿Cómo usar Architect?</h3>
                        <div className="space-y-3 text-sm text-muted-foreground">
                            <p><strong>1. Nombre del Proyecto:</strong> Dale un nombre identificable a tu proyecto.</p>
                            <p><strong>2. Dominio:</strong> Elige el área (SAP, Marketing, DevOps o Personalizado).</p>
                            <p><strong>3. Complejidad:</strong> Determina el nivel de detalle:</p>
                            <ul className="list-disc ml-6 space-y-1">
                                <li><strong>Sencillo:</strong> Para tareas simples, PRD básico.</li>
                                <li><strong>Medio:</strong> Para proyectos estándar, PRD detallado con más Skills.</li>
                                <li><strong>Difícil:</strong> Para proyectos complejos, PRD exhaustivo con análisis de riesgos.</li>
                            </ul>
                            <p><strong>4. Describe tu caso de uso:</strong> Explica qué quieres automatizar o resolver.</p>
                        </div>
                        <button onClick={() => setShowHelp(false)} className="mt-4 text-sm text-primary hover:underline">
                            Cerrar ayuda
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* WORKFLOW STEPS INDICATOR */}
            <div className="mb-8 p-4 bg-card border border-border rounded-2xl">
                <h3 className="text-sm font-medium text-muted-foreground mb-4">Flujo de trabajo interno</h3>
                <div className="flex items-center justify-between">
                    {workflowSteps.map((step, idx) => (
                        <div key={idx} className="flex items-center flex-1">
                            <div className={`flex items-center gap-3 p-3 rounded-xl transition-all ${activeStep === idx + 1
                                    ? 'bg-purple-500/20 border border-purple-500/40'
                                    : 'bg-muted/50'
                                }`}>
                                <step.icon className={`w-5 h-5 ${activeStep === idx + 1 ? 'text-purple-500 animate-pulse' : 'text-muted-foreground'}`} />
                                <div>
                                    <p className="text-sm font-medium">{step.title}</p>
                                    <p className="text-xs text-muted-foreground">{step.desc}</p>
                                </div>
                            </div>
                            {idx < workflowSteps.length - 1 && (
                                <ChevronRight className="w-5 h-5 text-muted-foreground mx-2" />
                            )}
                        </div>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* LEFT: EDITOR */}
                <div className="space-y-4">
                    <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            <Sparkles className="w-5 h-5 text-amber-500" />
                            Configuración del Proyecto
                        </h2>

                        <div className="space-y-4">
                            {/* Project Name */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Nombre del Proyecto *</label>
                                <input
                                    type="text"
                                    value={projectName}
                                    onChange={(e) => setProjectName(e.target.value)}
                                    placeholder="Mi Agente SAP, Automatización Marketing..."
                                    className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground"
                                />
                            </div>

                            {/* Domain */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Dominio</label>
                                <select
                                    value={domain}
                                    onChange={(e) => setDomain(e.target.value)}
                                    className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground"
                                >
                                    <option value="custom">Personalizado</option>
                                    <option value="sap">SAP (FI/CO/ABAP)</option>
                                    <option value="marketing">Marketing</option>
                                    <option value="devops">DevOps</option>
                                </select>
                            </div>

                            {/* Complexity Selector */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Nivel de Complejidad</label>
                                <div className="grid grid-cols-3 gap-3">
                                    {complexityOptions.map((opt) => (
                                        <button
                                            key={opt.value}
                                            onClick={() => setComplexity(opt.value as any)}
                                            className={`p-3 rounded-xl border-2 transition-all text-left ${complexity === opt.value
                                                    ? `border-${opt.color}-500 bg-${opt.color}-500/10`
                                                    : 'border-border hover:border-muted-foreground'
                                                }`}
                                        >
                                            <p className="font-medium text-sm">{opt.label}</p>
                                            <p className="text-xs text-muted-foreground">{opt.desc}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Use Case */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">Describe tu Caso de Uso</label>
                                    <button
                                        onClick={() => setShowQuestionnaire(true)}
                                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/10 text-purple-500 hover:bg-purple-500/20 transition-colors text-xs font-medium"
                                    >
                                        <MessageSquare className="w-3 h-3" />
                                        Usar Cuestionario Inteligente
                                    </button>
                                </div>
                                <textarea
                                    value={useCase}
                                    onChange={(e) => setUseCase(e.target.value)}
                                    placeholder="Ejemplo: Automatizar el cierre mensual financiero incluyendo validación AR/AP, reclasificaciones IFRS, conciliación bancaria y ajustes de FX..."
                                    className="w-full h-48 px-4 py-3 rounded-lg border border-border bg-background text-foreground font-mono text-sm resize-none focus:ring-2 focus:ring-primary/50"
                                />
                                {Object.keys(questionnaireAnswers).length > 0 && (
                                    <p className="mt-2 text-xs text-emerald-500 flex items-center gap-1">
                                        <Eye className="w-3 h-3" />
                                        Generado desde cuestionario inteligente
                                    </p>
                                )}
                            </div>

                            <button
                                onClick={handleGenerate}
                                disabled={!useCase || !projectName || isGenerating}
                                className="w-full px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold hover:opacity-90 disabled:opacity-50 transition-opacity"
                            >
                                {isGenerating ? 'Generando...' : 'Generar Payload de Contexto'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* RIGHT: PAYLOAD VIEWER */}
                <div className="space-y-4">
                    <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            <FileJson className="w-5 h-5 text-blue-500" />
                            Resultado Generado
                        </h2>

                        {!payload ? (
                            <div className="h-96 flex items-center justify-center text-muted-foreground text-sm">
                                El payload aparecerá aquí después de generar
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {/* PRD Summary */}
                                {payload.prd && (
                                    <div className="p-4 bg-muted/50 rounded-xl">
                                        <h4 className="font-medium text-sm mb-2">📋 PRD Generado</h4>
                                        <p className="text-xs text-muted-foreground">{payload.prd.title}</p>
                                        <p className="text-xs mt-1">Timeline: {payload.prd.timeline}</p>
                                    </div>
                                )}

                                {/* Spec Contract Summary */}
                                {payload.spec_contract && (
                                    <div className="p-4 bg-muted/50 rounded-xl">
                                        <h4 className="font-medium text-sm mb-2">⚙️ Spec Contract</h4>
                                        <div className="flex flex-wrap gap-1 mb-2">
                                            {payload.spec_contract.skills_required?.map((skill: string) => (
                                                <span key={skill} className="px-2 py-0.5 bg-purple-500/20 text-purple-600 rounded text-xs">
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                            {payload.spec_contract.mcps_required?.map((mcp: string) => (
                                                <span key={mcp} className="px-2 py-0.5 bg-blue-500/20 text-blue-600 rounded text-xs">
                                                    {mcp}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Full JSON */}
                                <details className="group">
                                    <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
                                        Ver JSON completo
                                    </summary>
                                    <pre className="mt-2 h-48 overflow-auto p-4 bg-muted rounded-lg text-xs font-mono">
                                        {JSON.stringify(payload, null, 2)}
                                    </pre>
                                </details>
                            </div>
                        )}
                    </div>

                    {/* Action Button */}
                    {payload && (
                        <div className="space-y-4">
                            {/* I/O Viewer Button */}
                            <div className="flex items-center justify-between">
                                <IOViewerButton 
                                    onClick={() => setShowIOViewer(true)} 
                                    label="Ver Input/Output completo"
                                    size="md"
                                />
                                <ProcessingTracker stats={stats} compact />
                            </div>
                            
                            {/* Skill Orchestrator Preview */}
                            <SkillOrchestrator 
                                projectContext={{
                                    domain: payload.domain,
                                    complexity: payload.complexity,
                                    objectives: payload.prd?.requirements?.functional || [],
                                    useCase: payload.use_case
                                }}
                            />
                            
                            <motion.button
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                onClick={handleSendToBuilder}
                                className="w-full px-6 py-4 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-lg shadow-purple-500/20"
                            >
                                Enviar a Builder
                                <ChevronRight className="w-5 h-5" />
                            </motion.button>
                        </div>
                    )}
                </div>
            </div>
            
            {/* I/O Viewer Modal */}
            <IOViewerModal
                isOpen={showIOViewer}
                onClose={() => setShowIOViewer(false)}
                title="Architect - Input/Output"
                data={ioData || { input: {}, output: {} }}
            />
            
            {/* Questionnaire Modal */}
            <AnimatePresence>
                {showQuestionnaire && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="w-full max-w-2xl"
                        >
                            <QuestionnaireFlow
                                complexity={complexity}
                                domain={domain}
                                onComplete={handleQuestionnaireComplete}
                                onCancel={() => setShowQuestionnaire(false)}
                            />
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </main>
    )
}
