// src/app/student/profile/page.tsx
'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute'; // Asegúrate de proteger esta ruta
import FormInput from '@/components/Input'; // Tu componente de input
import styles from './profile.module.scss'; // Módulo de estilos (necesario aunque sea básico)
import axiosInstance from '@/services/axiosConfig';

interface StudentProfileData {
    email: string;
    name: string; // Del modelo User
    role: string; // Del modelo User
    career: string;
    semestre: number | null;
    average: number | null;
    phone: string;
    address: string;
    availability: string;
    skills: string;
    portfolio_url: string;
    cv_path: string | null; // Nombre del archivo CV o path relativo
    cv_url: string | null; // URL completa para descargar/visualizar
    profile_picture_url: string | null; // URL completa de la foto de perfil
}

export default function StudentProfilePage() {
    const { user, loadingUser, revalidateUser } = useAuth();
    const [profile, setProfile] = useState<StudentProfileData | null>(null);
    const [loadingProfile, setLoadingProfile] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [cvFile, setCvFile] = useState<File | null>(null);
    const [profilePicFile, setProfilePicFile] = useState<File | null>(null);

    // Estados para los campos del formulario
    const [career, setCareer] = useState('');
    const [semestre, setSemestre] = useState<number | ''>('');
    const [average, setAverage] = useState<number | ''>('');
    const [phone, setPhone] = useState('');
    const [address, setAddress] = useState('');
    const [availability, setAvailability] = useState('');
    const [skills, setSkills] = useState('');
    const [portfolioUrl, setPortfolioUrl] = useState('');

    const fetchProfile = async () => {
        if (!user) return; // Esperar a que el usuario esté cargado

        setLoadingProfile(true);
        try {
            const token = localStorage.getItem('access_token');
            if (!token) throw new Error("No hay token de autenticación.");

            const response = await axiosInstance.get('http://localhost:5000/api/profile/me', {
                headers: { Authorization: `Bearer ${token}` }
            });
            const data = response.data;
            setProfile(data); // Guarda el perfil completo

            // Cargar los datos en los estados del formulario
            setCareer(data.career || '');
            setSemestre(data.semestre || '');
            setAverage(data.average || '');
            setPhone(data.phone || '');
            setAddress(data.address || '');
            setAvailability(data.availability || '');
            // Si las habilidades vienen como texto plano y quieres un array, aquí podrías splitarlas
            setSkills(data.skills || '');
            setPortfolioUrl(data.portfolio_url || '');

        } catch (err: any) {
            console.error("Error fetching profile:", err);
            toast.error(err.response?.data?.error || "Error al cargar el perfil.");
        } finally {
            setLoadingProfile(false);
        }
    };

    // Recargar perfil si el usuario cambia o al montar
    useEffect(() => {
        // Solo intenta cargar el perfil si el usuario es estudiante y ya está cargado
        if (user && user.role === 'student') {
            fetchProfile();
        }
    }, [user]); // Dependencia 'user' para recargar si el objeto user cambia

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        const formData = new FormData(); // Usaremos FormData para enviar archivos y texto

        // Adjuntar campos de texto
        formData.append('career', career);
        formData.append('semestre', semestre !== '' ? String(semestre) : '');
        formData.append('average', average !== '' ? String(average) : '');
        formData.append('phone', phone);
        formData.append('address', address);
        formData.append('availability', availability);
        formData.append('skills', skills);
        formData.append('portfolio_url', portfolioUrl);

        // --- ¡EL PUNTO CLAVE AQUÍ! ---
        // Adjuntar archivos si se seleccionaron
        if (cvFile) {
            console.log("DEBUG_FRONT: Adjuntando CV al FormData:", cvFile.name); // DEBUG FRONEND
            formData.append('cv_file', cvFile); // Asegúrate de que el nombre aquí ('cv_file') coincide con backend request.files
        } else {
            console.log("DEBUG_FRONT: No se seleccionó CV o cvFile es null."); // DEBUG FRONEND
        }

        if (profilePicFile) {
            console.log("DEBUG_FRONT: Adjuntando Foto de Perfil al FormData:", profilePicFile.name); // DEBUG FRONEND
            formData.append('profile_picture_file', profilePicFile); // Asegúrate de que el nombre aquí ('profile_picture_file') coincide con backend request.files
        } else {
            console.log("DEBUG_FRONT: No se seleccionó Foto de Perfil o profilePicFile es null."); // DEBUG FRONEND
        }
        // -----------------------------

        try {
            const token = localStorage.getItem('access_token');
            if (!token) throw new Error("No hay token de autenticación.");

            const response = await axiosInstance.put(
                `http://localhost:5000/api/profile/me`,
                formData, // <-- Aquí envías el FormData
                {
                    headers: {
                        'Content-Type': 'multipart/form-data', // Axios a veces lo maneja automáticamente con FormData, pero es bueno tenerlo
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            toast.success(response.data.message || "Perfil actualizado exitosamente. ✅");
            fetchProfile(); // Vuelve a cargar el perfil para ver los cambios
            setCvFile(null);
            setProfilePicFile(null);

        } catch (err: any) {
            console.error("Error updating profile:", err);
            toast.error(err.response?.data?.error || "Error al actualizar el perfil. ❌");
        } finally {
            setIsSubmitting(false);
        }
    };

    // Manejo del estado de carga y redirección por rol/autenticación
    if (loadingUser || loadingProfile) {
        return (
            <ProtectedRoute allowedRoles={['student']}>
                <div className={styles.loadingContainer}>Cargando perfil...</div>
            </ProtectedRoute>
        );
    }

    // Asegurarse de que solo estudiantes puedan ver esta página
    if (!user || user.role !== 'student') {
        // ProtectedRoute ya debería manejar esto, pero es un buen fallback visual
        return (
            <ProtectedRoute allowedRoles={['student']}>
                <div className={styles.unauthorizedContainer}>Acceso denegado.</div>
            </ProtectedRoute>
        );
    }

    // Si el perfil aún es nulo y no está cargando (raro, pero como fallback)
    if (!profile) {
        return (
            <ProtectedRoute allowedRoles={['student']}>
                <div className={styles.errorContainer}>No se pudo cargar la información del perfil.</div>
            </ProtectedRoute>
        );
    }

    return (
        <ProtectedRoute allowedRoles={['student']}>
            <div className={styles.container}>
                <div className={styles.profileCard}>
                    <h1 className={styles.title}>Mi Perfil de Estudiante</h1>

                    <div className={styles.profilePictureSection}>
                        {/* La imagen o el placeholder van primero como fondo */}
                        {profile.profile_picture_url ? (
                            <img src={profile.profile_picture_url} alt="Foto de perfil" className={styles.profilePicture} />
                        ) : (
                            <div className={styles.profilePicturePlaceholder}>
                                {/* Un ícono simple de usuario */}
                                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                            </div>
                        )}

                        {/* Input oculto, como ya lo tenías */}
                        <input
                            type="file"
                            id="profilePicUpload"
                            accept="image/*"
                            onChange={(e) => setProfilePicFile(e.target.files ? e.target.files[0] : null)}
                            className={styles.fileInput}
                            name="profile_picture_file"
                        />

                        {/* Este label es el overlay que aparece al hacer hover */}
                        <label htmlFor="profilePicUpload" className={`${styles.fileInputLabel} ${styles.profileOverlay}`}>
                            Cambiar
                        </label>
                    </div>
                    {/* Muestra el nombre del archivo nuevo si se ha seleccionado */}
                    {profilePicFile && <p className={styles.fileName}>Nuevo archivo: {profilePicFile.name}</p>}


                    <form onSubmit={handleSubmit} className={styles.form}>
                        {/* Campos de texto de User model (solo lectura) */}
                        <div className={styles.inputGroup}>
                            <FormInput label="Nombre de Usuario" name="name" type="text" value={profile.name || user.name} onChange={() => { }} readOnly />
                            <p className={styles.readOnlyHelp}>Tu nombre de usuario no se puede cambiar aquí.</p>
                        </div>
                        <div className={styles.inputGroup}>
                            <FormInput label="Email" name="email" type="email" value={profile.email || user.email} onChange={() => { }} readOnly />
                            <p className={styles.readOnlyHelp}>Tu email no se puede cambiar aquí.</p>
                        </div>

                        {/* Campos editables del StudentProfile */}
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Carrera"
                                name="career"
                                type="text"
                                value={career}
                                onChange={(e) => setCareer(e.target.value)}
                                placeholder="Ej. Ingeniería en Software"
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Semestre"
                                name="semestre"
                                type="number"
                                value={semestre}
                                onChange={(e) => setSemestre(e.target.valueAsNumber || '')}
                                placeholder="Ej. 5"
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Promedio"
                                name="average"
                                type="number"
                                step="0.01" // Permite decimales
                                value={average}
                                onChange={(e) => setAverage(e.target.valueAsNumber || '')}
                                placeholder="Ej. 8.5"
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Teléfono"
                                name="phone"
                                type="tel"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                                placeholder="Ej. +52 55 1234 5678"
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Dirección"
                                name="address"
                                type="text"
                                value={address}
                                onChange={(e) => setAddress(e.target.value)}
                                placeholder="Ej. Calle 123, Colonia, Ciudad"
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <label htmlFor="availability" className={styles.selectLabel}>Disponibilidad</label>
                            <select
                                id="availability"
                                name="availability"
                                value={availability}
                                onChange={(e) => setAvailability(e.target.value)}
                                className={styles.selectInput}
                            >
                                <option value="">Selecciona</option>
                                <option value="Tiempo Completo">Tiempo Completo</option>
                                <option value="Medio Tiempo">Medio Tiempo</option>
                                <option value="Por Proyecto">Por Proyecto</option>
                            </select>
                        </div>
                        <div className={styles.inputGroup}>
                            <label htmlFor="skills" className={styles.textareaLabel}>Habilidades (separadas por coma)</label>
                            <textarea
                                id="skills"
                                name="skills"
                                value={skills}
                                onChange={(e) => setSkills(e.target.value)}
                                placeholder="Ej. Python, SQL, React, Análisis de Datos"
                                rows={4}
                                className={styles.textareaInput}
                            ></textarea>
                        </div>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="URL de Portafolio"
                                name="portfolioUrl"
                                type="url"
                                value={portfolioUrl}
                                onChange={(e) => setPortfolioUrl(e.target.value)}
                                placeholder="Ej. https://tu-portafolio.com"
                            />
                        </div>

                        {/* Sección de Subida de CV */}
                        <div className={styles.cvUploadSection}>
                            {profile.cv_path && !cvFile ? (
                                <p className={styles.currentCv}>CV actual: <a href={profile.cv_url || '#'} target="_blank" rel="noopener noreferrer">{profile.cv_path.split('/').pop()}</a></p>
                            ) : (
                                <p className={styles.noCv}>Sube tu CV en formato PDF o DOCX.</p>
                            )}

                            <input
                                type="file"
                                id="cvUpload"
                                accept=".pdf,.doc,.docx"
                                onChange={(e) => setCvFile(e.target.files ? e.target.files[0] : null)}
                                className={styles.fileInput}
                            />

                            <label htmlFor="cvUpload" className={`${styles.fileInputLabel} ${styles.cvButton}`}>
                                {profile.cv_path ? 'Cambiar CV' : 'Seleccionar Archivo'}
                            </label>

                            {cvFile && <p className={styles.fileName}>Archivo seleccionado: {cvFile.name}</p>}
                        </div>

                        <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
                            {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
                        </button>
                    </form>
                </div>
            </div>
        </ProtectedRoute>
    );
}