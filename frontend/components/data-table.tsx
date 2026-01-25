"use client"

import * as React from "react"
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type UniqueIdentifier,
} from "@dnd-kit/core"
import { restrictToVerticalAxis } from "@dnd-kit/modifiers"
import {
  arrayMove,
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import {
  IconChevronDown,
  IconChevronLeft,
  IconChevronRight,
  IconChevronsLeft,
  IconChevronsRight,
  IconCircleCheckFilled,
  IconDotsVertical,
  IconFilter,
  IconGripVertical,
  IconLayoutColumns,
  IconLoader,
  IconRadar,
} from "@tabler/icons-react"
import {
  flexRender,
  getCoreRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type ColumnFiltersState,
  type Row,
  type SortingState,
  type VisibilityState,
} from "@tanstack/react-table"
import { toast } from "sonner"
import { z } from "zod"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import { BellIcon, PlusIcon } from "lucide-react"

import { useRouter } from "next/navigation"


export const schema = z.object({
  customer_id: z.union([z.string(), z.number()]),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  email: z.string().optional(),
  contract: z.string().optional(),
  monthly_charges: z.number().optional(),
  total_charges: z.number().optional(),
  notified: z.boolean().optional(),
  churn: z.boolean().optional(),
  churn_label: z.boolean().optional(),
  prediction_date: z.string().optional(),
  notified_date: z.string().optional(),
  feedback_date: z.string().optional(),
  feedback_answer: z.string().optional(),
})

// Create a separate component for the drag handle
function DragHandle({ id }: { id: string | number }) {
  const { attributes, listeners } = useSortable({
    id: String(id),
  })

  return (
    <Button
      {...attributes}
      {...listeners}
      variant="ghost"
      size="icon"
      className="text-muted-foreground size-7 hover:bg-transparent"
    >
      <IconGripVertical className="text-muted-foreground size-3" />
      <span className="sr-only">Drag to reorder</span>
    </Button>
  )
}

const columns: ColumnDef<z.infer<typeof schema>>[] = [
  {
    id: "drag",
    header: () => null,
    cell: ({ row }) => <DragHandle id={row.original.customer_id} />,
  },
  {
    id: "select",
    header: ({ table }) => (
      <div className="flex items-center justify-center">
        <Checkbox
          checked={
            table.getIsAllPageRowsSelected() ||
            (table.getIsSomePageRowsSelected() && "indeterminate")
          }
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      </div>
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
  },
  {
    accessorKey: "customer_id",
    header: "ID",
    cell: ({ row }) => {
      const router = useRouter();
      const handleClick = () => {
        router.push(`/customers/${row.original.customer_id}`);
      };
      return (
        <Button variant="link" onClick={handleClick}>
          {row.original.customer_id}
        </Button>
      );
    },
    enableHiding: false,
  },
  {
    id: "name",
    header: "Name",
    cell: ({ row }) => {
      const firstName = row.original.first_name || "";
      const lastName = row.original.last_name || "";
      return <span>{`${firstName} ${lastName}`.trim() || "-"}</span>;
    },
    enableHiding: false,
  },
  {
    accessorKey: "monthly_charges",
    header: "Monthly Charges",
    cell: ({ row }) => `$${row.original.monthly_charges?.toFixed(2) ?? "-"}`,
    enableHiding: false,
  },
  {
    accessorKey: "total_charges",
    header: "Total Charges",
    cell: ({ row }) => `$${row.original.total_charges?.toFixed(2) ?? "-"}`,
    enableHiding: false,
  },
  {
    id: "status",
    accessorKey: "notified_date",
    header: "Status",
    cell: ({ row }) => {
      const date = row.original.notified_date;
      if (!date) {
        return (
          <Badge variant="outline" className="bg-gray-100 text-gray-700 border-gray-300">
            Not Notified
          </Badge>
        );
      }
      return (
        <div className="flex flex-col gap-1">
          <Badge variant="outline" className="bg-emerald-100 text-emerald-700 border-emerald-300">
            Notified
          </Badge>
          <span className="text-xs text-muted-foreground">{new Date(date).toISOString().split('T')[0]}</span>
        </div>
      );
    },
    filterFn: (row, columnId, filterValue) => {
      if (!filterValue) return true;
      const notifiedDate = row.original.notified_date;
      const feedbackDate = row.original.feedback_date;
      const feedbackAnswer = row.original.feedback_answer;
      
      if (filterValue === "not_notified") return !notifiedDate;
      if (filterValue === "notified") return !!notifiedDate && !feedbackDate;
      if (filterValue === "responded_ok") return !!feedbackDate && feedbackAnswer?.toLowerCase() === "yes";
      if (filterValue === "responded_no") return !!feedbackDate && feedbackAnswer?.toLowerCase() !== "yes" && !!feedbackAnswer;
      return true;
    },
    enableHiding: false,
  },
  {
    accessorKey: "feedback_date",
    header: "Feedback",
    cell: ({ row }) => {
      const date = row.original.feedback_date;
      const answer = row.original.feedback_answer;
      const notifiedDate = row.original.notified_date;
      
      // If not notified, show '-'
      if (!notifiedDate) {
        return <span className="text-muted-foreground">-</span>;
      }
      
      // If notified but no feedback yet, show '-'
      if (!date || !answer) {
        return <span className="text-muted-foreground">-</span>;
      }
      
      // If feedback received
      const isPositive = answer.toLowerCase() === "yes";
      return (
        <div className="flex flex-col gap-1">
          <Badge 
            variant="outline" 
            className={isPositive 
              ? "bg-emerald-100 text-emerald-700 border-emerald-300" 
              : "bg-amber-100 text-amber-700 border-amber-300"
            }
          >
            {isPositive ? "Responded OK" : "Responded No"}
          </Badge>
          <span className="text-xs text-muted-foreground">{new Date(date).toISOString().split('T')[0]}</span>
        </div>
      );
    },
    enableHiding: false,
  },
  {
    accessorKey: "churn_label",
    header: "Churn",
    cell: ({ row }) => {
      const churn = row.original.churn_label;
      const predictionDate = row.original.prediction_date;
      
      // If not predicted yet, show '-'
      if (churn === null || churn === undefined || !predictionDate) {
        return <span className="text-muted-foreground">-</span>;
      }
      
      return (
        <Badge
          variant="outline"
          className={
            churn
              ? "bg-red-50 text-red-600 border-red-200"
              : "bg-green-50 text-green-600 border-green-200"
          }
        >
          {churn ? "Yes" : "No"}
        </Badge>
      );
    },
    enableHiding: false,
  },
]

function DraggableRow({ row }: { row: Row<z.infer<typeof schema>> }) {
  const { transform, transition, setNodeRef, isDragging } = useSortable({
    id: String(row.original.customer_id),
  })

  return (
    <TableRow
      data-state={row.getIsSelected() && "selected"}
      data-dragging={isDragging}
      ref={setNodeRef}
      className="relative z-0 data-[dragging=true]:z-10 data-[dragging=true]:opacity-80"
      style={{
        transform: CSS.Transform.toString(transform),
        transition: transition,
      }}
    >
      {row.getVisibleCells().map((cell) => (
        <TableCell key={cell.id}>
          {flexRender(cell.column.columnDef.cell, cell.getContext())}
        </TableCell>
      ))}
    </TableRow>
  )
}

export function DataTable({
  data: initialData = [], // Provide a default empty array
}: {
  data?: z.infer<typeof schema>[] // Make the data prop optional
}) {
  const [data, setData] = React.useState(() => initialData)
  const [isUploading, setIsUploading] = React.useState(false)
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const [rowSelection, setRowSelection] = React.useState({})
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [pagination, setPagination] = React.useState({
    pageIndex: 0,
    pageSize: 10,
  })
  const sortableId = React.useId()
  const sensors = useSensors(
    useSensor(MouseSensor, {}),
    useSensor(TouchSensor, {}),
    useSensor(KeyboardSensor, {})
  )

  const dataIds = React.useMemo<UniqueIdentifier[]>(
    () => data?.map((item) => String(item.customer_id)) || [],
    [data]
  )

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnVisibility,
      rowSelection,
      columnFilters,
      pagination,
    },
    getRowId: (row) => (row.customer_id ? String(row.customer_id) : `row-${Math.random()}`),
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
  })

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (active && over && active.id !== over.id) {
      setData((data) => {
        const oldIndex = dataIds.indexOf(active.id)
        const newIndex = dataIds.indexOf(over.id)
        return arrayMove(data, oldIndex, newIndex)
      })
    }
  }

  async function handleCsvUpload(file: File) {
    setIsUploading(true)
    try {
      const form = new FormData()
      form.append("file", file)

      const baseUrl = process.env.NEXT_PUBLIC_API_URL 
      const res = await fetch(`${baseUrl}/customers/upload_csv`, {
        method: "POST",
        body: form,
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `HTTP ${res.status}`)
      }

      const json = await res.json()
      const processed = json?.processed ?? 0
      const errors = json?.errors?.length ?? 0
      const generated = json?.generated_ids?.length ?? 0
      toast.success(
        `Uploaded ${processed} customers${generated ? `, ${generated} IDs generated` : ""}${errors ? `, ${errors} errors` : ""}`
      )
    } catch (err: any) {
      toast.error(`Upload failed: ${err?.message || String(err)}`)
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ""
    }
  }

  async function handleNotifyCustomers() {
    const selectedRows = table.getFilteredSelectedRowModel().rows
    
    if (selectedRows.length === 0) {
      toast.error("Please select at least one customer to notify")
      return
    }

    const customerIds = selectedRows.map(row => row.original.customer_id)

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/notify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ customer_ids: customerIds }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `HTTP ${res.status}`)
      }

      const json = await res.json()
      toast.success(json?.message || `${selectedRows.length} customer(s) notified successfully!`)
    } catch (err: any) {
      toast.error(`Notification failed: ${err?.message || String(err)}`)
    }
  }

  async function handlePredictChurn() {
    const selectedRows = table.getFilteredSelectedRowModel().rows
    
    if (selectedRows.length === 0) {
      toast.error("Please select at least one customer for prediction")
      return
    }

    const customerIds = selectedRows.map(row => row.original.customer_id)

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL
      const res = await fetch(`${baseUrl}/predict/batch`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ customer_ids: customerIds }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `HTTP ${res.status}`)
      }

      const json = await res.json()
      const successCount = json?.predictions?.length || 0
      const failCount = json?.failed?.length || 0
      
      if (successCount > 0) {
        toast.success(json?.message || `Predictions completed for ${successCount} customer(s)!`)
        // Refresh the page to show updated predictions
        window.location.reload()
      }
      
      if (failCount > 0) {
        toast.warning(`${failCount} prediction(s) failed`)
      }
    } catch (err: any) {
      toast.error(`Prediction failed: ${err?.message || String(err)}`)
    }
  }

  return (
    <Tabs
      defaultValue="outline"
      className="w-full flex-col justify-start gap-6"
    >
      <div className="flex items-center justify-between px-4 lg:px-6">
        <h2 className="text-base font-medium">All Customers</h2>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <IconFilter className="h-4 w-4 mr-2" />
                Status
                <IconChevronDown className="h-4 w-4 ml-1" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuCheckboxItem
                checked={!table.getColumn("status")?.getFilterValue()}
                onCheckedChange={() => table.getColumn("status")?.setFilterValue(undefined)}
              >
                All
              </DropdownMenuCheckboxItem>
              <DropdownMenuSeparator />
              <DropdownMenuCheckboxItem
                checked={table.getColumn("status")?.getFilterValue() === "notified"}
                onCheckedChange={() => table.getColumn("status")?.setFilterValue("notified")}
              >
                Notified
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={table.getColumn("status")?.getFilterValue() === "not_notified"}
                onCheckedChange={() => table.getColumn("status")?.setFilterValue("not_notified")}
              >
                Not Notified
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={table.getColumn("status")?.getFilterValue() === "responded_ok"}
                onCheckedChange={() => table.getColumn("status")?.setFilterValue("responded_ok")}
              >
                Responded OK
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={table.getColumn("status")?.getFilterValue() === "responded_no"}
                onCheckedChange={() => table.getColumn("status")?.setFilterValue("responded_no")}
              >
                Responded No
              </DropdownMenuCheckboxItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <IconFilter className="h-4 w-4 mr-2" />
                Actions
                <IconChevronDown className="h-4 w-4 ml-1" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleNotifyCustomers}>
                <BellIcon className="h-4 w-4 mr-2" />
                Notify Customers
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handlePredictChurn}>
                <IconRadar className="h-4 w-4 mr-2" />
                Predict Churn
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,text/csv"
            style={{ display: "none" }}
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) handleCsvUpload(file)
            }}
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            {isUploading ? (
              <IconLoader className="h-5 w-5 mr-2 animate-spin" />
            ) : (
              <PlusIcon className="h-5 w-5 mr-2" />
            )}
            New Customers
          </Button>
        </div>
      </div>
      <TabsContent
        value="outline"
        className="relative flex flex-col gap-4 px-4 lg:px-6"
      >
        <div className="overflow-auto max-h-[calc(100vh-200px)] rounded-lg border">
          <DndContext
            collisionDetection={closestCenter}
            modifiers={[restrictToVerticalAxis]}
            onDragEnd={handleDragEnd}
            sensors={sensors}
            id={sortableId}
          >
            <Table>
              <TableHeader className="bg-muted sticky top-0 z-10">
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => {
                      return (
                        <TableHead key={header.id} colSpan={header.colSpan}>
                          {header.isPlaceholder
                            ? null
                            : flexRender(
                                header.column.columnDef.header,
                                header.getContext()
                              )}
                        </TableHead>
                      )
                    })}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody className="**:data-[slot=table-cell]:first:w-8">
                {table.getRowModel().rows?.length ? (
                  <SortableContext
                    items={dataIds}
                    strategy={verticalListSortingStrategy}
                  >
                    {table.getRowModel().rows.map((row) => (
                      <DraggableRow key={row.id} row={row} />
                    ))}
                  </SortableContext>
                ) : (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length}
                      className="h-24 text-center"
                    >
                      No results.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </DndContext>
        </div>
        <div className="flex items-center justify-between px-4">
          <div className="text-muted-foreground hidden flex-1 text-sm lg:flex">
            {table.getFilteredSelectedRowModel().rows.length} of{" "}
            {table.getFilteredRowModel().rows.length} row(s) selected.
          </div>
          <div className="flex w-full items-center gap-8 lg:w-fit">
            <div className="hidden items-center gap-2 lg:flex">
              <Label htmlFor="rows-per-page" className="text-sm font-medium">
                Rows per page
              </Label>
              <Select
                value={`${table.getState().pagination.pageSize}`}
                onValueChange={(value) => {
                  table.setPageSize(Number(value))
                }}
              >
                <SelectTrigger size="sm" className="w-20" id="rows-per-page">
                  <SelectValue
                    placeholder={table.getState().pagination.pageSize}
                  />
                </SelectTrigger>
                <SelectContent side="top">
                  {[10, 20, 30, 40, 50].map((pageSize) => (
                    <SelectItem key={pageSize} value={`${pageSize}`}>
                      {pageSize}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex w-fit items-center justify-center text-sm font-medium">
              Page {table.getState().pagination.pageIndex + 1} of{" "}
              {table.getPageCount()}
            </div>
            <div className="ml-auto flex items-center gap-2 lg:ml-0">
              <Button
                variant="outline"
                className="hidden h-8 w-8 p-0 lg:flex"
                onClick={() => table.setPageIndex(0)}
                disabled={!table.getCanPreviousPage()}
              >
                <span className="sr-only">Go to first page</span>
                <IconChevronsLeft />
              </Button>
              <Button
                variant="outline"
                className="size-8"
                size="icon"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                <span className="sr-only">Go to previous page</span>
                <IconChevronLeft />
              </Button>
              <Button
                variant="outline"
                className="size-8"
                size="icon"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                <span className="sr-only">Go to next page</span>
                <IconChevronRight />
              </Button>
              <Button
                variant="outline"
                className="hidden size-8 lg:flex"
                size="icon"
                onClick={() => table.setPageIndex(table.getPageCount() - 1)}
                disabled={!table.getCanNextPage()}
              >
                <span className="sr-only">Go to last page</span>
                <IconChevronsRight />
              </Button>
            </div>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  )
}
