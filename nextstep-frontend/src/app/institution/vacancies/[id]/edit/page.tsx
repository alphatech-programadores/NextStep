// src/app/institution/vacancies/[id]/edit/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import toast from 'react-hot-toast';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getVacancyById, updateVacancy, NewVacancyData } from '../../../../../services/institucionApi';
// Reutilizamos los mismos estilos del formulario de creación
import styles from '../../new/form.module.scss';

export default function EditVacancyPage() {
    const router = useRouter();
    const params = useParams();
    const id = params.id as string; // Obtenemos el ID de la URL

    const [formData, setFormData] = useState<NewVacancyData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        if (id) {
            const fetchVacancyData = async () => {
                try {
                    const data = await getVacancyById(id);
                    setFormData(data);
                } catch (error) {
                    toast.error('No se pudieron cargar los datos de la vacante.');
                    router.push('/institution/dashboard'); // Redirige si hay error
                } finally {
                    setIsLoading(false);
                }
            };
            fetchVacancyData();
        }
    }, [id, router]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        if (formData) {
            setFormData(prev => ({ ...prev!, [name]: value }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData) return;

        setIsSubmitting(true);
        try {
            await updateVacancy(id, formData);
            toast.success('¡Vacante actualizada exitosamente!');
            router.push('/institution/dashboard');
        } catch (error: any) {
            toast.error(error.response?.data?.error || 'No se pudo actualizar la vacante.');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) {
        return <ProtectedRoute allowedRoles={['institution']}><div>Cargando formulario...</div></ProtectedRoute>;
    }

    if (!formData) {
        return <ProtectedRoute allowedRoles={['institution']}><div>No se encontraron datos para esta vacante.</div></ProtectedRoute>;
    }

    return (
        <ProtectedRoute allowedRoles={['institution']}>
            <div className={styles.container}>
                <div className={styles.formCard}>
                    <h1 className={styles.title}>Editar Vacante</h1>
                    <p className={styles.subtitle}>Modifica los detalles de la oportunidad de práctica.</p>

                    <form onSubmit={handleSubmit} className={styles.form}>
                        {/* El formulario es idéntico al de creación, pero los valores vienen del estado */}
                        <div className={styles.inputGroup}>
                            <label htmlFor="area">Área o Título del Puesto</label>
                            <input type="text" id="area" name="area" value={formData.area} onChange={handleChange} required />
                        </div>

                        <div className={styles.inputGroup}>
                            <label htmlFor="description">Descripción del Puesto</label>
                            <textarea id="description" name="description" value={formData.description} onChange={handleChange} rows={5} required />
                        </div>

                        <div className={styles.inputGroup}>
                            <label htmlFor="requirements">Requisitos</label>
                            <textarea id="requirements" name="requirements" value={formData.requirements} onChange={handleChange} rows={5} required />
                        </div>

                        <div className={styles.grid}>
                            <div className={styles.inputGroup}>
                                <label htmlFor="hours">Horas / Salario</label>
                                <input type="text" id="hours" name="hours" value={formData.hours} onChange={handleChange} />
                            </div>
                            <div className={styles.inputGroup}>
                                <label htmlFor="modality">Modalidad</label>
                                <select id="modality" name="modality" value={formData.modality} onChange={handleChange}>
                                    <option value="Presencial">Presencial</option>
                                    <option value="Híbrido">Híbrido</option>
                                    <option value="Remoto">Remoto</option>
                                </select>
                            </div>
                        </div>

                        <div className={styles.inputGroup}>
                            <label htmlFor="location">Ubicación</label>
                            <input type="text" id="location" name="location" value={formData.location} onChange={handleChange} required />
                        </div>

                        <div className={styles.inputGroup}>
                            <label htmlFor="tags">Etiquetas (separadas por coma)</label>
                            <input type="text" id="tags" name="tags" value={formData.tags} onChange={handleChange} />
                        </div>

                        <div className={styles.buttonContainer}>
                            <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
                                {isSubmitting ? 'Guardando...' : 'Guardar Cambios'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </ProtectedRoute>
    );
}
