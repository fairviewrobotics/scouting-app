import TeamEntry from "@/app/components/TeamEntry";
import Image from "next/image";
import Link from "next/link";
import TeamTable from "@/app/components/TeamTable";

async function fetchTeams() {
  const apiURL = process.env.NEXT_PUBLIC_API_URL;
  const compKey = process.env.NEXT_PUBLIC_COMP_KEY;
  const res = await fetch(`${apiURL}/data/all_teams/${compKey}`);
  return res.json();
}

export default async function AllData() {
  const teams = await fetchTeams();

  return (
    <main className="container">
      <TeamTable teams={teams} />
    </main>
  );

  // return (
  //   <div className="h-screen w-screen bg-main-grey-dark">
  //     <h1>All Data</h1>
  //     <p>Here is all the data</p>
  //     <TeamEntry />
  //   </div>
  // );
}
