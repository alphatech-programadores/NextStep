// src/components/Navbar/Navbar.tsx

'use client'; // Necesario para usar hooks y la interacción del cliente

import React, { useState, useRef } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext'; // ¡Importa el hook de autenticación!
import styles from './navbar.module.scss'; // Módulo de estilos para el Navbar
import { useOnClickOutside } from '@/hooks/useOnClickOutside'; // Importa el nuevo hook

export default function Navbar() {
    const { user, loadingUser, logout } = useAuth();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    // --- CORRECCIÓN 1 ---
    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    // No es necesario un toggle para el dropdown si usamos el hook, pero lo dejamos por si acaso
    const dropdownRef = useRef<HTMLDivElement>(null);

    // --- CORRECIÓN 2 ---
    useOnClickOutside(dropdownRef as React.RefObject<HTMLElement>, () => setIsDropdownOpen(false));

    if (loadingUser) {
        // Puedes mostrar un skeleton o nada mientras se carga la sesión del usuario
        return (
            <nav className={styles.navbar}>
                <div className={styles.brand}>NextStep</div>
                {/* Opcional: Un spinner de carga aquí */}
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

            {/* --- PASO 2.1: BOTÓN HAMBURGUESA --- */}
            {/* Este botón solo será visible en móviles gracias al SCSS */}
            <button className={styles.hamburger} onClick={toggleMenu} aria-label="Toggle menu">
                {/* Un ícono simple de hamburguesa/cierre. Puedes usar una librería de íconos si prefieres. */}
                {isMenuOpen ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                )}
            </button>

            {/* --- PASO 2.2: ENLACES CON CLASE CONDICIONAL --- */}
            {/* Añadimos la clase 'menuOpen' cuando el estado es true */}
            <div className={`${styles.navLinks} ${isMenuOpen ? styles.menuOpen : ''}`}>
                {user ? (
                    // Navbar para usuario AUTENTICADO
                    <>
                        <Link href="/dashboard" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>Dashboard</Link>
                        {/* El link a Vacantes puede quedar fuera si es una acción principal */}
                        <Link href="/vacancies" className={styles.navLink} onClick={() => setIsMenuOpen(false)}>Explorar Prácticas</Link>

                        {/* --- PASO 2: CONTENEDOR DEL MENÚ DE USUARIO --- */}
                        <div className={styles.userMenu} ref={dropdownRef}>
                            {/* El botón que abre/cierra el dropdown */}
                            <button onClick={() => setIsDropdownOpen(!isDropdownOpen)} className={styles.userMenuButton}>
                                <span>Hola, {user.name}</span>
                                {/* Ícono de flecha hacia abajo */}
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
                            </button>

                            {/* El menú desplegable, se muestra solo si isDropdownOpen es true */}
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

                                    {/* Separador visual */}
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


