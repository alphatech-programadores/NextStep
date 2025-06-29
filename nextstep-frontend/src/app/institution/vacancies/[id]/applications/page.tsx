// src/app/institution/vacancies/[id]/applications/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import toast from 'react-hot-toast';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getVacancyApplicants, decideOnApplication, VacancyApplication } from '../../../../../services/institucionApi';
import styles from './applications.module.scss';

export default function ViewApplicantsPage() {
    const params = useParams();
    const vacancyId = params.id as string;

    const [applicants, setApplicants] = useState<VacancyApplication[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchApplicants = async () => {
        if (!vacancyId) return;
        try {
            const data = await getVacancyApplicants(vacancyId);
            setApplicants(data);
        } catch (err) {
            setError('No se pudieron cargar los postulantes.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchApplicants();
    }, [vacancyId]);

    const handleDecision = async (applicationId: number, decision: 'aceptado' | 'rechazado') => {
        const originalApplicants = [...applicants];

        // Actualización optimista de la UI
        setApplicants(prev => prev.map(app =>
            app.application_id === applicationId ? { ...app, status: decision } : app
        ));

        try {
            await decideOnApplication(applicationId, decision);
            toast.success(`Postulante ${decision === 'aceptado' ? 'aceptado' : 'rechazado'} con éxito.`);
            // Opcional: recargar los datos para asegurar consistencia
            // await fetchApplicants(); 
        } catch (error) {
            toast.error('No se pudo procesar la decisión.');
            // Revertir si hay un error
            setApplicants(originalApplicants);
        }
    };

    if (isLoading) {
        return <ProtectedRoute allowedRoles={['institution']}><div>Cargando postulantes...</div></ProtectedRoute>;
    }

    return (
        <ProtectedRoute allowedRoles={['institution']}>
            <div className={styles.container}>
                <header className={styles.header}>
                    <h1 className={styles.title}>Postulantes a la Vacante</h1>
                    {/* Aquí podrías añadir el título de la vacante si lo pasas o lo cargas */}
                </header>

                {error && <p className={styles.error}>{error}</p>}

                {applicants.length > 0 ? (
                    <div className={styles.applicantsList}>
                        {applicants.map(({ application_id, status, student }) => (
                            <div key={application_id} className={styles.applicantCard}>
                                <div className={styles.cardHeader}>
                                    <h2 className={styles.studentName}>{student.name}</h2>
                                    <span className={`${styles.statusBadge} ${styles[status]}`}>{status}</span>
                                </div>
                                <div className={styles.studentInfo}>
                                    <p><strong>Carrera:</strong> {student.career}</p>
                                    <p><strong>Semestre:</strong> {student.semester || 'N/A'}</p>
                                </div>
                                <div className={styles.skillsSection}>
                                    <strong>Habilidades:</strong>
                                    <div className={styles.skillTagList}>
                                        {student.skills.length > 0 ? student.skills.map((skill, i) => (
                                            <span key={i} className={styles.skillTag}>{skill}</span>
                                        )) : <p>No especificadas</p>}
                                    </div>
                                </div>
                                <div className={styles.cardFooter}>
                                    {student.cv_url && (
                                        <a href={student.cv_url} target="_blank" rel="noopener noreferrer" className={styles.actionButton}>Ver CV</a>
                                    )}
                                    {status === 'pendiente' && (
                                        <>
                                            <button onClick={() => handleDecision(application_id, 'rechazado')} className={`${styles.actionButton} ${styles.reject}`}>Rechazar</button>
                                            <button onClick={() => handleDecision(application_id, 'aceptado')} className={`${styles.actionButton} ${styles.accept}`}>Aceptar</button>
                                        </>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className={styles.noApplicants}>
                        <p>Esta vacante aún no tiene postulantes.</p>
                    </div>
                )}
            </div>
        </ProtectedRoute>
    );
}
