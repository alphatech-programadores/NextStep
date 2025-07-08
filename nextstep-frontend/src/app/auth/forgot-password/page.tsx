// src/app/auth/forgot-password/page.tsx

'use client';

import { useState } from 'react';
import toast from 'react-hot-toast'; // Para notificaciones
import FormInput from '@/components/Input'; // Asumiendo tu componente FormInput
import { useRouter } from 'next/navigation'; // Para posible redirección

// Importa el módulo de estilos específico para esta página
import styles from './forgot-password.module.scss'; // Asegúrate de que esta ruta sea correcta
import axiosInstance from '@/services/axiosConfig';

export default function ForgotPasswordPage() {
    const router = useRouter(); // Lo añadimos por si queremos añadir una redirección
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false); // Estado para manejar el loading del botón

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true); // Activar estado de carga

        try {
            const response = await axiosInstance.post('http://localhost:5000/api/auth/forgot-password', { email });

            // El backend ya devuelve un mensaje genérico por seguridad, lo cual es bueno.
            // Lo mostramos directamente.
            toast.success(response.data.message || 'Instrucciones enviadas si el correo está registrado. ✅');
            // Opcional: Redirigir al usuario a una página de "Revisa tu email"
            // router.push("/auth/check-email");
        } catch (error: any) {
            console.error("Error al solicitar restablecimiento de contraseña:", error);
            // El backend también envía un mensaje de éxito genérico incluso si el correo no existe por seguridad.
            // Pero si hay un error real de la API (ej. servidor caído, error 500), lo capturamos.
            const errorMessage = error.response?.data?.error
                ? error.response.data.error
                : "Ocurrió un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.";

            toast.error(errorMessage);
        } finally {
            setLoading(false); // Desactivar estado de carga
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <h1 className={styles.title}>¿Olvidaste tu contraseña?</h1>
                <p className={styles.description}>
                    Ingresa tu correo electrónico y te enviaremos un enlace para restablecerla.
                </p>
                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <FormInput
                            label="Correo electrónico"
                            name="email"
                            type="email"
                            placeholder="domain@ejemplo.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={loading} // Deshabilitar el botón mientras carga
                    >
                        {loading ? 'Enviando...' : 'Enviar enlace de recuperación'}
                    </button>

                    {/* Enlace para volver al login */}
                    <p className={styles.loginLink}>
                        <a href="/auth/login">Volver al inicio de sesión</a>
                    </p>
                </form>
            </div>
        </div>
    );
}