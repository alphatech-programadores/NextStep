import styles from "@/components/styles/landing.module.scss";
import LandingHeader from "@/components/LandingHeader";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import LandingPage from "@/components/LandingPage";
import LandingFooter from "@/components/LandingFooter";
import "leaflet/dist/leaflet.css";


export default function Home() {
  return (
    <main className={styles.containter}>
      <LandingPage />
    </main>
  );
}
