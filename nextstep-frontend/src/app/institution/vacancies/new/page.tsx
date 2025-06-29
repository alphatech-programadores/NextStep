// src/app/institution/vacancies/new/page.tsx

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import ProtectedRoute from '@/components/ProtectedRoute';
import { createVacancy, NewVacancyData } from '../../../../services/institucionApi';
import styles from './form.module.scss';

export default function CreateVacancyPage() {
    const router = useRouter();
    const [formData, setFormData] = useState<NewVacancyData>({
        area: '',
        description: '',
        requirements: '',
        hours: '',
        modality: 'Presencial',
        location: '',
        tags: '',
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            await createVacancy(formData);
            toast.success('¡Vacante creada exitosamente!');
            router.push('/institution'); // Redirige al dashboard después de crear
        } catch (error: any) {
            toast.error(error.response?.data?.error || 'No se pudo crear la vacante.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <ProtectedRoute allowedRoles={['institution']}>
            <div className={styles.container}>
                <div className={styles.formCard}>
                    <h1 className={styles.title}>Crear Nueva Vacante</h1>
                    <p className={styles.subtitle}>Completa los detalles para publicar una nueva oportunidad de práctica.</p>

                    <form onSubmit={handleSubmit} className={styles.form}>
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
                                <input type="text" id="hours" name="hours" value={formData.hours} onChange={handleChange} placeholder="Ej. 20 hrs/semana, Beca de $5,000" />
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
                            <input type="text" id="location" name="location" value={formData.location} onChange={handleChange} placeholder="Ej. CDMX, Remoto" required />
                        </div>

                        <div className={styles.inputGroup}>
                            <label htmlFor="tags">Etiquetas (separadas por coma)</label>
                            <input type="text" id="tags" name="tags" value={formData.tags} onChange={handleChange} placeholder="Ej. Finanzas, Análisis de Datos, Excel" />
                        </div>

                        <div className={styles.buttonContainer}>
                            <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
                                {isSubmitting ? 'Publicando...' : 'Publicar Vacante'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </ProtectedRoute>
    );
}
