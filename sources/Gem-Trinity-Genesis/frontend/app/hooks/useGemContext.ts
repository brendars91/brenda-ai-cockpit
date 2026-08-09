

import { useState, useEffect } from 'react';

// API Base URL - Configurable via Env Var for Vercel/Cloud
// API Base URL - Configurable via Env Var, normalized to always end in /api
const RAW_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE = RAW_URL.replace(/\/api\/?$/, '') + '/api';

export interface GemContextData {

    systemStatus: {
        system: string;
        mirror_sync: string;
        integrity: string;
        integrity_msg: string;
        mode: string;
    };
    context: {
        skills_index: {
            skills: any[];
        };
        project_status: {
            architect: string;
            builder: string;
            engine: string;
        };
        timestamp: number;
        iso_timestamp: string;
    };
    mcpStatus: {
        servers: any[];
    } | null;
    isLoading: boolean;
    error: string | null;
}

export function useGemContext() {
    const [data, setData] = useState<GemContextData>({
        systemStatus: { system: 'connecting...', mirror_sync: 'unknown', integrity: 'unknown', integrity_msg: 'Checking...', mode: 'unknown' },
        context: {
            skills_index: { skills: [] },
            project_status: { architect: 'unknown', builder: 'unknown', engine: 'unknown' },
            timestamp: 0,
            iso_timestamp: ''
        },
        mcpStatus: null,
        isLoading: true,
        error: null,
    });

    const fetchData = async () => {
        try {
            // Parallel Fetching
            const [statusRes, contextRes, mcpRes] = await Promise.all([
                fetch(`${API_BASE}/status`),
                fetch(`${API_BASE}/context`),
                fetch(`${API_BASE}/mcp`)
            ]);

            if (!statusRes.ok) throw new Error('Backend Offline');

            const systemStatus = await statusRes.json();
            const context = await contextRes.json();
            const mcpStatus = await mcpRes.json();

            setData({
                systemStatus,
                context,
                mcpStatus,
                isLoading: false,
                error: null,
            });
        } catch (err: any) {
            console.error("Gem Trinity API Error:", err);
            setData(prev => ({
                ...prev,
                isLoading: false,
                error: `Connection Error: ${err.message}`,
                systemStatus: { ...prev.systemStatus, system: 'offline' }
            }));
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    const triggerAction = async (action: string, target: string) => {
        await fetch(`${API_BASE}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, target })
        });
    };

    const toggleMirror = async () => {
        await fetch(`${API_BASE}/mirror/toggle`, { method: 'POST' });
        fetchData(); // Instant refresh
    };

    return { ...data, triggerAction, toggleMirror };
}
