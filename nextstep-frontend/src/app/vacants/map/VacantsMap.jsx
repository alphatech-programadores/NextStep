import { useEffect, useState, useRef } from "react";
import styles from "./VacantsMap.module.scss";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import axiosInstance from "@/services/axiosConfig"; // CAMBIO AQUÍ: Importar axiosInstance

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

const VacantsMap = () => {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const [lng, setLng] = useState(-99.1332); // Default to Mexico City
    const [lat, setLat] = useState(19.4326);
    const [zoom, setZoom] = useState(9);
    const [vacancies, setVacancies] = useState([]);
    const markers = useRef({}); // To keep track of markers

    useEffect(() => {
        if (map.current) return; // initialize map only once
        map.current = new mapboxgl.Map({
            container: mapContainer.current,
            style: "mapbox://styles/mapbox/streets-v11",
            center: [lng, lat],
            zoom: zoom,
        });

        map.current.on("move", () => {
            setLng(map.current.getCenter().lng.toFixed(4));
            setLat(map.current.getCenter().lat.toFixed(4));
            setZoom(map.current.getZoom().toFixed(2));
        });

        map.current.addControl(new mapboxgl.NavigationControl(), "top-right");
        map.current.addControl(new mapboxgl.FullscreenControl(), "bottom-right");

        // Clean up map on unmount
        return () => {
            map.current.remove();
            map.current = null;
        };
    }, []);

    useEffect(() => {
        const fetchVacancies = async () => {
            try {
                const response = await axiosInstance.get("/vacants/map"); // CAMBIO AQUÍ: Usar axiosInstance
                setVacancies(response.data.data);
            } catch (error) {
                console.error("Error fetching vacancies:", error);
            }
        };
        fetchVacancies();
    }, []);

    useEffect(() => {
        // Add markers for new vacancies
        vacancies.forEach((vacancy) => {
            if (!markers.current[vacancy.id]) {
                const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(
                    `<h3>${vacancy.position}</h3><p>${vacancy.description}</p>`
                );

                const marker = new mapboxgl.Marker()
                    .setLngLat([vacancy.long, vacancy.lat])
                    .setPopup(popup)
                    .addTo(map.current);

                markers.current[vacancy.id] = marker;
            }
        });

        // Remove markers for vacancies that are no longer in the list
        const currentVacancyIds = new Set(vacancies.map((v) => v.id));
        for (const id in markers.current) {
            if (!currentVacancyIds.has(parseInt(id))) {
                markers.current[id].remove();
                delete markers.current[id];
            }
        }
    }, [vacancies]);

    return (
        <div className={styles.mapContainer}>
            <div ref={mapContainer} className={styles.map} />
            <div className={styles.sidebar}>
                Longitude: {lng} | Latitude: {lat} | Zoom: {zoom}
            </div>
        </div>
    );
};

export default VacantsMap;