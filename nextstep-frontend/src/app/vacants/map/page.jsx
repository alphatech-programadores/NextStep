// src/app/vacants/map/page.jsx
'use client';

import { useEffect, useState, useRef } from "react";
import styles from "./VacantsMap.module.scss";

// --- CAMBIOS CLAVE: Importar dynamic para SSR: false ---
import dynamic from 'next/dynamic';
import 'leaflet/dist/leaflet.css'; // Importar los estilos CSS de Leaflet

// NO IMPORTAR 'L' DIRECTAMENTE AQUÍ. Se importará condicionalmente más abajo.
// import L from 'leaflet';

import axiosInstance from "@/services/axiosConfig";
import toast from 'react-hot-toast';
import Link from 'next/link';

// --- CAMBIO CLAVE: Importar MapContainer y sus hijos dinámicamente con SSR deshabilitado ---
// Esto asegura que Leaflet solo se cargue en el cliente
const MapContainer = dynamic(
    () => import('react-leaflet').then(mod => {
        // IMPORTAR 'L' AQUÍ Y CONFIGURAR ICONOS DENTRO DEL CONTEXTO DEL CLIENTE
        // Esto asegura que 'L' solo se use cuando 'window' esté definido.
        const L = require('leaflet');
        delete L.Icon.Default.prototype._getIconUrl;

        L.Icon.Default.mergeOptions({
            iconRetinaUrl: '/leaflet/images/marker-icon-2x.png',
            iconUrl: '/leaflet/images/marker-icon.png',
            shadowUrl: '/leaflet/images/marker-shadow.png',
        });
        // --- FIN DE LA CONFIGURACIÓN DEL ICONO ---

        return mod.MapContainer;
    }),
    { ssr: false }
);

const TileLayer = dynamic(
    () => import('react-leaflet').then(mod => mod.TileLayer),
    { ssr: false }
);
const Marker = dynamic(
    () => import('react-leaflet').then(mod => mod.Marker),
    { ssr: false }
);
const Popup = dynamic(
    () => import('react-leaflet').then(mod => mod.Popup),
    { ssr: false }
);
// ---------------------------------------------------------------------------------


const VacantsMap = () => {
    const [centerLng, setCenterLng] = useState(-99.1332);
    const [centerLat, setCenterLat] = useState(19.4326);
    const [initialZoom, setInitialZoom] = useState(9);

    const [vacancies, setVacancies] = useState([]);

    const [loadingVacancies, setLoadingVacancies] = useState(true);
    const [errorFetchingVacancies, setErrorFetchingVacancies] = useState(null);

    useEffect(() => {
        const fetchVacancies = async () => {
            setLoadingVacancies(true);
            setErrorFetchingVacancies(null);
            try {
                const response = await axiosInstance.get("/vacants/map");
                const vacanciesList = Array.isArray(response.data) ? response.data : response.data.vacancies || [];
                const validVacancies = vacanciesList.filter(v => v.latitude && v.longitude);
                setVacancies(validVacancies);
            } catch (error) {
                console.error("Error fetching vacancies:", error);
                setErrorFetchingVacancies(error.response?.data?.error || "No se pudieron cargar las vacantes.");
                toast.error("Error al cargar vacantes en el mapa.");
            } finally {
                setLoadingVacancies(false);
            }
        };
        fetchVacancies();
    }, []);


    return (
        <div className={styles.mapPage}>
            <h1 className={styles.title}>Mapa de Oportunidades</h1>

            <div className={styles.mapContainer}>
                {/* Renderiza MapContainer y sus hijos solo si ya se cargó el componente dinámicamente */}
                {/* La comprobación typeof window !== 'undefined' ya no es estrictamente necesaria si todo es dynamic(ssr:false) */}
                <MapContainer
                    center={[centerLat, centerLng]}
                    zoom={initialZoom}
                    scrollWheelZoom={true}
                    className={styles.map}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />

                    {vacancies.map((vacancy) => (
                        vacancy.latitude && vacancy.longitude && (
                            <Marker key={vacancy.id} position={[vacancy.latitude, vacancy.longitude]}>
                                <Popup>
                                    <div className={styles.popupContent}>
                                        <h3 className={styles.popupTitle}>{vacancy.position || vacancy.area}</h3>
                                        <p className={styles.popupDescription}>
                                            {vacancy.description ? vacancy.description.substring(0, 100) + '...' : 'Sin descripción.'}
                                        </p>
                                        <p className={styles.popupLocation}>{vacancy.location}</p>
                                        <Link href={`/vacancies/${vacancy.id}`} className={styles.popupLink}>
                                            Ver Detalles
                                        </Link>
                                    </div>
                                </Popup>
                            </Marker>
                        )
                    ))}
                </MapContainer>

                <div className={styles.sidebar}>
                    Longitud: {centerLng} | Latitud: {centerLat} | Zoom: {initialZoom}
                </div>

                {/* Mensajes de estado */}
                {loadingVacancies && (
                    <div className={styles.overlayMessage}>Cargando vacantes en el mapa...</div>
                )}
                {errorFetchingVacancies && (
                    <div className={`${styles.overlayMessage} ${styles.errorMessage}`}>
                        Error: {errorFetchingVacancies}
                    </div>
                )}
                {!loadingVacancies && !errorFetchingVacancies && vacancies.length === 0 && (
                    <div className={styles.overlayMessage}>No se encontraron vacantes para mostrar en el mapa.</div>
                )}
            </div>
        </div>
    );
};

export default VacantsMap;