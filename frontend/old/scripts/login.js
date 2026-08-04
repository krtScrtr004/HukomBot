(() => {
    const root = document.documentElement;

    const themeToggle = document.getElementById('themeToggle');
    const themeToggleIcon = document.getElementById('themeToggleIcon');
    const themeToggleLabel = document.getElementById('themeToggleLabel');
    const themeColorMeta = document.getElementById('theme-color-meta');

    const googleLoginButton = document.getElementById('googleLoginButton');
    const googleLoginLabel = document.getElementById('googleLoginLabel');
    const googleLoginAssistive = document.getElementById('googleLoginAssistive');
    const googleButtonMarkup = googleLoginLabel.innerHTML;

    function setTheme(theme) {
        root.dataset.theme = theme;
        localStorage.setItem('hukombot-theme', theme);

        const isDark = theme === 'dark';
        themeToggle.setAttribute('aria-pressed', String(isDark));
        themeToggleIcon.textContent = isDark ? '☀' : '☾';
        themeToggleLabel.textContent = isDark ? 'Light mode' : 'Dark mode';
        themeColorMeta.setAttribute('content', isDark ? '#111827' : '#f7f8fa');
    }

    function getTheme() {
        return root.dataset.theme === 'dark' ? 'dark' : 'light';
    }

    function setGoogleLoading(isLoading) {
        googleLoginButton.disabled = isLoading;

        if (isLoading) {
            googleLoginLabel.innerHTML = '<span class="provider-button__spinner" aria-hidden="true"></span><span>Signing in with Google…</span>';
            googleLoginAssistive.textContent = 'Google authentication in progress.';
            return;
        }

        googleLoginLabel.innerHTML = googleButtonMarkup;
        googleLoginAssistive.textContent = 'Google authentication is ready.';
    }

    function handleGoogleLogin(e) {
        if (googleLoginButton.disabled) {
            return;
        }

        try {
            const url = googleLoginButton.getAttribute("data-redirect-url")
            if (!url) {
                throw Error("Google login error")
            }

            setGoogleLoading(true);
            window.location.href = url
        } catch (error) {
            console.error(error)
        } finally {
            setGoogleLoading(false);
        }
    }

    themeToggle.addEventListener('click', () => {
        setTheme(getTheme() === 'dark' ? 'light' : 'dark');
    });

    googleLoginButton.addEventListener('click', handleGoogleLogin);

    window.handleGoogleLogin = handleGoogleLogin;

    setTheme(
        localStorage.getItem('hukombot-theme') || 
        root.dataset.theme || 
        'light'
    );
})();
