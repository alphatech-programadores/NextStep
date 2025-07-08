// src/app/institution/vacancies/page.tsx

"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import axiosInstance from "@/services/axiosConfig";
import styles from "./vacancies.module.scss";

interface Vacant {
    id: number;
    title: string;
    area: string;
    modality: string;
    location: string;
    status: string;
    created_at: string;
}

const InstitutionVacanciesPage: React.FC = () => {
    const [vacancies, setVacancies] = useState<Vacant[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchVacancies = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get("/vacants/my"); // Ajusta si tu endpoint es diferente
            setVacancies(response.data);
            setError(null);
        } catch (e: any) {
            console.error(e);
            setError(e.message || "Error al cargar vacantes.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchVacancies();
    }, []);

    if (loading) return <div className={styles.loading}>Cargando vacantes...</div>;
    if (error) return <div className={styles.error}>Error: {error}</div>;

    return (
        <div className={styles.container}>
            <h1 className={styles.title}>Mis Vacantes Publicadas</h1>
            {vacancies.length === 0 ? (
                <p>No tienes vacantes publicadas aún.</p>
            ) : (
                <div className={styles.vacanciesGrid}>
                    {vacancies.map((vacant) => (
                        <div key={vacant.id} className={styles.vacancyCard}>
                            <h2>{vacant.title}</h2>
                            <p><strong>Área:</strong> {vacant.area}</p>
                            <p><strong>Modalidad:</strong> {vacant.modality}</p>
                            <p><strong>Ubicación:</strong> {vacant.location}</p>
                            <p><strong>Estado:</strong> {vacant.status}</p>
                            <p><small>Creada: {new Date(vacant.created_at).toLocaleDateString()}</small></p>

                            <div className={styles.cardActions}>
                                <Link href={`/institution/vacancies/${vacant.id}/edit`} className={styles.editButton}>
                                    Editar
                                </Link>
                                <Link href={`/institution/vacancies/${vacant.id}/applications`} className={styles.viewApplicationsButton}>
                                    Ver Postulaciones
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default InstitutionVacanciesPage;
