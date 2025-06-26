import styles from "./styles/landing.module.scss";

export default function HeroSection() {
    return (
        <section className={styles.hero}>
            <h2>Bienvenido a</h2>
            <h1>NextStep</h1>
            <p>El puente entre tu formación y la práctica profesional. Encuentra oportunidades reales para desarrollarte.</p>
            <a href="/auth/register" className={styles.ctaButton}>Comienza ahora</a>
        </section>
    );
}
