// src/services/institutionApi.ts

import axiosInstance from './axiosConfig'; // Reutilizamos nuestra instancia de Axios

// Define la interfaz de cómo se verá una vacante en la lista
export interface InstitutionVacancy {
    id: number;
    area: string;
    status: string;
    is_draft: boolean;
    applications_count: number;
    status_summary: 'borrador' | 'cerrada' | 'activa_con_postulaciones' | 'activa_sin_postulaciones';
}

/**
 * Obtiene la lista de vacantes para la institución autenticada.
 * Llama al endpoint GET /api/vacants/my
 */
export const getMyInstitutionVacancies = async (): Promise<InstitutionVacancy[]> => {
    try {
        const response = await axiosInstance.get('/vacants/my');
        // El backend devuelve directamente el array de vacantes
        return response.data;
    } catch (error) {
        console.error("Error al obtener las vacantes de la institución:", error);
        throw error;
    }
};


// Define la interfaz para los datos de una nueva vacante
export interface NewVacancyData {
    area: string;
    description: string;
    requirements: string;
    hours: string;
    modality: 'Presencial' | 'Híbrido' | 'Remoto';
    location: string;
    tags: string; // Comma-separated string, e.g., "React,Node.js,SQL"
    is_draft?: boolean;
}

/**
 * Crea una nueva vacante para la institución autenticada.
 * Llama al endpoint POST /api/vacants/
 * @param vacancyData - Los datos de la nueva vacante.
 */
export const createVacancy = async (vacancyData: NewVacancyData): Promise<any> => {
    try {
        // El backend espera un POST en la ruta raíz de vacants
        const response = await axiosInstance.post('/vacants/', vacancyData);
        return response.data;
    } catch (error) {
        console.error("Error al crear la vacante:", error);
        throw error;
    }
};


export interface VacancyDetails extends NewVacancyData {
    id: number;
    // Añade otros campos que la API pueda devolver si los necesitas
}

/**
 * Obtiene los detalles de una única vacante por su ID.
 * Llama al endpoint GET /api/vacants/<id>
 */
export const getVacancyById = async (id: string): Promise<VacancyDetails> => {
    try {
        const response = await axiosInstance.get(`/vacants/${id}`);
        return response.data;
    } catch (error) {
        console.error(`Error al obtener la vacante con ID ${id}:`, error);
        throw error;
    }
};

/**
 * Actualiza una vacante existente.
 * Llama al endpoint PUT /api/vacants/<id>
 */
export const updateVacancy = async (id: string, vacancyData: NewVacancyData): Promise<any> => {
    try {
        const response = await axiosInstance.put(`/vacants/${id}`, vacancyData);
        return response.data;
    } catch (error) {
        console.error(`Error al actualizar la vacante con ID ${id}:`, error);
        throw error;
    }
};

export interface ApplicantStudent {
    name: string;
    email: string;
    career: string;
    semester: number; // El semestre puede no estar definido
    skills: string[];
    cv_url?: string; // La URL del CV también puede ser nula
}

// Define la interfaz para una postulación completa
export interface VacancyApplication {
    application_id: number;
    status: 'pendiente' | 'aceptado' | 'rechazado';
    submitted_at: string;
    student: ApplicantStudent;
}

/**
 * Obtiene la lista de postulantes para una vacante específica.
 * Llama al endpoint GET /api/vacants/<id>/applications
 */
export const getVacancyApplicants = async (vacancyId: string): Promise<VacancyApplication[]> => {
    try {
        const response = await axiosInstance.get(`/vacants/${vacancyId}/applications`);
        return response.data;
    } catch (error) {
        console.error(`Error al obtener los postulantes para la vacante ${vacancyId}:`, error);
        throw error;
    }
};

/**
 * Envía una decisión (aceptar/rechazar) para una postulación.
 * Llama al endpoint PATCH /api/applications/<application_id>/decision
 */
export const decideOnApplication = async (applicationId: number, decision: 'aceptado' | 'rechazado'): Promise<any> => {
    try {
        const response = await axiosInstance.patch(`/applications/${applicationId}/decision`, { decision });
        return response.data;
    } catch (error) {
        console.error(`Error al tomar una decisión para la postulación ${applicationId}:`, error);
        throw error;
    }
};

