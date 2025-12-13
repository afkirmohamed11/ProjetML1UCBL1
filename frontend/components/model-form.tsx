"use client"

import { Button } from "@/components/ui/button"
import {
  Field,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { useState } from "react"

export function ModelForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [customer, setCustomer] = useState({
    name: "",
    email: "",
    age: "",
    tenure: "",
    monthlyCharges: "",
  })

  const [prediction, setPrediction] = useState<string | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setCustomer((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // Simulate a prediction API call
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(customer),
    })
    const data = await response.json()
    setPrediction(data.churn ? "Churn" : "No Churn")
  }

  return (
    <form className="p-6 md:p-8" onSubmit={handleSubmit}>
      <FieldGroup>
        <div className="flex flex-col items-center gap-2 text-center">
          <h1 className="text-2xl font-bold">Try the model</h1>
          <p className="text-muted-foreground text-balance">
            Fill out the form below to predict customer churn.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field>
            <FieldLabel htmlFor="name">Name</FieldLabel>
            <Input
              id="name"
              name="name"
              value={customer.name}
              onChange={handleChange}
              required
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="email">Email</FieldLabel>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="m@example.com"
              value={customer.email}
              onChange={handleChange}
              required
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="age">Age</FieldLabel>
            <Input
              id="age"
              name="age"
              type="number"
              value={customer.age}
              onChange={handleChange}
              required
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="tenure">Tenure (months)</FieldLabel>
            <Input
              id="tenure"
              name="tenure"
              type="number"
              value={customer.tenure}
              onChange={handleChange}
              required
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="monthlyCharges">Monthly Charges</FieldLabel>
            <Input
              id="monthlyCharges"
              name="monthlyCharges"
              type="number"
              value={customer.monthlyCharges}
              onChange={handleChange}
              required
            />
          </Field>
        </div>
        <Field>
          <Button type="submit">Predict</Button>
        </Field>
      </FieldGroup>
      {prediction && (
        <div className="prediction-result">
          <h3>Prediction: {prediction}</h3>
        </div>
      )}
    </form>
  )
}
