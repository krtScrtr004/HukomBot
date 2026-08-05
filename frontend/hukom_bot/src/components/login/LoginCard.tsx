import googleLogo from '@/assets/icon/google.png';

import Logo from '@/components/ui/Logo';
import ProviderButton from '@/components/ui/ProviderButton';

export default function LoginCard() {
	return (
		<>
			<section className="bg-surface flex flex-col items-center justify-center w-100 p-5 gap-10 rounded-md shadow-lg font-sans transition-colors duration-fast">
				<div>
					<Logo />

					<p className="text-center text-base text-text-primary font-body">
						AI Legal Research
					</p>
				</div>

				<div>
					<h1 className="text-center text-3xl text-text-primary font-heading mb-3">
						Welcome to HukomBot
					</h1>

					<p className="text-center text-l text-text-secondary">
						AI-powered legal research and case analysis for
						Philippine jurisprudence
					</p>
				</div>

				<section className="w-full">
					{/* Google Login */}
					<ProviderButton
						id="google_login_button"
						title="Google"
						link="http://127.0.0.1:8000/api/v1/auth/google/login"
						imgSrc={googleLogo}
					/>
				</section>
			</section>
		</>
	);
}