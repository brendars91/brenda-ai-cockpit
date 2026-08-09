import React from 'react';
import { Terminal, FileJson, FileText, Check, X } from 'lucide-react';

interface ArtifactViewerProps {
    title: string;
    data: any;
    type: 'json' | 'text' | 'markdown';
    onApprove?: () => void;
    onReject?: () => void;
    autoHeight?: boolean;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ title, data, type, onApprove, onReject, autoHeight = false }) => {
    return (
        <div className={`glass-panel rounded-xl overflow-hidden border border-slate-700/50 flex flex-col ${autoHeight ? '' : 'h-[300px] sm:h-[400px] md:h-[500px]'}`}>
            {/* Header - Responsive */}
            <div className="bg-slate-900/50 p-2 sm:p-3 border-b border-slate-700/50 flex justify-between items-center">
                <div className="flex items-center gap-1.5 sm:gap-2">
                    {type === 'json' ? <FileJson className="w-3 h-3 sm:w-4 sm:h-4 text-blue-400" /> : <FileText className="w-3 h-3 sm:w-4 sm:h-4 text-emerald-400" />}
                    <span className="text-[10px] sm:text-xs font-bold text-slate-300 uppercase tracking-wider truncate max-w-[150px] sm:max-w-none">{title}</span>
                </div>
                <div className="flex gap-2">
                    <div className="flex gap-1">
                        <span className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-red-500/50"></span>
                        <span className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-yellow-500/50"></span>
                        <span className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-green-500/50"></span>
                    </div>
                </div>
            </div>

            {/* Content - Responsive */}
            <div className="flex-1 overflow-auto p-2 sm:p-4 bg-slate-950/80 font-mono text-[10px] sm:text-xs text-slate-300 custom-scrollbar">
                {type === 'json' ? (
                    <pre className="whitespace-pre-wrap break-words text-blue-300">
                        {JSON.stringify(data, null, 2)}
                    </pre>
                ) : (
                    <div className="whitespace-pre-wrap prose prose-invert max-w-none text-slate-300 text-[10px] sm:text-xs">
                        {typeof data === 'string' ? data : JSON.stringify(data)}
                    </div>
                )}
            </div>

            {/* Actions Footer - Responsive with Touch Targets */}
            {(onApprove || onReject) && (
                <div className="p-2 sm:p-4 bg-slate-900/50 border-t border-slate-700/50 flex flex-col sm:flex-row gap-2 sm:gap-4">
                    {onReject && (
                        <button
                            onClick={onReject}
                            className="flex-1 py-3 sm:py-2 rounded bg-red-500/10 hover:bg-red-500/20 active:bg-red-500/30 border border-red-500/30 text-red-400 text-xs font-bold transition-all flex items-center justify-center gap-2 min-h-[44px]">
                            <X className="w-4 h-4" /> REJECT
                        </button>
                    )}
                    {onApprove && (
                        <button
                            onClick={onApprove}
                            className="flex-1 py-3 sm:py-2 rounded bg-green-500/20 hover:bg-green-500/30 active:bg-green-500/40 border border-green-500/40 text-green-400 text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(34,197,94,0.1)] min-h-[44px]">
                            <Check className="w-4 h-4" /> APPROVE & PROCEED
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};
