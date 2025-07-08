// src/app/layout.tsx

import './globals.scss';
import { ReactNode } from 'react';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/context/AuthContext';
import Navbar from '@/components/Navbar'; // ¡Importa tu Navbar!
import "leaflet/dist/leaflet.css";


export const metadata = {
  title: 'NextStep',
  description: 'Plataforma de gestión de vacantes y postulaciones.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <AuthProvider>
          <Navbar /> {/* ¡Añade el Navbar aquí! */}
          {children}
          <Toaster position="top-center" reverseOrder={false} />
        </AuthProvider>
      </body>
    </html>
  );
}