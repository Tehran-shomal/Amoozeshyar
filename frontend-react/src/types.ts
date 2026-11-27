export interface PortalBootstrap {
  page: string;
  apiUrl: string;
  submitUrl: string;
  loginUrl: string;
  logoutUrl: string;
  homeUrl: string;
  sectionUrlTemplate: string;
  kind?: "portal" | "login";
  loginCopy?: Record<string, string>;
  loginError?: string;
}

declare global {
  interface Window {
    portalBootstrap?: PortalBootstrap;
  }
}
