import axiosInstance from './axiosConfig';

export interface InstitutionVacancy {
    id: number;
    area: string;
    status: string;
    is_draft: boolean;
    applications_count: number;
    status_summary: 'borrador' | 'cerrada' | 'activa_con_postulaciones' | 'activa_sin_postulaciones';
}

export interface NewVacancyData {
    area: string;
    description: string;
    requirements: string;
    hours: string;
    modality: 'Presencial' | 'Híbrido' | 'Remoto';
    location: string;
    tags: string;
    is_draft?: boolean;
}

export const getMyInstitutionVacancies = async (): Promise<InstitutionVacancy[]> => {
    const response = await axiosInstance.get('/vacants/my');
    return response.data;
};

export const createVacancy = async (vacancyData: NewVacancyData): Promise<any> => {
    const response = await axiosInstance.post('/vacants/', vacancyData);
    return response.data;
};

export interface VacancyDetails extends NewVacancyData {
    id: number;
}

export const getVacancyById = async (id: string): Promise<VacancyDetails> => {
    const response = await axiosInstance.get(`/vacants/${id}`);
    return response.data;
};

export const updateVacancy = async (id: string, vacancyData: NewVacancyData): Promise<any> => {

    const response = await axiosInstance.put(`/vacants/${id}`, vacancyData);
    return response.data;
};

export interface ApplicantStudent {
    name: string;
    email: string;
    career: string;
    semester: number;
    skills: string[];
    cv_url?: string;
}

export interface VacancyApplication {
    application_id: number;
    status: 'pendiente' | 'aceptado' | 'rechazado';
    submitted_at: string;
    student: ApplicantStudent;
}

export const getVacancyApplicants = async (vacancyId: string): Promise<VacancyApplication[]> => {
    const response = await axiosInstance.get(`/vacants/${vacancyId}/applications`);
    return response.data;
};

// ✅ La correcta para tu backend actual (usa PUT y la ruta /apply)
export const decideOnApplication = async (
    applicationId: number,
    status: 'aceptado' | 'rechazado',
    feedback?: string
): Promise<any> => {
    return await axiosInstance.patch(`/vacants/${applicationId}/decision`, { decision: status, feedback });
};
