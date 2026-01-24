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

  // Map backend response to PredictRecord
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
        // Get churn from prediction if available, otherwise from customer table
        churned: get("churn_prediction") !== null && get("churn_prediction") !== undefined 
          ? bool(get("churn_prediction")) 
          : bool(get("churn")),
        // Build status from notified and feedback data
        status: (() => {
          const feedbackAnswer = get("feedback_answer");
          const feedbackDate = get("feedback_date");
          const notifiedDate = get("notified_date");
          
          if (feedbackDate && feedbackAnswer) {
            return String(feedbackAnswer).toLowerCase() === "yes" ? "responded_ok" : "responded_no";
          }
          if (notifiedDate) {
            return "notified";
          }
          return "not_notified";
        })(),
        notified: bool(get("notified_date")),
        first_name: String(get("first_name") ?? ""),
        last_name: String(get("last_name") ?? ""),
        email: String(get("email") ?? ""),
        churn_probability: num(get("churn_probability")),
        // Include notification and feedback dates
        notified_date: get("notified_date") ? String(get("notified_date")) : undefined,
        feedback_date: get("feedback_date") ? String(get("feedback_date")) : undefined,
        feedback_answer: get("feedback_answer") ? String(get("feedback_answer")) : undefined,
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
