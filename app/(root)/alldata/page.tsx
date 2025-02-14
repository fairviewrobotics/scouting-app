import TeamEntry from "@/app/components/TeamEntry";
import Image from "next/image";
import Link from "next/link";

export default function AllData() {
  return (
    <div className="h-screen w-screen bg-main-grey-dark">
      <h1>All Data</h1>
      <p>Here is all the data</p>
      <TeamEntry />
    </div>
  );
}
