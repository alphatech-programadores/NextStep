// src/app/auth/register/page.tsx

'use client'; // Esto es necesario para usar hooks de React como useState

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import FormInput from '@/components/Input'; // Asumiendo que Input.tsx es tu FormInput
import toast from 'react-hot-toast'; // Para notificaciones

// ¡Importa tu módulo de estilos!
import styles from './register.module.scss'; // Asegúrate de que esta ruta sea correcta
import axiosInstance from '@/services/axiosConfig';

export default function RegisterPage() {
    const router = useRouter();
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false); // Estado para manejar el loading del botón
    const [role, setRole] = useState("student")

    const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            toast.error("Las contraseñas no coinciden. 😔");
            return;
        }

        setLoading(true);

        try {
            const response = await axiosInstance.post("auth/register", {
                name,
                email,
                password,
                role,
            });

            toast.success("Registro exitoso. ¡Bienvenido a NextStep! 🎉 Ahora puedes iniciar sesión.");
            router.push("/auth/login");
        } catch (error: any) {
            console.error("Error de registro:", error);

            // --- ¡CAMBIO CLAVE AQUÍ! ---
            // Intenta obtener el mensaje de error del backend
            const errorMessage = error.response && error.response.data && error.response.data.error
                ? error.response.data.error // Mensaje específico del backend
                : "Error al registrarte. Por favor, inténtalo de nuevo."; // Mensaje genérico de fallback

            toast.error(errorMessage); // Muestra el mensaje específico o el genérico
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.card}>
                <h1 className={styles.title}>Crear una Cuenta</h1>
                <form onSubmit={handleRegister} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <FormInput
                            label="Nombre Completo"
                            name="name"
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required // Hacer el campo requerido
                            placeholder=''
                        />
                    </div>
                    <div className={styles.inputGroup}>
                        <FormInput
                            label="Correo electrónico"
                            name="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
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
                            required
                            placeholder=''
                        />
                    </div>
                    <div className={styles.inputGroup}>
                        <FormInput
                            label="Confirmar Contraseña"
                            name="confirmPassword"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            placeholder=''
                        />
                    </div>

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={loading} // Deshabilitar el botón mientras carga
                    >
                        {loading ? 'Registrando...' : 'Registrarse'}
                    </button>

                    <p className={styles.loginLink}>
                        ¿Ya tienes una cuenta? <a href="/auth/login">Inicia Sesión</a>
                    </p>
                </form>
            </div>
        </div>
    );
}