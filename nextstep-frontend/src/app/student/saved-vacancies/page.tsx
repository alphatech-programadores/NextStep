// src/app/student/saved-vacancies/page.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import styles from './saved-vacancies.module.scss';
import axiosInstance from '@/services/axiosConfig';
import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';

// Interfaz para una Vacante Guardada (ajusta exactamente a la respuesta JSON proporcionada)
interface SavedVacancy {
    student_email: string;
    vacant_id: number;
    saved_at: string;
    vacant_details: {
        id: number;
        area: string;
        description: string;
        hours: string;
        modality: string;
        location: string;
        tags: string[];
        institution_email: string;
        company_name?: string; // Asegurarse de que esté aquí
    };
}

export default function SavedVacanciesPage() {
    const { user, loadingUser } = useAuth();
    const [savedVacancies, setSavedVacancies] = useState<SavedVacancy[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchSavedVacancies = useCallback(async () => {
        if (!user || user.role !== 'student') {
            setLoading(false);
            setError("Debes iniciar sesión como estudiante para ver tus vacantes guardadas.");
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const response = await axiosInstance.get('/saved-vacancies/');
            setSavedVacancies(response.data.data || []);
        } catch (err: any) {
            console.error("Error fetching saved vacancies:", err);
            setError(err.response?.data?.error || "No se pudieron cargar tus vacantes guardadas.");
            toast.error(err.response?.data?.error || "Error al cargar vacantes guardadas.");
        } finally {
            setLoading(false);
        }
    }, [user]);

    useEffect(() => {
        fetchSavedVacancies();
    }, [fetchSavedVacancies]);

    const handleRemoveSavedVacancy = async (vacantId: number) => {
        if (!user || user.role !== 'student') {
            toast.error("Error de autenticación.");
            return;
        }
        if (!confirm("¿Estás seguro de que quieres eliminar esta vacante de tus guardados?")) {
            return;
        }

        try {
            const response = await axiosInstance.post(`/saved-vacancies/toggle/${vacantId}`);
            toast.success(response.data.message || "Vacante eliminada de tus guardados.");
            setSavedVacancies(prev => prev.filter(sv => sv.vacant_id !== vacantId));
        } catch (error: any) {
            console.error("Error removing saved vacancy:", error);
            toast.error(error.response?.data?.error || "Error al eliminar la vacante de guardados.");
        }
    };


    if (loadingUser || loading) {
        return <ProtectedRoute allowedRoles={['student']}><div className={styles.loadingContainer}>Cargando vacantes guardadas...</div></ProtectedRoute>;
    }

    if (error) {
        return <ProtectedRoute allowedRoles={['student']}><div className={styles.errorContainer}>{error}</div></ProtectedRoute>;
    }

    if (savedVacancies.length === 0) {
        return (
            <ProtectedRoute allowedRoles={['student']}>
                <div className={styles.savedVacanciesPage}>
                    <h1 className={styles.title}>Mis Vacantes Guardadas</h1>
                    <div className={styles.emptyState}>
                        <p>Aún no has guardado ninguna vacante. Empieza a explorar oportunidades. ✨</p>
                        <Link href="/vacancies" className={styles.exploreButton}>Explorar Vacantes</Link>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    return (
        <ProtectedRoute >
            <div className={styles.savedVacanciesPage}>
                <h1 className={styles.title}>Mis Vacantes Guardadas</h1>
                <div className={styles.vacanciesGrid}>
                    {savedVacancies.map((savedItem) => (
                        <div key={savedItem.vacant_id} className={styles.vacancyCard}>
                            <div className={styles.cardHeader}>
                                <h3 className={styles.cardTitle}>{savedItem.vacant_details.area}</h3>
                                <button
                                    className={styles.removeButton}
                                    onClick={() => handleRemoveSavedVacancy(savedItem.vacant_details.id)}
                                    title="Eliminar de guardados"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                                </button>
                            </div>
                            <p className={styles.cardInstitution}>{savedItem.vacant_details.company_name || 'Institución Desconocida'}</p>
                            <p className={styles.cardDescription}>
                                {savedItem.vacant_details.description ? savedItem.vacant_details.description.substring(0, 120) + '...' : 'Sin descripción.'}
                            </p>
                            <div className={styles.cardTags}>
                                {savedItem.vacant_details.tags && savedItem.vacant_details.tags.map((tag) => (
                                    <span key={tag.trim()} className={styles.tag}>{tag.trim()}</span>
                                ))}
                            </div>
                            <div className={styles.cardFooter}>
                                <span className={styles.cardLocation}>{savedItem.vacant_details.location}</span>
                                <span className={styles.cardModality}>{savedItem.vacant_details.modality}</span>
                                <Link href={`/vacancies/${savedItem.vacant_details.id}`} className={styles.viewDetailsButton}>
                                    Ver Detalles
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </ProtectedRoute>
    );
}