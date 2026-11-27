import type { PortalBootstrap } from "../types";

export function portalPageHref(slug: string, bootstrap: PortalBootstrap): string {
  const url = new URL(
    slug ? bootstrap.sectionUrlTemplate.replace("__slug__", encodeURIComponent(slug)) : bootstrap.homeUrl,
    window.location.origin,
  );
  const current = new URLSearchParams(window.location.search);
  for (const key of ["student_code", "term", "react", "legacy"]) {
    const value = current.get(key);
    if (value) url.searchParams.set(key, value);
  }
  return `${url.pathname}${url.search}`;
}

export function currentCsrfToken(): string {
  const cookie = document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith("csrftoken="));
  if (cookie) return decodeURIComponent(cookie.slice("csrftoken=".length));
  return document.querySelector<HTMLInputElement>(
    "#portal-csrf-token input[name='csrfmiddlewaretoken']",
  )?.value || "";
}
