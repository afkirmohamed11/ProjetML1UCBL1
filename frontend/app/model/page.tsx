import { AppSidebar } from "@/components/app-sidebar"
import { ModelForm } from "@/components/model-form"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import TableCellViewer, { PredictRecord } from "@/components/TableCellViewer"


export default function Page() {
  const exampleRecord: PredictRecord = {
    gender: "Female",
    senior_citizen: false,
    partner: true,
    dependents: false,
    tenure: 24,
    phone_service: true,
    multiple_lines: "No",
    internet_service: "Fiber optic",
    online_security: "No",
    online_backup: "Yes",
    device_protection: "No",
    tech_support: "No",
    streaming_tv: "Yes",
    streaming_movies: "No",
    contract: "Month-to-month",
    paperless_billing: true,
    payment_method: "Electronic check",
    monthly_charges: 70.35,
    total_charges: 1688.2,
    churn_probability: 0.17,
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
                <TableCellViewer data={exampleRecord} />
              </div>
          </div>
      </SidebarInset>
    </SidebarProvider>
  )
}



