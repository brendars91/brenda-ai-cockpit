import { Github, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface GitHubStatus {
    status: string
    is_production: boolean
    is_configured: boolean
    user?: string
    repos?: number
}

const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE = RAW_URL.replace(/\/api\/?$/, '') + '/api';

export function GitHubStatusBadge() {
    const [status, setStatus] = useState<GitHubStatus | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await fetch(`${API_BASE}/github/status`)
                if (res.ok) {
                    const data = await res.json()
                    setStatus(data)
                }
            } catch (err) {
                console.error("GitHub status check failed", err)
            } finally {
                setLoading(false)
            }
        }
        checkStatus()
    }, [])

    if (loading) return null

    const isConnected = status?.status === 'connected'
    const isProd = status?.is_production

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className={`
            flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border
            ${isConnected
                    ? 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700'
                    : 'bg-amber-500/10 text-amber-600 border-amber-500/20'}
        `} title={isConnected ? `Conectado como ${status?.user}` : 'Modo Local - GitHub no conectado'}>
            <Github className="w-3.5 h-3.5" />

            {isConnected ? (
                <div className="flex items-center gap-1.5">
                    <span>Synced</span>
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    {isProd && <span className="ml-1 opacity-50 text-[10px] uppercase tracking-wider border-l border-current pl-1.5">Prod</span>}
                </div>
            ) : (
                <span>Local Mode</span>
            )}
        </motion.div>
    )
}
