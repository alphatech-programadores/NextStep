'use client';

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import axiosInstance from "@/services/axiosConfig";
import styles from "@/app/student/profile/profile.module.scss";

interface StudentProfile {
    email: string;
    name: string;
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
}

export default function StudentProfileView() {
    const params = useParams();
    const emailParam = params.email as string;

    // 🚨 Solución correcta:
    const decoded = decodeURIComponent(emailParam);
    const safeEmail = encodeURIComponent(decoded);

    const [profile, setProfile] = useState<StudentProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchProfile = async () => {
        setLoading(true);
        try {
            console.log("Solicitando perfil de:", safeEmail);
            const res = await axiosInstance.get(`/students/${safeEmail}/`);
            setProfile(res.data);
        } catch (e: any) {
            console.error(e);
            setError(
                e.response?.data?.error || e.message || "Error al cargar perfil."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (safeEmail) {
            fetchProfile();
        }
    }, [safeEmail]);

    if (loading)
        return <div className={styles.loadingContainer}>Cargando perfil...</div>;
    if (error)
        return <div className={styles.errorContainer}>{error}</div>;
    if (!profile)
        return (
            <div className={styles.errorContainer}>No se encontró el perfil.</div>
        );

    return (
        <div className={styles.profilePage}>
            <h1 className={styles.title}>Perfil del Estudiante</h1>
            {/* Tu render normal */}
        </div>
    );
}
