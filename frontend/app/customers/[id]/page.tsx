import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import TableCellViewer from "@/components/TableCellViewer"
import CustomerActions from "@/components/customer-actions"
import type { PredictRecord } from "@/components/TableCellViewer"


export default async function CustomerPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const res = await fetch(
    `${process.env.API_INTERNAL_URL}/customers/${id}`,
    { cache: "no-store" }
  );

  const payload = await res.json();

  if (!res.ok) {
    return <div>Error: {payload.error || "Customer not found"}</div>;
  }

  const source = payload?.customer ?? payload;

  // Map either an object (column-named) or legacy array to PredictRecord
  const toRecord = (src: unknown): PredictRecord | null => {
      const o = src as Record<string, unknown>;
      const get = (k: string) => o[k];
      const bool = (v: unknown) => Boolean(v);
      const num = (v: unknown) => (typeof v === "number" ? v : Number(v ?? 0));
      return {
        gender: String(get("gender") ?? "-").toLowerCase(),
        senior_citizen: bool(get("senior_citizen")),
        partner: bool(get("partner")),
        dependents: bool(get("dependents")),
        tenure: num(get("tenure")),
        phone_service: bool(get("phone_service")),
        multiple_lines: String(get("multiple_lines") ?? "No"),
        internet_service: String(get("internet_service") ?? "No"),
        online_security: String(get("online_security") ?? "No"),
        online_backup: String(get("online_backup") ?? "No"),
        device_protection: String(get("device_protection") ?? "No"),
        tech_support: String(get("tech_support") ?? "No"),
        streaming_tv: String(get("streaming_tv") ?? "No"),
        streaming_movies: String(get("streaming_movies") ?? "No"),
        contract: String(get("contract") ?? "Month-to-month"),
        paperless_billing: bool(get("paperless_billing")),
        payment_method: String(get("payment_method") ?? ""),
        monthly_charges: num(get("monthly_charges")),
        total_charges: num(get("total_charges")),
        churned: typeof get("churn") === "boolean" ? (get("churn") as boolean) : false,
        status: String(get("status") ?? ""),
        notified: bool(get("notified")),
        first_name: String(get("first_name") ?? ""),
        last_name: String(get("last_name") ?? ""),
        email: String(get("email") ?? ""),
        churn_probability: num(get("churn_probability")),
      };

  };

  const mapped = toRecord(source);
  if (!mapped) {
    console.error("Unexpected customer response shape", payload);
    return <div>Error: Unexpected data format</div>;
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
        <SiteHeader title="Customer Details" />
          <div className="flex justify-center w-full px-4 lg:px-6">
              <div className="w-full md:max-w-6xl space-y-4">
                  <div className="rounded-xl border bg-background p-4">
                    <TableCellViewer data={mapped} />
                  </div>
                  <div className="flex items-center justify-end gap-2 p-4">
                    <CustomerActions customerId={id} />
                  </div>
              </div>
          </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
