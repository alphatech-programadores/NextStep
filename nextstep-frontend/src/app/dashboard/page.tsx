// src/app/dashboard/page.tsx

'use client';

import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from "@/components/ProtectedRoute";
import styles from './dashboard.module.scss';
import Link from 'next/link';

// Importa todos tus componentes de tarjeta
import RecentApplicationsCard from '@/components/RecentApplicationsCard';
import ProfileProgressCard from '@/components/ProfileProgressCard';
import KeySkillsCard from '@/components/KeySkillsCard';
import KeySkillStats from '@/components/KeySkillStats'; // Asegúrate de que este componente existe y es funcional
// import RecommendedVacanciesCard from '@/components/RecommendedVacanciesCard'; // Sugerencia: Crea este componente
// import SavedVacanciesCard from '@/components/SavedVacanciesCard'; // Sugerencia: Crea este componente

export default function DashboardPage() {
    const { user, loadingUser } = useAuth();

    if (loadingUser) {
        return <ProtectedRoute><div>Cargando...</div></ProtectedRoute>;
    }
    if (!user) {
        return <ProtectedRoute><div>Acceso no autorizado.</div></ProtectedRoute>;
    }

    return (
        <ProtectedRoute allowedRoles={['student']}>
            <div className={styles.dashboardContainer}>
                {/* 1. CABECERA DE BIENVENIDA */}
                <header className={styles.welcomeHeader}>
                    <div>
                        <h1 className={styles.welcomeTitle}>¡Bienvenido de vuelta, {user.name}!<span className={styles.emoji}>👋</span></h1>
                        <p className={styles.welcomeMessage}>Aquí tienes un resumen de tu actividad y progreso.</p>
                    </div>
                    <Link href="/vacancies" className={styles.mainCtaButton}>
                        Explorar Prácticas <span className={styles.icon}>🚀</span>
                    </Link>
                </header>

                {/* 2. REJILLA DE TARJETAS PRINCIPALES */}
                <div className={styles.dashboardGrid}>
                    {/* Grupo: Progreso del Perfil */}
                    <div className={styles.gridItem}>
                        <div className={styles.cardWrapper}>
                            <ProfileProgressCard />
                        </div>
                        <div className={styles.descriptionWrapper}>
                            <p className={styles.sectionDescription}>
                                Mantén tu perfil completo y actualizado para aumentar tus posibilidades de encontrar la práctica ideal.
                                Un perfil detallado ayuda a las instituciones a conocerte mejor.
                            </p>
                        </div>
                    </div>

                    {/* Grupo: Postulaciones Recientes */}
                    <div className={styles.gridItem}>
                        <div className={styles.cardWrapper}>
                            <RecentApplicationsCard />
                        </div>
                        <div className={styles.descriptionWrapper}>
                            <p className={styles.sectionDescription}>
                                Revisa el estado de tus postulaciones más recientes. Mantente al tanto de si están pendientes,
                                en entrevista, aceptadas o rechazadas.
                            </p>
                        </div>
                    </div>

                    {/* Grupo: Habilidades Clave */}
                    <div className={styles.gridItem}>
                        <div className={styles.cardWrapper}>
                            <KeySkillsCard />
                        </div>
                        <div className={styles.descriptionWrapper}>
                            <p className={styles.sectionDescription}>
                                Tus habilidades son fundamentales para que las vacantes adecuadas te encuentren.
                                Asegúrate de listar todas tus competencias relevantes.
                            </p>
                        </div>
                    </div>

                    {/* Grupo: Estadísticas de Habilidades */}
                    <div className={styles.gridItem}>
                        <div className={styles.cardWrapper}>
                            <KeySkillStats />
                        </div>
                        <div className={styles.descriptionWrapper}>
                            <p className={styles.sectionDescription}>
                                Visualiza un análisis de tus habilidades más destacadas y cómo se comparan con las demandas del mercado laboral.
                                Identifica áreas de mejora o fortalezas clave.
                            </p>
                        </div>
                    </div>

                    {/* Sección de Vacantes Recomendadas (ocupa todo el ancho si es necesario) */}
                    <section className={styles.fullWidthSection}>
                        <h2 className={styles.sectionTitle}>Vacantes Recomendadas para Ti</h2>
                        <div className={styles.fullWidthContent}>
                            <p className={styles.sectionDescription}>
                                Explora las oportunidades de prácticas que mejor se ajustan a tus habilidades e intereses.
                                Nuestro sistema de recomendación te ayuda a descubrir vacantes relevantes.
                            </p>
                            {/* Aquí iría el componente RecommendedVacanciesCard */}
                            {/* Ejemplo de placeholder si RecommendedVacanciesCard no existe aún */}
                            <div className={styles.placeholderCard}>
                                <p>Cargando recomendaciones...</p>
                                <Link href="/student/recommendations" className={styles.viewAllButton}>Ver todas las recomendaciones</Link>
                            </div>
                        </div>
                    </section>


                    {/* Sección de Vacantes Guardadas (ocupa todo el ancho si es necesario) */}
                    <section className={styles.fullWidthSection}>
                        <h2 className={styles.sectionTitle}>Mis Vacantes Guardadas</h2>
                        <div className={styles.fullWidthContent}>
                            <p className={styles.sectionDescription}>
                                Accede rápidamente a las vacantes que has guardado para revisar más tarde o postularte cuando estés listo.
                                No pierdas de vista ninguna oportunidad.
                            </p>
                            {/* Aquí iría el componente SavedVacanciesCard */}
                            {/* Ejemplo de placeholder si SavedVacanciesCard no existe aún */}
                            <div className={styles.placeholderCard}>
                                <p>No tienes vacantes guardadas.</p>
                                <Link href="/student/saved-vacancies" className={styles.viewAllButton}>Ver todas las guardadas</Link>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </ProtectedRoute>
    );
}
