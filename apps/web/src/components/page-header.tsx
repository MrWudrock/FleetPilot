import type { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  badge?: ReactNode;
};

export function PageHeader({ title, subtitle, actions, badge }: PageHeaderProps) {
  return (
    <header
      className="flex min-h-14 flex-wrap items-center justify-between gap-3 border-b border-zinc-200 bg-white px-4 py-3 sm:px-6"
      data-testid="page-header"
    >
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="text-lg font-semibold text-zinc-900" data-testid="page-title">
            {title}
          </h1>
          {badge}
        </div>
        {subtitle ? <p className="text-xs text-zinc-500">{subtitle}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </header>
  );
}
