'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import toast from 'react-hot-toast';
import ProtectedRoute from '@/components/ProtectedRoute';
import {
    getVacancyApplicants,
    decideOnApplication,
    VacancyApplication
} from '../../../../../services/institucionApi';
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
            console.error("Error al cargar postulantes:", err); // Log original error
            setError('No se pudieron cargar los postulantes.');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchApplicants();
    }, [vacancyId]);

    const handleDecision = async (applicationId: number, decision: 'aceptado' | 'rechazado') => {
        const originalApplicants = [...applicants]; // Save current state for rollback

        try {
            // Attempt to make the decision API call
            const response = await decideOnApplication(applicationId, decision);

            // Log the successful response from the backend
            console.log("Respuesta exitosa de la decisión:", response);

            // Show success toast using the message from the backend response
            toast.success(response.message || 'Decisión procesada con éxito.');

            // Update UI state to reflect the change immediately
            setApplicants(prev => prev.map(app =>
                app.application_id === applicationId ? { ...app, status: decision } : app
            ));

        } catch (error: any) {
            // Log the full error object for detailed debugging
            console.error("Error completo al procesar la decisión:", error);
            if (error.response) {
                // Log the response data if available (from backend)
                console.error("Datos de error del backend:", error.response.data);
                // Show toast with backend error message if available, otherwise a generic one
                toast.error(error.response.data.error || 'No se pudo procesar la decisión.');
            } else {
                // Show generic error for network issues or unexpected errors
                toast.error('No se pudo procesar la decisión. Error de red o inesperado.');
            }
            setApplicants(originalApplicants); // Rollback to original state on error
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
