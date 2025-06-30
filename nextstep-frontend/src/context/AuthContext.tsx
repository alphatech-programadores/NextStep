// src/context/AuthContext.tsx

'use client'; // Necesario para usar Context y Hooks

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import toast from 'react-hot-toast';
import axiosInstance from '@/services/axiosConfig';


// Define la interfaz para el usuario (lo que esperarías de tu token/API)
interface User {
    email: string;
    name: string;
    role: 'student' | 'institution' | 'admin'; // Añade 'admin' si aplica
}

// Define la interfaz para el contexto
interface AuthContextType {
    user: User | null;
    loadingUser: boolean;
    login: (token: string, userData: User) => void;
    logout: () => void;
    // Opcional: una función para revalidar el usuario si su información cambia
    revalidateUser: () => Promise<void>;
}

// Crea el contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Proveedor del contexto
export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loadingUser, setLoadingUser] = useState(true); // Para saber si estamos cargando la sesión del usuario
    const router = useRouter();

    // Función para cargar el usuario desde el token (ej. al cargar la página)
    const loadUserFromToken = useCallback(async () => {
        setLoadingUser(true);
        try {
            const token = localStorage.getItem('access_token');
            if (token) {
                // Aquí podrías hacer una llamada a tu API de backend
                // para verificar la validez del token y obtener los detalles del usuario.
                // Por ejemplo, una ruta /api/auth/me que devuelve la info del usuario.
                const response = await axiosInstance.get('http://localhost:5000/api/profile/me', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setUser(response.data); // Asumiendo que tu API devuelve { user: { email, name, role } }
            } else {
                setUser(null);
            }
        } catch (error) {
            console.error("Error al cargar el usuario desde el token:", error);
            localStorage.removeItem('access_token'); // Limpiar token inválido
            setUser(null);
            // toast.error("Tu sesión ha expirado o es inválida. Por favor, inicia sesión de nuevo.");
        } finally {
            setLoadingUser(false);
        }
    }, []);

    useEffect(() => {
        loadUserFromToken();
    }, [loadUserFromToken]);

    const login = (token: string, userData: User) => {
        localStorage.setItem('access_token', token);
        setUser(userData);
        // Opcional: redirigir a dashboard si aún no estás allí
        // router.push('/dashboard');
    };

    const logout = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (token) {
                await axiosInstance.post('http://localhost:5000/api/auth/logout', {}, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                toast.success("Has cerrado sesión exitosamente.");
            }
        } catch (error) {
            console.error("Error al cerrar sesión en el backend:", error);
            toast.error("Hubo un problema al cerrar sesión completamente, pero tu sesión local ha sido terminada.");
        } finally {
            localStorage.removeItem('access_token');
            setUser(null);

            // --- ¡CAMBIO CLAVE AQUÍ! ---
            // Redirige directamente a la página de login usando un query parameter
            router.push('/auth/login?fromLogout=true'); // Pasa 'fromLogout=true' como query param
        }
    };


    // Función para revalidar el usuario, útil si su información cambia (ej. actualización de perfil)
    const revalidateUser = useCallback(async () => {
        await loadUserFromToken();
    }, [loadUserFromToken]);

    return (
        <AuthContext.Provider value={{ user, loadingUser, login, logout, revalidateUser }}>
            {children}
        </AuthContext.Provider>
    );
};


export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};