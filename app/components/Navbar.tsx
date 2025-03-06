"use client";

import React from "react";
import { usePathname } from "next/navigation";
import Image from "next/image";

const Navbar = () => {
  const pathname = usePathname();

  const linkClasses = (path: string) =>
    `hover:bg-main-grey-dark rounded px-4 md:px-3 pb-[0.09rem] md:pb-1 ${
      pathname === path ? "bg-main-grey-dark" : ""
    }`;

  return (
    <div className="fixed left-0 right-0 top-0 z-50 bg-main-grey pt-1">
      <div className="flex flex-row px-5 py-2 pb-1 text-xl md:text-3xl">
        <a href="/alldata">
          <Image
            src="/blackknightslogo.png"
            width={40}
            height={40}
            alt=""
            className="mx-2 h-7 w-7 md:h-10 md:w-10"
          />
        </a>
        <h1 className="text-main-red">Team 2036 Scouting</h1>
      </div>
      <div className="mt-2 px-2 text-xs text-main-red md:mt-0 md:px-3 md:text-base">
        <a href="/alldata" className={linkClasses("/alldata")}>
          All Data
        </a>
        <a href="/matchscouting" className={linkClasses("/matchscouting")}>
          Match Scouting
        </a>
        <a href="/pitscouting" className={linkClasses("/pitscouting")}>
          Pit Scouting
        </a>
        <a href="/scores" className={linkClasses("/scores")}>
          Scores
        </a>
      </div>
    </div>
  );
};

export default Navbar;
