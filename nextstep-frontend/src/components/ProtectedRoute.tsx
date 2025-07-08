// src/components/ProtectedRoute.tsx
'use client';

import { useEffect, useRef } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation'; // ¡Asegúrate de importar useSearchParams!
import { useAuth } from '@/context/AuthContext';
import toast from 'react-hot-toast';

interface ProtectedRouteProps {
    children: React.ReactNode;
    allowedRoles?: string[];
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
    const { user, loadingUser } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams(); // Hook para leer los parámetros de búsqueda (query params)
    const toastDisplayedRef = useRef(false);

    useEffect(() => {
        // Reiniciar el ref si la ruta protegida cambia para permitir un nuevo toast en otra página
        toastDisplayedRef.current = false;
    }, [pathname]);


    useEffect(() => {
        // Si aún estamos cargando la información del usuario, no hagas nada todavía.
        if (loadingUser) {
            return;
        }

        // --- ¡CAMBIO CLAVE AQUÍ! ---
        // Leer el query parameter 'fromLogout'
        const fromLogout = searchParams.get('fromLogout') === 'true';

        // Si el usuario NO está autenticado después de cargar
        if (!user) {
            // Solo muestra el toast si NO venimos de un logout intencional
            // Y si no se ha mostrado un toast ya en esta carga de página.
            if (!fromLogout && !toastDisplayedRef.current) {
                toast.error("Por favor, inicia sesión para acceder a esta página.");
                toastDisplayedRef.current = true; // Marca que el toast ya se mostró
            }
            // Realiza la redirección
            router.push('/auth/login');
            return;
        }

        // Si se especifican roles y el rol del usuario no está permitido
        if (allowedRoles && !allowedRoles.includes(user.role)) {
            if (!toastDisplayedRef.current) { // Asegura que solo se muestre una vez
                toast.error("No tienes permisos para acceder a esta página.");
                toastDisplayedRef.current = true;
            }
            router.push('/dashboard'); // O a una página de "acceso denegado"
            return;
        }

    }, [user, loadingUser, router, allowedRoles, searchParams]); // Añadir searchParams a las dependencias

    // Mientras se carga el usuario...
    if (loadingUser) {
        return <div>Cargando contenido seguro...</div>;
    }

    // Una vez que el usuario ha cargado y está autenticado y autorizado
    if (user && (!allowedRoles || allowedRoles.includes(user.role))) {
        return <>{children}</>;
    }

    // Si el usuario no está autenticado o no tiene el rol correcto, no renderices los hijos
    // El useEffect ya debería haber disparado la redirección
    return null;
}