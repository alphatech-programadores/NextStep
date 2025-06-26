import styles from "./styles/landing.module.scss";

export default function LandingFooter() {
    return (
        <footer className={styles.footer}>
            © {new Date().getFullYear()} NextStep. Todos los derechos reservados.
        </footer>
    );
}
