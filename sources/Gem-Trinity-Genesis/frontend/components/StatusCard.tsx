import { LucideIcon } from 'lucide-react';
import React from 'react';

interface StatusCardProps {
    title: string;
    description: string;
    icon: LucideIcon;
    status: string;
    color: 'blue' | 'purple' | 'emerald';
    onClick?: () => void;
}

export function StatusCard({ title, description, icon: Icon, status, color, onClick }: StatusCardProps) {
    const colorStyles = {
        blue: 'bg-blue-50 text-blue-600 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800',
        purple: 'bg-purple-50 text-purple-600 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400 dark:border-purple-800',
        emerald: 'bg-emerald-50 text-emerald-600 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800'
    };

    const statusColors = {
        online: 'bg-emerald-500',
        offline: 'bg-rose-500',
        idle: 'bg-amber-500',
        unknown: 'bg-slate-300'
    };

    return (
        <div
            onClick={onClick}
            className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-md hover:-translate-y-1 dark:bg-slate-900 dark:border-slate-800 cursor-pointer"
        >
            <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl border ${colorStyles[color]}`}>
                <Icon className="h-6 w-6" />
            </div>

            <h3 className="mb-2 text-xl font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                {title}
            </h3>

            <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
                {description}
            </p>

            <div className="flex items-center justify-between border-t border-slate-100 pt-4 dark:border-slate-800">
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Status</span>
                <div className="flex items-center gap-2">
                    <span className={`h-2 w-2 rounded-full ${statusColors[status.toLowerCase() as keyof typeof statusColors] || 'bg-slate-300'} shadow-[0_0_8px_rgba(0,0,0,0.1)]`}></span>
                    <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">{status}</span>
                </div>
            </div>
        </div>
    );
}
