'use client'
// React hooks and utilities
import { useState, useEffect } from 'react';
// Axios instance for API requests, configured with base URL and interceptors
import axiosInstance from '@/services/axiosConfig';
// Toast notifications for user feedback
import toast from 'react-hot-toast';
// SCSS module for styling this specific page
import styles from './recommendations.module.scss';

// Interface defining the structure of a recommended vacancy object
interface RecommendedVacancy {
    id: number;
    area: string;
    description: string;
    modality: string;
    location: string;
    match_score: number;
    // Add other relevant fields you want to display from the backend
}

/**
 * MyRecommendationsPage Component
 * Displays a list of job vacancies recommended to the logged-in student based on their skills.
 */
const MyRecommendationsPage = () => {
    // State to store the list of recommended vacancies
    const [recommendations, setRecommendations] = useState<RecommendedVacancy[]>([]);
    // State to manage loading status during API calls
    const [loading, setLoading] = useState(true);
    // State to store any error messages
    const [error, setError] = useState<string | null>(null);

    // useEffect hook to fetch recommendations when the component mounts
    useEffect(() => {
        /**
         * Asynchronous function to fetch recommendations from the backend API.
         */
        const fetchRecommendations = async () => {
            setLoading(true); // Set loading to true before the API call
            try {
                // Make a GET request to the recommendations API endpoint
                // The base URL 'http://localhost:5000/api' is prepended by axiosInstance
                const response = await axiosInstance.get('/recommendations');
                setRecommendations(response.data); // Update state with fetched data
            } catch (err: any) {
                // Log and handle errors during the API call
                console.error('Error fetching recommendations:', err);
                setError(err.response?.data?.error || 'No se pudieron cargar las recomendaciones.');
                toast.error('Error al cargar recomendaciones.'); // Show a toast notification
            } finally {
                setLoading(false); // Set loading to false after the API call completes
            }
        };

        fetchRecommendations(); // Call the fetch function
    }, []); // Empty dependency array ensures this effect runs only once on mount

    // Render loading state while data is being fetched
    if (loading) {
        return (
            <div className={styles.recommendationsPage}>
                <p>Cargando recomendaciones...</p>
            </div>
        );
    }

    // Render error state if an error occurred during data fetching
    if (error) {
        return (
            <div className={styles.recommendationsPage}>
                <p>Error: {error}</p>
            </div>
        );
    }

    // Main component render
    return (
        <div className={styles.recommendationsPage}>
            <div className={styles.header}>
                <h1>Vacantes Recomendadas para ti</h1>
            </div>

            {/* Conditionally render recommendations list or a "no recommendations" message */}
            {recommendations.length > 0 ? (
                <ul className={styles.recommendationsList}>
                    {recommendations.map(vacant => (
                        <li key={vacant.id} className={styles.vacancyCard}>
                            <div>
                                <h3>{vacant.area}</h3>
                                <p>Descripción: {vacant.description}</p>
                                <p>Modalidad: {vacant.modality}</p>
                                <p>Ubicación: {vacant.location}</p>
                                {/* Display match score, formatted to two decimal places */}
                                <p className={styles.matchScore}>Puntuación de Coincidencia: {vacant.match_score.toFixed(2)}</p>
                            </div>
                            {/* Link to the detailed page of the vacancy */}
                            <a href={`/vacancies/${vacant.id}`}>Ver Detalles</a>
                        </li>
                    ))}
                </ul>
            ) : (
                // Message displayed when no recommendations are found
                <p className={styles.noRecommendations}>
                    No se encontraron vacantes recomendadas en este momento.
                    Asegúrate de tener tu perfil de estudiante completo con habilidades.
                </p>
            )}
        </div>
    );
};

export default MyRecommendationsPage;
