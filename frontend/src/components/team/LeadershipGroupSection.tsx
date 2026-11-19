"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Shield, Users, ArrowRight, Award } from "lucide-react";
import { fetchLeadershipGroup } from "@/lib/api";
import { LeadershipGroupResponse, LeadershipMember } from "@/lib/types";
import Badge from "@/components/ui/Badge";

interface LeadershipGroupSectionProps {
  compact?: boolean;
  className?: string;
}

export default function LeadershipGroupSection({
  compact = false,
  className = "",
}: LeadershipGroupSectionProps) {
  const [leadership, setLeadership] = useState<LeadershipGroupResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    fetchLeadershipGroup()
      .then((data) => {
        if (isMounted && data) {
          setLeadership(data);
        }
      })
      .catch((err) => {
        console.error("Failed to load leadership group:", err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const members: LeadershipMember[] = leadership?.members && leadership.members.length > 0
    ? leadership.members
    : [
        {
          id: "1",
          player_id: "a378e4c6-f1f1-4304-9a7f-6ac754f2e014",
          player_name: "Nuno Reis",
          jersey_number: 4,
          position: "Defender",
          primary_position: "CB",
          nationality: "Portugal",
          is_indian: false,
          leadership_role: "Leadership Group",
          is_captain: false,
          is_vice_captain: false,
        },
        {
          id: "2",
          player_id: "77bee327-2929-4d41-9329-e2f2bd18c88e",
          player_name: "P. C. Laldinpuia",
          jersey_number: 3,
          position: "Defender",
          primary_position: "CB",
          nationality: "India",
          is_indian: true,
          leadership_role: "Leadership Group",
          is_captain: false,
          is_vice_captain: false,
        },
        {
          id: "3",
          player_id: "3a79ed6c-7620-44aa-8568-b1f2b3650062",
          player_name: "Nikola Stojanović",
          jersey_number: 8,
          position: "Midfielder",
          primary_position: "CM",
          nationality: "Serbia",
          is_indian: false,
          leadership_role: "Leadership Group",
          is_captain: false,
          is_vice_captain: false,
        },
        {
          id: "4",
          player_id: "ee362980-f66b-417d-8abb-c4004b703320",
          player_name: "Samik Mitra",
          jersey_number: 1,
          position: "Goalkeeper",
          primary_position: "GK",
          nationality: "India",
          is_indian: true,
          leadership_role: "Leadership Group",
          is_captain: false,
          is_vice_captain: false,
        },
        {
          id: "5",
          player_id: "f1f1efd2-6b7f-4f22-aba3-2bf79404a683",
          player_name: "Mohammad Nawaz",
          jersey_number: 13,
          position: "Goalkeeper",
          primary_position: "GK",
          nationality: "India",
          is_indian: true,
          leadership_role: "Leadership Group",
          is_captain: false,
          is_vice_captain: false,
        },
      ];

  return (
    <section className={`bg-white border border-[#E2EAE3] rounded-2xl p-5 shadow-xs ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-[#E2EAE3]">
        <div className="space-y-0.5">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-[#246B45]" />
            <h3 className="text-sm font-bold text-[#26332B] uppercase tracking-wider font-mono">
              Season Leadership Group • ISL 2026–27
            </h3>
          </div>
          <p className="text-xs text-[#718078] font-sans">
            Chennaiyin FC&apos;s verified five-member senior player leadership council
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="px-2.5 py-1 rounded-lg bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7] text-xs font-mono font-bold">
            5 Senior Leaders
          </span>
          <span className="text-xs text-[#718078] font-mono hidden md:inline">
            Non-hierarchical collective
          </span>
        </div>
      </div>

      {/* Grid of 5 Leadership Group Members */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
        {members.map((member) => (
          <div
            key={member.player_id}
            className="p-3.5 bg-[#F4F8F4] border border-[#E2EAE3] hover:border-[#246B45]/40 rounded-xl transition-all flex flex-col justify-between group shadow-2xs"
          >
            <div>
              {/* Top Row: Authentic Kit Badge + Leadership Tag */}
              <div className="flex items-center justify-between mb-3">
                <div className="w-10 h-10 rounded-xl bg-[#246B45] text-white flex items-center justify-center font-mono font-black text-sm shadow-xs border border-[#174B32]">
                  {member.jersey_number ? `#${member.jersey_number}` : "CFC"}
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7]">
                  Leadership Group
                </span>
              </div>

              {/* Player Name & Role */}
              <h4 className="text-sm font-bold text-[#26332B] font-sans group-hover:text-[#246B45] transition-colors leading-snug">
                {member.player_name}
              </h4>
              <div className="flex items-center space-x-2 mt-1 text-xs font-mono text-[#718078]">
                <span className="font-semibold text-[#246B45]">{member.position}</span>
                <span>•</span>
                <span>{member.nationality === "India" ? "🇮🇳 India" : member.nationality}</span>
              </div>
            </div>

            {/* Bottom link to Profile */}
            <div className="pt-3 mt-3 border-t border-[#E2EAE3]/80 flex items-center justify-between text-[11px] font-mono">
              <span className="text-[#718078]">Senior Squad</span>
              <Link
                href={`/players/${member.player_id}`}
                className="text-[#246B45] hover:text-[#174B32] font-semibold flex items-center space-x-1 group-hover:underline"
              >
                <span>Profile</span>
                <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
