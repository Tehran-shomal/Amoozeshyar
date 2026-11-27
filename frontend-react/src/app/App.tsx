import { useEffect, useState } from "react";
import { PortalApi, PortalApiError } from "../api/client";
import type { PagePayload } from "../api/types";
import type { PortalBootstrap } from "../types";
import { PortalShell } from "../components/PortalShell";
import { LoginPage } from "../pages/LoginPage";
import { SystemErrorPage } from "../pages/SystemErrorPage";
import { resolvePage } from "./routes";

interface AppProps {
  bootstrap?: PortalBootstrap;
}

export function App({ bootstrap }: AppProps) {
  const [payload, setPayload] = useState<PagePayload | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (resolvePage(window.location.pathname).kind !== "portal") return;
    if (!bootstrap?.apiUrl) {
      setError(new Error("اطلاعات شروع پرتال در دسترس نیست."));
      return;
    }
    let active = true;
    PortalApi.getPage(bootstrap.apiUrl)
      .then((page) => {
        if (active) setPayload(page);
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(reason instanceof Error ? reason : new Error("دریافت صفحه انجام نشد."));
        }
      });
    return () => {
      active = false;
    };
  }, [bootstrap?.apiUrl]);

  if (!bootstrap) {
    return <main className="portal-page-loading" role="alert">اطلاعات شروع پرتال در دسترس نیست.</main>;
  }
  const route = resolvePage(window.location.pathname);
  if (route.kind === "login" && bootstrap.kind === "login") {
    return <LoginPage copy={bootstrap.loginCopy || {}} error={bootstrap.loginError || ""} loginUrl={bootstrap.loginUrl} />;
  }
  if (route.kind !== "portal" || route.slug !== bootstrap.page) {
    return <main className="portal-page-loading" role="alert">این مسیر برای پیش‌نمایش React ثبت نشده است.</main>;
  }
  if (error) {
    const status = error instanceof PortalApiError ? error.status : 0;
    const title = status === 503 ? "دیتابیس آمادهٔ پاسخ‌گویی نیست" : status === 401 ? "نشست شما نیاز به ورود دوباره دارد" : "بارگذاری صفحه انجام نشد";
    const message = status === 503
      ? "ساختار یا دسترسی دیتابیس باید توسط مسئول سامانه بررسی شود. هیچ اطلاعات نمایشی جایگزین نشده است."
      : status === 401
        ? "برای ادامه دوباره وارد سامانه شوید."
        : status === 403
          ? "دسترسی به اطلاعات درخواستی برای این حساب مجاز نیست."
          : error.message;
    return <SystemErrorPage status={status} title={title} message={message} onRetry={() => window.location.reload()} />;
  }
  if (!payload) {
    return <main className="portal-page-loading" role="status" aria-live="polite">در حال دریافت اطلاعات…</main>;
  }
  return <PortalShell bootstrap={bootstrap} payload={payload} />;
}
