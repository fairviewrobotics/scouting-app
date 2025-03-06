import Image from "next/image";
import Link from "next/link";

import MatchScoutingForm from "../../components/MatchScoutingForm";

export default function MatchScouting() {
  return (
    <main className="h-screen bg-main-grey-dark">
      <MatchScoutingForm />
    </main>
  );
}
