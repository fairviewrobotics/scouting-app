"use client";

import { useEffect, useState } from "react";
import TeamTable from "@/app/components/TeamTable";
import Weights from "@/app/components/Weights";

async function fetchTeams(weights: Record<string, number>) {
  const res = await fetch(
    `http://scouting-app-livid.vercel.app/api/py/data/weighted_all_teams/2025code/${encodeURIComponent(JSON.stringify(weights))}`,
  );
  return res.json();
}

async function fetchSchema() {
  const res = await fetch(
    "http://scouting-app-livid.vercel.app/api/py/json/schema",
  );
  return res.json();
}

export default function AllData() {
  const [teams, setTeams] = useState([]);
  const [schema, setSchema] = useState<Record<string, string>>({});
  const [weights, setWeights] = useState<Record<string, number>>(() => ({})); // Explicitly use a function to initialize

  useEffect(() => {
    fetchSchema().then((data) => {
      setSchema(data);
      const initialWeights = Object.keys(data)
        .filter((key) => key !== "team_number" && key !== "team_name")
        .reduce(
          (acc, key) => ({ ...acc, [key]: 1 }),
          {} as Record<string, number>,
        ); // Ensure correct type
      setWeights(initialWeights);
    });
  }, []);

  useEffect(() => {
    if (Object.keys(weights).length > 0) {
      fetchTeams(weights).then(setTeams);
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
