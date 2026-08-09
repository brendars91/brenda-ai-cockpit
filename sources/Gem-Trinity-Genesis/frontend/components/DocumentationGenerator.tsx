"use client"
import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Download, Eye, CheckCircle, Clock, Wrench, Server, FileJson, Copy, Check } from 'lucide-react'

interface ProjectDocumentation {
    projectName: string
    createdAt: string
    domain: string
    complexity: string
    prd: {
        title: string
        overview: any
        requirements: any
        constraints: string[]
        timeline: string
    }
    specContract: {
        skills_required: string[]
        mcps_required: string[]
        execution_mode: string
    }
    transferredResources: {
        skills: { name: string; description: string; adapted: boolean }[]
        mcps: { name: string; description: string }[]
    }
    executionHistory?: {
        timestamp: string
        task: string
        result: string
        tokensUsed: number
    }[]
    processingStats?: {
        llmPercentage: number
        deterministicPercentage: number
        totalTokens: number
    }
}

interface DocumentationGeneratorProps {
    projectId: string
    documentation?: ProjectDocumentation
}

export function DocumentationGenerator({ projectId, documentation }: DocumentationGeneratorProps) {
    const [isGenerating, setIsGenerating] = useState(false)
    const [isDownloading, setIsDownloading] = useState(false)
    const [showPreview, setShowPreview] = useState(false)
    const [copied, setCopied] = useState(false)

    const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const API_BASE = RAW_URL.replace(/\/api\/?$/, '') + '/api'

    const generateMarkdown = (doc: ProjectDocumentation): string => {
        return `# ${doc.projectName}

> Documentación generada automáticamente por Gem Trinity Genesis
> Fecha: ${new Date(doc.createdAt).toLocaleDateString('es-ES', { dateStyle: 'full' })}

---

## 📋 Información General

| Campo | Valor |
|-------|-------|
| **Dominio** | ${doc.domain} |
| **Complejidad** | ${doc.complexity} |
| **Timeline** | ${doc.prd.timeline} |

---

## 📝 PRD (Product Requirements Document)

### ${doc.prd.title}

#### Problema a Resolver
${doc.prd.overview?.problem_statement || 'No especificado'}

#### Usuarios Objetivo
${(doc.prd.overview?.target_users || []).map((u: string) => `- ${u}`).join('\n')}

#### Métricas de Éxito
${(doc.prd.overview?.success_metrics || []).map((m: string) => `- ${m}`).join('\n')}

### Requisitos

#### Funcionales
${(doc.prd.requirements?.functional || []).map((r: string) => `- ${r}`).join('\n')}

#### No Funcionales
${(doc.prd.requirements?.non_functional || []).map((r: string) => `- ${r}`).join('\n')}

### Restricciones
${doc.prd.constraints.map(c => `- ${c}`).join('\n')}

---

## ⚙️ Especificación Técnica (Spec Contract)

### Skills Requeridas
${doc.specContract.skills_required.map(s => `- \`${s}\``).join('\n')}

### MCPs Requeridos
${doc.specContract.mcps_required.map(m => `- \`${m}\``).join('\n')}

### Modo de Ejecución
\`${doc.specContract.execution_mode}\`

---

## 🔧 Recursos Transferidos al Proyecto

### Skills Adaptadas
${doc.transferredResources.skills.map(s =>
            `- **${s.name}** ${s.adapted ? '(Adaptada 100%)' : ''}: ${s.description}`
        ).join('\n')}

### MCPs Configurados
${doc.transferredResources.mcps.map(m =>
            `- **${m.name}**: ${m.description}`
        ).join('\n')}

---

${doc.executionHistory && doc.executionHistory.length > 0 ? `
## 📊 Historial de Ejecuciones

| Fecha | Tarea | Tokens |
|-------|-------|--------|
${doc.executionHistory.map(e =>
            `| ${new Date(e.timestamp).toLocaleString()} | ${e.task.substring(0, 50)}... | ${e.tokensUsed} |`
        ).join('\n')}
` : ''}

${doc.processingStats ? `
## 📈 Estadísticas de Procesamiento

- **Determinístico**: ${doc.processingStats.deterministicPercentage}%
- **LLM**: ${doc.processingStats.llmPercentage}%
- **Total Tokens**: ${doc.processingStats.totalTokens.toLocaleString()}

> 💡 Un alto porcentaje determinístico indica eficiencia y reducción de costos.
` : ''}

---

## 📚 README del Proyecto

### Descripción
Este proyecto fue generado usando la plataforma **Gem Trinity Genesis**, un orquestador de agentes de IA que combina procesamiento determinístico con capacidades LLM para máxima eficiencia.

### Cómo Usar

1. **Configuración Inicial**
   - Asegúrate de tener configurados los MCPs listados arriba
   - Instala las dependencias del proyecto

2. **Ejecución**
   - El agente está preconfigurado con las skills adaptadas al 100%
   - Ejecuta el comando principal según tu entorno

3. **Personalización**
   - Las skills transferidas pueden modificarse en \`/skills\`
   - La configuración de MCPs está en \`/config/mcps.json\`

### Arquitectura

\`\`\`
┌─────────────────────────────────────────┐
│           Gem Trinity Genesis           │
├─────────────┬─────────────┬─────────────┤
│  Architect  │   Builder   │   Engine    │
│  (Diseño)   │ (Compila)   │ (Ejecuta)   │
└─────────────┴─────────────┴─────────────┘
        │              │              │
        ▼              ▼              ▼
   ┌────────┐    ┌────────┐    ┌────────┐
   │  PRD   │    │ Skills │    │ Output │
   │  Spec  │    │  MCPs  │    │  Logs  │
   └────────┘    └────────┘    └────────┘
\`\`\`

### Soporte
- Documentación: [Gem Trinity Genesis Docs]
- Issues: [GitHub Repository]

---

*Generado con ❤️ por Gem Trinity Genesis v2026.2.0*
`
    }

    const handleDownloadMarkdown = async () => {
        if (!documentation) return

        setIsDownloading(true)
        try {
            const markdown = generateMarkdown(documentation)
            const blob = new Blob([markdown], { type: 'text/markdown' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${documentation.projectName.replace(/\s+/g, '_')}_documentation.md`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)
        } finally {
            setIsDownloading(false)
        }
    }

    const handleCopyMarkdown = async () => {
        if (!documentation) return
        const markdown = generateMarkdown(documentation)
        await navigator.clipboard.writeText(markdown)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    if (!documentation) {
        return (
            <div className="bg-card border border-border rounded-xl p-6">
                <div className="flex items-center gap-3 text-muted-foreground">
                    <FileText className="w-5 h-5" />
                    <span>Cargando documentación del proyecto...</span>
                </div>
            </div>
        )
    }

    return (
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border bg-muted/20">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-amber-500/20">
                        <FileText className="w-5 h-5 text-amber-500" />
                    </div>
                    <div>
                        <h3 className="font-semibold">Documentación Completa</h3>
                        <p className="text-xs text-muted-foreground">PRD + Spec + Skills + MCPs + README</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowPreview(!showPreview)}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm"
                    >
                        <Eye className="w-4 h-4" />
                        {showPreview ? 'Ocultar' : 'Vista Previa'}
                    </button>
                    <button
                        onClick={handleCopyMarkdown}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm"
                    >
                        {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                        {copied ? 'Copiado' : 'Copiar'}
                    </button>
                    <button
                        onClick={handleDownloadMarkdown}
                        disabled={isDownloading}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 text-white hover:opacity-90 transition-opacity text-sm font-medium"
                    >
                        <Download className="w-4 h-4" />
                        {isDownloading ? 'Descargando...' : 'Descargar MD'}
                    </button>
                </div>
            </div>

            {/* Summary Cards */}
            <div className="p-4 grid grid-cols-4 gap-4">
                <div className="p-3 bg-purple-500/10 rounded-xl border border-purple-500/20">
                    <div className="flex items-center gap-2 mb-1">
                        <FileJson className="w-4 h-4 text-purple-500" />
                        <span className="text-xs text-muted-foreground">PRD</span>
                    </div>
                    <p className="text-sm font-medium truncate">{documentation.prd.title}</p>
                </div>
                <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
                    <div className="flex items-center gap-2 mb-1">
                        <Wrench className="w-4 h-4 text-blue-500" />
                        <span className="text-xs text-muted-foreground">Skills</span>
                    </div>
                    <p className="text-sm font-medium">{documentation.transferredResources.skills.length} transferidas</p>
                </div>
                <div className="p-3 bg-cyan-500/10 rounded-xl border border-cyan-500/20">
                    <div className="flex items-center gap-2 mb-1">
                        <Server className="w-4 h-4 text-cyan-500" />
                        <span className="text-xs text-muted-foreground">MCPs</span>
                    </div>
                    <p className="text-sm font-medium">{documentation.transferredResources.mcps.length} configurados</p>
                </div>
                <div className="p-3 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
                    <div className="flex items-center gap-2 mb-1">
                        <Clock className="w-4 h-4 text-emerald-500" />
                        <span className="text-xs text-muted-foreground">Timeline</span>
                    </div>
                    <p className="text-sm font-medium">{documentation.prd.timeline}</p>
                </div>
            </div>

            {/* Preview */}
            {showPreview && (
                <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    className="border-t border-border"
                >
                    <pre className="p-4 bg-slate-950 text-slate-300 text-xs font-mono overflow-auto max-h-96 whitespace-pre-wrap">
                        {generateMarkdown(documentation)}
                    </pre>
                </motion.div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between p-4 border-t border-border bg-muted/20">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <CheckCircle className="w-3 h-3 text-emerald-500" />
                    Documentación incluye README detallado
                </div>
                <span className="text-xs text-muted-foreground">
                    Última actualización: {new Date().toLocaleString()}
                </span>
            </div>
        </div>
    )
}
