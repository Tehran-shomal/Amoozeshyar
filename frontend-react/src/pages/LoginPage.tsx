import { currentCsrfToken } from "../app/navigation";

interface LoginPageProps {
  copy: Record<string, string>;
  error: string;
  loginUrl: string;
}

export function LoginPage({ copy, error, loginUrl }: LoginPageProps) {
  const csrfToken = currentCsrfToken();
  const currentUrl = `${window.location.pathname}${window.location.search}`;

  return (
    <main className="login-page">
      <section className="login-card" aria-label={copy.brand_title || "ورود به سامانه"}>
        <div className="login-brand-panel">
          <div className="login-brand-heading">
            <span className="login-university">{copy.university}</span>
            <img className="login-logo" src="/static/core/azad-logo.png" alt="" />
          </div>
          <div className="login-brand-copy">
            <h1>{copy.brand_title}</h1>
            <h2>{copy.brand_slogan}</h2>
            <p>{copy.brand_description}</p>
          </div>
          <div className="login-art" aria-hidden="true">
            <span className="login-art-circle login-art-circle--one" />
            <span className="login-art-circle login-art-circle--two" />
          </div>
          <p className="login-brand-footer">{copy.brand_version}</p>
        </div>
        <div className="login-form-panel">
          <div className="login-heading">
            <span className="eyebrow">{copy.heading}</span>
            <h2>{copy.heading}</h2>
            <p>{copy.intro}</p>
          </div>
          <form className="login-form" method="post" action={currentUrl || loginUrl} autoComplete="on">
            <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
            <label className="form-field">
              <span>{copy.username_label}</span>
              <input type="text" name="username" placeholder={copy.username_placeholder} autoComplete="username" required />
            </label>
            <label className="form-field">
              <span>{copy.password_label}</span>
              <input type="password" name="password" placeholder={copy.password_placeholder} autoComplete="current-password" required />
            </label>
            <div className="login-options">
              <label><input type="checkbox" name="remember_me" /><span>{copy.remember}</span></label>
              <span className="login-recovery">{copy.recovery}</span>
            </div>
            <button className="button button--primary button--wide" type="submit">{copy.submit} <span aria-hidden="true">←</span></button>
          </form>
          {copy.warning && <div className="login-warning" role="note"><span aria-hidden="true">i</span><p>{copy.warning}</p></div>}
          {error && <div className="inline-notice" role="alert"><span aria-hidden="true">!</span><p>{error}</p></div>}
          <span className="login-support-link">{copy.support}</span>
        </div>
      </section>
    </main>
  );
}
