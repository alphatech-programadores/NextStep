import Link from "next/link";
import styles from "./styles/landing.module.scss";

export default function LandingPage() {
    return (
        <div className={styles.pageWrapper}>
            <section className={styles.hero}>
                <div className={styles.overlay}></div>
                <div className={styles.heroContent}>
                    <h2>Bienvenido a</h2>
                    <h1>NextStep</h1>
                    <p>
                        El puente entre tu formación académica y tu práctica profesional.
                        Encuentra vacantes reales, aplica fácilmente y haz crecer tu perfil.
                    </p>
                    <Link href="/auth/register" className={styles.ctaButton}>
                        Comienza ahora
                    </Link>
                </div>
            </section>

            <section className={styles.features}>
                <h2>¿Qué puedes hacer como estudiante?</h2>
                <div className={styles.featuresGrid}>
                    <div className={styles.featureItem}>
                        <h3>🔍 Buscar prácticas</h3>
                        <p>Accede a vacantes alineadas con tu carrera profesional.</p>
                    </div>
                    <div className={styles.featureItem}>
                        <h3>👤 Crear tu perfil</h3>
                        <p>
                            Muestra tus habilidades, sube tu CV, enlaza tu portafolio y genera
                            una presentación profesional.
                        </p>
                    </div>
                    <div className={styles.featureItem}>
                        <h3>🧩 Desarrollar habilidades</h3>
                        <p>
                            Registra competencias adquiridas, retos superados y experiencias
                            clave.
                        </p>
                    </div>
                    <div className={styles.featureItem}>
                        <h3>📨 Postular y recibir feedback</h3>
                        <p>
                            Postula a vacantes, consulta tu estado y recibe retroalimentación
                            útil.
                        </p>
                    </div>
                </div>
            </section>

            <section className={styles.institutionSection}>
                <h2>¿Eres una institución?</h2>
                <p>
                    Publica vacantes, gestiona postulaciones y encuentra talento joven que
                    impulse tu organización.
                </p>
                <Link href="/auth/register" className={styles.ctaButtonSecondary}>
                    Registrarse como institución
                </Link>
            </section>

            <section className={styles.whySection}>
                <h2>¿Por qué NextStep?</h2>
                <ul className={styles.whyList}>
                    <li>✅ Interfaz intuitiva para estudiantes e instituciones.</li>
                    <li>✅ Seguimiento en tiempo real de postulaciones.</li>
                    <li>✅ Enlace directo entre el CV del estudiante y la vacante.</li>
                    <li>✅ Notificaciones automáticas y comunicación clara.</li>
                    <li>✅ Feedback estructurado para mejorar continuamente.</li>
                    <li>✅ Plataforma diseñada por y para estudiantes universitarios.</li>
                </ul>
            </section>

            <section className={styles.faqSection}>
                <h2>Preguntas Frecuentes</h2>
                <div className={styles.faqItem}>
                    <h3>¿Qué tipo de vacantes se publican?</h3>
                    <p>
                        Vacantes para prácticas profesionales, estadías técnicas y oportunidades de
                        vinculación en múltiples sectores del conocimiento.
                    </p>
                </div>
                <div className={styles.faqItem}>
                    <h3>¿Necesito experiencia previa?</h3>
                    <p>
                        No, muchas vacantes están diseñadas específicamente para estudiantes sin
                        experiencia laboral previa.
                    </p>
                </div>
                <div className={styles.faqItem}>
                    <h3>¿Cuánto cuesta usar NextStep?</h3>
                    <p>NextStep es completamente gratuito para estudiantes.</p>
                </div>
                <div className={styles.faqItem}>
                    <h3>¿Las instituciones verifican los perfiles?</h3>
                    <p>
                        Sí, las instituciones revisan la información del perfil antes de aceptar
                        postulaciones. La transparencia es clave.
                    </p>
                </div>
                <div className={styles.faqItem}>
                    <h3>¿Puedo actualizar mi perfil después de postular?</h3>
                    <p>
                        Sí, puedes editar tu perfil en cualquier momento y tus cambios se reflejarán
                        automáticamente en futuras postulaciones.
                    </p>
                </div>
            </section>

            <footer className={styles.footer}>
                <div className={styles.footerContent}>
                    <p>© 2025 NextStep. Todos los derechos reservados.</p>
                    <p>
                        Desarrollado por estudiantes para estudiantes, con el objetivo de
                        conectar talento con oportunidades reales.
                    </p>
                </div>
            </footer>
        </div>
    );
}
