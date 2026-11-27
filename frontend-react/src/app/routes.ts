const portalSlugs = new Set([
  "home",
  "academic-activities",
  "add-drop",
  "announcements",
  "attendance",
  "calendar",
  "curriculum",
  "education-certificate",
  "emergency-drop",
  "enrollment",
  "evaluation",
  "evaluation-form",
  "exam-card",
  "financial-aid",
  "grade-appeal",
  "graduation",
  "graduation-certificate",
  "guest-request",
  "guide",
  "internship",
  "messages",
  "notifications",
  "payments",
  "registration-status",
  "requests",
  "schedule",
  "secure-payment",
  "selected-courses",
  "settings",
  "student-card",
  "support",
  "transcript",
  "tuition",
]);

export type ResolvedRoute =
  | { kind: "portal"; slug: string }
  | { kind: "login" }
  | { kind: "not-found" };

export function resolvePage(pathname: string): ResolvedRoute {
  if (pathname === "/login/" || pathname === "/login") return { kind: "login" };
  if (pathname === "/" || pathname === "") return { kind: "portal", slug: "home" };
  const match = pathname.match(/^\/portal\/([a-z0-9-]+)\/?$/i);
  if (match && portalSlugs.has(match[1])) return { kind: "portal", slug: match[1] };
  return { kind: "not-found" };
}

export function hasReactPage(slug: string): boolean {
  return portalSlugs.has(slug);
}

export function getReactPageSlugs(): string[] {
  return [...portalSlugs].sort();
}
