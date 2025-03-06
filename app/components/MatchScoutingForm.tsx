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

  // Fetch scouting questions
  useEffect(() => {
    async function fetchQuestions() {
      try {
        const apiURL = process.env.NEXT_PUBLIC_API_URL;
        const response = await fetch(`${apiURL}/json/match_scouting`); // Adjust endpoint as needed
        const data: Question[] = await response.json();

        console.log("Fetched questions:", data);

        setQuestions(data);

        // Initialize form state with default values
        const initialData: { [key: string]: string | number | boolean } = {};
        data.forEach((q) => {
          initialData[q.name] = q.type === "Boolean" ? false : ""; // Default false for booleans, empty for others
        });
        setFormData(initialData);
      } catch (error) {
        console.error("Error fetching questions:", error);
      }
    }
    fetchQuestions();
  }, []);

  // Handle form changes
  const handleChange = (name: string, value: string | number | boolean) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle form submission
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
      className="mx-auto mt-20 max-w-2xl space-y-4 rounded-lg bg-main-grey-dark p-4 text-main-red shadow-2xl shadow-black"
    >
      {questions.map((q) => (
        <div key={q.name} className="flex flex-col">
          <label className="mb-1 font-medium">{q.question}</label>
          {q.type === "String" && (
            <input
              type="text"
              value={formData[q.name] as string}
              onChange={(e) => handleChange(q.name, e.target.value)}
              className="rounded border bg-main-grey p-2"
            />
          )}
          {q.type === "Integer" && (
            <input
              type="number"
              value={formData[q.name] as number}
              onChange={(e) => handleChange(q.name, Number(e.target.value))}
              className="rounded border bg-main-grey p-2"
            />
          )}
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
        className={`rounded px-20 py-2 text-white ${submitted ? "bg-green-600" : clicked ? "bg-orange-700" : "bg-main-red"}`}
      >
        {submitted ? "Submitted!" : clicked ? "Processing..." : "Submit"}
      </button>
    </form>
  );
}
