import { useState, useEffect } from 'react';

export interface SystemMetrics {
    total_operations: number;
    determinism_percentage: number;
    llm_percentage: number;
    metrics_history: number[]; // For sparkline
    status: 'healthy' | 'degraded' | 'down';
    pod_name: string;
}

export function useSystemMetrics() {
    const [metrics, setMetrics] = useState<SystemMetrics>({
        total_operations: 0,
        determinism_percentage: 100,
        llm_percentage: 0,
        metrics_history: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        status: 'healthy',
        pod_name: 'gem-node-01'
    });

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                // Fetch metrics
                const metricsRes = await fetch('http://localhost:8000/api/metrics');
                const metricsData = await metricsRes.json();

                // Fetch health (for status)
                const healthRes = await fetch('http://localhost:8000/api/health/');
                const healthData = await healthRes.json();

                setMetrics(prev => {
                    const newHistory = [...prev.metrics_history.slice(1), metricsData.total_operations];

                    return {
                        total_operations: metricsData.total_operations,
                        determinism_percentage: metricsData.determinism_percentage,
                        llm_percentage: metricsData.llm_percentage,
                        metrics_history: newHistory,
                        status: healthData.status === 'healthy' ? 'healthy' : 'degraded',
                        pod_name: 'gem-node-v2026'
                    };
                });
            } catch (error) {
                console.error("Failed to fetch metrics", error);
                setMetrics(prev => ({ ...prev, status: 'down' }));
            }
        };

        const interval = setInterval(fetchMetrics, 2000);
        fetchMetrics(); // Initial call

        return () => clearInterval(interval);
    }, []);

    return metrics;
}
