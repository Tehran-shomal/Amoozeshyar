import type { PortalShellData } from "../api/types";
import { currentCsrfToken, portalPageHref } from "../app/navigation";
import type { PortalBootstrap } from "../types";

interface SidebarProps {
  shell: PortalShellData;
  page: string;
  bootstrap: PortalBootstrap;
  search: string;
  onClose: () => void;
}

export function Sidebar({ shell, page, bootstrap, search, onClose }: SidebarProps) {
  const query = search.trim().toLocaleLowerCase();
  return (
    <aside className="sidebar" id="portal-sidebar" aria-label="منوی اصلی">
      <a className="brand" href={portalPageHref("", bootstrap)} onClick={onClose}>
        <span className="brand-copy"><strong>آموزشیار</strong><small>دانشگاه آزاد اسلامی</small></span>
        <img className="university-logo" src="/static/core/azad-logo.png" alt="" />
      </a>
      <nav className="sidebar-nav" aria-label="بخش‌های سامانه">
        {shell.nav_groups.map((group, groupIndex) => {
          const items = group.items.filter((item) => !query || item.label.toLocaleLowerCase().includes(query));
          if (!items.length) return null;
          if (!group.title) {
            return items.map((item) => (
              <a
                className={`nav-link nav-link--dashboard${page === "home" ? " is-active" : ""}`}
                href={portalPageHref("", bootstrap)} key={`${groupIndex}-${item.slug}`} onClick={onClose}
              >
                <span className="nav-icon" aria-hidden="true">{item.icon}</span><span>{item.label}</span>
              </a>
            ));
          }
          const active = items.some((item) => item.slug === page);
          return (
            <details className="nav-group" data-nav-group={group.title} open={active} key={`${group.title}-${groupIndex}`}>
              <summary>{group.title}<span aria-hidden="true">⌄</span></summary>
              <span className="nav-group-reference" aria-hidden="true"><span>{group.title}</span><span>‹</span></span>
              <div className="nav-group-items">
                {items.map((item) => (
                  <a className={`nav-link${page === item.slug ? " is-active" : ""}`} href={portalPageHref(item.slug, bootstrap)} key={item.slug} onClick={onClose}>
                    <span className="nav-icon" aria-hidden="true">{item.icon}</span><span>{item.label}</span>
                  </a>
                ))}
              </div>
            </details>
          );
        })}
      </nav>
      <div className="sidebar-footer-links">
        {shell.sidebar_footer.map((item, index) => item.action ? (
          <form action={bootstrap.logoutUrl} method="post" className="logout-form" key={`${item.label}-${index}`}>
            <input type="hidden" name="csrfmiddlewaretoken" value={currentCsrfToken()} />
            <button type="submit"><span aria-hidden="true">{item.icon}</span>{item.label}</button>
          </form>
        ) : (
          <a href={portalPageHref(item.slug, bootstrap)} key={`${item.label}-${index}`} onClick={onClose}>
            <span aria-hidden="true">{item.icon}</span>{item.label}
          </a>
        ))}
      </div>
    </aside>
  );
}
