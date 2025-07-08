// src/app/vacants/map/page.tsx

"use client"; // ¡Esta directiva es ABSOLUTAMENTE NECESARIA aquí!

import dynamic from 'next/dynamic'; // Importa el cargador dinámico de Next.js
import React from 'react'; // Necesitas React para el componente de la página

// Importa los estilos CSS de Leaflet y tus estilos SCSS del mapa.
// Es mejor importarlos aquí directamente para que estén disponibles.
import 'leaflet/dist/leaflet.css';
import '../../../components/VacanciesMap/VacanciesMap.scss'; // Asegúrate de que esta ruta sea correcta

// ============================================================================
// ESTA ES LA PARTE CLAVE: Carga el componente VacanciesMap dinámicamente
// y le indica a Next.js que NO lo renderice en el servidor (ssr: false).
// Esto evita el error "window is not defined".
// ============================================================================
const DynamicVacanciesMap = dynamic(
  // La función de importación debe apuntar a la ruta EXACTA de tu componente VacanciesMap.
  // La ruta es relativa a la raíz del proyecto o a un alias configurado.
  // Si tu componente está en src/components/VacanciesMap/VacanciesMap.tsx
  // y tu página está en src/app/vacants/map/page.tsx, esta ruta es correcta.
  () => import('../../../components/VacanciesMap/VacanciesMap'),
  {
    ssr: false, // ¡Muy importante! Deshabilita el Server-Side Rendering para este componente.
    loading: () => <p>Cargando el mapa de vacantes...</p>, // Muestra un mensaje mientras el mapa carga.
  }
);

// Este es el componente principal de tu página /vacants/map
const VacantsMapPage: React.FC = () => {
  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        Explora Vacantes en el Mapa
      </h1>
      {/* Aquí es donde se renderiza tu componente de mapa cargado dinámicamente */}
      <DynamicVacanciesMap />
      <p style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
        Haz clic en los marcadores para ver los detalles de la vacante.
      </p>
    </div>
  );
};

export default VacantsMapPage;
