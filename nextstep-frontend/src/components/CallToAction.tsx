import Link from "next/link";

export default function CallToAction() {
    return (
        <div className="mt-8 flex gap-4 justify-center">
            <Link href="/auth/register">
                <button className="bg-green-700 text-white px-5 py-2 rounded-full hover:bg-green-800 transition">
                    Registrarse
                </button>
            </Link>
            <Link href="/auth/login">
                <button className="bg-white border border-green-700 text-green-700 px-5 py-2 rounded-full hover:bg-green-100 transition">
                    Iniciar sesión
                </button>
            </Link>
        </div>
    );
}
