'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
// 1. Importar el tipo 'Application' junto con la función de la API
import { getMyApplications, Application } from '@/services/studentApi';
import styles from './Card.module.scss';

// 2. Eliminar la definición duplicada de la interfaz 'Application' que estaba aquí.

export default function RecentApplicationsCard() {
    // Ahora 'useState' usa el tipo 'Application' importado, garantizando consistencia.
    const [applications, setApplications] = useState<Application[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchApplications = async () => {
            try {
                const data = await getMyApplications({ page: 1, per_page: 3 });
                // Ahora los tipos coinciden perfectamente, eliminando el error.
                setApplications(data.applications);
            } catch (err) {
                // Es buena práctica registrar el error real en la consola.
                console.error("Failed to fetch applications:", err);
                setError("No se pudieron cargar las postulaciones.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchApplications();
    }, []); // El array vacío [] asegura que esto se ejecute solo una vez.

    // El resto del componente para renderizar la UI sigue igual...
    if (isLoading) {
        return <div className={styles.card}>Cargando postulaciones...</div>;
    }

    if (error) {
        return <div className={styles.card}><p style={{ color: 'red' }}>{error}</p></div>;
    }

    return (
        <div className={styles.card}>
            <h2 className={styles.cardTitle}>Mis Postulaciones Recientes</h2>
            <ul className={styles.applicationList}>
                {applications.length > 0 ? (
                    applications.map(app => (
                        <li key={app.id} className={styles.applicationItem}>
                            <span className={styles.appTitle}>{app.vacant_title}</span>
                            <span className={styles.appCompany}> - {app.company_name}</span>
                            <span className={`${styles.appStatus} ${styles[app.status.toLowerCase()]}`}>{app.status}</span>
                        </li>
                    ))
                ) : (
                    <p className={styles.noData}>Aún no has postulado a ninguna vacante.</p>
                )}
            </ul>
            <Link href="/applications" className={styles.cardLink}>Ver Todas Mis Postulaciones</Link>
        </div>
    );
}