// src/app/student/profile/page.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import axiosInstance from '@/services/axiosConfig';
import toast from 'react-hot-toast';
import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import FormInput from '@/components/Input';
import styles from './profile.module.scss';
import Modal from '@/components/Modal';

// Definir la interfaz para el perfil del estudiante basada en el modelo de backend
interface StudentProfile {
    email: string;
    career: string | null;
    semestre: number | null;
    average: number | null;
    phone: string | null;
    address: string | null;
    availability: string | null;
    skills: string;
    portfolio_url: string | null;
    cv_path: string | null;
    profile_picture_url: string | null;
    name: string;
}

export default function StudentProfilePage() {
    // --- CAMBIO AQUÍ: Desestructurar revalidateUser de useAuth ---
    const { user, logout, revalidateUser } = useAuth();
    // -----------------------------------------------------------
    const [profile, setProfile] = useState<StudentProfile | null>(null);
    const [loadingProfile, setLoadingProfile] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Estados para los campos del formulario
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [career, setCareer] = useState('');
    const [semestre, setSemestre] = useState<number | ''>('');
    const [average, setAverage] = useState<number | ''>('');
    const [addressLine, setAddressLine] = useState('');

    const [availability, setAvailability] = useState('');
    const [skills, setSkills] = useState('');
    const [portfolioUrl, setPortfolioUrl] = useState('');

    const [profilePicFile, setProfilePicFile] = useState<File | null>(null);
    const [cvFile, setCvFile] = useState<File | null>(null);
    const [profilePicPreview, setProfilePicPreview] = useState<string | null>(null);

    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);


    const fetchProfile = async () => {
        if (!user) return;

        setLoadingProfile(true);
        try {
            const response = await axiosInstance.get('/profile/me');
            const data = response.data;
            setProfile(data);

            setName(user?.name || '');
            setEmail(user?.email || '');

            setCareer(data.career || '');
            setSemestre(data.semestre !== null ? data.semestre : '');
            setAverage(data.average !== null ? data.average : '');
            setPhone(data.phone || '');

            setAddressLine(data.address || '');

            setAvailability(data.availability || '');
            setSkills(data.skills ? data.skills.split(', ').join(', ') : '');
            setPortfolioUrl(data.portfolio_url || '');

            if (data.profile_picture_url) {
                setProfilePicPreview(data.profile_picture_url);
            }

        } catch (err: any) {
            console.error("Error fetching profile:", err);
            toast.error(err.response?.data?.error || "Error al cargar el perfil.");
        } finally {
            setLoadingProfile(false);
        }
    };

    useEffect(() => {
        fetchProfile();
    }, [user]);

    const handleProfilePicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setProfilePicFile(file);
            setProfilePicPreview(URL.createObjectURL(file));
        } else {
            setProfilePicFile(null);
            setProfilePicPreview(profile?.profile_picture_url || null);
        }
    };

    const handleCvChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setCvFile(e.target.files[0]);
        } else {
            setCvFile(null);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        const formData = new FormData();
        formData.append('name', name);
        formData.append('email', email);
        formData.append('career', career);
        formData.append('semestre', semestre !== '' ? String(semestre) : '');
        formData.append('average', average !== '' ? String(average) : '');
        formData.append('phone', phone);

        formData.append('address', addressLine);

        formData.append('availability', availability);
        formData.append('skills', skills);
        formData.append('portfolio_url', portfolioUrl);

        if (profilePicFile) {
            formData.append('profile_picture_file', profilePicFile);
        }
        if (cvFile) {
            formData.append('cv_file', cvFile);
        }

        try {
            const response = await axiosInstance.put(
                `/profile/me`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    }
                }
            );

            toast.success(response.data.message || "Perfil actualizado exitosamente. ✅");
            fetchProfile();
            setCvFile(null);
            // --- CAMBIO CLAVE AQUÍ: Llamar a revalidateUser ---
            await revalidateUser(); // Notificar al AuthContext que recargue la información del usuario
            // ----------------------------------------------------

        } catch (err: any) {
            console.error("Error updating profile:", err);
            toast.error(err.response?.data?.error || "Error al actualizar el perfil. ❌");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDeleteAccount = async () => {
        setIsDeleting(true);
        try {
            await axiosInstance.delete('/profile/me');
            toast.success("Tu cuenta ha sido eliminada exitosamente. ¡Adiós! 👋");
            logout();
        } catch (err: any) {
            console.error("Error deleting account:", err);
            toast.error(err.response?.data?.error || "Error al eliminar la cuenta. Por favor, inténtalo de nuevo.");
        } finally {
            setIsDeleting(false);
            setShowDeleteModal(false);
        }
    };

    if (loadingProfile) {
        return <ProtectedRoute><div className={styles.loadingContainer}>Cargando perfil...</div></ProtectedRoute>;
    }

    if (!profile) {
        return <ProtectedRoute><div className={styles.errorContainer}>No se pudo cargar el perfil.</div></ProtectedRoute>;
    }

    return (
        <ProtectedRoute allowedRoles={['student']}>
            <div className={styles.profilePage}>
                <h1 className={styles.title}>Mi Perfil de Estudiante</h1>

                <form onSubmit={handleSubmit} className={styles.profileForm}>
                    {/* Sección de Foto de Perfil */}
                    <section className={styles.formSection}>
                        <h2>Foto de Perfil</h2>
                        <div className={styles.profilePictureSection}>
                            {profilePicPreview ? (
                                <img src={profilePicPreview} alt="Vista previa de perfil" className={styles.profileImagePreview} />
                            ) : (
                                <div className={styles.profileImagePlaceholder}>
                                    <span>No hay foto</span>
                                </div>
                            )}
                            <div className={styles.fileUploadGroup}>
                                <label htmlFor="profilePic" className={styles.customFileUploadButton}>
                                    {profilePicFile ? 'Cambiar Foto' : 'Subir Nueva Foto'}
                                </label>
                                <input
                                    type="file"
                                    id="profilePic"
                                    accept="image/*"
                                    onChange={handleProfilePicChange}
                                    className={styles.hiddenFileInput}
                                />
                                {profilePicFile && <p>Archivo seleccionado: {profilePicFile.name}</p>}
                                {profile?.profile_picture_url && !profilePicFile && (
                                    <p>Foto actual: <a href={profile.profile_picture_url} target="_blank" rel="noopener noreferrer">Ver foto actual</a></p>
                                )}
                            </div>
                        </div>
                    </section>


                    {/* Sección de Información Personal */}
                    <section className={styles.formSection}>
                        <h2>Información Personal</h2>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Nombre Completo"
                                name="name"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                                disabled
                            />
                            <FormInput
                                label="Correo Electrónico"
                                name="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                disabled
                            />
                            <FormInput
                                label="Número de Teléfono"
                                name="phone"
                                type="text"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                            />
                        </div>
                    </section>

                    {/* Sección de Información Académica */}
                    <section className={styles.formSection}>
                        <h2>Información Académica</h2>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Carrera"
                                name="career"
                                type="text"
                                value={career}
                                onChange={(e) => setCareer(e.target.value)}
                            />
                            <FormInput
                                label="Semestre"
                                name="semestre"
                                type="number"
                                value={semestre}
                                onChange={(e) => setSemestre(e.target.value === '' ? '' : Number(e.target.value))}
                            />
                            <FormInput
                                label="Promedio"
                                name="average"
                                type="number"
                                step="0.01"
                                value={average}
                                onChange={(e) => setAverage(e.target.value === '' ? '' : Number(e.target.value))}
                            />
                            <FormInput
                                label="Disponibilidad"
                                name="availability"
                                type="text"
                                value={availability}
                                onChange={(e) => setAvailability(e.target.value)}
                                placeholder="Ej: Tiempo Completo, Medio Tiempo, Prácticas"
                            />
                        </div>
                    </section>

                    {/* Sección de Dirección */}
                    <section className={styles.formSection}>
                        <h2>Dirección</h2>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Dirección Completa (Calle, Número, Ciudad, Estado, Código Postal, País)"
                                name="addressLine"
                                type="text"
                                value={addressLine}
                                onChange={(e) => setAddressLine(e.target.value)}
                                placeholder="Ej: Calle Falsa 123, Ciudad de México, CDMX, 00000, México"
                            />
                        </div>
                    </section>

                    {/* Sección de Habilidades */}
                    <section className={styles.formSection}>
                        <h2>Habilidades y Portafolio</h2>
                        <div className={styles.inputGroup}>
                            <FormInput
                                label="Habilidades (separadas por comas)"
                                name="skills"
                                type="text"
                                value={skills}
                                onChange={(e) => setSkills(e.target.value)}
                                placeholder="Ej: React, Node.js, SQL, Diseño UI/UX"
                            />
                            <FormInput
                                label="URL de Portafolio"
                                name="portfolioUrl"
                                type="url"
                                value={portfolioUrl}
                                onChange={(e) => setPortfolioUrl(e.target.value)}
                                placeholder="Ej: https://tumiportafolio.com"
                            />
                        </div>
                    </section>

                    {/* Sección de CV */}
                    <section className={styles.formSection}>
                        <h2>Curriculum Vitae (CV)</h2>
                        <div className={styles.fileUploadGroup}>
                            <label htmlFor="cvFile" className={styles.customFileUploadButton}>
                                {cvFile ? 'Cambiar CV' : 'Subir CV'}
                            </label>
                            <input
                                type="file"
                                id="cvFile"
                                accept=".pdf,.doc,.docx"
                                onChange={handleCvChange}
                                className={styles.hiddenFileInput}
                            />
                            {cvFile && <p>Archivo seleccionado: {cvFile.name}</p>}
                            {profile?.cv_path && !cvFile && (
                                <p>CV actual: <a href={profile.cv_path} target="_blank" rel="noopener noreferrer">Ver CV actual</a></p>
                            )}
                        </div>
                    </section>

                    <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
                        {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
                    </button>
                </form>

                {/* Sección de Eliminar Cuenta */}
                <div className={styles.deleteAccountSection}>
                    <button
                        className={styles.deleteButton}
                        onClick={() => setShowDeleteModal(true)}
                        disabled={isDeleting}
                    >
                        Eliminar Cuenta
                    </button>
                </div>

                {/* Modal de Confirmación */}
                {showDeleteModal && (
                    <Modal
                        title="Confirmar Eliminación de Cuenta"
                        onClose={() => setShowDeleteModal(false)}
                    >
                        <p>¿Estás seguro de que quieres eliminar tu cuenta? Esta acción es irreversible y se perderán todos tus datos.</p>
                        <div className={styles.modalActions}>
                            <button
                                className={styles.cancelButton}
                                onClick={() => setShowDeleteModal(false)}
                                disabled={isDeleting}
                            >
                                Cancelar
                            </button>
                            <button
                                className={styles.confirmDeleteButton}
                                onClick={handleDeleteAccount}
                                disabled={isDeleting}
                            >
                                {isDeleting ? 'Eliminando...' : 'Sí, Eliminar Mi Cuenta'}
                            </button>
                        </div>
                    </Modal>
                )}
            </div>
        </ProtectedRoute>
    );
}