'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getStudentProfile } from '@/services/studentApi';
import styles from './Card.module.scss'; // Reutilizamos los estilos base de la tarjeta
import skillStyles from './KeySkillsCard.module.scss'; // Estilos específicos para esta tarjeta

export default function KeySkillsCard() {
    const [skills, setSkills] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSkills = async () => {
            try {
                const data = await getStudentProfile();
                if (data.profile && data.profile.skills) {
                    // Tomamos el string de habilidades, lo separamos por comas,
                    // y limpiamos los espacios en blanco de cada habilidad.
                    const skillsArray = (data.profile.skills as unknown as string)
                        .split(',')
                        .map(skill => skill.trim())
                        .filter(skill => skill); // Filtramos para eliminar habilidades vacías

                    setSkills(skillsArray);
                }
            } catch (err) {
                setError("No se pudieron cargar tus habilidades.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchSkills();
    }, []);

    if (isLoading) {
        return <div className={styles.card}>Cargando habilidades...</div>;
    }

    if (error) {
        return <div className={styles.card}><p style={{ color: 'red' }}>{error}</p></div>;
    }

    return (
        <div className={styles.card}>
            <h2 className={styles.cardTitle}>Mis Habilidades Clave</h2>
            {skills.length > 0 ? (
                <div className={skillStyles.skillTagList}>
                    {skills.map((skill, index) => (
                        <span key={index} className={skillStyles.skillTag}>
                            {skill}
                        </span>
                    ))}
                </div>
            ) : (
                <p className={styles.noData}>
                    Aún no has añadido ninguna habilidad.
                </p>
            )}
            <Link href="/student/profile" className={styles.cardLink}>
                Gestionar Habilidades
            </Link>
        </div>
    );
}
