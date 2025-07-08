// src/app/vacancies/[id]/page.tsx
'use client';

import { useState, useEffect, useCallback } from 'react'; // Added useCallback
import { useParams, useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { useAuth } from '@/context/AuthContext';
import styles from './VacancyDetailsPage.module.scss';
import Link from 'next/link';
import axiosInstance from '@/services/axiosConfig';

interface VacancyDetails {
    id: number;
    title: string;
    description: string;
    requirements: string;
    responsibilities: string;
    location: string;
    modality: string;
    type: string;
    salary_range: string;
    posted_date: string;
    application_deadline: string;
    company_name: string;
    institution_email: string;
    tags: string[];
}

export default function VacancyDetailsPage() {
    const { id } = useParams();
    const router = useRouter();
    const { user, loadingUser } = useAuth();
    const [vacancy, setVacancy] = useState<VacancyDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isApplying, setIsApplying] = useState(false);
    // Renamed hasApplied to applicationStatus to store the actual status
    const [applicationStatus, setApplicationStatus] = useState<string | null>(null);

    const fetchVacancyAndApplicationStatus = useCallback(async () => {
        if (!id) return;

        setLoading(true);
        setError(null);
        try {
            const response = await axiosInstance.get(`/vacants/${id}`);
            setVacancy(response.data);

            if (user && user.role === 'student') {
                const token = localStorage.getItem('access_token');
                if (token) {
                    try {
                        const checkResponse = await axiosInstance.get(`/vacants/check_status/${id}`, {
                            headers: { Authorization: `Bearer ${token}` }
                        });
                        // Set the actual application status
                        setApplicationStatus(checkResponse.data.application_status);
                    } catch (checkError) {
                        console.error("Error checking application status:", checkError);
                        setApplicationStatus(null); // Reset if there's an error
                    }
                }
            } else {
                setApplicationStatus(null); // Reset if not a student or not logged in
            }

        } catch (err: any) {
            console.error("Error fetching vacancy details:", err);
            if (err.response && err.response.status === 404) {
                setError("La vacante no fue encontrada o está inactiva.");
            } else {
                setError("No se pudieron cargar los detalles de la vacante. Inténtalo de nuevo.");
            }
            toast.error("Error al cargar detalles de vacante.");
        } finally {
            setLoading(false);
        }
    }, [id, user]); // Added user to dependencies

    useEffect(() => {
        fetchVacancyAndApplicationStatus();
    }, [fetchVacancyAndApplicationStatus]);

    const handleApply = async () => {
        if (!user) {
            toast.error("Debes iniciar sesión para postularte a una vacante.");
            router.push('/auth/login');
            return;
        }
        if (user.role !== 'student') {
            toast.error("Solo los estudiantes pueden postularse a vacantes.");
            return;
        }

        setIsApplying(true);
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                toast.error("No se encontró tu sesión. Por favor, inicia sesión de nuevo.");
                router.push('/auth/login');
                return;
            }

            const response = await axiosInstance.post(
                `/vacants/${vacancy?.id}/apply`,
                {},
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );
            toast.success(response.data.message || "Postulación enviada exitosamente!");
            // After successful application (or re-application), re-fetch status
            await fetchVacancyAndApplicationStatus(); // Refresh the status
        } catch (err: any) {
            console.error("Error applying to vacancy:", err);
            const errorMessage = err.response?.data?.error || err.response?.data?.message || "Ocurrió un error al enviar tu postulación.";
            toast.error(errorMessage);
        } finally {
            setIsApplying(false);
        }
    };

    if (loading || loadingUser) {
        return <div className={styles.loadingContainer}>Cargando detalles de la vacante...</div>;
    }

    if (error) {
        return <div className={styles.errorContainer}>{error}</div>;
    }

    if (!vacancy) {
        return <div className={styles.errorContainer}>No se pudo cargar la vacante.</div>;
    }

    const isStudent = user && user.role === 'student';

    // Determine if the "Apply" button should be shown
    // Show apply button if no application, or if application is cancelled/rejected
    const showApplyButton = isStudent && (!applicationStatus || ['cancelada', 'rechazado'].includes(applicationStatus));
    // Show "Already Applied" message if application is pending, reviewed, or in interview
    const showAppliedMessage = isStudent && ['pendiente', 'revisada', 'entrevista', 'aceptado'].includes(applicationStatus || '');


    return (
        <div className={styles.container}>
            <div className={styles.vacancyDetailsCard}>
                <h1 className={styles.title}>{vacancy.title}</h1>
                <p className={styles.companyName}>Publicado por: {vacancy.company_name}</p>
                <div className={styles.metaInfo}>
                    <span>📍 {vacancy.location}</span>
                    <span>💼 {vacancy.modality}</span>
                    <span>🗓️ {vacancy.type}</span>
                    <span>💰 {vacancy.salary_range}</span>
                </div>
                <p className={styles.postedDate}>Publicado el: {vacancy.posted_date}</p>
                {vacancy.application_deadline && (
                    <p className={styles.deadline}>Fecha límite: {vacancy.application_deadline}</p>
                )}
                {vacancy.tags && vacancy.tags.length > 0 && (
                    <div className={styles.tagsContainer}>
                        {vacancy.tags.map(tag => (
                            <span key={tag} className={styles.tag}>{tag}</span>
                        ))}
                    </div>
                )}

                <h2 className={styles.sectionTitle}>Descripción</h2>
                <p className={styles.content}>{vacancy.description}</p>

                <h2 className={styles.sectionTitle}>Requisitos</h2>
                <p className={styles.content}>{vacancy.requirements}</p>

                <h2 className={styles.sectionTitle}>Responsabilidades</h2>
                <p className={styles.content}>{vacancy.responsibilities}</p>

                {showApplyButton && (
                    <div className={styles.applySection}>
                        <h2 className={styles.sectionTitle}>Postúlate a esta Vacante</h2>
                        <button
                            onClick={handleApply}
                            className={styles.applyButton}
                            disabled={isApplying}
                        >
                            {isApplying ? 'Enviando Postulación...' : 'Postularme Ahora'}
                        </button>
                    </div>
                )}

                {showAppliedMessage && (
                    <div className={styles.appliedMessage}>
                        <p>
                            ✅ ¡Ya te has postulado a esta vacante! Estado actual:
                            <span className={`${styles.statusBadge} ${styles[applicationStatus?.toLowerCase() || '']}`}>
                                {/* Updated line for safer string manipulation */}
                                {applicationStatus ? (applicationStatus.charAt(0).toUpperCase() + applicationStatus.slice(1)) : ''}
                            </span>
                        </p>
                        <Link href="/applications" className={styles.viewApplicationsLink}>
                            Ver el estado de mis postulaciones
                        </Link>
                    </div>
                )}

                {!isStudent && user && user.role === 'institution' && (
                    <p className={styles.institutionMessage}>
                        Estás viendo esta vacante como institución.
                    </p>
                )}

                {!user && (
                    <p className={styles.loginToApplyMessage}>
                        <Link href="/auth/login" className={styles.loginLink}>Inicia sesión</Link> como estudiante para postularte.
                    </p>
                )}
            </div>
        </div>
    );
}
