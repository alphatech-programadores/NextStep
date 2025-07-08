// src/app/vacancies/page.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import styles from './VacanciesPage.module.scss';
import FormInput from '@/components/Input';
import axiosInstance from '@/services/axiosConfig';
import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';

// Interfaz unificada de vacante (ajustada para incluir is_applied)
interface Vacancy {
    id: number;
    area: string;
    description: string;
    hours: string;
    modality: string;
    requirements: string;
    status: string;
    start_date: string;
    end_date: string;
    location: string;
    tags: string[];
    institution_email: string;
    company_name: string;
    is_saved?: boolean;
    is_applied?: boolean; // NUEVO: Para guardar el estado de aplicación
}

export default function VacanciesPage() {
    const { user, loadingUser } = useAuth();
    const [vacancies, setVacancies] = useState<Vacancy[]>([]);
    const [loadingVacancies, setLoadingVacancies] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [searchTerm, setSearchTerm] = useState('');
    const [areaFilter, setAreaFilter] = useState('');
    const [modalityFilter, setModalityFilter] = useState('');
    const [hoursFilter, setHoursFilter] = useState('');
    const [locationFilter, setLocationFilter] = useState('');
    const [tagFilter, setTagFilter] = useState('');

    const [uniqueAreas, setUniqueAreas] = useState<string[]>([]);
    const [uniqueModalities, setUniqueModalities] = useState<string[]>([]);
    const [uniqueHours, setUniqueHours] = useState<string[]>([]);
    const [uniqueLocations, setUniqueLocations] = useState<string[]>([]);
    const [uniqueTags, setUniqueTags] = useState<string[]>([]);

    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const fetchVacancies = useCallback(async (page: number = 1) => {
        setLoadingVacancies(true);
        setError(null);
        try {
            const params = {
                q: searchTerm,
                area: areaFilter,
                modality: modalityFilter,
                hours: hoursFilter,
                location: locationFilter,
                tag: tagFilter,
                page: page,
                per_page: 10,
            };
            const response = await axiosInstance.get('/vacants/', { params });
            let fetchedVacancies: Vacancy[] = response.data.vacancies || [];

            // --- NUEVO: Obtener estado de guardado Y estado de aplicación para cada vacante si el usuario es estudiante ---
            if (user && user.role === 'student') {
                const vacanciesWithStatus = await Promise.all(
                    fetchedVacancies.map(async (vac) => {
                        let isSaved = false;
                        let isApplied = false;
                        try {
                            // Verificar si está guardada
                            const savedStatusRes = await axiosInstance.get(`/saved-vacancies/is-saved/${vac.id}`);
                            isSaved = savedStatusRes.data.is_saved;
                        } catch (savedErr) {
                            console.error(`Error checking saved status for vacant ${vac.id}:`, savedErr);
                        }
                        try {
                            // Verificar si ya ha postulado
                            const appliedStatusRes = await axiosInstance.get(`/vacants/check_status/${vac.id}`);
                            isApplied = appliedStatusRes.data.has_applied; // Asegúrate de que el backend envíe 'has_applied'
                        } catch (appliedErr) {
                            console.error(`Error checking applied status for vacant ${vac.id}:`, appliedErr);
                        }
                        return { ...vac, is_saved: isSaved, is_applied: isApplied };
                    })
                );
                setVacancies(vacanciesWithStatus);
            } else {
                setVacancies(fetchedVacancies);
            }
            // --------------------------------------------------------------------------------------------------------
            setTotalPages(response.data.total_pages || 1);
            setCurrentPage(response.data.current_page || page);

        } catch (err: any) {
            console.error("Error fetching vacancies:", err);
            setError(err.response?.data?.error || "No se pudieron cargar las vacantes. Inténtalo de nuevo más tarde.");
            toast.error(err.response?.data?.error || "Error al cargar vacantes.");
        } finally {
            setLoadingVacancies(false);
        }
    }, [searchTerm, areaFilter, modalityFilter, hoursFilter, locationFilter, tagFilter, user]);

    const fetchFilterOptions = useCallback(async () => {
        try {
            const [areasRes, modalitiesRes, hoursRes, locationsRes, tagsRes] = await Promise.all([
                axiosInstance.get('/vacants/filters/areas'),
                axiosInstance.get('/vacants/filters/modalities'),
                axiosInstance.get('/vacants/filters/hours'),
                axiosInstance.get('/vacants/filters/locations'),
                axiosInstance.get('/vacants/filters/tags'),
            ]);
            setUniqueAreas(areasRes.data);
            setUniqueModalities(modalitiesRes.data);
            setUniqueHours(hoursRes.data);
            setUniqueLocations(locationsRes.data);
            setUniqueTags(tagsRes.data);
        } catch (err) {
            console.error("Error fetching filter options:", err);
            toast.error("Error al cargar opciones de filtro.");
        }
    }, []);

    useEffect(() => {
        fetchVacancies(1);
        fetchFilterOptions();
    }, [fetchVacancies, fetchFilterOptions]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        fetchVacancies(1);
    };

    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearchTerm(e.target.value);
    };

    const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const { name, value } = e.target;
        if (name === "area") setAreaFilter(value);
        else if (name === "modality") setModalityFilter(value);
        else if (name === "hours") setHoursFilter(value);
        else if (name === "location") setLocationFilter(value);
        else if (name === "tag") setTagFilter(value);
    };

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= totalPages) {
            fetchVacancies(newPage);
        }
    };

    const handleToggleSaveVacancy = async (vacancyId: number) => {
        if (!user || user.role !== 'student') {
            toast.error("Debes ser estudiante para guardar vacantes.");
            return;
        }
        try {
            const response = await axiosInstance.post(`/saved-vacancies/toggle/${vacancyId}`);
            toast.success(response.data.message);
            setVacancies(prevVacancies =>
                prevVacancies.map(vac =>
                    vac.id === vacancyId ? { ...vac, is_saved: response.data.action === 'added' } : vac
                )
            );
        } catch (error: any) {
            console.error("Error toggling save status:", error);
            toast.error(error.response?.data?.error || "Error al guardar/eliminar vacante.");
        }
    };

    if (loadingUser) {
        return <ProtectedRoute><div className={styles.loadingMessage}>Cargando usuario...</div></ProtectedRoute>;
    }

    return (
        <ProtectedRoute>
            <div className={styles.vacanciesPage}>
                <h1 className={styles.title}>Explorar Oportunidades de Prácticas</h1>

                <form onSubmit={handleSearch} className={styles.searchForm}>
                    <FormInput
                        type="text"
                        placeholder="Buscar por palabra clave (descripción, requisitos, área...)"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className={styles.searchInput}
                        name="searchTerm"
                    />
                    <select name="area" value={areaFilter} onChange={handleFilterChange} className={styles.filterSelect}>
                        <option value="">Todas las Áreas</option>
                        {uniqueAreas.map((area) => (
                            <option key={area} value={area}>{area}</option>
                        ))}
                    </select>
                    <select name="modality" value={modalityFilter} onChange={handleFilterChange} className={styles.filterSelect}>
                        <option value="">Todas las Modalidades</option>
                        {uniqueModalities.map((mod) => (
                            <option key={mod} value={mod}>{mod}</option>
                        ))}
                    </select>
                    <select name="hours" value={hoursFilter} onChange={handleFilterChange} className={styles.filterSelect}>
                        <option value="">Todas las Horas</option>
                        {uniqueHours.map((hours) => (
                            <option key={hours} value={hours}>{hours}</option>
                        ))}
                    </select>
                    <select name="location" value={locationFilter} onChange={handleFilterChange} className={styles.filterSelect}>
                        <option value="">Todas las Ubicaciones</option>
                        {uniqueLocations.map((loc) => (
                            <option key={loc} value={loc}>{loc}</option>
                        ))}
                    </select>
                    <select name="tag" value={tagFilter} onChange={handleFilterChange} className={styles.filterSelect}>
                        <option value="">Todas las Etiquetas</option>
                        {uniqueTags.map((tag) => (
                            <option key={tag} value={tag}>{tag}</option>
                        ))}
                    </select>
                    <button type="submit" className={styles.searchButton}>Buscar</button>
                </form>

                {loadingVacancies && <p className={styles.loadingMessage}>Cargando vacantes...</p>}
                {error && <p className={styles.errorMessage}>{error}</p>}

                {!loadingVacancies && !error && vacancies.length === 0 && (
                    <p className={styles.noResults}>No se encontraron vacantes con los criterios de búsqueda.</p>
                )}

                <div className={styles.vacanciesGrid}>
                    {vacancies.map((vacancy) => (
                        <div key={vacancy.id} className={styles.vacancyCard}>
                            <div className={styles.cardHeader}>
                                <h3 className={styles.cardTitle}>{vacancy.area}</h3>
                                {user && user.role === 'student' && (
                                    <button
                                        className={`${styles.saveButton} ${vacancy.is_saved ? styles.saved : ''}`}
                                        onClick={() => handleToggleSaveVacancy(vacancy.id)}
                                        title={vacancy.is_saved ? 'Eliminar de guardados' : 'Guardar vacante'}
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill={vacancy.is_saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>
                                    </button>
                                )}
                            </div>
                            <p className={styles.cardInstitution}>{vacancy.company_name}</p>
                            <p className={styles.cardDescription}>
                                {vacancy.description ? vacancy.description.substring(0, 120) + '...' : 'Sin descripción.'}
                            </p>
                            <div className={styles.cardTags}>
                                {vacancy.tags && vacancy.tags.map((tag) => (
                                    <span key={tag.trim()} className={styles.tag}>{tag.trim()}</span>
                                ))}
                            </div>
                            <div className={styles.cardFooter}>
                                <span className={styles.cardLocation}>{vacancy.location}</span>
                                <span className={styles.cardModality}>{vacancy.modality}</span>
                                <Link href={`/vacancies/${vacancy.id}`} className={styles.viewDetailsButton}>
                                    Ver Detalles
                                </Link>
                            </div>
                            {/* NUEVO: Indicador de Postulado */}
                            {user && user.role === 'student' && vacancy.is_applied && (
                                <div className={styles.appliedIndicator}>
                                    <span>✅ Postulado</span>
                                </div>
                            )}
                        </div>
                    ))}
                </div>

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