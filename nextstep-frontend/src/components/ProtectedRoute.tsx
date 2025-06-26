"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, ReactNode } from "react";

interface ProtectedRouteProps {
    children: ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
    const router = useRouter();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        console.log("Token en ProtectedRoute:", token);

        if (!token) {
            router.push("/auth/login");
        } else {
            setLoading(false);
        }
    }, [router]);

    if (loading) {
        return <div>Cargando...</div>;
    }

    return <>{children}</>;
}
