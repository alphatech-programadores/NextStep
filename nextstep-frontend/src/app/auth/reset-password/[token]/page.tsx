// src/app/auth/reset-password/[token]/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import FormInput from '@/components/Input'; // Asumiendo tu componente FormInput
import toast from 'react-hot-toast'; // Para notificaciones

// Importa el módulo de estilos específico para esta página
import styles from './reset-password.module.scss'; // Asegúrate de que esta ruta sea correcta
import axiosInstance from '@/services/axiosConfig';

export default function ResetPasswordPage() {
    const router = useRouter();
    const params = useParams();
    const token = params.token as string; // El token de la URL
    const [newPassword, setNewPassword] = useState('');
    const [confirmNewPassword, setConfirmNewPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [initialCheckComplete, setInitialCheckComplete] = useState(false); // Para el check inicial del token

    useEffect(() => {
        // Opcional: Verificar la validez básica del token al cargar la página
        // Esto es una mejora UX. La validación real ocurre en el backend.
        if (!token) {
            toast.error("El enlace de restablecimiento de contraseña es inválido o no existe.");
            router.push("/auth/forgot-password"); // Redirigir a solicitar nuevo enlace
        }
        setInitialCheckComplete(true);
    }, [token, router]);

    const handleReset = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!initialCheckComplete) return;

        if (!token) {
            toast.error("Error: Token no encontrado en la URL.");
            return;
        }

        if (!newPassword || !confirmNewPassword) {
            toast.error("Por favor, rellena ambos campos de contraseña.");
            return;
        }

        if (newPassword.length < 6) {
            toast.error("La contraseña debe tener al menos 6 caracteres.");
            return;
        }

        if (newPassword !== confirmNewPassword) {
            toast.error("Las contraseñas no coinciden. Por favor, inténtalo de nuevo.");
            return;
        }

        setLoading(true);

        try {
            // --- CORRECCIÓN CLAVE AQUÍ: Añadir '/auth' al path ---
            const response = await axiosInstance.post(`/auth/reset-password/${token}`, {
                new_password: newPassword, // Asegúrate de que el campo sea 'new_password' como espera el backend
            });

            toast.success(response.data.message || "Contraseña restablecida correctamente. ✅ Redirigiendo al login...");
            setTimeout(() => router.push("/auth/login"), 3000);

        } catch (error: any) {
            console.error("Error al restablecer la contraseña:", error);
            const errorMessage = error.response?.data?.error
                ? error.response.data.error
                : "Error al restablecer la contraseña. El enlace podría ser inválido o haber expirado.";

            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    // No renderizar nada hasta que se haya completado la verificación inicial del token
    if (!initialCheckComplete) {
        return (
            <div className={styles.container}>
                <div className={styles.card}>
                    <h1 className={styles.title}>Cargando...</h1>
                    <p className={styles.message}>Verificando el enlace de restablecimiento.</p>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <h1 className={styles.title}>Restablecer Contraseña</h1>
                <p className={styles.description}>Ingresa tu nueva contraseña a continuación.</p>
                <form onSubmit={handleReset} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <FormInput
                            label="Nueva Contraseña"
                            name="newPassword"
                            type="password"
                            placeholder="Mínimo 6 caracteres"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            required
                        />
                    </div>
                    <div className={styles.inputGroup}>
                        <FormInput
                            label="Confirmar Nueva Contraseña"
                            name="confirmNewPassword"
                            type="password"
                            placeholder="Repite tu nueva contraseña"
                            value={confirmNewPassword}
                            onChange={(e) => setConfirmNewPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={loading}
                    >
                        {loading ? 'Restableciendo...' : 'Cambiar Contraseña'}
                    </button>

                    {/* Puedes añadir un enlace para volver a la página de login si lo desean */}
                    <p className={styles.loginLink}>
                        <a href="/auth/login">Volver al inicio de sesión</a>
                    </p>
                </form>
            </div>
        </div>
    );
}