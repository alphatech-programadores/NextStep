// src/app/student/applications/page.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import styles from './ApplicationsPage.module.scss';
import axiosInstance from '@/services/axiosConfig';

interface ApplicationData {
    id: number;
    status: string;
    vacant_id: number;
    vacant_title: string;
    company_name: string;
    application_status: string; // This seems redundant if 'status' is already there
    applied_at: string;
    vacant_location: string;
    vacant_modality: string;
    vacant_hours: string;
}

export default function ApplicationsPage() {
    const { user, loadingUser } = useAuth();
    const [applications, setApplications] = useState<ApplicationData[]>([]);
    const [loadingApplications, setLoadingApplications] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [statusFilter, setStatusFilter] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const fetchApplications = useCallback(async (page: number = 1) => {
        if (loadingUser || !user || user.role !== 'student') return;

        setLoadingApplications(true);
        setError(null);
        try {
            const params = {
                status: statusFilter,
                page: page,
                per_page: 10,
            };

            const response = await axiosInstance.get('/apply/me', {
                params,
            });
            setApplications(response.data.applications);
            setTotalPages(response.data.total_pages);
            setCurrentPage(response.data.current_page);
        } catch (err: any) {
            console.error("Error fetching applications:", err);
            setError(err.response?.data?.error || "Error al cargar tus postulaciones.");
            toast.error("Error al cargar postulaciones.");
        } finally {
            setLoadingApplications(false);
        }
    }, [user, loadingUser, statusFilter]);

    useEffect(() => {
        if (!loadingUser && user && user.role === 'student') {
            fetchApplications(1);
        }
    }, [fetchApplications, loadingUser, user]);

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= totalPages) {
            fetchApplications(newPage);
        }
    };

    const handleCancelApplication = async (applicationId: number) => {
        if (!confirm("¿Estás seguro de que quieres cancelar esta postulación?")) {
            return;
        }

        try {
            // New API call for cancellation
            await axiosInstance.patch(`/apply/${applicationId}/cancel`);
            toast.success("Postulación cancelada correctamente.");
            // Refresh the applications list after cancellation
            fetchApplications(currentPage);
        } catch (err: any) {
            console.error("Error cancelling application:", err);
            toast.error(err.response?.data?.error || "Error al cancelar la postulación.");
        }
    };


    if (loadingUser || (user && user.role !== 'student')) {
        return (
            <ProtectedRoute allowedRoles={['student']}>
                <div className={styles.loadingContainer}>Cargando...</div>
            </ProtectedRoute>
        );
    }

    if (loadingApplications) {
        return (
            <ProtectedRoute allowedRoles={['student']}>
                <div className={styles.loadingContainer}>Cargando tus postulaciones...</div>
            </ProtectedRoute>
        );
    }

    if (error) {
        return (
            <ProtectedRoute allowedRoles={['student']}>
                <div className={styles.errorContainer}>{error}</div>
            </ProtectedRoute>
        );
    }

    return (
        <ProtectedRoute allowedRoles={['student']}>
            <div className={styles.container}>
                <h1 className={styles.title}>Mis Postulaciones</h1>

                <div className={styles.filterSection}>
                    <label htmlFor="statusFilter">Filtrar por estado:</label>
                    <select
                        id="statusFilter"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className={styles.filterSelect}
                    >
                        <option value="">Todos</option>
                        <option value="pendiente">Pendiente</option>
                        <option value="revisada">Revisada</option>
                        <option value="entrevista">Entrevista</option>
                        <option value="aceptado">Aceptado</option>
                        <option value="rechazado">Rechazado</option>
                        <option value="cancelada">Cancelada</option> {/* Add new status */}
                    </select>
                    <button onClick={() => fetchApplications(1)} className={styles.applyFilterButton}>Aplicar Filtro</button>
                </div>

                {applications.length === 0 ? (
                    <p className={styles.noApplications}>Aún no tienes postulaciones. ¡Es hora de explorar vacantes!</p>
                ) : (
                    <div className={styles.applicationsGrid}>
                        {applications.map((app) => (
                            <div key={app.id} className={styles.applicationCard}>
                                <h2 className={styles.vacantTitle}>{app.vacant_title}</h2>
                                <p className={styles.companyName}>{app.company_name}</p>
                                <p className={styles.metaInfo}>
                                    📍 {app.vacant_location} | 💼 {app.vacant_modality}
                                </p>
                                <p className={styles.hoursInfo}>Horas/Salario: {app.vacant_hours}</p>
                                <div className={styles.statusBadgeContainer}>
                                    <span className={`${styles.statusBadge} ${styles[app.status.toLowerCase()]}`}>
                                        {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                                    </span>
                                    <span className={styles.appliedAt}>Postulado el: {app.applied_at}</span>
                                </div>
                                <Link href={`/vacancies/${app.vacant_id}`} className={styles.viewDetailsButton}>
                                    Ver Vacante
                                </Link>
                                {/* Add Cancel button */}
                                {app.status !== 'aceptado' && app.status !== 'rechazado' && app.status !== 'cancelada' && (
                                    <button
                                        onClick={() => handleCancelApplication(app.id)}
                                        className={styles.cancelButton} // Define this style in your SCSS
                                    >
                                        Cancelar Postulación
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {totalPages > 1 && (
                    <div className={styles.pagination}>
                        <button
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                            className={styles.paginationButton}
                        >
                            Anterior
                        </button>
                        <span>Página {currentPage} de {totalPages}</span>
                        <button
                            onClick={() => handlePageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
                            className={styles.paginationButton}
                        >
                            Siguiente
                        </button>
                    </div>
                )}
            </div>
        </ProtectedRoute>
    );
}