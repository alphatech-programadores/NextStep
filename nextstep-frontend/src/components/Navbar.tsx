// src/components/Navbar/Navbar.tsx

'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import styles from './navbar.module.scss';
import { useOnClickOutside } from '@/hooks/useOnClickOutside';
import axiosInstance from '@/services/axiosConfig';
import { logout as logoutApi } from '@/services/authService';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';

export default function Navbar() {
    const router = useRouter();
    const { user, loadingUser, logout } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [unreadNotificationsCount, setUnreadNotificationsCount] = useState(0);

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    const dropdownRef = useRef<HTMLDivElement>(null);

    useOnClickOutside(dropdownRef as React.RefObject<HTMLElement>, () => setIsDropdownOpen(false));

    const fetchUnreadNotificationsCount = useCallback(async () => {
        if (!user || user.role !== 'student') {
            setUnreadNotificationsCount(0);
            return;
        }
        try {
            const response = await axiosInstance.get('/notifications/unread_count');
            setUnreadNotificationsCount(response.data.unread_count);
        } catch (error) {
            console.error("Error fetching unread notifications count:", error);
        }
    }, [user]);

    useEffect(() => {
        if (user && user.role === 'student') {
            fetchUnreadNotificationsCount();

            const intervalId = setInterval(fetchUnreadNotificationsCount, 30000);
            return () => clearInterval(intervalId);
        } else {
            setUnreadNotificationsCount(0);
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
                        {/* DASHBOARD según el rol */}
                        {user.role === 'institution' ? (
                            <Link href="/institution" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                                Dashboard
                            </Link>
                        ) : (
                            <Link href="/dashboard" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                                Dashboard
                            </Link>
                        )}

                        {/* Opciones Institución */}
                        {user.role === 'institution' && (
                            <>
                                <Link href="/institution/vacancies" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                                    Gestionar Vacantes
                                </Link>
                                <Link href="/institution/vacancies/new" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                                    Crear Vacante
                                </Link>
                            </>
                        )}

                        {/* Opciones Estudiante */}
                        {user.role === 'student' && (
                            <>
                                <Link href="/vacancies" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                                    Explorar Prácticas
                                </Link>
                                <Link href="/vacants/map" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                                    Mapa de Vacantes
                                </Link>
                                <Link href="/student/saved-vacancies" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                                    Mis Guardados
                                </Link>
                                <Link href="/notifications" className={styles.notificationsLink} onClick={() => setIsMenuOpen(false)}>
                                    Notificaciones
                                    {unreadNotificationsCount > 0 && (
                                        <span className={styles.notificationsBadge}>{unreadNotificationsCount}</span>
                                    )}
                                </Link>
                            </>
                        )}

                        {/* Menú desplegable de usuario */}
                        <div className={styles.userMenu} ref={dropdownRef}>
                            <button
                                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                className={styles.userMenuButton}
                            >
                                {user.profile_picture_url ? (
                                    <img
                                        src={user.profile_picture_url}
                                        alt="Foto de perfil"
                                        className={styles.profilePic}
                                    />
                                ) : (
                                    <span className={styles.profileInitials}>
                                        {user.name.charAt(0).toUpperCase()}
                                    </span>
                                )}
                                <span>Hola, {user.name}</span>
                                <svg
                                    width="16"
                                    height="16"
                                    viewBox="0 0 16 16"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <path
                                        d="M4 6L8 10L12 6"
                                        stroke="currentColor"
                                        strokeWidth="1.5"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                    />
                                </svg>
                            </button>

                            {isDropdownOpen && (
                                <div className={styles.dropdownMenu}>
                                    {user.role === 'student' && (
                                        <>
                                            <Link
                                                href="/student/profile"
                                                className={styles.dropdownLink}
                                                onClick={() => setIsDropdownOpen(false)}
                                            >
                                                Mi Perfil
                                            </Link>
                                            <Link
                                                href="/applications"
                                                className={styles.dropdownLink}
                                                onClick={() => setIsDropdownOpen(false)}
                                            >
                                                Mis Postulaciones
                                            </Link>
                                        </>
                                    )}

                                    {user.role === 'institution' && (
                                        <Link
                                            href="/institution/profile"
                                            className={styles.dropdownLink}
                                            onClick={() => setIsDropdownOpen(false)}
                                        >
                                            Mi Perfil de Institución
                                        </Link>
                                    )}

                                    <div className={styles.dropdownDivider} />

                                    <button
                                        onClick={async () => {
                                            await logout();
                                            setIsDropdownOpen(false);
                                        }}
                                        className={styles.dropdownLink}
                                    >
                                        Cerrar Sesión
                                    </button>
                                </div>
                            )}
                        </div>
                    </>
                ) : (
                    <>
                        <Link href="/" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                            Inicio
                        </Link>
                        <Link href="/auth/login" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>
                            Iniciar Sesión
                        </Link>
                        <Link
                            href="/auth/register"
                            className={`${styles.navLink} ${styles.registerButton}`}
                            onClick={() => setIsMenuOpen(false)}
                        >
                            Registrarse
                        </Link>
                    </>
                )}
            </div>

        </nav>
    );
}