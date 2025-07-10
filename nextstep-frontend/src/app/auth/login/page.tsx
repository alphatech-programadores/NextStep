'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import FormInput from '@/components/Input';
import toast from 'react-hot-toast';
import styles from './login.module.scss';
import { login as authServiceLogin } from '@/services/authService';

export default function LoginPage() {
    const router = useRouter();
    const { login: contextLogin } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);

        try {
            const responseData = await authServiceLogin(email, password);
            // CORREGIDO: Destructurar user_role directamente, no 'user: userData'
            const { access_token, user_role } = responseData;

            contextLogin(access_token);
            toast.success("Inicio de sesión exitoso ✅");

            // --- Aquí decides a dónde redirigir ---
            if (user_role === "institution") {
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
        <div className={styles.container}>
            <div className={styles.card}>
                <h1 className={styles.title}>Iniciar Sesión</h1>
                <form onSubmit={handleLogin} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <FormInput
                            label="Correo electrónico"
                            name="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder=''
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
                        className={styles.submitButton}
                        disabled={loading}
                    >
                        {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
                    </button>

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
