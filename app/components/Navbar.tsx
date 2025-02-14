"use client";

import React from "react";
import { usePathname } from "next/navigation";

const Navbar = () => {
  const pathname = usePathname();

  const linkClasses = (path: string) =>
    `hover:bg-main-grey-dark rounded px-3 pb-2 ${
      pathname === path ? "bg-main-grey-dark" : ""
    }`;

  return (
    <div>
      <div className="flex flex-row px-5 py-2 pb-1 text-3xl">
        <a href="/alldata">
          <img src="/blackknightslogo.png" className="h-10 w-auto px-2"></img>
        </a>
        <h1 className="text-main-red">Team 2036 Scouting</h1>
      </div>
      <div className="text-s px-3 text-main-red">
        <a href="/alldata" className={linkClasses("/alldata")}>
          All Data
        </a>
        <a href="/matchscouting" className={linkClasses("/matchscouting")}>
          Match Scouting
        </a>
        <a href="/pitscouting" className={linkClasses("/pitscouting")}>
          Pit Scouting
        </a>
        <a href="/rankings" className={linkClasses("/rankings")}>
          Rankings
        </a>
        <a href="/about" className={linkClasses("/about")}>
          About
        </a>
      </div>
    </div>
  );
};

export default Navbar;
