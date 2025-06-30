// src/app/vacancies/[id]/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '@/context/AuthContext';
import styles from './VacancyDetailsPage.module.scss';
import Link from 'next/link';
import axiosInstance from '@/services/axiosConfig';

interface VacancyDetails { // Ajustar nombres de propiedades
    id: number;
    title: string; // 'area' del modelo Vacant
    description: string;
    requirements: string;
    responsibilities: string; // Usaremos 'requirements' si tu modelo no tiene este campo separado
    location: string;
    modality: string;
    type: string; // También 'area' del modelo Vacant
    salary_range: string; // 'hours' del modelo Vacant
    posted_date: string; // 'start_date'
    application_deadline: string; // 'end_date'
    company_name: string;
    institution_email: string;
    tags: string[]; // Nuevo
}

export default function VacancyDetailsPage() {
    const { id } = useParams();
    const router = useRouter();
    const { user, loadingUser } = useAuth();
    const [vacancy, setVacancy] = useState<VacancyDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isApplying, setIsApplying] = useState(false);
    // const [coverLetter, setCoverLetter] = useState(''); // No se usa si Application no tiene cover_letter
    const [hasApplied, setHasApplied] = useState(false);

    useEffect(() => {
        if (!id) return;

        const fetchVacancy = async () => {
            setLoading(true);
            setError(null);
            try {
                // Llama al endpoint de detalles de vacante
                const response = await axiosInstance.get(`http://localhost:5000/api/vacants/${id}`);
                setVacancy(response.data);

                if (user && user.role === 'student') {
                    const token = localStorage.getItem('access_token');
                    if (token) {
                        try {
                            // Llama al endpoint de check_status
                            const checkResponse = await axiosInstance.get(`http://localhost:5000/api/vacants/check_status/${id}`, {
                                headers: { Authorization: `Bearer ${token}` }
                            });
                            setHasApplied(checkResponse.data.has_applied);
                        } catch (checkError) {
                            console.error("Error checking application status:", checkError);
                        }
                    }
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
        };

        fetchVacancy();
    }, [id, user]);

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
                `http://localhost:5000/api/vacants/${vacancy?.id}/apply`,
                {}, // Envía un objeto vacío si tu modelo Application no tiene cover_letter
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );
            toast.success(response.data.message || "Postulación enviada exitosamente!");
            setHasApplied(true);
            // setCoverLetter(''); // No se limpia si no se usa
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

    return (
        <div className={styles.container}>
            <div className={styles.vacancyDetailsCard}>
                <h1 className={styles.title}>{vacancy.title}</h1> {/* Muestra el 'area' como título */}
                <p className={styles.companyName}>Publicado por: {vacancy.company_name}</p>
                <div className={styles.metaInfo}>
                    <span>📍 {vacancy.location}</span>
                    <span>💼 {vacancy.modality}</span>
                    <span>🗓️ {vacancy.type}</span> {/* Muestra 'area' como tipo */}
                    <span>💰 {vacancy.salary_range}</span> {/* Muestra 'hours' como rango salarial/horas */}
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
                {/* Usamos responsibilities que ahora viene del backend (o requirements si no existe) */}
                <p className={styles.content}>{vacancy.responsibilities}</p>

                {isStudent && !hasApplied && (
                    <div className={styles.applySection}>
                        <h2 className={styles.sectionTitle}>Postúlate a esta Vacante</h2>
                        {/* Remueve la carta de presentación si tu modelo Application no la soporta */}
                        {/* <textarea
                            className={styles.coverLetterTextarea}
                            placeholder="Escribe aquí tu carta de presentación (opcional)..."
                            value={coverLetter}
                            onChange={(e) => setCoverLetter(e.target.value)}
                            rows={5}
                        ></textarea> */}
                        <button
                            onClick={handleApply}
                            className={styles.applyButton}
                            disabled={isApplying}
                        >
                            {isApplying ? 'Enviando Postulación...' : 'Postularme Ahora'}
                        </button>
                    </div>
                )}

                {isStudent && hasApplied && (
                    <div className={styles.appliedMessage}>
                        <p>✅ ¡Ya te has postulado a esta vacante!</p>
                        <Link href="/student/applications" className={styles.viewApplicationsLink}>
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