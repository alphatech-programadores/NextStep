import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect, useState } from 'react';
import axios from 'axios';

const VacantsMap = () => {
    const [vacants, setVacants] = useState([]);

    useEffect(() => {
        axios.get("/api/vacants/map", {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`
            }
        })
            .then(res => setVacants(res.data))
            .catch(err => console.error(err));
    }, []);

    return (
        <MapContainer center={[19.4326, -99.1332]} zoom={5} style={{ height: "600px", width: "100%" }}>
            <TileLayer
                attribution='&copy; OpenStreetMap'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {vacants.map(v => (
                <Marker key={v.id} position={[v.latitude, v.longitude]}>
                    <Popup>
                        <strong>{v.area}</strong><br />
                        {v.description.slice(0, 100)}...<br />
                        <a href={`/vacants/${v.id}`}>Ver vacante</a>
                    </Popup>
                </Marker>
            ))}
        </MapContainer>
    );
};

export default VacantsMap;
