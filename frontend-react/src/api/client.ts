import { currentCsrfToken } from "../app/navigation";
import type { ApiErrorBody, CourseOffering, EnrollmentApiResult, PagePayload, SubmitResult } from "./types";

export const REACT_ACCEPT = "application/vnd.amoozeshyar.react+json";

export class PortalApiError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, error: ApiErrorBody) {
    super(error.message || "درخواست انجام نشد.");
    this.name = "PortalApiError";
    this.status = status;
    this.code = error.code || "request_failed";
  }
}

function redirectToLogin(): void {
  const loginHref = window.portalBootstrap?.loginUrl;
  if (!loginHref) return;
  const target = new URL(loginHref, window.location.href);
  if (new URLSearchParams(window.location.search).get("react") === "1") {
    target.searchParams.set("react", "1");
  }
  if (window.location.pathname !== target.pathname || window.location.search !== target.search) {
    window.location.assign(`${target.pathname}${target.search}`);
  }
}

function errorFromPayload(payload: unknown): ApiErrorBody {
  if (typeof payload === "object" && payload !== null && "error" in payload) {
    const error = (payload as { error?: unknown }).error;
    if (typeof error === "object" && error !== null) {
      const candidate = error as Partial<ApiErrorBody>;
      return {
        code: typeof candidate.code === "string" ? candidate.code : "request_failed",
        message: typeof candidate.message === "string" ? candidate.message : "درخواست انجام نشد.",
      };
    }
  }
  return { code: "request_failed", message: "پاسخ سامانه قابل خواندن نیست." };
}

async function requestJson<T>(url: string, init: RequestInit, allowValidationResponse = false): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", REACT_ACCEPT);
  if (init.body instanceof FormData) headers.delete("Content-Type");

  const response = await fetch(url, { ...init, headers, credentials: "same-origin" });
  const payload: unknown = await response.json().catch(() => null);
  if (response.status === 401) redirectToLogin();
  if (!response.ok && !(allowValidationResponse && response.status === 400)) {
    throw new PortalApiError(response.status, errorFromPayload(payload));
  }
  if (typeof payload !== "object" || payload === null) {
    throw new PortalApiError(response.status, {
      code: "invalid_response",
      message: "پاسخ سامانه قابل خواندن نیست.",
    });
  }
  return payload as T;
}

export const PortalApi = {
  getPage(url: string): Promise<PagePayload> {
    return requestJson<PagePayload>(url, { method: "GET" });
  },

  submitPage(url: string, values: FormData | Record<string, unknown>): Promise<SubmitResult> {
    const csrfToken = currentCsrfToken();
    if (!csrfToken) {
      throw new PortalApiError(403, {
        code: "csrf_token_missing",
        message: "نشست امن فرم در دسترس نیست؛ صفحه را تازه‌سازی کنید.",
      });
    }

    const isFormData = values instanceof FormData;
    return requestJson<SubmitResult>(
      url,
      {
        method: "POST",
        headers: {
          ...(isFormData ? {} : { "Content-Type": "application/json" }),
          "X-CSRFToken": csrfToken,
        },
        body: isFormData ? values : JSON.stringify(values),
      },
      true,
    );
  },

  getOfferings(termCode: string | null): Promise<{ offerings: CourseOffering[] }> {
    const query = termCode ? `?term=${encodeURIComponent(termCode)}` : "";
    return requestJson<{ offerings: CourseOffering[] }>(`/api/scheduling/offerings/${query}`, { method: "GET" });
  },

  registerOffering(offeringId: number, studentCode: string | null): Promise<EnrollmentApiResult> {
    return enrollmentPost(`/api/enrollment/register/${positiveId(offeringId, "offering")}/`, studentCode);
  },

  dropEnrollment(enrollmentId: number, studentCode: string | null): Promise<EnrollmentApiResult> {
    return enrollmentPost(`/api/enrollment/drop/${positiveId(enrollmentId, "enrollment")}/`, studentCode);
  },

  emergencyDropEnrollment(enrollmentId: number, studentCode: string | null): Promise<EnrollmentApiResult> {
    return enrollmentPost(`/api/enrollment/emergency-drop/${positiveId(enrollmentId, "enrollment")}/`, studentCode);
  },
};

function positiveId(value: number, kind: string): number {
  if (Number.isInteger(value) && value > 0) return value;
  throw new PortalApiError(400, {
    code: `invalid_${kind}_id`,
    message: "شناسهٔ عملیات معتبر نیست.",
  });
}

function enrollmentPost(path: string, studentCode: string | null): Promise<EnrollmentApiResult> {
  const csrfToken = currentCsrfToken();
  if (!csrfToken) {
    throw new PortalApiError(403, {
      code: "csrf_token_missing",
      message: "نشست امن عملیات در دسترس نیست؛ صفحه را تازه‌سازی کنید.",
    });
  }
  return requestJson<EnrollmentApiResult>(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(studentCode ? { student_code: studentCode } : {}),
  });
}
