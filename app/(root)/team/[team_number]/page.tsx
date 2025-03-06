async function fetchTeams(team_number: number) {
  const apiURL = process.env.NEXT_PUBLIC_API_URL;
  const compKey = process.env.NEXT_PUBLIC_COMP_KEY;
  const res = await fetch(
    `${apiURL}/data/single_pit_scouting/${team_number}/${compKey}`,
  );
  return res.json();
}

export default async function Page({
  params,
}: {
  params: { team_number: number };
}) {
  const { team_number } = await params;
  const data = await fetchTeams(team_number);

  return (
    <div className="mx-auto mt-20 max-w-2xl p-4">
      <h1 className="mb-4 text-2xl font-bold text-main-red">
        Team {team_number} Pit Scouting Data
      </h1>
      <div className="space-y-4">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="rounded-lg bg-main-grey-dark p-4 shadow-lg">
            <p className="font-medium text-white">{key}</p>
            {key === "robot_image" && typeof value === "string" ? (
              <img
                src={`${value}`}
                alt="Robot"
                className="mt-2 max-w-full rounded-lg shadow-md"
              />
            ) : (
              <p className="text-main-red">{String(value)}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
