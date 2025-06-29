import axiosInstance from './axiosConfig'; // Importamos nuestra instancia configurada

// Define la interfaz de una postulación (lo que esperamos de la API)
interface Application {
    id: number;
    vacant_title: string;
    company_name: string;
    application_status: string;

    // ... cualquier otro campo que devuelva tu API
}

// Define la respuesta de la API de postulaciones
interface ApplicationsResponse {
    stats: Stats;
    applications: Application[];
    total_pages: number;
    current_page: number;
    total_items: number;
}

interface Stats {
    total: number;
    pending: number;
    interview: number;
    accepted: number;
}

interface StudentProfile {
    profile: any;
    profile_completeness: number;
    // podrías añadir más datos aquí en el futuro, como las habilidades
    // skills: string[]; 
}

// Nuestra primera función de API
export const getMyApplications = async (params?: { page?: number, per_page?: number }): Promise<ApplicationsResponse> => {
    try {
        // Usamos nuestra instancia. La URL será 'http://localhost:5000/api' + '/apply/me'
        const response = await axiosInstance.get('/apply/me', { params });

        // Devolvemos los datos. El interceptor ya añadió el token por nosotros.
        return response.data;
    } catch (error) {
        console.error("Error al obtener las postulaciones:", error);
        // Lanzamos el error para que el componente que llama pueda manejarlo
        throw error;
    }
};

export const getStudentProfile = async (): Promise<StudentProfile> => {
    try {
        // Necesitarás crear esta ruta en tu backend: GET /api/profile/student/me
        // Debería devolver un JSON como: { "profile_completeness": 75 }
        const response = await axiosInstance.get('/profile/student/me');
        return response.data;
    } catch (error) {
        console.error("Error al obtener el perfil del estudiante:", error);
        throw error;
    }
};