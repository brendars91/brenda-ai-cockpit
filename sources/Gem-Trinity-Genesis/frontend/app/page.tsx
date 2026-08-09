"use client";

import React, { useEffect, useState } from 'react';
import { useSystemMetrics } from '../hooks/useSystemMetrics';
import { Activity, Cpu, Shield, Zap, Terminal, Box, Play, FileJson, CheckCircle } from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';
import { Doughnut, Line } from 'react-chartjs-2';
import { ArtifactViewer } from './components/ArtifactViewer';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement);

type WorkflowStep = 'IDLE' | 'ARCHITECTING' | 'ARCHITECT_REVIEW' | 'BUILDING' | 'ENGINE_ACTIVE';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
    const metrics = useSystemMetrics();

    // Charts Data
    const doughnutData = {
        labels: ['Deterministic (Code)', 'LLM (AI)'],
        datasets: [{
            data: [metrics.determinism_percentage, metrics.llm_percentage],
            backgroundColor: ['#3B82F6', '#8B5CF6'],
            borderColor: ['rgba(59, 130, 246, 0.5)', 'rgba(139, 92, 246, 0.5)'],
            borderWidth: 1,
        }]
    };

    const lineData = {
        labels: metrics.metrics_history.map((_, i) => i),
        datasets: [{
            label: 'Ops/sec',
            data: metrics.metrics_history,
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };

    const [loading, setLoading] = useState(false);
    const [notification, setNotification] = useState<string | null>(null);

    // Glass Box Workflow State
    const [workflowStep, setWorkflowStep] = useState<WorkflowStep>('IDLE');
    const [architectData, setArchitectData] = useState<any>(null);

    const [showModal, setShowModal] = useState(false);
    const [projectData, setProjectData] = useState({ use_case: '', domain: 'custom', complexity: 'medium' });

    const handleCreateProject = async () => {
        setShowModal(false);
        setLoading(true);
        setWorkflowStep('ARCHITECTING');
        setNotification(`Architect: Analyzing requirements for '${projectData.domain}' project...`);
        try {
            const res = await fetch(`${API_URL}/api/architect/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    use_case: projectData.use_case,
                    domain: projectData.domain,
                    complexity: projectData.complexity,
                    model: "gemini-pro"
                })
            });
            if (res.ok) {
                const data = await res.json();
                setArchitectData(data);
                setWorkflowStep('ARCHITECT_REVIEW'); // PAUSE FOR REVIEW
                setNotification(`Architect: Blueprint Ready. Please Review Artifacts.`);
                setLoading(false); // Stop generic loading, we are now in review mode
            } else {
                setNotification("Architect Error: Failed to generate spec.");
                setWorkflowStep('IDLE');
                setLoading(false);
            }
        } catch (e) {
            setNotification("Connection Error: Backend unreachable.");
            setWorkflowStep('IDLE');
            setLoading(false);
        }
    };

    const handleApproveAndBuild = async () => {
        if (!architectData) return;

        setWorkflowStep('BUILDING');
        setLoading(true);
        setNotification(`Builder: Compiling '${architectData.project_name}'...`);

        try {
            await fetch(`${API_URL}/api/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'compile', target: architectData.payload_id })
            });
            // We assume it's queued. In a real app we'd poll for status. 
            // For now, let's auto-transition visually after a delay or just stay in 'BUILDING' until webhook
            setNotification("Builder: Tasks Queued. Monitoring build process...");
            setTimeout(() => {
                setWorkflowStep('ENGINE_ACTIVE');
                setLoading(false);
                setNotification("Engine: Project Active.");
            }, 3000);

        } catch (e) {
            setNotification("Builder Error: Failed to queue tasks.");
            setLoading(false);
        }
    };
    return (
        <main className="min-h-screen p-3 sm:p-4 md:p-8 relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
                <div className="absolute top-[-10%] right-[-5%] w-[300px] sm:w-[500px] h-[300px] sm:h-[500px] bg-blue-600/20 rounded-full blur-[80px] sm:blur-[100px] animate-pulse-glow"></div>
                <div className="absolute bottom-[-10%] left-[-5%] w-[300px] sm:w-[500px] h-[300px] sm:h-[500px] bg-purple-600/20 rounded-full blur-[80px] sm:blur-[100px] animate-pulse-glow" style={{ animationDelay: '1.5s' }}></div>
            </div>

            {/* Header - Responsive */}
            <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-0 mb-6 sm:mb-10 glass-panel p-3 sm:p-4 rounded-xl">
                <div className="flex items-center gap-3">
                    <div className="bg-blue-500/20 p-2 rounded-lg border border-blue-500/50">
                        <Box className="w-5 h-5 sm:w-6 sm:h-6 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-lg sm:text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                            Gem Trinity Genesis
                        </h1>
                        <p className="text-[10px] sm:text-xs text-slate-400">v2026.2.1 • {metrics.pod_name}</p>
                    </div>
                </div>

                <div className="flex items-center gap-2 sm:gap-4 w-full sm:w-auto justify-end">
                    {notification && (
                        <div className="fixed top-16 sm:top-24 left-2 right-2 sm:left-1/2 sm:right-auto sm:transform sm:-translate-x-1/2 glass-panel px-4 sm:px-6 py-2 sm:py-3 rounded-full border border-blue-500/50 text-blue-300 text-xs sm:text-sm font-bold shadow-[0_0_20px_rgba(59,130,246,0.5)] animate-float z-50 text-center">
                            {notification}
                        </div>
                    )}
                    <div className={`px-2 sm:px-3 py-1 rounded-full text-[10px] sm:text-xs font-bold flex items-center gap-1.5 sm:gap-2 border ${metrics.status === 'healthy' ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-red-500/10 border-red-500/30 text-red-400'
                        }`}>
                        <span className={`w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full ${metrics.status === 'healthy' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></span>
                        {metrics.status.toUpperCase()}
                    </div>
                </div>
            </header>

            {/* Glass Box Workflow Visualization */}
            {workflowStep !== 'IDLE' && (
                <div className="mb-4 sm:mb-6 glass-panel p-3 sm:p-6 rounded-xl border-indigo-500/20">
                    {/* Steps Progress - Responsive */}
                    <div className="flex justify-between items-center mb-4 sm:mb-8 px-2 sm:px-10 relative">
                        {/* Connecting Line */}
                        <div className="absolute top-1/2 left-0 w-full h-0.5 sm:h-1 bg-slate-800 -z-10"></div>
                        <div className={`absolute top-1/2 left-0 h-0.5 sm:h-1 bg-indigo-500 transition-all duration-1000 -z-10`} style={{ width: workflowStep === 'ARCHITECTING' ? '33%' : workflowStep === 'BUILDING' ? '66%' : workflowStep === 'ENGINE_ACTIVE' ? '100%' : '15%' }}></div>

                        {/* Step 1: Architect */}
                        <div className={`flex flex-col items-center gap-1 sm:gap-2 ${['ARCHITECTING', 'ARCHITECT_REVIEW', 'BUILDING', 'ENGINE_ACTIVE'].includes(workflowStep) ? 'text-indigo-400' : 'text-slate-600'}`}>
                            <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center border-2 ${['ARCHITECTING', 'ARCHITECT_REVIEW'].includes(workflowStep) ? 'bg-indigo-600 border-indigo-400 animate-pulse' : 'bg-slate-900 border-slate-700'}`}>
                                <Shield className="w-4 h-4 sm:w-5 sm:h-5" />
                            </div>
                            <span className="text-[10px] sm:text-xs font-bold">ARCHITECT</span>
                        </div>

                        {/* Step 2: Builder */}
                        <div className={`flex flex-col items-center gap-1 sm:gap-2 ${['BUILDING', 'ENGINE_ACTIVE'].includes(workflowStep) ? 'text-emerald-400' : 'text-slate-600'}`}>
                            <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center border-2 ${workflowStep === 'BUILDING' ? 'bg-emerald-600 border-emerald-400 animate-pulse' : 'bg-slate-900 border-slate-700'}`}>
                                <Terminal className="w-4 h-4 sm:w-5 sm:h-5" />
                            </div>
                            <span className="text-[10px] sm:text-xs font-bold">BUILDER</span>
                        </div>

                        {/* Step 3: Engine */}
                        <div className={`flex flex-col items-center gap-1 sm:gap-2 ${workflowStep === 'ENGINE_ACTIVE' ? 'text-cyan-400' : 'text-slate-600'}`}>
                            <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center border-2 ${workflowStep === 'ENGINE_ACTIVE' ? 'bg-cyan-600 border-cyan-400 animate-pulse' : 'bg-slate-900 border-slate-700'}`}>
                                <Cpu className="w-4 h-4 sm:w-5 sm:h-5" />
                            </div>
                            <span className="text-[10px] sm:text-xs font-bold">ENGINE</span>
                        </div>
                    </div>

                    {/* Artifact Reviews */}
                    {workflowStep === 'ARCHITECT_REVIEW' && architectData && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <ArtifactViewer
                                title="Optimized Prompt (Context)"
                                type="text"
                                data={architectData.optimized_prompt}
                            />
                            <ArtifactViewer
                                title="Product Requirements Doc (v2.0)"
                                type="json"
                                data={architectData.prd}
                                onApprove={handleApproveAndBuild}
                                onReject={() => setWorkflowStep('IDLE')}
                            />
                        </div>
                    )}

                </div>
            )}

            {/* Main Grid - Responsive */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">

                {/* Left Column: Metrics (4 cols on desktop) */}
                <div className="lg:col-span-4 grid grid-cols-2 lg:grid-cols-1 gap-4 sm:gap-6">
                    {/* Operations Card */}
                    <div className="glass-card p-4 sm:p-6 rounded-xl relative group">
                        <h3 className="text-slate-400 text-[10px] sm:text-sm font-medium flex items-center gap-1.5 sm:gap-2 mb-2 sm:mb-4">
                            <Zap className="w-3 h-3 sm:w-4 sm:h-4 text-yellow-400" /> System Load
                        </h3>
                        <div className="h-24 sm:h-40">
                            <Line data={lineData} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }} />
                        </div>
                        <div className="absolute top-4 sm:top-6 right-4 sm:right-6 text-lg sm:text-2xl font-bold font-mono">
                            {metrics.total_operations} <span className="text-[10px] sm:text-xs text-slate-500">OPS</span>
                        </div>
                    </div>

                    {/* Logic Ratio Card */}
                    <div className="glass-card p-4 sm:p-6 rounded-xl">
                        <h3 className="text-slate-400 text-[10px] sm:text-sm font-medium flex items-center gap-1.5 sm:gap-2 mb-2 sm:mb-4">
                            <Cpu className="w-3 h-3 sm:w-4 sm:h-4 text-blue-400" /> Cognitive Engine
                        </h3>
                        <div className="h-32 sm:h-48 relative flex justify-center">
                            <Doughnut data={doughnutData} options={{ cutout: '70%', plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } } } }} />
                            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                <div className="text-center">
                                    <div className="text-base sm:text-xl font-bold text-white">{metrics.determinism_percentage}%</div>
                                    <div className="text-[10px] sm:text-xs text-slate-500">Deterministic</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Agent Grid - Responsive 2x2 on mobile, 3 cols on tablet, 3 cols on desktop */}
                <div className="lg:col-span-8 grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6 agent-grid">

                    {/* Agent Card: Architect */}
                    <div className={`glass-card p-3 sm:p-6 rounded-xl hover:bg-slate-800/60 cursor-pointer group ${loading ? 'opacity-50 pointer-events-none' : ''}`}>
                        <div className="flex justify-between items-start mb-2 sm:mb-4">
                            <div className="p-2 sm:p-3 rounded-lg bg-indigo-500/20 border border-indigo-500/30 group-hover:border-indigo-400 transition-colors">
                                <Shield className="w-4 h-4 sm:w-6 sm:h-6 text-indigo-400" />
                            </div>
                            <span className="text-[10px] sm:text-xs bg-slate-700/50 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded text-slate-300">IDLE</span>
                        </div>
                        <h2 className="text-sm sm:text-xl font-bold mb-0.5 sm:mb-1 text-white group-hover:text-indigo-300 transition-colors">Architect</h2>
                        <p className="text-[10px] sm:text-xs text-slate-400 mb-2 sm:mb-4 h-6 sm:h-10 line-clamp-2">Master Planner. PRDs & Blueprints.</p>
                        <button
                            onClick={(e) => { e.stopPropagation(); setShowModal(true); }}
                            className="w-full py-2 sm:py-2 min-h-[40px] sm:min-h-[36px] rounded bg-indigo-600/20 hover:bg-indigo-600/40 active:bg-indigo-600/60 border border-indigo-500/50 text-indigo-300 text-[10px] sm:text-xs font-medium transition-all flex justify-center items-center gap-1 sm:gap-2">
                            {loading ? <span className="animate-spin">⟳</span> : "NEW PROJECT"}
                        </button>
                    </div>

                    {/* Agent Card: Builder */}
                    <div className="glass-card p-3 sm:p-6 rounded-xl hover:bg-slate-800/60 cursor-pointer group" onClick={() => alert("Builder Agent:\nLoading Construction Tasks...\n(Endpoint: /api/execute)")}>
                        <div className="flex justify-between items-start mb-2 sm:mb-4">
                            <div className="p-2 sm:p-3 rounded-lg bg-emerald-500/20 border border-emerald-500/30 group-hover:border-emerald-400 transition-colors">
                                <Terminal className="w-4 h-4 sm:w-6 sm:h-6 text-emerald-400" />
                            </div>
                            <span className="text-[10px] sm:text-xs bg-slate-700/50 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded text-slate-300">IDLE</span>
                        </div>
                        <h2 className="text-sm sm:text-xl font-bold mb-0.5 sm:mb-1 text-white group-hover:text-emerald-300 transition-colors">Builder</h2>
                        <p className="text-[10px] sm:text-xs text-slate-400 mb-2 sm:mb-4 h-6 sm:h-10 line-clamp-2">Code Synthesis & Implementation.</p>
                        <button className="w-full py-2 min-h-[40px] sm:min-h-[36px] rounded bg-emerald-600/20 hover:bg-emerald-600/40 active:bg-emerald-600/60 border border-emerald-500/50 text-emerald-300 text-[10px] sm:text-xs font-medium transition-all">
                            VIEW TASKS
                        </button>
                    </div>

                    {/* Agent Card: Engine */}
                    <div className="glass-card p-3 sm:p-6 rounded-xl hover:bg-slate-800/60 cursor-pointer group" onClick={() => alert("Engine Core:\nStatus: ACTIVE\nVersion: 4.0\nLoad: Optimal")}>
                        <div className="flex justify-between items-start mb-2 sm:mb-4">
                            <div className="p-2 sm:p-3 rounded-lg bg-cyan-500/20 border border-cyan-500/30 group-hover:border-cyan-400 transition-colors">
                                <Cpu className="w-4 h-4 sm:w-6 sm:h-6 text-cyan-400" />
                            </div>
                            <span className="text-[10px] sm:text-xs bg-green-500/20 text-green-400 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded border border-green-500/30">ACTIVE</span>
                        </div>
                        <h2 className="text-sm sm:text-xl font-bold mb-0.5 sm:mb-1 text-white group-hover:text-cyan-300 transition-colors">Engine</h2>
                        <p className="text-[10px] sm:text-xs text-slate-400 mb-2 sm:mb-4 h-6 sm:h-10 line-clamp-2">Core Execution Runtime (v4.0).</p>
                        <div className="h-1 bg-slate-700/50 rounded-full overflow-hidden mt-auto">
                            <div className="h-full bg-cyan-500/50 w-full animate-pulse"></div>
                        </div>
                    </div>

                    {/* Agent Card: Guardian */}
                    <div className="glass-card p-3 sm:p-6 rounded-xl hover:bg-slate-800/60 cursor-pointer group" onClick={() => alert("Guardian Agent:\nSecurity Scan: OK\nThreat Level: LOW")}>
                        <div className="flex justify-between items-start mb-2 sm:mb-4">
                            <div className="p-2 sm:p-3 rounded-lg bg-red-500/20 border border-red-500/30 group-hover:border-red-400 transition-colors">
                                <Activity className="w-4 h-4 sm:w-6 sm:h-6 text-red-400" />
                            </div>
                            <span className="text-[10px] sm:text-xs bg-green-500/20 text-green-400 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded border border-green-500/30">SECURE</span>
                        </div>
                        <h2 className="text-sm sm:text-xl font-bold mb-0.5 sm:mb-1 text-white group-hover:text-red-300 transition-colors">Guardian</h2>
                        <p className="text-[10px] sm:text-xs text-slate-400 mb-2 sm:mb-4 h-6 sm:h-10 line-clamp-2">Red Team & Runtime Protection.</p>
                        <div className="flex items-center gap-1.5 sm:gap-2 text-[8px] sm:text-[10px] text-slate-500 font-mono">
                            <span className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-green-500 animate-pulse"></span>
                            SCANNING
                        </div>
                    </div>

                    {/* Agent Card: Auditor */}
                    <div className="glass-card p-3 sm:p-6 rounded-xl hover:bg-slate-800/60 cursor-pointer group" onClick={() => alert("Auditor Agent:\nQuality Score: 98/100\nLast Audit: Just now")}>
                        <div className="flex justify-between items-start mb-2 sm:mb-4">
                            <div className="p-2 sm:p-3 rounded-lg bg-yellow-500/20 border border-yellow-500/30 group-hover:border-yellow-400 transition-colors">
                                <Box className="w-4 h-4 sm:w-6 sm:h-6 text-yellow-400" />
                            </div>
                            <span className="text-[10px] sm:text-xs bg-slate-700/50 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded text-slate-300">IDLE</span>
                        </div>
                        <h2 className="text-sm sm:text-xl font-bold mb-0.5 sm:mb-1 text-white group-hover:text-yellow-300 transition-colors">Auditor</h2>
                        <p className="text-[10px] sm:text-xs text-slate-400 mb-2 sm:mb-4 h-6 sm:h-10 line-clamp-2">Quality Assurance & Compliance.</p>
                        <button className="w-full py-2 min-h-[40px] sm:min-h-[36px] rounded bg-yellow-600/20 hover:bg-yellow-600/40 active:bg-yellow-600/60 border border-yellow-500/50 text-yellow-300 text-[10px] sm:text-xs font-medium transition-all">
                            RUN AUDIT
                        </button>
                    </div>

                </div>

                {/* Bottom: Console Feed - Responsive */}
                <div className="lg:col-span-12 glass-panel p-2 sm:p-4 rounded-xl font-mono text-xs sm:text-sm max-h-28 sm:max-h-40 overflow-y-auto custom-scrollbar hide-scrollbar-mobile">
                    <div className="flex items-center gap-1.5 sm:gap-2 mb-1.5 sm:mb-2 text-slate-500 border-b border-slate-700 pb-1.5 sm:pb-2">
                        <Terminal className="w-3 h-3 sm:w-4 sm:h-4" /> <span className="text-[10px] sm:text-sm">System Logs</span>
                    </div>
                    <div className="space-y-0.5 sm:space-y-1 text-[10px] sm:text-xs">
                        <div className="text-green-400">[16:42:01] System operational. All circuits stable.</div>
                        <div className="text-blue-400">[16:42:03] Metrics polling... OK.</div>
                        <div className="text-slate-400">[16:42:05] Waiting for User Input...</div>
                        <div className="text-purple-400 animate-pulse">[16:42:06] Void Glass UI loaded successfully.</div>
                    </div>
                </div>

                {/* Project Creation Modal - Responsive */}
                {showModal && (
                    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-0 sm:p-4" onClick={() => setShowModal(false)}>
                        <div className="glass-panel w-full sm:max-w-lg p-4 sm:p-6 rounded-t-2xl sm:rounded-xl border-indigo-500/30 shadow-[0_0_50px_rgba(79,70,229,0.2)] max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
                            {/* Drag Indicator (Mobile) */}
                            <div className="w-10 h-1 bg-slate-600 rounded-full mx-auto mb-4 sm:hidden"></div>

                            <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4 flex items-center gap-2">
                                <Shield className="w-4 h-4 sm:w-5 sm:h-5 text-indigo-400" /> New Project Protocol
                            </h2>

                            <div className="space-y-3 sm:space-y-4">
                                <div>
                                    <label className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider font-bold block mb-1.5 sm:mb-2">Target Domain</label>
                                    <select
                                        className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 text-sm text-white focus:border-indigo-500 focus:outline-none transition-colors min-h-[48px]"
                                        value={projectData.domain}
                                        onChange={e => setProjectData({ ...projectData, domain: e.target.value })}
                                    >
                                        <option value="custom">Custom Application</option>
                                        <option value="web">Modern Web App (Next.js)</option>
                                        <option value="sap">SAP Module Extension</option>
                                        <option value="data">Data Science Pipeline</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider font-bold block mb-1.5 sm:mb-2">Complexity Matrix</label>
                                    <select
                                        className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 text-sm text-white focus:border-indigo-500 focus:outline-none transition-colors min-h-[48px]"
                                        value={projectData.complexity}
                                        onChange={e => setProjectData({ ...projectData, complexity: e.target.value })}
                                    >
                                        <option value="simple">Simple (Proof of Concept)</option>
                                        <option value="medium">Standard (MVP)</option>
                                        <option value="complex">High (Enterprise Scale)</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="text-[10px] sm:text-xs text-slate-400 uppercase tracking-wider font-bold block mb-1.5 sm:mb-2">Mission Brief (Use Case)</label>
                                    <textarea
                                        className="w-full h-24 sm:h-32 bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 text-sm text-white focus:border-indigo-500 focus:outline-none transition-colors resize-none"
                                        placeholder="Describe the application you want to build..."
                                        value={projectData.use_case}
                                        onChange={e => setProjectData({ ...projectData, use_case: e.target.value })}
                                    />
                                </div>

                                <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-slate-700/50">
                                    <button
                                        onClick={() => setShowModal(false)}
                                        className="sm:flex-1 py-3 min-h-[48px] rounded-lg bg-slate-800 hover:bg-slate-700 active:bg-slate-600 text-slate-300 text-sm font-bold transition-all order-2 sm:order-1"
                                    >
                                        ABORT
                                    </button>
                                    <button
                                        onClick={handleCreateProject}
                                        disabled={!projectData.use_case}
                                        className="sm:flex-1 py-3 min-h-[48px] rounded-lg bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-400 text-white text-sm font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-900/20 order-1 sm:order-2"
                                    >
                                        INITIALIZE AGENTS
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </main >
    );
}
