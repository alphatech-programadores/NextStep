// src/app/auth/confirm/[token]/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axiosInstance from '@/services/axiosConfig';
import toast from 'react-hot-toast';
import styles from './confirm.module.scss'; // Tu módulo SCSS
import FormInput from '@/components/Input'; // Asegúrate de tener este componente
import Link from "next/link"

export default function ConfirmEmailPage() {
    const router = useRouter();
    const params = useParams();

    const token = params.token; // Obtener el token de la URL


    // Estados para el flujo de confirmación automática por token
    const [isConfirmingByToken, setIsConfirmingByToken] = useState(true);
    const [tokenConfirmationStatus, setTokenConfirmationStatus] = useState<'loading' | 'success' | 'error' | null>(null);

    // Estados para el flujo de confirmación manual por email y código
    const [showManualForm, setShowManualForm] = useState(false);
    const [manualEmail, setManualEmail] = useState('');
    const [manualCode, setManualCode] = useState('');
    const [isConfirmingManually, setIsConfirmingManually] = useState(false);
    const [manualConfirmationMessage, setManualConfirmationMessage] = useState('');


    // Efecto para intentar la confirmación automática por token
    useEffect(() => {
        const confirmWithToken = async () => {
            // No necesitas router.isReady aquí en el App Router
            if (!token || typeof token !== 'string') {
                // No hay token en la URL, mostrar el formulario manual
                setIsConfirmingByToken(false);
                setShowManualForm(true);
                return;
            }

            setTokenConfirmationStatus('loading');
            try {
                const response = await axiosInstance.get(`/auth/confirm/${token}`);
                setTokenConfirmationStatus('success');
                setManualConfirmationMessage(response.data.message || 'Correo confirmado exitosamente.');
                toast.success(response.data.message || '¡Tu correo ha sido confirmado! ✅');
                // Redirigir a login después de un breve delay
                setTimeout(() => {
                    router.push('/auth/login?confirmed=true');
                }, 3000);
            } catch (error: any) {
                setTokenConfirmationStatus('error');
                const errorMessage = error.response?.data?.error || "Error al confirmar tu correo.";
                setManualConfirmationMessage(errorMessage); // Mostrar el error en la UI
                toast.error(errorMessage);
                // Si falla la confirmación por token, mostrar el formulario manual
                setShowManualForm(true);
            } finally {
                setIsConfirmingByToken(false);
            }
        };

        // Simplemente llama a la función de confirmación sin la condición router.isReady
        confirmWithToken();
    }, [token, router]); // La dependencia `token` ya es suficiente para re-ejecutar cuando el token esté disponible.


    // Manejador para el envío del formulario de confirmación manual
    const handleManualConfirmationSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsConfirmingManually(true);
        setManualConfirmationMessage(''); // Limpiar mensajes previos

        try {
            const response = await axiosInstance.post('/auth/confirm', { // Usar la ruta POST
                email: manualEmail,
                code: manualCode.toUpperCase(), // Convertir a mayúsculas para coincidir con el backend
            });
            setManualConfirmationMessage(response.data.message || 'Correo confirmado exitosamente.');
            toast.success(response.data.message || '¡Tu correo ha sido confirmado! ✅');
            // Redirigir a login después de un breve delay
            setTimeout(() => {
                router.push('/auth/login?confirmed=true');
            }, 3000);
        } catch (error: any) {
            const errorMessage = error.response?.data?.error || "Error al confirmar tu correo con el código.";
            setManualConfirmationMessage(errorMessage);
            toast.error(errorMessage);
        } finally {
            setIsConfirmingManually(false);
        }
    };


    return (
        <div className={styles.confirmPage}>
            <div className={styles.card}>
                <h1 className={styles.title}>Confirmar Correo Electrónico</h1>

                {/* Mensajes de estado para la confirmación automática por token */}
                {isConfirmingByToken && tokenConfirmationStatus === 'loading' && (
                    <p className={styles.statusMessage}>Confirmando tu correo... por favor espera. ✨</p>
                )}
                {tokenConfirmationStatus === 'success' && (
                    <p className={`${styles.statusMessage} ${styles.success}`}>
                        ¡Correo confirmado exitosamente! Serás redirigido en breve.
                        <br />{manualConfirmationMessage}
                    </p>
                )}
                {tokenConfirmationStatus === 'error' && (
                    <p className={`${styles.statusMessage} ${styles.error}`}>
                        {manualConfirmationMessage}
                    </p>
                )}

                {/* Formulario de confirmación manual (mostrado si no hay token o la confirmación automática falla) */}
                {showManualForm && (
                    <div className={styles.manualConfirmationSection}>
                        <p className={styles.instructionText}>
                            Si tu enlace expiró o no funciona, puedes confirmar tu cuenta ingresando tu email y el código recibido.
                        </p>
                        <form onSubmit={handleManualConfirmationSubmit} className={styles.manualForm}>
                            <FormInput
                                label="Correo Electrónico"
                                name="email"
                                type="email"
                                value={manualEmail}
                                onChange={(e) => setManualEmail(e.target.value)}
                                required
                                placeholder="tu@ejemplo.com"
                            />
                            <FormInput
                                label="Código de Confirmación"
                                name="code"
                                type="text"
                                value={manualCode}
                                onChange={(e) => setManualCode(e.target.value)}
                                required
                                placeholder="EJ: ABC123"
                                maxLength={6}
                            />
                            <button type="submit" className={styles.submitButton} disabled={isConfirmingManually}>
                                {isConfirmingManually ? 'Confirmando...' : 'Confirmar Cuenta'}
                            </button>
                        </form>
                        {manualConfirmationMessage && tokenConfirmationStatus !== 'success' && (
                            <p className={`${styles.statusMessage} ${tokenConfirmationStatus === 'error' ? styles.error : ''}`}>
                                {manualConfirmationMessage}
                            </p>
                        )}
                    </div>
                )}

                <Link href="/auth/login" className={styles.loginLink}>
                    Ir a Iniciar Sesión
                </Link>
            </div>
        </div>
    );
}