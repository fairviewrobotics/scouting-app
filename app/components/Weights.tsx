"use client";

import { useState, useEffect } from "react";
import { useDebounce } from "@/app/hooks/useDebounce";

export default function Weights({
  data,
  weights,
  setWeights,
}: {
  data: Record<string, string>;
  weights: Record<string, number>;
  setWeights: React.Dispatch<React.SetStateAction<Record<string, number>>>;
}) {
  const [localWeights, setLocalWeights] = useState(weights);

  useEffect(() => {
    setLocalWeights(weights);
  }, [weights]);

  const debouncedSetWeights = useDebounce((key: string, value: number) => {
    setWeights((prev) => ({
      ...prev,
      [key]: value,
    }));
  }, 1000); //<-- time value in milliseconds

  const handleChange = (key: string, value: number) => {
    setLocalWeights((prev) => ({
      ...prev,
      [key]: value,
    }));
    debouncedSetWeights(key, value);
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
              value={localWeights[key] ?? 1}
              onChange={(e) => handleChange(key, parseFloat(e.target.value))}
              className="slider mt-[0.7rem] w-full flex-shrink-0"
            />
            <span className="ml-3 flex-grow text-lg">
              {localWeights[key] ?? 1}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
