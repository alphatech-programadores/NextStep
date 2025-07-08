'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getStudentProfile } from '@/services/studentApi';
import styles from './Card.module.scss'; // Reutilizamos los estilos base de la tarjeta
import progressStyles from './ProfileProgressCard.module.scss'; // Estilos específicos para esta tarjeta

export default function ProfileProgressCard() {
    const [completeness, setCompleteness] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const data = await getStudentProfile();
                setCompleteness(data.profile_completeness);
            } catch (err) {
                setError("No se pudo cargar tu perfil.");
            } finally {
                setIsLoading(false);
            }
        };
        fetchProfile();
    }, []);

    if (isLoading) {
        return <div className={styles.card}>Cargando perfil...</div>;
    }

    if (error) {
        return <div className={styles.card}><p style={{ color: 'red' }}>{error}</p></div>;
    }

    return (
        <div className={styles.card}>
            <h2 className={styles.cardTitle}>Mi Perfil de Estudiante</h2>
            <p className={progressStyles.progressText}>
                Tu perfil está al <strong className={progressStyles.progressPercentage}>{completeness}%</strong> completo.
            </p>
            <div className={progressStyles.progressBarContainer}>
                <div className={progressStyles.progressBar} style={{ width: `${completeness}%` }}></div>
            </div>
            {completeness < 100 && (
                <p className={progressStyles.profileAdvice}>¡Un perfil completo aumenta tus oportunidades!</p>
            )}
            <Link href="/student/profile" className={styles.cardLink}>Editar Mi Perfil</Link>
        </div>
    );
}