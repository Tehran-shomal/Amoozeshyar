/* مبینا: ورود واقعی به نشست موجود سامانه. */
document.addEventListener("DOMContentLoaded", () => {
    const api = window.PortalApi, ui = window.PortalUI;
    const form = document.querySelector("[data-login-form]");
    form?.addEventListener("submit", async event => {
        event.preventDefault();
        const button = form.querySelector('[type="submit"]');
        button.disabled = true;
        const values = new FormData(form);
        try {
            await api.login({
                username: values.get("username"),
                password: values.get("password"),
                remember_me: values.get("remember_me") === "on",
            });
            const session = await api.me();
            if (!session.user) throw new Error("نشست تأیید نشد.");
            window.location.assign(form.dataset.loginRedirect);
        } catch (error) { ui.showStatus(ui.errorMessage(error), "[data-login-status]"); }
        finally { button.disabled = false; }
    });
});
