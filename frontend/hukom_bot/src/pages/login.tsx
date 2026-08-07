import CenteredLayout from '@/layouts/CenteredLayout'
import LogoCard from '@/components/login/LoginCard'
import ThemeTogggle from '@/components/ui/ThemeToggle';

export default function Login() {
    return (
        <CenteredLayout className="bg-background relative p-0.5">
            <ThemeTogggle className="bg-background absolute top-5 right-5 rounded-full border border-primary hover:bg-primary hover:text-background" />

            <LogoCard />
        </CenteredLayout>
    )
}