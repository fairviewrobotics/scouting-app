import Image from "next/image";
import Link from "next/link";

import MatchScoutingForm from "../../components/MatchScoutingForm";

export default function MatchScouting() {
  return (
    <main className="h-max bg-main-grey-dark">
      <MatchScoutingForm />
    </main>
  );
}
