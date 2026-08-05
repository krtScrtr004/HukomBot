import CenteredLayout from '@/layouts/CenteredLayout'
import LogoCard from '@/components/login/LoginCard'
import ThemeTogggle from '@/components/ui/ThemeToggle';

function Login() {
    return (
        <CenteredLayout className="bg-background relative p-0.5">
            <ThemeTogggle />

            <LogoCard />
        </CenteredLayout>
    )
}

export default Login;