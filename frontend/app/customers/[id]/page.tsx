import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import TableCellViewer from "@/components/TableCellViewer"


export default async function CustomerPage({ params }: { params: { id: string } }) {
  // Ensure params is resolved
  const resolvedParams = await params;

  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/customers/${resolvedParams.id}`,
    { cache: "no-store" }
  );

  const customer = await res.json();

  if (!res.ok) {
    return <div>Error: {customer.error || "Customer not found"}</div>;
  }

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader title="Try Out The Model" />
          <div className="w-full md:max-w-6xl">
              <div className="rounded-xl border bg-background p-4">
                <TableCellViewer data={customer} />
              </div>
          </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
