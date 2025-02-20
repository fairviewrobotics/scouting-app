"use client";

import { useEffect, useState } from "react";
import TeamTable from "@/app/components/TeamTable";
import Weights from "@/app/components/Weights";

async function fetchTeams(weights: Record<string, number>) {
  try {
    console.log("fetching teams with weights", weights);
    const res = await fetch(
      `https://scouting-app-livid.vercel.app/api/py/data/weighted_all_teams/2025code`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ weights }),
      },
    );
    if (!res.ok) throw new Error("Failed to fetch teams");
    return res.json();
  } catch (error) {
    console.error("Error fetching teams:", error);
    return [];
  }
}

async function fetchSchema() {
  try {
    const res = await fetch(
      "https://scouting-app-livid.vercel.app/api/py/json/schema",
    );
    if (!res.ok) throw new Error("Failed to fetch schema");
    return res.json();
  } catch (error) {
    console.error("Error fetching schema:", error);
    return {};
  }
}

export default function AllData() {
  const [teams, setTeams] = useState([]);
  const [schema, setSchema] = useState<Record<string, string>>({});
  const [weights, setWeights] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchSchema().then((data) => {
      setSchema(data);

      const initialWeights = Object.keys(data)
        .filter((key) => key !== "team_number" && key !== "team_name")
        .reduce(
          (acc, key) => ({ ...acc, [key]: 1 }),
          {} as Record<string, number>,
        );

      setWeights(initialWeights);
    });
  }, []);

  useEffect(() => {
    if (Object.keys(weights).length > 0) {
      console.log("Weights changed, fetching teams...");
      fetchTeams(weights).then((data) => {
        setTeams(data);
      });
    }
  }, [weights]);

  return (
    <main className="container flex justify-center bg-main-grey-dark">
      <div className="w-1/4">
        <Weights data={schema} weights={weights} setWeights={setWeights} />
      </div>
      <div className="w-3/4">
        <TeamTable teams={teams} />
      </div>
    </main>
  );
}
