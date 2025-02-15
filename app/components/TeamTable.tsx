"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  SortingState,
} from "@tanstack/react-table";

interface TeamData {
  [key: string]: string | number | null;
}

export default function TeamTable({ teams }: { teams: TeamData[] }) {
  const router = useRouter();

  const [sorting, setSorting] = useState<SortingState>([]);

  // Dynamically generate column definitions based on keys in the data
  const columns = useMemo<ColumnDef<TeamData>[]>(
    () =>
      Object.keys(teams[0] || {}).map((key) => ({
        accessorKey: key,
        header: key.replace(/_/g, " ").toUpperCase(), // Format headers nicely
      })),
    [teams],
  );

  const table = useReactTable({
    data: teams,
    columns,
    state: { sorting },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
  });

  return (
    <div className="mt-20 w-max bg-main-grey-dark p-4 text-main-red">
      <table className="w-full border border-black shadow-lg">
        <thead className="sticky top-20 z-50 bg-black">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  className="cursor-pointer p-2 text-left"
                  onClick={header.column.getToggleSortingHandler()}
                >
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext(),
                  )}
                  {header.column.getIsSorted()
                    ? header.column.getIsSorted() === "asc"
                      ? " ↑"
                      : " ↓"
                    : ""}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              className="cursor-pointer hover:bg-main-grey"
              onClick={() => router.push(`/team/${row.original.team_number}`)}
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="border-b border-black p-2">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
