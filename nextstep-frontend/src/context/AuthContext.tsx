// src/context/AuthContext.tsx
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import axiosInstance from '@/services/axiosConfig'; // Asegúrate de que esta ruta sea correcta
import toast from 'react-hot-toast';

// Interfaz para el objeto de usuario que se almacena en el contexto
interface User {
    email: string;
    name: string;
    role: 'student' | 'institution';
    profile_picture_url?: string; // NUEVO: Hacerlo opcional por si no todos los roles lo tienen o está vacío
}

// Interfaz para el tipo del contexto de autenticación
interface AuthContextType {
    user: User | null;
    loadingUser: boolean;
    login: (token: string) => void;
    logout: () => void;
    revalidateUser: () => Promise<void>; // Para refrescar la información del usuario
}

// Crea el contexto con un valor por defecto (puede ser null o un objeto con valores iniciales)
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loadingUser, setLoadingUser] = useState(true);
    const router = useRouter();

    const loadUserFromToken = useCallback(async () => {
        setLoadingUser(true);
        try {
            const token = localStorage.getItem('access_token');
            if (token) {
                // Hacer una llamada al endpoint de perfil para obtener todos los detalles del usuario
                const response = await axiosInstance.get('/profile/me');
                const userData = response.data; // Esta es la data combinada de User y StudentProfile/InstitutionProfile

                // Mapear los datos al objeto de usuario del contexto
                setUser({
                    email: userData.email,
                    name: userData.name,
                    role: userData.role,
                    profile_picture_url: userData.profile_picture_url || undefined, // NUEVO: Añadir URL de foto de perfil
                });
            } else {
                setUser(null);
            }
        } catch (error: any) {
            console.error("Error al cargar el usuario desde el token:", error);
            localStorage.removeItem('access_token'); // Limpiar token inválido
            setUser(null);
            toast.error(error.response?.data?.error || "Tu sesión ha expirado o es inválida. Por favor, inicia sesión de nuevo.");
            // Opcional: router.push('/auth/login'); // Redirigir a login si la sesión es inválida
        } finally {
            setLoadingUser(false);
        }
    }, []);

    // Se ejecuta una vez al montar el componente para cargar la sesión inicial
    useEffect(() => {
        loadUserFromToken();
    }, [loadUserFromToken]);

    // Función de login: guarda el token y carga la información del usuario
    const login = useCallback((token: string) => {
        localStorage.setItem('access_token', token); // 1. Guardar token
        loadUserFromToken(); // 2. Inmediatamente cargar datos del usuario con token válido
    }, [loadUserFromToken]);


    // Función de logout: limpia el token y redirige
    const logout = useCallback(async () => {
        try {
          await axiosInstance.post('/auth/logout'); // POST preferido
          toast.success("Has cerrado sesión exitosamente.");
        } catch (error: any) {
          if (error.response?.status === 401 && error.response.data?.message === "Token has been revoked") {
            // Token ya revocado: consideramos logout OK
            toast.success("Has cerrado sesión exitosamente.");
          } else {
            toast.error(error.response?.data?.error || "Error al cerrar sesión");
            console.error("Error al cerrar sesión en backend:", error);
          }
        } finally {
          localStorage.removeItem('access_token');
          setUser(null);
          router.push('/'); // Aquí rediriges al home después del logout
        }
      }, [router]);


    // revalidateUser para refrescar el usuario (ej. después de actualizar el perfil)
    const revalidateUser = useCallback(async () => {
        await loadUserFromToken();
    }, [loadUserFromToken]);


    const contextValue = {
        user,
        loadingUser,
        login,
        logout,
        revalidateUser,
    };

    return (
        <AuthContext.Provider value={contextValue}>
            {children}
        </AuthContext.Provider>
    );
};

// Hook personalizado para usar el contexto de autenticación
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};