import styles from "./styles/landing.module.scss";

export default function FeaturesSection() {
    return (
        <section className={styles.features}>
            <h2>¿Qué puedes hacer como estudiante?</h2>
            <div className={styles.featuresGrid}>
                <div className={styles.featureItem}>
                    <h3>🔍 Buscar prácticas</h3>
                    <p>Accede a vacantes alineadas con tu carrera.</p>
                </div>
                <div className={styles.featureItem}>
                    <h3>👤 Perfil profesional</h3>
                    <p>Crea un CV atractivo directamente en la plataforma.</p>
                </div>
                <div className={styles.featureItem}>
                    <h3>🧩 Desarrollar habilidades</h3>
                    <p>Lleva un registro de tus competencias y retos.</p>
                </div>
                <div className={styles.featureItem}>
                    <h3>🏢 Conectar con empresas</h3>
                    <p>Postula directamente a organizaciones interesadas.</p>
                </div>
            </div>
        </section>
    );
}
