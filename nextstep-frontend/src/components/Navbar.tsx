// src/components/Navbar/Navbar.tsx

'use client'; // Necesario para usar hooks y la interacción del cliente

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext'; // ¡Importa el hook de autenticación!
import styles from './navbar.module.scss'; // Módulo de estilos para el Navbar

export default function Navbar() {
    const { user, loadingUser, logout } = useAuth(); // Obtén el estado del usuario y la función de logout

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
            <div className={styles.navLinks}>
                {user ? (
                    // Navbar para usuario AUTENTICADO
                    <>
                        <Link href="/dashboard" className={styles.navLink}>Dashboard</Link>
                        {user.role === 'student' && (
                            <Link href="/student/profile" className={styles.navLink}>Mi Perfil</Link>
                        )}
                        {user.role === 'institution' && (
                            <Link href="/institution/vacancies" className={styles.navLink}>Mis Vacantes</Link>
                        )}
                        {user.role === 'admin' && ( // Si tienes rol de admin
                            <Link href="/admin" className={styles.navLink}>Panel Admin</Link>
                        )}
                        <span className={styles.welcomeText}>Hola, {user.name}</span>
                        <button onClick={logout} className={styles.logoutButton}>Cerrar Sesión</button>
                    </>
                ) : (
                    // Navbar para usuario NO AUTENTICADO
                    <>
                        <Link href="/" className={styles.navLink}>Inicio</Link>
                        <Link href="/auth/login" className={styles.navLink}>Iniciar Sesión</Link>
                        <Link href="/auth/register" className={`${styles.navLink} ${styles.registerButton}`}>Registrarse</Link>
                    </>
                )}
            </div>
        </nav>
    );
}