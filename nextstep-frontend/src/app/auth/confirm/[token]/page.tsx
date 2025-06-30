// src/app/auth/confirm/[token]/page.tsx

'use client'; // Necesario para usar hooks de React como useState, useRouter, useParams

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axios from 'axios';
import toast from 'react-hot-toast'; // Para notificaciones al usuario

// Importa tu módulo de estilos para esta página
import styles from './confirm.module.scss'; // Asegúrate de que esta ruta sea correcta
import axiosInstance from '@/services/axiosConfig';

export default function ConfirmEmailPage() {
    const router = useRouter();
    const params = useParams();
    const token = params.token as string; // El token viene de la URL dinámica
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [message, setMessage] = useState('');

    useEffect(() => {
        // Ejecuta la lógica de confirmación una vez que el componente se monta
        const confirmEmail = async () => {
            if (!token) {
                setStatus('error');
                setMessage('Error: El token de confirmación no fue encontrado en la URL.');
                toast.error('Token de confirmación no encontrado. 🙁');
                return;
            }

            try {
                const response = await axiosInstance.get(`http://localhost:5000/api/auth/confirm/${token}`);
                setStatus('success');
                setMessage(response.data.message || 'Tu correo ha sido confirmado exitosamente. Redirigiendo al login...');
                toast.success(response.data.message || '¡Correo confirmado! ✅');

                // Redirige al usuario a la página de login después de un breve retraso
                setTimeout(() => router.push("/auth/login"), 3000);

            } catch (error: any) {
                console.error("Error al confirmar correo:", error);
                setStatus('error');
                const errorMessage = error.response?.data?.error || "Error al confirmar tu correo. Por favor, intenta de nuevo o solicita un nuevo enlace.";
                setMessage(errorMessage);
                toast.error(errorMessage);

                // Opcional: Redirigir al usuario a una página para solicitar un nuevo enlace de confirmación si hay un error
                // setTimeout(() => router.push("/auth/resend-confirmation"), 5000);
            }
        };

        confirmEmail();
    }, [token, router]); // Dependencias: el token y el objeto router

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                {status === 'loading' && (
                    <>
                        <h1 className={styles.title}>Confirmando tu correo...</h1>
                        <p className={styles.message}>Por favor, espera un momento. Esto puede tardar unos segundos.</p>
                        {/* Puedes añadir un spinner o animación de carga aquí */}
                    </>
                )}
                {status === 'success' && (
                    <>
                        <h1 className={styles.title}>¡Correo Confirmado!</h1>
                        <p className={styles.message}>{message}</p>
                        <button onClick={() => router.push('/auth/login')} className={styles.actionButton}>
                            Ir a Iniciar Sesión
                        </button>
                    </>
                )}
                {status === 'error' && (
                    <>
                        <h1 className={styles.title}>Error de Confirmación</h1>
                        <p className={`${styles.message} ${styles.errorMessage}`}>{message}</p>
                        <button onClick={() => router.push('/auth/register')} className={styles.actionButton}>
                            Regresar a Registrarme
                        </button>
                        {/* O un botón para solicitar reenviar el correo de confirmación */}
                        {/* <button onClick={() => router.push('/auth/resend-confirmation')} className={styles.actionButton}>
                            Solicitar nuevo enlace
                        </button> */}
                    </>
                )}
            </div>
        </div>
    );
}