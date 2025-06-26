import styles from "@/components/styles/landing.module.scss";
import LandingHeader from "@/components/LandingHeader";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import LandingFooter from "@/components/LandingFooter";

export default function Home() {
  return (
    <main className={styles.containter}>
      <LandingHeader />
      <HeroSection />
      <FeaturesSection />
      <LandingFooter />
    </main>
  );
}
