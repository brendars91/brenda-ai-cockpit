"use client"
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight, ChevronLeft, CheckCircle, HelpCircle, Lightbulb, Target, Settings, AlertTriangle } from 'lucide-react'

interface Question {
    id: string
    text: string
    hint: string
    category: 'core' | 'integration' | 'security' | 'architecture' | 'risk'
    required: boolean
}

interface QuestionnaireFlowProps {
    complexity: 'simple' | 'medium' | 'difficult'
    domain: string
    onComplete: (answers: Record<string, string>) => void
    onCancel: () => void
}

// Preguntas base - Las 4 de Oro (siempre se muestran)
const CORE_QUESTIONS: Question[] = [
    {
        id: 'problem',
        text: '¿Qué problema específico resuelves y para quién?',
        hint: 'Ejemplo: "Los contadores de mi empresa pierden 2 horas diarias reconciliando facturas manualmente"',
        category: 'core',
        required: true
    },
    {
        id: 'io',
        text: '¿Qué input recibe y qué output exacto debe entregar?',
        hint: 'Ejemplo: Input: "Archivo Excel con transacciones" → Output: "Reporte PDF con discrepancias marcadas"',
        category: 'core',
        required: true
    },
    {
        id: 'constraints',
        text: '¿Qué restricciones técnicas o de negocio son innegociables?',
        hint: 'Ejemplo: "Debe funcionar offline", "No puede acceder a datos personales", "Debe cumplir GDPR"',
        category: 'core',
        required: true
    },
    {
        id: 'success',
        text: '¿Cómo sabremos que ha tenido éxito? ¿Qué KPI o métrica usamos?',
        hint: 'Ejemplo: "Reducir tiempo de reconciliación a <10 minutos", "Tasa de error <1%"',
        category: 'core',
        required: true
    }
]

// Preguntas contextuales por nivel
const CONTEXTUAL_QUESTIONS: Record<string, Question[]> = {
    simple: [
        {
            id: 'frequency',
            text: '¿Con qué frecuencia se ejecutará esta tarea?',
            hint: 'Diario, semanal, mensual, bajo demanda...',
            category: 'integration',
            required: false
        },
        {
            id: 'users',
            text: '¿Cuántos usuarios aproximadamente lo usarán?',
            hint: '1-5 usuarios, equipo pequeño, empresa completa...',
            category: 'integration',
            required: false
        }
    ],
    medium: [
        {
            id: 'frequency',
            text: '¿Con qué frecuencia se ejecutará y qué volumen de datos maneja?',
            hint: 'Ejemplo: "Diario, ~1000 registros por ejecución"',
            category: 'integration',
            required: true
        },
        {
            id: 'integrations',
            text: '¿Con qué sistemas externos debe integrarse?',
            hint: 'Ejemplo: "SAP, Salesforce, API interna de facturación"',
            category: 'integration',
            required: true
        },
        {
            id: 'auth',
            text: '¿Qué nivel de autenticación/autorización necesita?',
            hint: 'Ejemplo: "Solo usuarios con rol Finance pueden ejecutar"',
            category: 'security',
            required: true
        },
        {
            id: 'errors',
            text: '¿Qué debe pasar cuando algo falla? ¿Notificación, rollback, retry?',
            hint: 'Ejemplo: "Reintentar 3 veces, luego notificar a admin por email"',
            category: 'architecture',
            required: true
        }
    ],
    difficult: [
        {
            id: 'frequency',
            text: '¿Cuál es el SLA esperado? (tiempo de respuesta, disponibilidad)',
            hint: 'Ejemplo: "99.9% uptime, respuesta <2 segundos"',
            category: 'integration',
            required: true
        },
        {
            id: 'integrations',
            text: '¿Qué sistemas existentes deben integrarse y cómo se comunicarán?',
            hint: 'APIs REST, webhooks, mensajería (Kafka/RabbitMQ), bases de datos compartidas...',
            category: 'integration',
            required: true
        },
        {
            id: 'auth',
            text: '¿Qué requisitos de seguridad y compliance debe cumplir?',
            hint: 'GDPR, SOC2, ISO 27001, encriptación en reposo/tránsito, auditoría...',
            category: 'security',
            required: true
        },
        {
            id: 'scalability',
            text: '¿Cómo debe escalar? ¿Horizontal, vertical? ¿Límites esperados?',
            hint: 'Ejemplo: "De 100 a 10,000 usuarios en 6 meses"',
            category: 'architecture',
            required: true
        },
        {
            id: 'recovery',
            text: '¿Cuál es la estrategia de recuperación ante fallos?',
            hint: 'Rollback automático, circuit breaker, degradación graceful, DR site...',
            category: 'architecture',
            required: true
        },
        {
            id: 'risks',
            text: '¿Cuáles son los principales riesgos técnicos o de negocio?',
            hint: 'Ejemplo: "Dependencia de API externa inestable", "Datos sensibles de clientes"',
            category: 'risk',
            required: true
        }
    ]
}

// Preguntas específicas por dominio
const DOMAIN_QUESTIONS: Record<string, Question[]> = {
    sap: [
        {
            id: 'sap_modules',
            text: '¿Qué módulos SAP están involucrados?',
            hint: 'FI, CO, SD, MM, PP, HR, ABAP custom...',
            category: 'integration',
            required: true
        },
        {
            id: 'sap_transactions',
            text: '¿Qué transacciones o BAPIs se utilizarán?',
            hint: 'Ejemplo: FB50, F110, BAPI_ACC_DOCUMENT_POST...',
            category: 'integration',
            required: true
        }
    ],
    devops: [
        {
            id: 'devops_stack',
            text: '¿Cuál es el stack de infraestructura actual?',
            hint: 'AWS/GCP/Azure, Kubernetes, Docker, Terraform...',
            category: 'integration',
            required: true
        },
        {
            id: 'devops_pipeline',
            text: '¿Qué herramienta de CI/CD usas actualmente?',
            hint: 'GitHub Actions, Jenkins, GitLab CI, CircleCI...',
            category: 'integration',
            required: true
        }
    ],
    marketing: [
        {
            id: 'marketing_channels',
            text: '¿Qué canales de marketing están en scope?',
            hint: 'Email, Social Media, PPC, SEO, Content...',
            category: 'integration',
            required: true
        },
        {
            id: 'marketing_tools',
            text: '¿Qué herramientas de marketing usas?',
            hint: 'HubSpot, Mailchimp, Google Analytics, Hootsuite...',
            category: 'integration',
            required: true
        }
    ]
}

export function QuestionnaireFlow({ complexity, domain, onComplete, onCancel }: QuestionnaireFlowProps) {
    const [currentIndex, setCurrentIndex] = useState(0)
    const [answers, setAnswers] = useState<Record<string, string>>({})
    const [showHint, setShowHint] = useState(false)

    // Construir lista de preguntas según complejidad y dominio
    const questions = [
        ...CORE_QUESTIONS,
        ...(CONTEXTUAL_QUESTIONS[complexity] || []),
        ...(DOMAIN_QUESTIONS[domain] || [])
    ]

    const currentQuestion = questions[currentIndex]
    const progress = ((currentIndex + 1) / questions.length) * 100
    const canProceed = currentQuestion
        ? (answers[currentQuestion.id]?.trim().length ?? 0) > 0 || !currentQuestion.required
        : true

    const getCategoryIcon = (category: string) => {
        switch (category) {
            case 'core': return <Target className="w-4 h-4 text-purple-500" />
            case 'integration': return <Settings className="w-4 h-4 text-blue-500" />
            case 'security': return <AlertTriangle className="w-4 h-4 text-amber-500" />
            case 'architecture': return <Settings className="w-4 h-4 text-cyan-500" />
            case 'risk': return <AlertTriangle className="w-4 h-4 text-red-500" />
            default: return <HelpCircle className="w-4 h-4" />
        }
    }

    const getCategoryLabel = (category: string) => {
        switch (category) {
            case 'core': return 'Pregunta Fundamental'
            case 'integration': return 'Integración'
            case 'security': return 'Seguridad'
            case 'architecture': return 'Arquitectura'
            case 'risk': return 'Riesgos'
            default: return 'General'
        }
    }

    const handleNext = () => {
        if (currentIndex < questions.length - 1) {
            setCurrentIndex(currentIndex + 1)
            setShowHint(false)
        } else {
            onComplete(answers)
        }
    }

    const handlePrev = () => {
        if (currentIndex > 0) {
            setCurrentIndex(currentIndex - 1)
            setShowHint(false)
        }
    }

    return (
        <div className="bg-card border border-border rounded-2xl p-6 shadow-lg">
            {/* Progress Bar */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">
                        Pregunta {currentIndex + 1} de {questions.length}
                    </span>
                    <span className="text-sm font-medium text-cyan-500">
                        {Math.round(progress)}% completado
                    </span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.3 }}
                    />
                </div>
            </div>

            {/* Question Card */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentQuestion?.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="space-y-4"
                >
                    {/* Category Badge */}
                    <div className="flex items-center gap-2">
                        {currentQuestion && getCategoryIcon(currentQuestion.category)}
                        <span className="text-xs text-muted-foreground uppercase tracking-wide">
                            {currentQuestion && getCategoryLabel(currentQuestion.category)}
                        </span>
                        {currentQuestion?.required && (
                            <span className="text-xs text-red-400">*Requerida</span>
                        )}
                    </div>

                    {/* Question Text */}
                    <h3 className="text-xl font-semibold leading-relaxed">
                        {currentQuestion?.text}
                    </h3>

                    {/* Answer Input */}
                    {currentQuestion && (
                        <textarea
                            value={answers[currentQuestion.id] || ''}
                            onChange={(e) => setAnswers({ ...answers, [currentQuestion.id]: e.target.value })}
                            placeholder="Escribe tu respuesta aquí..."
                            className="w-full h-32 px-4 py-3 rounded-xl border border-border bg-background text-foreground font-mono text-sm resize-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
                        />
                    )}

                    {/* Hint Toggle */}
                    <button
                        onClick={() => setShowHint(!showHint)}
                        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <Lightbulb className={`w-4 h-4 ${showHint ? 'text-amber-500' : ''}`} />
                        {showHint ? 'Ocultar ejemplo' : 'Ver ejemplo'}
                    </button>

                    {/* Hint Content */}
                    <AnimatePresence>
                        {showHint && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl"
                            >
                                <p className="text-sm text-amber-200">
                                    💡 {currentQuestion?.hint}
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </AnimatePresence>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-8 pt-4 border-t border-border">
                <button
                    onClick={currentIndex === 0 ? onCancel : handlePrev}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-muted transition-colors text-sm"
                >
                    <ChevronLeft className="w-4 h-4" />
                    {currentIndex === 0 ? 'Cancelar' : 'Anterior'}
                </button>

                <div className="flex items-center gap-1">
                    {questions.map((q, idx) => (
                        <div
                            key={q.id || idx}
                            className={`w-2 h-2 rounded-full transition-colors ${idx === currentIndex
                                    ? 'bg-cyan-500'
                                    : q.id && answers[q.id]
                                        ? 'bg-emerald-500'
                                        : 'bg-muted'
                                }`}
                        />
                    ))}
                </div>

                <button
                    onClick={handleNext}
                    disabled={!canProceed}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 text-white hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
                >
                    {currentIndex === questions.length - 1 ? (
                        <>
                            <CheckCircle className="w-4 h-4" />
                            Completar
                        </>
                    ) : (
                        <>
                            Siguiente
                            <ChevronRight className="w-4 h-4" />
                        </>
                    )}
                </button>
            </div>
        </div>
    )
}
