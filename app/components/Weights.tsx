"use client";

export default function Weights({
  data,
  weights,
  setWeights,
}: {
  data: Record<string, string>;
  weights: Record<string, number>;
  setWeights: React.Dispatch<React.SetStateAction<Record<string, number>>>; // Correct type for useState setter
}) {
  const handleChange = (key: string, value: number) => {
    setWeights((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  return (
    <div className="ml-0 mt-20 space-y-2 bg-main-grey-dark px-10 py-6 pl-10">
      {Object.keys(weights).map((key) => (
        <div key={key} className="flex flex-col">
          <label className="text-sm font-normal text-black">
            {key.replace(/_/g, " ").toUpperCase()}
          </label>
          <div className="flex">
            <input
              type="range"
              min="0"
              max="10"
              step="0.1"
              value={weights[key]}
              onChange={(e) => handleChange(key, parseFloat(e.target.value))}
              className="slider mt-[0.7rem] w-full flex-shrink-0"
            />
            <span className="ml-3 flex-grow text-lg">{weights[key]}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
