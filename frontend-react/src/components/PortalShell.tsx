import { useEffect, useState } from "react";
import type { PagePayload } from "../api/types";
import type { PortalBootstrap } from "../types";
import { PageRenderer } from "./PageRenderer";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

interface PortalShellProps {
  bootstrap: PortalBootstrap;
  payload: PagePayload;
}

export function PortalShell({ bootstrap, payload }: PortalShellProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    document.body.classList.toggle("sidebar-open", menuOpen);
    return () => document.body.classList.remove("sidebar-open");
  }, [menuOpen]);

  useEffect(() => {
    const input = document.querySelector<HTMLInputElement>("[data-global-search]");
    if (!input) return;
    const update = () => setSearch(input.value);
    input.addEventListener("input", update);
    return () => input.removeEventListener("input", update);
  }, [payload.page]);

  return (
    <div className="portal-shell" data-portal-page={payload.page} data-page-api-url={bootstrap.apiUrl}>
      <Sidebar shell={payload.shell} page={payload.page} bootstrap={bootstrap} search={search} onClose={() => setMenuOpen(false)} />
      <button className="sidebar-backdrop" type="button" aria-label="بستن منو" onClick={() => setMenuOpen(false)} />
      <div className="portal-main">
        {payload.shell.profile_notice && <div className="inline-notice" role="status"><p>{payload.shell.profile_notice}</p></div>}
        <Topbar shell={payload.shell} onMenuToggle={() => setMenuOpen((value) => !value)} />
        <main className="workspace">
          <PageRenderer payload={payload} bootstrap={bootstrap} />
        </main>
      </div>
    </div>
  );
}
