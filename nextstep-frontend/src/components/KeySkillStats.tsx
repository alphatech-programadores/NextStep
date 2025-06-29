// src/components/dashboard/KeyStatsCard.tsx

'use client';

import { useState, useEffect } from 'react';
import { getMyApplications } from '@/services/studentApi';
import styles from './Card.module.scss';
import statStyles from './KeySkillStats.module.scss';

// Define la interfaz para las estadísticas
interface Stats {
    total: number;
    pending: number;
    interview: number;
    accepted: number;
}

// Un pequeño componente para cada item de estadística
const StatItem = ({ icon, value, label }: { icon: React.ReactNode, value: number, label: string }) => (
    <div className={statStyles.statItem}>
        <div className={statStyles.statIcon}>{icon}</div>
        <div className={statStyles.statValue}>{value}</div>
        <div className={statStyles.statLabel}>{label}</div>
    </div>
);

export default function KeyStatsCard() {
    const [stats, setStats] = useState<Stats | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                // La función getMyApplications ahora devuelve también las estadísticas
                const data = await getMyApplications();
                setStats(data.stats);
            } catch (err) {
                console.error("Error fetching stats:", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (isLoading) {
        return <div className={styles.card}>Cargando estadísticas...</div>;
    }

    return (
        <div className={`${styles.card} ${statStyles.statsCard}`}>
            <h2 className={styles.cardTitle}>Tu Actividad</h2>
            <div className={statStyles.statsGrid}>
                <StatItem
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>}
                    value={stats?.total || 0}
                    label="Enviadas"
                />
                <StatItem
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>}
                    value={stats?.pending || 0}
                    label="Pendientes"
                />
                <StatItem
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>}
                    value={stats?.interview || 0}
                    label="Entrevistas"
                />
                <StatItem
                    icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>}
                    value={stats?.accepted || 0}
                    label="Aceptadas"
                />
            </div>
        </div>
    );
}
