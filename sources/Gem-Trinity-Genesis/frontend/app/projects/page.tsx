"use client"
import Link from 'next/link'
import { ArrowLeft, FolderKanban, Trash2, Play, Layers, Code, RefreshCw, FileText } from 'lucide-react'
import { motion } from 'framer-motion'
import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { DoubleConfirmDelete, DeleteButton } from '@/components/DoubleConfirmDelete'
import { DocumentationGenerator } from '@/components/DocumentationGenerator'
import { GitHubStatusBadge } from '@/components/index'

export default function ProjectsPage() {
    const router = useRouter()
    const [projects, setProjects] = useState<any[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [deletingProject, setDeletingProject] = useState<any>(null)
    const [showDocumentation, setShowDocumentation] = useState<string | null>(null)
    const [documentation, setDocumentation] = useState<any>(null)

    const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const API_BASE = RAW_URL.replace(/\/api\/?$/, '') + '/api';

    const fetchProjects = useCallback(async () => {
        setIsLoading(true)
        try {
            const res = await fetch(`${API_BASE}/projects`)
            const data = await res.json()
            setProjects(data.projects || [])
        } catch (err) {
            console.error(err)
        } finally {
            setIsLoading(false)
        }
    }, [API_BASE])

    useEffect(() => {
        fetchProjects()
    }, [fetchProjects])

    const handleDelete = async (projectId: string) => {
        try {
            const res = await fetch(`${API_BASE}/projects/${projectId}`, { method: 'DELETE' })
            if (!res.ok) {
                throw new Error('Error al eliminar el proyecto')
            }
            await fetchProjects()
            setDeletingProject(null)
        } catch (err) {
            console.error(err)
            throw err
        }
    }
    
    const fetchDocumentation = async (projectId: string) => {
        try {
            const res = await fetch(`${API_BASE}/documentation/${projectId}`)
            const data = await res.json()
            setDocumentation(data)
            setShowDocumentation(projectId)
        } catch (err) {
            console.error(err)
        }
    }

    const getStageInfo = (stage: string) => {
        switch (stage) {
            case 'design':
                return { label: 'Diseño', color: 'bg-purple-500/10 text-purple-600 border-purple-500/20', icon: Code }
            case 'compiled':
                return { label: 'Compilado', color: 'bg-blue-500/10 text-blue-600 border-blue-500/20', icon: Layers }
            case 'executed':
                return { label: 'Ejecutado', color: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20', icon: Play }
            default:
                return { label: stage, color: 'bg-muted text-muted-foreground', icon: FolderKanban }
        }
    }

    const getNextAction = (project: any) => {
        if (project.stage === 'design') {
            return { label: 'Compilar', href: `/builder?payload=${project.id}`, color: 'bg-blue-600 hover:bg-blue-700' }
        }
        if (project.stage === 'compiled' && project.agent_id) {
            return { label: 'Ejecutar', href: `/engine?agent=${project.agent_id}`, color: 'bg-emerald-600 hover:bg-emerald-700' }
        }
        return null
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
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
                            <FolderKanban className="w-6 h-6 text-amber-600" />
                        </div>
                        <div>
                            <h1 className="text-4xl font-bold font-heading text-foreground">Proyectos</h1>
                            <p className="text-muted-foreground text-sm flex items-center gap-2">
                                Gestiona todos tus proyectos de agentes de IA
                                <span className="mx-2">|</span>
                                <GitHubStatusBadge />
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={fetchProjects}
                        className="p-2 rounded-lg hover:bg-muted transition-colors"
                        title="Actualizar"
                    >
                        <RefreshCw className={`w-5 h-5 text-muted-foreground ${isLoading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </motion.header>

            {/* PROJECTS GRID */}
            <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold">Todos los Proyectos</h2>
                    <span className="text-sm text-muted-foreground">{projects.length} proyecto(s)</span>
                </div>

                {isLoading ? (
                    <div className="h-64 flex items-center justify-center">
                        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    </div>
                ) : projects.length === 0 ? (
                    <div className="h-64 flex flex-col items-center justify-center text-muted-foreground">
                        <FolderKanban className="w-12 h-12 mb-4 opacity-50" />
                        <p>No hay proyectos</p>
                        <p className="text-sm mt-2">Crea tu primer proyecto en Architect</p>
                        <Link href="/architect" className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm">
                            Ir a Architect
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {projects.map((project, idx) => {
                            const stageInfo = getStageInfo(project.stage)
                            const nextAction = getNextAction(project)
                            const StageIcon = stageInfo.icon

                            return (
                                <motion.div
                                    key={project.id || idx}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: idx * 0.05 }}
                                    className="border border-border rounded-xl p-4 bg-background/50 hover:bg-background transition-colors"
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            <StageIcon className="w-4 h-4 text-muted-foreground" />
                                            <h3 className="font-semibold text-sm truncate max-w-[180px]">
                                                {project.name || `Proyecto ${project.id?.slice(0, 8)}`}
                                            </h3>
                                        </div>
                                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${stageInfo.color}`}>
                                            {stageInfo.label}
                                        </span>
                                    </div>

                                    <p className="text-xs text-muted-foreground mb-1">
                                        Dominio: {project.domain || 'custom'}
                                    </p>
                                    <p className="text-xs text-muted-foreground mb-3">
                                        ID: {project.id?.slice(0, 12)}...
                                    </p>

                                    <div className="flex items-center gap-2 pt-3 border-t border-border">
                                        {nextAction && (
                                            <Link
                                                href={nextAction.href}
                                                className={`flex-1 px-3 py-1.5 rounded-lg text-white text-xs font-medium text-center ${nextAction.color} transition-colors`}
                                            >
                                                {nextAction.label}
                                            </Link>
                                        )}
                                        <button
                                            onClick={() => fetchDocumentation(project.id)}
                                            className="p-1.5 rounded-lg bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 transition-colors"
                                            title="Ver Documentación"
                                        >
                                            <FileText className="w-4 h-4" />
                                        </button>
                                        <DeleteButton
                                            onClick={() => setDeletingProject(project)}
                                            size="sm"
                                        />
                                    </div>
                                </motion.div>
                            )
                        })}
                    </div>
                )}
            </div>

            {/* Quick Stats */}
            <div className="mt-6 grid grid-cols-3 gap-4">
                <div className="bg-card border border-border rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-purple-600">
                        {projects.filter(p => p.stage === 'design').length}
                    </p>
                    <p className="text-xs text-muted-foreground">En Diseño</p>
                </div>
                <div className="bg-card border border-border rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-blue-600">
                        {projects.filter(p => p.stage === 'compiled').length}
                    </p>
                    <p className="text-xs text-muted-foreground">Compilados</p>
                </div>
                <div className="bg-card border border-border rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-emerald-600">
                        {projects.filter(p => p.stage === 'executed').length}
                    </p>
                    <p className="text-xs text-muted-foreground">Ejecutados</p>
                </div>
            </div>
            
            {/* Double Confirm Delete Modal */}
            <DoubleConfirmDelete
                isOpen={!!deletingProject}
                onClose={() => setDeletingProject(null)}
                onConfirm={() => handleDelete(deletingProject?.id)}
                projectName={deletingProject?.name || `Proyecto ${deletingProject?.id?.slice(0, 8)}`}
                itemType="project"
            />
            
            {/* Documentation Modal */}
            {showDocumentation && documentation && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowDocumentation(null)}>
                    <div className="w-full max-w-4xl max-h-[85vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
                        <DocumentationGenerator
                            projectId={showDocumentation}
                            documentation={documentation}
                        />
                    </div>
                </div>
            )}
        </main>
    )
}
