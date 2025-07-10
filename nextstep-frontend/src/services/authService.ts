'use client';

import axiosInstance from './axiosConfig';

// REMOVIDO: const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';
// axiosInstance ya tiene la baseURL configurada, no necesitamos prefijos adicionales aquí.

export async function login(email: string, password: string) {
    // CORREGIDO: Usar solo la ruta relativa, axiosInstance se encarga de la baseURL
    const response = await axiosInstance.post('/auth/login', { email, password });
    return response.data;
}

export async function register(name: string, email: string, password: string, role: string) {
    // CORREGIDO: Usar solo la ruta relativa
    const response = await axiosInstance.post('/auth/register', { name, email, password, role });
    return response.data;
}

export async function logout() {
    const response = await axiosInstance.post('/auth/logout');
    return response.data;
}
