// src/app/dashboard/page.tsx
'use client';

import { useAuth } from '@/context/AuthContext'; // Importa useAuth
import ProtectedRoute from "@/components/ProtectedRoute";
import styles from './dashboard.module.scss'; // Módulo de estilos para el dashboard
import Link from 'next/link'; // Para enlaces
import { useEffect, useState } from 'react';
// Importa cualquier otro componente de UI que uses (ej. Card, Spinner)
// import VacancyCard from '@/components/VacancyCard'; // Si tienes un componente de tarjeta de vacante
// import ApplicationStatusCard from '@/components/ApplicationStatusCard'; // Si tienes un componente de estado de postulación

export default function DashboardPage() {
    const { user, loadingUser } = useAuth(); // Obtén el usuario y el estado de carga

    // Simulación de datos (esto vendría de tu API en un proyecto real)
    const [recentApplications, setRecentApplications] = useState([
        { id: 1, title: 'Práctica Desarrollador Frontend', company: 'Tech Solutions', status: 'Pendiente', date: '2025-06-20' },
        { id: 2, title: 'Internship Data Analyst', company: 'Data Insights Corp.', status: 'Entrevista', date: '2025-06-15' },
    ]);
    const [profileProgress, setProfileProgress] = useState(75); // % completado

    if (loadingUser) {
        return (
            <ProtectedRoute>
                <div className={styles.loadingContainer}>Cargando Dashboard...</div>
            </ProtectedRoute>
        );
    }

    // Si por alguna razón el usuario no está disponible (ej. ProtectedRoute no funcionó, o token expiró en loadUserFromToken)
    if (!user || user.role !== 'student') {
        // Esto debería ser manejado por ProtectedRoute, pero es un buen fallback
        return (
            <ProtectedRoute>
                <div className={styles.unauthorizedContainer}>Acceso no autorizado. Redirigiendo...</div>
            </ProtectedRoute>
        );
    }

    return (
        <ProtectedRoute>
            <div className={styles.dashboardContainer}>
                {/* Sección de Bienvenida */}
                <header className={styles.welcomeHeader}>
                    <h1 className={styles.welcomeTitle}>Bienvenido, {user.name}!</h1>
                    <p className={styles.welcomeMessage}>
                        ¡Estamos emocionados de verte en NextStep! Aquí tienes un resumen de tu actividad.
                    </p>
                    <Link href="/vacancies" className={styles.mainCtaButton}>
                        Explorar Nuevas Prácticas
                    </Link>
                </header>

                <div className={styles.dashboardGrid}>
                    {/* Tarjeta de Resumen de Postulaciones */}
                    <div className={styles.card}>
                        <h2 className={styles.cardTitle}>Mis Postulaciones Recientes</h2>
                        <ul className={styles.applicationList}>
                            {recentApplications.length > 0 ? (
                                recentApplications.map(app => (
                                    <li key={app.id} className={styles.applicationItem}>
                                        <span className={styles.appTitle}>{app.title}</span>
                                        <span className={styles.appCompany}> - {app.company}</span>
                                        <span className={`${styles.appStatus} ${styles[app.status.toLowerCase()]}`}>{app.status}</span>
                                    </li>
                                ))
                            ) : (
                                <p className={styles.noData}>Aún no has postulado a ninguna vacante.</p>
                            )}
                        </ul>
                        <Link href="/student/applications" className={styles.cardLink}>Ver Todas Mis Postulaciones</Link>
                    </div>

                    {/* Tarjeta de Progreso del Perfil */}
                    <div className={styles.card}>
                        <h2 className={styles.cardTitle}>Mi Perfil de Estudiante</h2>
                        <p className={styles.profileProgressText}>
                            Tu perfil está al <strong style={{ color: '#00796b' }}>{profileProgress}%</strong> completo.
                        </p>
                        <div className={styles.progressBarContainer}>
                            <div className={styles.progressBar} style={{ width: `${profileProgress}%` }}></div>
                        </div>
                        <p className={styles.profileAdvice}>¡Un perfil completo aumenta tus oportunidades!</p>
                        <Link href="/student/profile" className={styles.cardLink}>Editar Mi Perfil</Link>
                    </div>

                    {/* Tarjeta de Vacantes Recomendadas (simuladas) */}
                    <div className={styles.card}>
                        <h2 className={styles.cardTitle}>Vacantes Recomendadas</h2>
                        <ul className={styles.recommendedVacanciesList}>
                            {/* Esto debería ser un bucle de vacantes reales */}
                            <li className={styles.recommendedVacancyItem}>Desarrollador Fullstack - Startup X</li>
                            <li className={styles.recommendedVacancyItem}>Diseñador UI/UX - Agencia Creativa</li>
                        </ul>
                        <Link href="/vacancies" className={styles.cardLink}>Explorar Más Vacantes</Link>
                    </div>

                    {/* Tarjeta de Habilidades (Placeholder) */}
                    <div className={styles.card}>
                        <h2 className={styles.cardTitle}>Mis Habilidades Clave</h2>
                        <p className={styles.noData}>Añade tus habilidades para recibir mejores recomendaciones.</p>
                        <Link href="/student/profile#skills" className={styles.cardLink}>Gestionar Habilidades</Link>
                    </div>

                </div> {/* Fin dashboardGrid */}
            </div> {/* Fin dashboardContainer */}
        </ProtectedRoute>
    );
}