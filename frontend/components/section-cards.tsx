import { IconTrendingDown, IconTrendingUp, IconAlertTriangle, IconUsers, IconBell } from "@tabler/icons-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

interface DashboardStats {
  total_customers: number
  churn_percentage: number
  churn_count: number
  notified_count: number
  at_risk_count: number
  response_rate: number
  customers_with_predictions: number
}

async function fetchDashboardStats(): Promise<DashboardStats | null> {
  try {
    const res = await fetch(`${process.env.API_INTERNAL_URL}/dashboard/stats`, {
      cache: "no-store",
    })
    if (!res.ok) return null
    return res.json()
  } catch (error) {
    console.error("Failed to fetch dashboard stats:", error)
    return null
  }
}

export async function SectionCards() {
  const stats = await fetchDashboardStats()

  // Fallback values if API fails
  const totalCustomers = stats?.total_customers ?? 0
  const churnPercentage = stats?.churn_percentage ?? 0
  const atRiskCount = stats?.at_risk_count ?? 0
  const notifiedCount = stats?.notified_count ?? 0
  const responseRate = stats?.response_rate ?? 0

  const isHighChurn = churnPercentage > 20
  const isLowResponse = responseRate < 50

  return (
    <div className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Churn Rate</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {churnPercentage}%
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className={isHighChurn ? "border-red-300 text-red-600" : "border-green-300 text-green-600"}>
              {isHighChurn ? <IconTrendingUp /> : <IconTrendingDown />}
              {isHighChurn ? "High" : "Normal"}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {stats?.churn_count ?? 0} customers predicted to churn
          </div>
          <div className="text-muted-foreground">
            {isHighChurn ? "Urgent attention required" : "Within acceptable range"}
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Total Customers</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {totalCustomers.toLocaleString()}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              <IconUsers className="size-3" />
              Active
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {stats?.customers_with_predictions ?? 0} have predictions
          </div>
          <div className="text-muted-foreground">
            In the customer database
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>At-Risk Customers</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {atRiskCount.toLocaleString()}
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className={atRiskCount > 0 ? "border-amber-300 text-amber-600" : "border-green-300 text-green-600"}>
              <IconAlertTriangle className="size-3" />
              {atRiskCount > 0 ? "Alert" : "OK"}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            High churn probability (&gt;70%)
          </div>
          <div className="text-muted-foreground">
            {atRiskCount > 0 ? "Consider proactive outreach" : "No immediate concerns"}
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card">
        <CardHeader>
          <CardDescription>Notified Customers</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            {notifiedCount.toLocaleString()}
          </CardTitle>
          <CardAction>
            <Badge variant="outline">
              <IconBell className="size-3" />
              {responseRate}% responded
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-1.5 text-sm">
          <div className="line-clamp-1 flex gap-2 font-medium">
            {isLowResponse && notifiedCount > 0 ? "Low response rate" : "Engagement tracking"}
          </div>
          <div className="text-muted-foreground">
            Retention outreach sent
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
