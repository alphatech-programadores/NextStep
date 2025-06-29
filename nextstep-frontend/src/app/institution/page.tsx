// src/app/institution/dashboard/page.tsx

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getMyInstitutionVacancies, InstitutionVacancy } from '../../services/institucionApi';
import styles from './dashboard.module.scss';

// Un pequeño componente para mostrar un ícono y texto
const InfoTag = ({ icon, text }: { icon: React.ReactNode, text: string | number }) => (
    <div className={styles.infoTag}>
        {icon}
        <span>{text}</span>
    </div>
);

export default function InstitutionDashboardPage() {
    const { user } = useAuth();
    const [vacancies, setVacancies] = useState<InstitutionVacancy[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (user?.role === 'institution') {
            const fetchVacancies = async () => {
                try {
                    const data = await getMyInstitutionVacancies();
                    setVacancies(data);
                } catch (err) {
                    setError('No se pudieron cargar tus vacantes. Inténtalo de nuevo más tarde.');
                } finally {
                    setIsLoading(false);
                }
            };
            fetchVacancies();
        }
    }, [user]);

    if (isLoading) {
        return <ProtectedRoute allowedRoles={['institution']}><div>Cargando dashboard...</div></ProtectedRoute>;
    }

    return (
        <ProtectedRoute allowedRoles={['institution']}>
            <div className={styles.container}>
                <header className={styles.header}>
                    <h1 className={styles.title}>Mis Vacantes</h1>
                    <Link href="/institution/vacancies/new" className={styles.createButton}>
                        + Crear Nueva Vacante
                    </Link>
                </header>

                {error && <p className={styles.error}>{error}</p>}

                {vacancies.length > 0 ? (
                    <div className={styles.vacanciesGrid}>
                        {vacancies.map(vacant => (
                            <Link key={vacant.id} href={`/institution/vacancies/${vacant.id}/edit`} className={styles.vacancyCard}>
                                <div className={`${styles.statusBadge} ${styles[vacant.status_summary]}`}>
                                    {vacant.status_summary.replace('_', ' ')}
                                </div>
                                <h2 className={styles.vacantTitle}>{vacant.area}</h2>
                                <div className={styles.vacantInfo}>
                                    <InfoTag
                                        icon={<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>}
                                        text={`${vacant.applications_count} Postulantes`}
                                    />
                                </div>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <div className={styles.noVacancies}>
                        <p>Aún no has creado ninguna vacante.</p>
                        <p>¡Empieza ahora para encontrar a los mejores practicantes!</p>
                    </div>
                )}
            </div>
        </ProtectedRoute>
    );
}
