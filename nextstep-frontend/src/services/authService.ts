'use client';

import axiosInstance from './axiosConfig';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

export async function login(email: string, password: string) {
    const response = await axiosInstance.post(`${API_URL}/auth/login`, { email, password });
    return response.data;
}

export async function register(name: string, email: string, password: string, role: string) {
    const response = await axiosInstance.post(`${API_URL}/auth/register`, { name, email, password, role });
    return response.data;
}

export async function logout() {
    const response = await axiosInstance.post('/auth/logout'); // ✅ método POST
    return response.data;
}