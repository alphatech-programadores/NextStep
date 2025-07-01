// src/components/Navbar/Navbar.tsx

'use client'; // Necesario para usar hooks y la interacción del cliente

import React, { useState, useRef, useEffect, useCallback } from 'react'; // Importar useEffect y useCallback
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import styles from './navbar.module.scss';
import { useOnClickOutside } from '@/hooks/useOnClickOutside';
import axiosInstance from '@/services/axiosConfig'; // Importa axiosInstance

export default function Navbar() {
    const { user, loadingUser, logout } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [unreadNotificationsCount, setUnreadNotificationsCount] = useState(0); // Inicializar en 0

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const dropdownRef = useRef<HTMLDivElement>(null);

    useOnClickOutside(dropdownRef as React.RefObject<HTMLElement>, () => setIsDropdownOpen(false));

    // NUEVA FUNCIÓN PARA OBTENER EL CONTEO DE NOTIFICACIONES NO LEÍDAS
    const fetchUnreadNotificationsCount = useCallback(async () => {
        if (!user || user.role !== 'student') { // Solo estudiantes tienen notificaciones
            setUnreadNotificationsCount(0);
            return;
        }
        try {
            const response = await axiosInstance.get('/notifications/unread_count'); // Llama al endpoint de backend
            setUnreadNotificationsCount(response.data.unread_count);
        } catch (error) {
            console.error("Error fetching unread notifications count:", error);
            // Manejar error, quizás resetear el contador si el token es inválido
            // Si el error es 401, el interceptor de axiosInstance y AuthContext ya deberían manejar el logout
        }
    }, [user]);

    useEffect(() => {
        // Cargar el conteo inicial cuando el usuario se carga o cambia
        if (user && user.role === 'student') {
            fetchUnreadNotificationsCount();

            // Configurar polling para actualizar el conteo periódicamente (ej. cada 30 segundos)
            const intervalId = setInterval(fetchUnreadNotificationsCount, 30000); // 30 segundos

            // Limpiar el intervalo cuando el componente se desmonte o el usuario cambie
            return () => clearInterval(intervalId);
        } else {
            setUnreadNotificationsCount(0); // Resetear si no hay usuario o no es estudiante
        }
    }, [user, fetchUnreadNotificationsCount]);


    if (loadingUser) {
        return (
            <nav className={styles.navbar}>
                <div className={styles.brand}>NextStep</div>
                <div className={styles.navLinks}>Cargando...</div>
            </nav>
        );
    }

    return (
        <nav className={styles.navbar}>
            <div className={styles.brand}>
                <Link href="/" className={styles.brandLink}>
                    NextStep
                </Link>
            </div>

            <button className={styles.hamburger} onClick={toggleMenu} aria-label="Toggle menu">
                {isMenuOpen ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                )}
            </button>

            <div className={`${styles.navLinks} ${isMenuOpen ? styles.menuOpen : ''}`}>
                {user ? (
                    <>
                        <Link href="/dashboard" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>Dashboard</Link>
                        <Link href="/vacancies" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>Explorar Prácticas</Link>

                        {/* Ícono de Notificaciones para Estudiantes (con conteo real) */}
                        {user.role === 'student' && (
                            <Link href="/notifications" className={styles.notificationsLink} onClick={() => setIsMenuOpen(false)}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                                {unreadNotificationsCount > 0 && (
                                    <span className={styles.notificationsBadge}>{unreadNotificationsCount}</span>
                                )}
                            </Link>
                        )}

                        <div className={styles.userMenu} ref={dropdownRef}>
                            <button onClick={() => setIsDropdownOpen(!isDropdownOpen)} className={styles.userMenuButton}>
                                <span>Hola, {user.name}</span>
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
                            </button>

                            {isDropdownOpen && (
                                <div className={styles.dropdownMenu}>
                                    {user.role === 'student' && (
                                        <Link href="/student/profile" className={styles.dropdownLink} onClick={() => setIsDropdownOpen(false)}>Mi Perfil</Link>
                                    )}
                                    {user.role === 'student' && (
                                        <Link href="/applications" className={styles.dropdownLink} onClick={() => setIsDropdownOpen(false)}>Mis Postulaciones</Link>
                                    )}
                                    {user.role === 'institution' && (
                                        <Link href="/institution/vacancies" className={styles.dropdownLink} onClick={() => setIsDropdownOpen(false)}>Gestionar Vacantes</Link>
                                    )}

                                    <div className={styles.dropdownDivider} />

                                    <button onClick={() => { logout(); setIsDropdownOpen(false); }} className={styles.dropdownLink}>
                                        Cerrar Sesión
                                    </button>
                                </div>
                            )}
                        </div>
                    </>
                ) : (
                    // Navbar para usuario NO AUTENTICADO
                    <>
                        <Link href="/" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>Inicio</Link>
                        <Link href="/auth/login" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>Iniciar Sesión</Link>
                        <Link href="/auth/register" className={`${styles.navLink} ${styles.registerButton}`} onClick={() => setIsMenuOpen(false)}>Registrarse</Link>
                    </>
                )}
            </div>
        </nav>
    );
}