"use client";

import { useState, useEffect } from "react";

interface Question {
  question: string;
  name: string;
  type: "String" | "Integer" | "Boolean";
}

export default function MatchScoutingForm() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [formData, setFormData] = useState<{
    [key: string]: string | number | boolean;
  }>({});
  const [submitted, setSubmitted] = useState(false);
  const [clicked, setClicked] = useState(false);

  useEffect(() => {
    async function fetchQuestions() {
      try {
        const apiURL = process.env.NEXT_PUBLIC_API_URL;
        const response = await fetch(`${apiURL}/json/match_scouting`);
        const data: Question[] = await response.json();

        setQuestions(data);

        const initialData: { [key: string]: string | number | boolean } = {};
        data.forEach((q) => {
          if (q.type === "Boolean") {
            initialData[q.name] = false;
            // } else if (q.type === "Integer") {
            //   initialData[q.name] = 0;
          } else {
            initialData[q.name] = "";
          }
        });
        setFormData(initialData);
      } catch (error) {
        console.error("Error fetching questions:", error);
      }
    }
    fetchQuestions();
  }, []);

  const handleChange = (name: string, value: string | number | boolean) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const incrementValue = (name: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: (prev[name] as number) + 1,
    }));
  };

  const decrementValue = (name: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: Math.max(0, (prev[name] as number) - 1),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiURL = process.env.NEXT_PUBLIC_API_URL;
      const compKey = process.env.NEXT_PUBLIC_COMP_KEY;
      const response = await fetch(
        `${apiURL}/update_data/add_match_scouting/${compKey}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        },
      );
      if (response.ok) {
        setSubmitted(true);
      }
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="mx-auto mt-16 max-w-2xl space-y-4 rounded-lg bg-main-grey-dark p-4 text-main-red shadow-2xl shadow-black md:mt-20"
    >
      {questions.map((q) => (
        <div key={q.name} className="flex flex-col">
          <label className="mb-1 font-medium">{q.question}</label>

          {q.type === "String" && (
            <input
              type="text"
              value={formData[q.name] as string}
              onChange={(e) => handleChange(q.name, e.target.value)}
              className="w-full rounded border bg-main-grey p-2"
            />
          )}

          {q.type === "Integer" &&
          q.name !== "team_number" &&
          q.name !== "match_number" ? (
            <div className="flex w-full items-center space-x-2">
              <button
                type="button"
                onClick={() => decrementValue(q.name)}
                className="h-8 w-8 rounded bg-main-red text-white shadow-md transition hover:bg-red-700"
              >
                -
              </button>
              <input
                type="number"
                value={formData[q.name] as number}
                onChange={(e) => handleChange(q.name, Number(e.target.value))}
                className="w-full rounded border bg-main-grey p-2 text-center"
              />
              <button
                type="button"
                onClick={() => incrementValue(q.name)}
                className="h-8 w-8 rounded bg-main-red text-white shadow-md transition hover:bg-red-700"
              >
                +
              </button>
            </div>
          ) : q.type === "Integer" ? (
            <input
              type="number"
              value={formData[q.name] as number}
              onChange={(e) => handleChange(q.name, Number(e.target.value))}
              className="w-full rounded border bg-main-grey p-2"
            />
          ) : null}

          {q.type === "Boolean" && (
            <input
              type="checkbox"
              checked={formData[q.name] as boolean}
              onChange={(e) => handleChange(q.name, e.target.checked)}
              className="h-5 w-5 accent-main-grey"
            />
          )}
        </div>
      ))}

      <button
        type="submit"
        disabled={submitted}
        onClick={() => setClicked(true)}
        className={`rounded px-20 py-2 text-white ${
          submitted ? "bg-green-600" : clicked ? "bg-orange-700" : "bg-main-red"
        }`}
      >
        {submitted ? "Submitted!" : clicked ? "Processing..." : "Submit"}
      </button>
    </form>
  );
}
