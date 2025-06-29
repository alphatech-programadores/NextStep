// src/app/vacancies/page.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Link from 'next/link';
import toast from 'react-hot-toast';
import styles from './VacanciesPage.module.scss';
import FormInput from '@/components/Input';

interface Vacancy {
    id: number;
    title: string;
    description: string;
    location: string;
    modality: string;
    type: string;
    salary_range: string;
    posted_date: string;
    application_deadline: string;
    company_name: string;
    tags: string[];
}

export default function VacanciesPage() {
    const [vacancies, setVacancies] = useState<Vacancy[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Estados para los valores de los filtros seleccionados
    const [keywordSearch, setKeywordSearch] = useState('');
    const [locationFilter, setLocationFilter] = useState('');
    const [modalityFilter, setModalityFilter] = useState('');
    const [areaFilter, setAreaFilter] = useState('');
    const [tagFilter, setTagFilter] = useState('');

    // Estados para las OPCIONES de los filtros (que vendrán del backend)
    const [uniqueAreas, setUniqueAreas] = useState<string[]>([]);
    const [uniqueModalities, setUniqueModalities] = useState<string[]>([]);
    const [uniqueLocations, setUniqueLocations] = useState<string[]>([]);
    const [uniqueTags, setUniqueTags] = useState<string[]>([]);

    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    // Función para cargar las vacantes según los filtros
    const fetchVacancies = useCallback(async (page: number = 1) => {
        setLoading(true);
        setError(null);
        try {
            const params = {
                q: keywordSearch,
                location: locationFilter,
                modality: modalityFilter,
                area: areaFilter,
                tag: tagFilter,
                page: page,
                per_page: 10,
            };
            const response = await axios.get('http://localhost:5000/api/vacants/', { params });
            setVacancies(response.data.vacancies);
            setTotalPages(response.data.total_pages);
            setCurrentPage(response.data.current_page);
        } catch (err: any) {
            console.error("Error fetching vacancies:", err);
            setError("No se pudieron cargar las vacantes. Inténtalo de nuevo más tarde.");
            toast.error("Error al cargar vacantes.");
        } finally {
            setLoading(false);
        }
    }, [keywordSearch, locationFilter, modalityFilter, areaFilter, tagFilter]);

    // Función para cargar las opciones de filtro únicas
    const fetchFilterOptions = useCallback(async () => {
        try {
            const [areasRes, modalitiesRes, locationsRes, tagsRes] = await Promise.all([
                axios.get('http://localhost:5000/api/vacants/filters/areas'),
                axios.get('http://localhost:5000/api/vacants/filters/modalities'),
                axios.get('http://localhost:5000/api/vacants/filters/locations'),
                axios.get('http://localhost:5000/api/vacants/filters/tags'),
            ]);
            setUniqueAreas(areasRes.data);
            setUniqueModalities(modalitiesRes.data);
            setUniqueLocations(locationsRes.data);
            setUniqueTags(tagsRes.data);
        } catch (err) {
            console.error("Error fetching filter options:", err);
            toast.error("Error al cargar opciones de filtro.");
        }
    }, []);

    // Cargar vacantes y opciones de filtro al montar el componente
    useEffect(() => {
        fetchVacancies(1);
        fetchFilterOptions();
    }, [fetchVacancies, fetchFilterOptions]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        fetchVacancies(1);
    };

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= totalPages) {
            fetchVacancies(newPage);
        }
    };

    return (
        <div className={styles.container}>
            <h1 className={styles.title}>Explora Oportunidades de Práctica</h1>

            <form onSubmit={handleSearch} className={styles.searchForm}>
                <FormInput
                    type="text"
                    placeholder="Buscar por palabra clave (descripción, requisitos, área...)"
                    value={keywordSearch}
                    onChange={(e) => setKeywordSearch(e.target.value)}
                    className={styles.searchInput} name={''} />
                {/* Filtro por Ubicación */}
                <select
                    value={locationFilter}
                    onChange={(e) => setLocationFilter(e.target.value)}
                    className={styles.filterSelect}
                >
                    <option value="">Todas las Ubicaciones</option>
                    {uniqueLocations.map((loc) => (
                        <option key={loc} value={loc}>{loc}</option>
                    ))}
                </select>
                {/* Filtro por Modalidad */}
                <select
                    value={modalityFilter}
                    onChange={(e) => setModalityFilter(e.target.value)}
                    className={styles.filterSelect}
                >
                    <option value="">Todas las Modalidades</option>
                    {uniqueModalities.map((mod) => (
                        <option key={mod} value={mod}>{mod}</option>
                    ))}
                </select>
                {/* Filtro por Área */}
                <select
                    value={areaFilter}
                    onChange={(e) => setAreaFilter(e.target.value)}
                    className={styles.filterSelect}
                >
                    <option value="">Todas las Áreas</option>
                    {uniqueAreas.map((area) => (
                        <option key={area} value={area}>{area}</option>
                    ))}
                </select>
                {/* Filtro por Etiqueta (Tag) */}
                <select
                    value={tagFilter}
                    onChange={(e) => setTagFilter(e.target.value)}
                    className={styles.filterSelect} // Usar filterSelect para dropdowns
                >
                    <option value="">Todas las Etiquetas</option>
                    {uniqueTags.map((tag) => (
                        <option key={tag} value={tag}>{tag}</option>
                    ))}
                </select>
                <button type="submit" className={styles.searchButton}>Buscar</button>
            </form>

            {/* ... (el resto del JSX para mostrar vacantes, paginación, etc.) */}
            {loading && <p className={styles.loadingMessage}>Cargando vacantes...</p>}
            {error && <p className={styles.errorMessage}>{error}</p>}

            {!loading && !error && vacancies.length === 0 && (
                <p className={styles.noResults}>No se encontraron vacantes con los criterios de búsqueda.</p>
            )}

            <div className={styles.vacanciesGrid}>
                {vacancies.map((vacancy) => (
                    <div key={vacancy.id} className={styles.vacancyCard}>
                        <h2 className={styles.vacancyTitle}>{vacancy.title}</h2>
                        <p className={styles.companyName}>{vacancy.company_name}</p>
                        <p className={styles.vacancyMeta}>
                            {vacancy.location} | {vacancy.modality} | {vacancy.type}
                        </p>
                        <p className={styles.salaryRange}>{vacancy.salary_range}</p>
                        <p className={styles.descriptionSnippet}>
                            {vacancy.description.substring(0, 150)}...
                        </p>
                        {vacancy.tags && vacancy.tags.length > 0 && (
                            <div className={styles.tagsContainer}>
                                {vacancy.tags.map(tag => (
                                    <span key={tag} className={styles.tag}>{tag}</span>
                                ))}
                            </div>
                        )}
                        <Link href={`/vacancies/${vacancy.id}`} className={styles.detailsButton}>
                            Ver Detalles
                        </Link>
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
    );
}