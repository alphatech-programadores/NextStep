'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getMyApplications } from '@/services/studentApi'; // Importamos nuestra función de API
import styles from './Card.module.scss'; // Crearemos este archivo de estilos en un momento

// Define la interfaz para una sola aplicación dentro del componente
interface Application {
    status: string;
    id: number;
    vacant_title: string;
    company_name: string;
}

export default function RecentApplicationsCard() {
    // 3 estados: uno para los datos, uno para el estado de carga y otro para errores
    const [applications, setApplications] = useState<Application[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Función para cargar los datos
        const fetchApplications = async () => {
            try {
                // Traer solo las 3 más recientes para el dashboard
                const data = await getMyApplications({ page: 1, per_page: 3 });
                setApplications(data.applications);
            } catch (err) {
                setError("No se pudieron cargar las postulaciones.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchApplications();
    }, []); // El array vacío [] asegura que esto se ejecute solo una vez, cuando el componente se monta

    // Renderizado condicional basado en el estado
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