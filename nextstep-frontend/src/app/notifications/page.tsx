// src/app/notifications/page.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import axiosInstance from '@/services/axiosConfig'; // Asegúrate de que la ruta sea correcta
import toast from 'react-hot-toast';
import { useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute'; // Asegúrate de tener este componente
import { useRouter } from 'next/navigation'; // Para navegación programática
import Link from 'next/link';
import styles from './notifications.module.scss'; // Nuevo módulo de estilos

// Interfaz para la estructura de una notificación (debe coincidir con tu backend)
interface Notification {
    id: number;
    recipient_email: string;
    sender_email: string | null;
    type: string;
    message: string;
    link: string | null;
    related_id: number | null;
    is_read: boolean;
    created_at: string; // ISO format string
}

export default function NotificationsPage() {
    const { user, loadingUser, logout } = useAuth(); // Asume que useAuth proporciona el usuario logueado
    const router = useRouter(); // Instancia del router
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalItems, setTotalItems] = useState(0);
    const perPage = 10; // Coincidir con per_page en el backend

    const fetchNotifications = useCallback(async (page: number) => {
        if (!user) return; // No cargar si no hay usuario logueado

        setLoading(true);
        try {
            const response = await axiosInstance.get(`/notifications?page=${page}&per_page=${perPage}`);
            setNotifications(response.data.notifications);
            setTotalPages(response.data.total_pages);
            setTotalItems(response.data.total_items);
            setCurrentPage(response.data.current_page);
        } catch (error: any) {
            console.error("Error fetching notifications:", error);
            toast.error(error.response?.data?.error || "Error al cargar las notificaciones.");
            if (error.response?.status === 401) {
                logout(); // Desloguear si el token es inválido
                router.push('/auth/login');
            }
        } finally {
            setLoading(false);
        }
    }, [user, logout, router]);

    useEffect(() => {
        fetchNotifications(currentPage);
    }, [fetchNotifications, currentPage]);

    const handleMarkAsRead = async (id: number) => {
        try {
            await axiosInstance.put(`/notifications/${id}/mark_read`);
            toast.success("Notificación marcada como leída.");
            fetchNotifications(currentPage); // Recargar notificaciones
        } catch (error: any) {
            console.error("Error marking notification as read:", error);
            toast.error(error.response?.data?.error || "Error al marcar como leída.");
        }
    };

    const handleMarkAllAsRead = async () => {
        try {
            await axiosInstance.put(`/notifications/mark_all_read`);
            toast.success("Todas las notificaciones marcadas como leídas.");
            fetchNotifications(currentPage); // Recargar notificaciones
        } catch (error: any) {
            console.error("Error marking all notifications as read:", error);
            toast.error(error.response?.data?.error || "Error al marcar todas como leídas.");
        }
    };

    const handleDeleteNotification = async (id: number) => {
        if (!confirm("¿Estás seguro de que quieres eliminar esta notificación?")) {
            return;
        }
        try {
            await axiosInstance.delete(`/notifications/${id}`);
            toast.success("Notificación eliminada.");
            fetchNotifications(currentPage); // Recargar notificaciones
        } catch (error: any) {
            console.error("Error deleting notification:", error);
            toast.error(error.response?.data?.error || "Error al eliminar la notificación.");
        }
    };

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= totalPages) {
            setCurrentPage(newPage);
        }
    };

    if (loadingUser || loading) {
        return <ProtectedRoute allowedRoles={['student']}><div className={styles.loadingContainer}>Cargando notificaciones...</div></ProtectedRoute>;
    }

    if (!user) {
        // Redirigir si no hay usuario (ProtectedRoute ya debería manejar esto, pero es un fallback)
        router.push('/auth/login');
        return null;
    }

    return (
        <ProtectedRoute allowedRoles={['student']}>
            <div className={styles.notificationsPage}>
                <h1 className={styles.title}>Mis Notificaciones</h1>

                {notifications.length === 0 ? (
                    <div className={styles.emptyState}>
                        <p>No tienes notificaciones. ¡Todo tranquilo por aquí! 🎉</p>
                    </div>
                ) : (
                    <>
                        <div className={styles.actionsBar}>
                            <button className={styles.markAllReadButton} onClick={handleMarkAllAsRead}>
                                Marcar todas como leídas
                            </button>
                        </div>

                        <div className={styles.notificationsList}>
                            {notifications.map((notification) => (
                                <div key={notification.id} className={`${styles.notificationItem} ${notification.is_read ? styles.read : ''}`}>
                                    <div className={styles.notificationHeader}>
                                        <span className={styles.notificationType}>{notification.type.replace(/_/g, ' ')}</span>
                                        <span className={styles.notificationDate}>
                                            {new Date(notification.created_at).toLocaleString('es-ES', { dateStyle: 'medium', timeStyle: 'short' })}
                                        </span>
                                    </div>
                                    <p className={styles.notificationMessage}>{notification.message}</p>
                                    {notification.link && (
                                        <Link href={notification.link} className={styles.notificationLink} onClick={() => handleMarkAsRead(notification.id)}>
                                            Ver detalles
                                        </Link>
                                    )}
                                    <div className={styles.notificationActions}>
                                        {!notification.is_read && (
                                            <button className={styles.actionButton} onClick={() => handleMarkAsRead(notification.id)}>
                                                Marcar como leída
                                            </button>
                                        )}
                                        <button className={`${styles.actionButton} ${styles.deleteButton}`} onClick={() => handleDeleteNotification(notification.id)}>
                                            Eliminar
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {totalPages > 1 && (
                            <div className={styles.pagination}>
                                <button
                                    onClick={() => handlePageChange(currentPage - 1)}
                                    disabled={currentPage === 1}
                                    className={styles.paginationButton}
                                >
                                    Anterior
                                </button>
                                <span>Página {currentPage} de {totalPages}</span>
                                <button
                                    onClick={() => handlePageChange(currentPage + 1)}
                                    disabled={currentPage === totalPages}
                                    className={styles.paginationButton}
                                >
                                    Siguiente
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </ProtectedRoute>
    );
}