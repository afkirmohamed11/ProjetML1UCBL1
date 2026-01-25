import { AppSidebar } from "@/components/app-sidebar"
import { DataTable } from "@/components/data-table"
import { SiteHeader } from "@/components/site-header"
import { ChatbotButton } from "@/components/chatbot"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"


export default async function Page() {

  const res = await fetch(
    `${process.env.API_INTERNAL_URL}/customers`,
    { cache: "no-store" }
  );

  const rawCustomers = await res.json();
  
  // Backend now returns objects directly, not arrays
  const customers = Array.isArray(rawCustomers.customers)
    ? rawCustomers.customers
    : [];

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
        <SiteHeader title="Customers" />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              <DataTable data={customers} />
            </div>
          </div>
        </div>
        <ChatbotButton />
      </SidebarInset>
    </SidebarProvider>
  )
}
