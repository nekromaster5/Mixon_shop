document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('registration-modal');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('registration-form');
    if (!modal || !loginForm || !registerForm) return;

    const dialog = modal.querySelector('.registration-modal__dialog');
    const closeButton = modal.querySelector('[data-registration-close]');
    const tabs = modal.querySelectorAll('[data-auth-tab]');
    const panels = { login: loginForm, register: registerForm };

    const password = registerForm.querySelector('input[name="password1"]');
    const passwordConfirmation = registerForm.querySelector('input[name="password2"]');
    const passwordError = document.getElementById('registration-password-error');
    let returnFocusTo = null;

    const switchTab = name => {
        tabs.forEach(tab => {
            const isActive = tab.dataset.authTab === name;
            tab.classList.toggle('is-active', isActive);
            tab.setAttribute('aria-selected', String(isActive));
        });
        Object.entries(panels).forEach(([key, panel]) => { panel.hidden = key !== name; });
        panels[name].querySelector('input')?.focus();
    };

    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.authTab));
    });

    const openModal = (trigger, tab = 'login') => {
        returnFocusTo = trigger;
        modal.hidden = false;
        document.body.classList.add('registration-modal-open');
        window.requestAnimationFrame(() => {
            modal.classList.add('is-open');
            switchTab(tab);
        });
    };
    const closeModal = () => {
        modal.classList.remove('is-open');
        document.body.classList.remove('registration-modal-open');
        modal.hidden = true;
        passwordError.hidden = true;
        passwordConfirmation.setCustomValidity('');
        returnFocusTo?.focus();
    };

    document.addEventListener('click', event => {
        const trigger = event.target.closest('[data-registration-trigger]');
        if (!trigger) return;
        event.preventDefault();
        event.stopImmediatePropagation();
        openModal(trigger, trigger.dataset.registrationTrigger || 'login');
    }, true);
    closeButton.addEventListener('click', closeModal);
    modal.addEventListener('click', event => { if (event.target === modal) closeModal(); });
    dialog.addEventListener('click', event => event.stopPropagation());
    document.addEventListener('keydown', event => { if (!modal.hidden && event.key === 'Escape') closeModal(); });

    const validatePasswords = () => {
        const mismatch = Boolean(passwordConfirmation.value && password.value !== passwordConfirmation.value);
        passwordConfirmation.setCustomValidity(mismatch ? gettext('Пароли не совпадают') : '');
        passwordError.hidden = !mismatch;
        return !mismatch;
    };
    password.addEventListener('input', validatePasswords);
    passwordConfirmation.addEventListener('input', validatePasswords);
    registerForm.addEventListener('submit', event => {
        if (!validatePasswords()) { event.preventDefault(); passwordConfirmation.focus(); }
    });
});
