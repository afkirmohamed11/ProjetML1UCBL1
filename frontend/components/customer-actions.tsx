"use client"

import { BellIcon } from "lucide-react"
import { IconRadar } from "@tabler/icons-react"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"

export default function CustomerActions({ customerId }: { customerId: string }) {
  async function handleNotifyCustomer() {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/notify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ customer_ids: [parseInt(customerId)] }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `HTTP ${res.status}`)
      }

      const json = await res.json()
      toast.success(json?.message || "Customer notified successfully!")
    } catch (err: any) {
      toast.error(`Notification failed: ${err?.message || String(err)}`)
    }
  }

  async function handlePredictChurn() {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ customer_ids: [parseInt(customerId)] }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `HTTP ${res.status}`)
      }

      const json = await res.json()
      toast.success(json?.message || "Churn prediction completed!")
    } catch (err: any) {
      toast.error(`Prediction failed: ${err?.message || String(err)}`)
    }
  }

  return (
    <>
      <Button variant="outline" onClick={handleNotifyCustomer}>
        <BellIcon className="h-4 w-4 mr-2" />
        Notify Customer
      </Button>
      <Button variant="outline" onClick={handlePredictChurn}>
        <IconRadar className="h-4 w-4 mr-2" />
        Predict Churn
      </Button>
    </>
  )
}
