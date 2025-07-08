// src/app/auth/login/page.tsx (o donde esté tu LoginPage.tsx)

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import FormInput from '@/components/Input'; // Asumiendo que Input.tsx es tu FormInput
import toast from 'react-hot-toast';


// ¡Importa tu módulo de estilos!
import styles from './login.module.scss'; // Asegúrate de que esta ruta sea correcta
import axiosInstance from '@/services/axiosConfig';

export default function LoginPage() {
    const router = useRouter();
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false); // Estado para manejar el loading del botón

    const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await axiosInstance.post("/auth/login", { email, password });
            const { access_token, user: userData } = response.data;

            login(access_token);
            toast.success("Inicio de sesión exitoso ✅");

            // --- Aquí decides a dónde redirigir ---
            if (userData.role === "institution") {
                router.push("/institution");
            } else {
                router.push("/dashboard");
            }

        } catch (error: any) {
            console.error("Error de login:", error);
            const errorMessage = error.response && error.response.data && error.response.data.error
                ? error.response.data.error
                : "Error al iniciar sesión. Por favor, inténtalo de nuevo.";

            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };
    return (
        <div className={styles.container}> {/* Contenedor principal para centrar el formulario */}
            <div className={styles.card}> {/* Una "tarjeta" o panel para el formulario */}
                <h1 className={styles.title}>Iniciar Sesión</h1> {/* Título con estilo */}
                <form onSubmit={handleLogin} className={styles.form}> {/* Formulario con estilo */}
                    <div className={styles.inputGroup}> {/* Agrupamos cada input con su label si FormInput no lo hace */}
                        <FormInput
                            label="Correo electrónico" // Texto más amigable
                            name="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder=''
                        // Podrías añadir un className prop a FormInput si lo soporta para más personalización
                        />
                    </div>
                    <div className={styles.inputGroup}>
                        <FormInput
                            label="Contraseña"
                            name="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder=''
                        />
                    </div>

                    <button
                        type="submit"
                        className={styles.submitButton} // Botón con estilo
                        disabled={loading} // Deshabilitar el botón mientras carga
                    >
                        {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                    </button>

                    {/* Espacio para enlaces de recuperación de contraseña o registro */}
                    <p className={styles.forgotPassword}>
                        ¿Olvidaste tu contraseña? <a href="/auth/forgot-password">Recupérala aquí</a>
                    </p>
                    <p className={styles.registerLink}>
                        ¿No tienes cuenta? <a href="/auth/register">Regístrate</a>
                    </p>
                </form>
            </div>
        </div>
    );
}