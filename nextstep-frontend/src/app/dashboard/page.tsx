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
import KeySkillStats from '@/components/KeySkillStats';

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
                        <h1 className={styles.welcomeTitle}>¡Bienvenido de vuelta, {user.name}!</h1>
                        <p className={styles.welcomeMessage}>Aquí tienes un resumen de tu actividad y progreso.</p>
                    </div>
                    <Link href="/vacancies" className={styles.mainCtaButton}>
                        Explorar Prácticas
                    </Link>
                </header>

                {/* 2. REJILLA DE TARJETAS */}
                <div className={styles.dashboardGrid}>

                    <ProfileProgressCard />
                    <RecentApplicationsCard />
                    <KeySkillsCard />
                </div>
            </div>
        </ProtectedRoute>
    );
}

