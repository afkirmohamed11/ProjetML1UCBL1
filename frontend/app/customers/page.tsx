import { AppSidebar } from "@/components/app-sidebar"
import { DataTable } from "@/components/data-table"
import { SiteHeader } from "@/components/site-header"
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
  // console.log("Fetched customers:", rawCustomers);


  const customers = Array.isArray(rawCustomers.customers)
    ? rawCustomers.customers.map((customer) => ({
        id: customer[0],
        gender: customer[1],
        seniorCitizen: customer[2],
        partner: customer[3],
        dependents: customer[4],
        tenure: customer[5],
        phoneService: customer[6],
        multipleLines: customer[7],
        internetService: customer[8],
        onlineSecurity: customer[9],
        onlineBackup: customer[10],
        deviceProtection: customer[11],
        techSupport: customer[12],
        streamingTV: customer[13],
        streamingMovies: customer[14],
        contract: customer[15],
        paperlessBilling: customer[16],
        paymentMethod: customer[17],
        monthlyCharges: customer[18],
        totalCharges: customer[19],
        churn: customer[20],
        status: customer[21],
        notified: customer[22],
        updated_at: customer[23],
        first_name: customer[24],
        last_name: customer[25],
        email: customer[26],
      }))
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
      </SidebarInset>
    </SidebarProvider>
  )
}
