import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./app/App";
import "./app.css";
import type { PortalBootstrap } from "./types";

const rootElement = document.getElementById("portal-react-root");
const bootstrapElement = document.getElementById("portal-bootstrap-data");

if (rootElement) {
  let bootstrap: PortalBootstrap | undefined;
  try {
    bootstrap = bootstrapElement
      ? (JSON.parse(bootstrapElement.textContent || "") as PortalBootstrap)
      : undefined;
    window.portalBootstrap = bootstrap;
  } catch {
    bootstrap = undefined;
  }

  createRoot(rootElement).render(
    <StrictMode>
      <App bootstrap={bootstrap} />
    </StrictMode>,
  );
}
