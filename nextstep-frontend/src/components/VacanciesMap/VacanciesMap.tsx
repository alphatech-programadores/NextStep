import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import toast from "react-hot-toast";
import "leaflet/dist/leaflet.css";


// Tipo base de vacante
interface Vacant {
    id: number;
    area: string;
    description: string;
    latitude: number | null;
    longitude: number | null;
    modality: string;
    location: string;
    tags: string[];
}

// Vacante con coordenadas garantizadas
interface VacantWithCoords extends Vacant {
    latitude: number;
    longitude: number;
}

// Ícono personalizado
const customIcon = new L.Icon({
    iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
});




const DEFAULT_CENTER: [number, number] = [19.4326, -99.1332];
const DEFAULT_ZOOM = 12;

// Utilidad: distancia Haversine en metros
function haversine(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371e3;
    const toRad = (deg: number) => (deg * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
}

function MapRefSetter({ mapRef }: { mapRef: React.MutableRefObject<L.Map | null> }) {
    const map = useMap();
    useEffect(() => {
        mapRef.current = map;
    }, [map]);
    return null;
}


const VacanciesMap: React.FC = () => {
    const [vacants, setVacants] = useState<Vacant[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
    const [areaFilter, setAreaFilter] = useState("");
    const mapRef = useRef<L.Map | null>(null);
    const centerOnMyLocation = () => {
        if (!navigator.geolocation) {
            toast.error("Tu navegador no soporta geolocalización. Usando ubicación simulada.");
            const fallbackCoords: [number, number] = [19.4326, -99.1332]; // CDMX
            setUserLocation(fallbackCoords);
            if (mapRef.current) {
                mapRef.current.flyTo(fallbackCoords, DEFAULT_ZOOM);
            }
            return;
        }
        toast.loading("Obteniendo tu ubicación...");
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords: [number, number] = [pos.coords.latitude, pos.coords.longitude];
                setUserLocation(coords);
                if (mapRef.current) {
                    mapRef.current.flyTo(coords, DEFAULT_ZOOM);
                }
                toast.dismiss();
                toast.success("Mapa centrado en tu ubicación.");
            },
            (err) => {
                console.warn("Error real al obtener ubicación:", err);
                toast.dismiss();
                toast.error("No se pudo obtener tu ubicación real. Usando ubicación simulada.");
                const fallbackCoords: [number, number] = [19.4326, -99.1332]; // CDMX
                setUserLocation(fallbackCoords);
                if (mapRef.current) {
                    mapRef.current.flyTo(fallbackCoords, DEFAULT_ZOOM);
                }
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    };


    const fetchVacants = async (area?: string) => {
        setLoading(true);
        setError(null);
        try {
            const params = area ? `?area=${encodeURIComponent(area)}` : "";
            const res = await fetch(`/api/vacants/map${params}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data: Vacant[] = await res.json();
            setVacants(data);
        } catch (e: any) {
            console.error("Error al cargar vacantes:", e);
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchVacants();
    }, []);




    const findNearestVacant = () => {
        if (!navigator.geolocation) {
            toast.error("Tu navegador no soporta geolocalización.");
            return;
        }
        toast.loading("Buscando la vacante más cercana...");
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const [lat, lon] = [pos.coords.latitude, pos.coords.longitude];
                const withCoords: VacantWithCoords[] = vacants.filter(
                    (v): v is VacantWithCoords => v.latitude !== null && v.longitude !== null
                );
                if (withCoords.length === 0) {
                    toast.dismiss();
                    toast.error("No hay vacantes con coordenadas.");
                    return;
                }
                const nearest = withCoords.reduce((best, current) => {
                    const dist = haversine(lat, lon, current.latitude, current.longitude);
                    if (!best || dist < best.dist) return { vacant: current, dist };
                    return best;
                }, undefined as { vacant: VacantWithCoords; dist: number } | undefined);

                if (nearest && mapRef.current) {
                    mapRef.current.flyTo([nearest.vacant.latitude, nearest.vacant.longitude], DEFAULT_ZOOM + 2);
                    toast.dismiss();
                    toast.success(
                        `Vacante más cercana: ${nearest.vacant.area} (${(nearest.dist / 1000).toFixed(2)} km)`
                    );
                } else {
                    toast.dismiss();
                    toast.error("No se pudo encontrar la vacante más cercana.");
                }
            },
            (err) => {
                toast.dismiss();
                toast.error(`Error al obtener tu ubicación: ${err.message || "Desconocido"}`);
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    };

    const resetView = () => {
        if (mapRef.current) mapRef.current.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
        setAreaFilter("");
        fetchVacants();
        toast.success("Vista reiniciada.");
    };

    if (loading) return <div>Cargando mapa...</div>;
    if (error) return <div>Error: {error}</div>;

    const initialCenter: [number, number] = (() => {
        const first = vacants.find(
            (v): v is VacantWithCoords => v.latitude !== null && v.longitude !== null
        );
        return first
            ? [first.latitude, first.longitude]
            : DEFAULT_CENTER;
    })();

    return (
        <div className="flex flex-col items-center p-4">
            <div className="flex flex-wrap gap-2 mb-4">
                <input
                    value={areaFilter}
                    onChange={e => setAreaFilter(e.target.value)}
                    placeholder="Filtrar por área"
                    className="border p-2 rounded"
                />
                <button
                    onClick={() => fetchVacants(areaFilter)}
                    className="bg-green-500 text-white px-4 py-2 rounded"
                >
                    Aplicar filtro
                </button>
                <button
                    onClick={centerOnMyLocation}
                    className="bg-blue-500 text-white px-4 py-2 rounded"
                >
                    Mi ubicación
                </button>
                <button
                    onClick={findNearestVacant}
                    className="bg-purple-500 text-white px-4 py-2 rounded"
                >
                    Más cercana
                </button>
                <button
                    onClick={resetView}
                    className="bg-gray-500 text-white px-4 py-2 rounded"
                >
                    Reiniciar
                </button>
            </div>

            <div style={{ height: "600px", width: "100%" }}>

                <MapContainer
                    center={initialCenter}
                    zoom={DEFAULT_ZOOM}
                    scrollWheelZoom
                    style={{ height: "600px", width: "100%" }}

                >
                    <MapRefSetter mapRef={mapRef} />

                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    />
                    {vacants
                        .filter(v => v.latitude && v.longitude)
                        .map(v => (
                            <Marker
                                key={v.id}
                                position={[v.latitude!, v.longitude!]}
                                icon={customIcon}
                            >
                                <Popup>
                                    <h3 className="font-bold">{v.area}</h3>
                                    <p>{v.description}</p>
                                    <p><strong>Modalidad:</strong> {v.modality}</p>
                                    <p><strong>Ubicación:</strong> {v.location}</p>
                                    <p><strong>Etiquetas:</strong> {v.tags.join(", ")}</p>
                                    <a
                                        href={`/vacant/${v.id}`}
                                        className="text-blue-600 underline"
                                    >
                                        Ver detalles
                                    </a>
                                </Popup>
                            </Marker>
                        ))}
                </MapContainer>
            </div>
        </div >
    );
};

export default VacanciesMap;
