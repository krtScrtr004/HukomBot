import { useSearchParams } from 'react-router-dom';
import { useToast } from '@/contexts/ToastProvider';
import CenteredLayout from '@/layouts/CenteredLayout'
import LogoCard from '@/components/login/LoginCard'
import ThemeTogggle from '@/components/ui/ThemeToggle';
import { useEffect } from 'react';

export default function Login() {
    const [searchParams] = useSearchParams();
    const {showToast} = useToast();

    const hasError = searchParams.get("error_code");

    useEffect(() => {
        if (!hasError) {
            return;
        }

        showToast("Something went wrong while logging in! Please try again.", "error");
    }, [])

    return (
        <CenteredLayout className="bg-background relative p-0.5">
            <ThemeTogggle className="bg-background absolute top-5 right-5 rounded-full border border-primary hover:bg-primary hover:text-background" />

            <LogoCard />
        </CenteredLayout>
    )
}