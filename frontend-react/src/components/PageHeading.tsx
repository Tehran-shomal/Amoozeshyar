import type { NavigationGroup } from "../api/types";

interface PageHeadingProps {
  title: string;
  subtitle: string;
  groups: NavigationGroup[];
  slug: string;
  homeUrl: string;
}

export function PageHeading({ title, subtitle, groups, slug, homeUrl }: PageHeadingProps) {
  const group = groups.find((item) => item.items.some((link) => link.slug === slug));
  return (
    <header className="section-page-heading">
      <nav className="breadcrumbs" aria-label="مسیر صفحه">
        <a href={homeUrl}>داشبورد</a>
        {group?.title && <><span aria-hidden="true">/</span><span>{group.title}</span></>}
      </nav>
      <h1>{title}</h1>
      {subtitle && <p>{subtitle}</p>}
    </header>
  );
}
