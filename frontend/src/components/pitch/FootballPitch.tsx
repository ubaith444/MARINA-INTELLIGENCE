"use client";

import React, { useState } from "react";
import { clsx } from "clsx";
import {
  PitchMode,
  PitchPlayerMarker,
  PitchView,
  PassingNetworkNode,
  PassingNetworkEdge,
  ShotEvent,
} from "@/lib/types";
import { FORMATION_PRESETS, PITCH_METRICS } from "@/lib/constants";
import { Shield, Crosshair, Users, Activity, Eye } from "lucide-react";

interface DefensiveActionMarker {
  id: string;
  x: number;
  y: number;
  type: "TACKLE_WON" | "TACKLE_LOST" | "INTERCEPTION" | "CLEARANCE" | "BLOCK";
  player_name?: string;
  minute?: number;
}

interface HeatmapZone {
  x: number; // 0 to 100
  y: number; // 0 to 100
  intensity: number; // 0.1 to 1.0
}

interface FootballPitchProps {
  mode?: PitchMode;
  view?: PitchView;
  formation?: string;
  players?: PitchPlayerMarker[];
  passNodes?: PassingNetworkNode[];
  passEdges?: PassingNetworkEdge[];
  shots?: ShotEvent[];
  defensiveActions?: DefensiveActionMarker[];
  heatmapZones?: HeatmapZone[];
  onPlayerClick?: (player: PitchPlayerMarker) => void;
  className?: string;
}

export default function FootballPitch({
  mode = "FORMATION",
  view: initialView = "FULL",
  formation = "4-2-3-1",
  players,
  passNodes,
  passEdges,
  shots,
  defensiveActions,
  heatmapZones,
  onPlayerClick,
  className,
}: FootballPitchProps) {
  const [activeMode, setActiveMode] = useState<PitchMode>(mode);
  const [view, setView] = useState<PitchView>(initialView);
  const [activeFormation, setActiveFormation] = useState<string>(formation);
  const [selectedPlayer, setSelectedPlayer] = useState<PitchPlayerMarker | null>(null);
  const [selectedShot, setSelectedShot] = useState<ShotEvent | null>(null);

  // SVG Pitch Coordinate Space (Length = 1050, Width = 680)
  const SVG_LENGTH = 1050;
  const SVG_WIDTH = 680;

  // ViewBox: Full Pitch = "0 0 1050 680"; Attacking Half = "525 0 525 680"
  const viewBox = view === "FULL" ? `0 0 ${SVG_LENGTH} ${SVG_WIDTH}` : `525 0 525 680`;

  // Normalize coordinate helper: converts 0-100 or 0-105 to SVG coordinate
  const toSvgX = (x: number) => {
    if (x <= 100) return (x / 100) * SVG_LENGTH;
    return (x / PITCH_METRICS.LENGTH) * SVG_LENGTH;
  };

  const toSvgY = (y: number) => {
    if (y <= 100) return (y / 100) * SVG_WIDTH;
    return (y / PITCH_METRICS.WIDTH) * SVG_WIDTH;
  };

  // Determine active players for Formation mode
  const currentPreset = FORMATION_PRESETS[activeFormation] || FORMATION_PRESETS["4-2-3-1"];
  const displayPlayers: PitchPlayerMarker[] =
    players && players.length > 0
      ? players
      : currentPreset.players.map((p, idx) => ({
          id: `player-${idx}`,
          name: p.label,
          jersey_number: idx + 1,
          position: p.position,
          x: p.norm_x,
          y: p.norm_y,
          role: "STARTER",
        }));

  return (
    <div className={clsx("flex flex-col bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl", className)}>
      {/* Pitch Header Controls */}
      <div className="px-5 py-3.5 bg-slate-900/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        {/* Mode Selector Tabs */}
        <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800/80 text-xs">
          {(
            [
              "FORMATION",
              "PASSING NETWORK",
              "SHOT MAP",
              "DEFENSIVE ACTIONS",
              "HEATMAP",
            ] as PitchMode[]
          ).map((m) => (
            <button
              key={m}
              onClick={() => setActiveMode(m)}
              className={clsx(
                "px-3 py-1.5 rounded-lg font-semibold tracking-wider text-[11px] transition-all",
                activeMode === m
                  ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
                  : "text-slate-400 hover:text-slate-200"
              )}
            >
              {m}
            </button>
          ))}
        </div>

        {/* View and Formation Selectors */}
        <div className="flex items-center space-x-2.5">
          {activeMode === "FORMATION" && (
            <div className="flex items-center space-x-1.5 bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-xs">
              <span className="text-[10px] text-slate-500 uppercase font-mono">Preset:</span>
              <select
                value={activeFormation}
                onChange={(e) => setActiveFormation(e.target.value)}
                className="bg-transparent text-slate-200 text-xs font-semibold focus:outline-none cursor-pointer"
              >
                {Object.keys(FORMATION_PRESETS).map((f) => (
                  <option key={f} value={f} className="bg-slate-900 text-slate-200">
                    {f}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Full / Half View Toggle */}
          <div className="flex items-center space-x-1 bg-slate-950 border border-slate-800 p-0.5 rounded-lg text-xs font-mono">
            <button
              onClick={() => setView("FULL")}
              className={clsx(
                "px-2.5 py-1 rounded text-[11px] font-medium transition-colors",
                view === "FULL" ? "bg-slate-800 text-slate-100" : "text-slate-400 hover:text-slate-200"
              )}
            >
              Full Pitch
            </button>
            <button
              onClick={() => setView("HALF")}
              className={clsx(
                "px-2.5 py-1 rounded text-[11px] font-medium transition-colors",
                view === "HALF" ? "bg-slate-800 text-slate-100" : "text-slate-400 hover:text-slate-200"
              )}
            >
              Attacking Half
            </button>
          </div>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div className="relative w-full aspect-[105/68] max-h-[580px] bg-[#08170e] overflow-hidden select-none">
        <svg
          viewBox={viewBox}
          className="w-full h-full"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Turf Grass Alternating Stripes */}
            <pattern id="turf-stripes" width="105" height="680" patternUnits="userSpaceOnUse">
              <rect x="0" y="0" width="52.5" height="680" fill="#091b10" />
              <rect x="52.5" y="0" width="52.5" height="680" fill="#07170e" />
            </pattern>

            {/* Glowing marker gradients */}
            <radialGradient id="player-glow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#1e3a8a" stopOpacity="0.1" />
            </radialGradient>
            <radialGradient id="goal-glow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#047857" stopOpacity="0.2" />
            </radialGradient>
          </defs>

          {/* Background Grass Pattern */}
          <rect x="0" y="0" width={SVG_LENGTH} height={SVG_WIDTH} fill="url(#turf-stripes)" />

          {/* ==================================================== */}
          {/* Pitch Markings (White, semi-transparent crisp lines) */}
          {/* ==================================================== */}
          <g stroke="rgba(255, 255, 255, 0.45)" strokeWidth="2.5" fill="none">
            {/* Touchlines and Goal Lines Outer Boundary */}
            <rect x="2" y="2" width={SVG_LENGTH - 4} height={SVG_WIDTH - 4} />

            {/* Halfway Line */}
            <line x1="525" y1="0" x2="525" y2={SVG_WIDTH} />

            {/* Center Circle (Radius 91.5 = 9.15m) */}
            <circle cx="525" cy="340" r="91.5" />
            {/* Center Spot */}
            <circle cx="525" cy="340" r="4" fill="rgba(255, 255, 255, 0.6)" />

            {/* Left Penalty Area (165 x 403.2; y from 138.4 to 541.6) */}
            <rect x="0" y="138.4" width="165" height="403.2" />
            {/* Left 6-Yard Box (55 x 183.2; y from 248.4 to 431.6) */}
            <rect x="0" y="248.4" width="55" height="183.2" />
            {/* Left Penalty Spot (110m = 11m from goal) */}
            <circle cx="110" cy="340" r="4" fill="rgba(255, 255, 255, 0.6)" />
            {/* Left Penalty Arc */}
            <path d="M 165 275 A 91.5 91.5 0 0 1 165 405" />

            {/* Right Penalty Area (Opponent Box: x from 885 to 1050) */}
            <rect x="885" y="138.4" width="165" height="403.2" />
            {/* Right 6-Yard Box (x from 995 to 1050) */}
            <rect x="995" y="248.4" width="55" height="183.2" />
            {/* Right Penalty Spot (940m = 11m from opponent goal) */}
            <circle cx="940" cy="340" r="4" fill="rgba(255, 255, 255, 0.6)" />
            {/* Right Penalty Arc */}
            <path d="M 885 275 A 91.5 91.5 0 0 0 885 405" />

            {/* Corner Arcs (10m radius = 10 units) */}
            <path d="M 0 15 A 15 15 0 0 0 15 0" />
            <path d="M 0 665 A 15 15 0 0 1 15 680" />
            <path d="M 1035 0 A 15 15 0 0 0 1050 15" />
            <path d="M 1035 680 A 15 15 0 0 1 1050 665" />

            {/* Goals (Width 73.2 = 7.32m; y from 303.4 to 376.6) */}
            <rect x="-18" y="303.4" width="18" height="73.2" stroke="rgba(255, 255, 255, 0.7)" />
            <rect x="1050" y="303.4" width="18" height="73.2" stroke="rgba(255, 255, 255, 0.7)" />
          </g>

          {/* ==================================================== */}
          {/* LAYER 1: HEATMAP ZONES (When Mode == HEATMAP)        */}
          {/* ==================================================== */}
          {activeMode === "HEATMAP" && (
            <g>
              {(heatmapZones || [
                { x: 70, y: 30, intensity: 0.8 },
                { x: 75, y: 40, intensity: 0.9 },
                { x: 80, y: 50, intensity: 0.75 },
                { x: 65, y: 70, intensity: 0.6 },
                { x: 50, y: 45, intensity: 0.7 },
                { x: 45, y: 35, intensity: 0.5 },
                { x: 25, y: 50, intensity: 0.4 },
              ]).map((z, idx) => {
                const cx = toSvgX(z.x);
                const cy = toSvgY(z.y);
                const r = 50 + z.intensity * 40;
                return (
                  <circle
                    key={`heat-${idx}`}
                    cx={cx}
                    cy={cy}
                    r={r}
                    fill={`rgba(239, 68, 68, ${z.intensity * 0.45})`}
                    filter="blur(18px)"
                  />
                );
              })}
            </g>
          )}

          {/* ==================================================== */}
          {/* LAYER 2: PASSING NETWORK (When Mode == PASSING NETWORK)*/}
          {/* ==================================================== */}
          {activeMode === "PASSING NETWORK" && (
            <g>
              {/* Pass Connection Edges */}
              {(passEdges || [
                { passer_name: "Mitra", recipient_name: "Edwards", pass_count: 8, passer_id: "1", recipient_id: "6" },
                { passer_name: "Edwards", recipient_name: "Jiteshwor", pass_count: 14, passer_id: "6", recipient_id: "8" },
                { passer_name: "Jiteshwor", recipient_name: "Brambilla", pass_count: 18, passer_id: "8", recipient_id: "10" },
                { passer_name: "Brambilla", recipient_name: "Farukh", pass_count: 11, passer_id: "10", recipient_id: "11" },
                { passer_name: "Brambilla", recipient_name: "Wilmar", pass_count: 9, passer_id: "10", recipient_id: "9" },
              ]).map((edge, idx) => {
                // Find node positions
                const nodesList = passNodes || [
                  { player_id: "1", player_name: "Mitra", jersey_number: 1, avg_x: 12, avg_y: 50, touches: 32 },
                  { player_id: "6", player_name: "Edwards", jersey_number: 6, avg_x: 31, avg_y: 65, touches: 61 },
                  { player_id: "8", player_name: "Jiteshwor", jersey_number: 8, avg_x: 48, avg_y: 45, touches: 75 },
                  { player_id: "10", player_name: "Brambilla", jersey_number: 10, avg_x: 68, avg_y: 52, touches: 68 },
                  { player_id: "11", player_name: "Farukh", jersey_number: 11, avg_x: 72, avg_y: 24, touches: 49 },
                  { player_id: "9", player_name: "Wilmar", jersey_number: 9, avg_x: 86, avg_y: 50, touches: 38 },
                ];
                const fromNode = nodesList.find((n) => n.player_id === edge.passer_id);
                const toNode = nodesList.find((n) => n.player_id === edge.recipient_id);
                if (!fromNode || !toNode) return null;

                const x1 = toSvgX(fromNode.avg_x);
                const y1 = toSvgY(fromNode.avg_y);
                const x2 = toSvgX(toNode.avg_x);
                const y2 = toSvgY(toNode.avg_y);
                const strokeWidth = Math.min(8, Math.max(1.5, edge.pass_count * 0.45));

                return (
                  <line
                    key={`edge-${idx}`}
                    x1={x1}
                    y1={y1}
                    x2={x2}
                    y2={y2}
                    stroke="rgba(96, 165, 250, 0.75)"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                  />
                );
              })}

              {/* Player Average Position Nodes */}
              {(passNodes || [
                { player_id: "1", player_name: "Mitra", jersey_number: 1, avg_x: 12, avg_y: 50, touches: 32 },
                { player_id: "6", player_name: "Edwards", jersey_number: 6, avg_x: 31, avg_y: 65, touches: 61 },
                { player_id: "8", player_name: "Jiteshwor", jersey_number: 8, avg_x: 48, avg_y: 45, touches: 75 },
                { player_id: "10", player_name: "Brambilla", jersey_number: 10, avg_x: 68, avg_y: 52, touches: 68 },
                { player_id: "11", player_name: "Farukh", jersey_number: 11, avg_x: 72, avg_y: 24, touches: 49 },
                { player_id: "9", player_name: "Wilmar", jersey_number: 9, avg_x: 86, avg_y: 50, touches: 38 },
              ]).map((node) => {
                const cx = toSvgX(node.avg_x);
                const cy = toSvgY(node.avg_y);
                const radius = Math.min(26, Math.max(14, node.touches * 0.3));

                return (
                  <g key={`pnode-${node.player_id}`}>
                    <circle cx={cx} cy={cy} r={radius + 4} fill="rgba(59, 130, 246, 0.25)" />
                    <circle cx={cx} cy={cy} r={radius} fill="#1d4ed8" stroke="#ffffff" strokeWidth="2" />
                    <text
                      x={cx}
                      y={cy + 4}
                      fill="#ffffff"
                      fontSize="11"
                      fontWeight="bold"
                      textAnchor="middle"
                      className="font-mono"
                    >
                      {node.jersey_number || node.player_name.slice(0, 2)}
                    </text>
                    <text
                      x={cx}
                      y={cy + radius + 14}
                      fill="#e2e8f0"
                      fontSize="10"
                      fontWeight="600"
                      textAnchor="middle"
                    >
                      {node.player_name}
                    </text>
                  </g>
                );
              })}
            </g>
          )}

          {/* ==================================================== */}
          {/* LAYER 3: SHOT MAP (When Mode == SHOT MAP)            */}
          {/* ==================================================== */}
          {activeMode === "SHOT MAP" && (
            <g>
              {(shots || [
                { shot_id: "1", minute: 12, player_name: "Farukh Choudhary", team_name: "CFC", x: 92.4, y: 40, outcome: "GOAL", expected_goals: 0.32, distance_meters: 14.2, angle_degrees: 28 },
                { shot_id: "2", minute: 24, player_name: "Wilmar Jordan Gil", team_name: "CFC", x: 99.2, y: 52, outcome: "GOAL", expected_goals: 0.44, distance_meters: 6.8, angle_degrees: 54 },
                { shot_id: "3", minute: 38, player_name: "Farukh Choudhary", team_name: "CFC", x: 86.0, y: 32, outcome: "SAVED", expected_goals: 0.08, distance_meters: 20.5, angle_degrees: 18 },
                { shot_id: "4", minute: 45, player_name: "Lukas Brambilla", team_name: "CFC", x: 94.0, y: 50, outcome: "GOAL", expected_goals: 0.79, distance_meters: 11.0, angle_degrees: 36.8 },
                { shot_id: "5", minute: 67, player_name: "Wilmar Jordan Gil", team_name: "CFC", x: 101.5, y: 48, outcome: "GOAL", expected_goals: 0.68, distance_meters: 4.2, angle_degrees: 68 },
                { shot_id: "6", minute: 90, player_name: "Irfan Yadwad", team_name: "CFC", x: 96.0, y: 54, outcome: "GOAL", expected_goals: 0.54, distance_meters: 9.5, angle_degrees: 42 },
              ]).map((shot) => {
                const cx = toSvgX(shot.x);
                const cy = toSvgY(shot.y);
                const r = 8 + (shot.expected_goals || 0.1) * 16;
                const isGoal = shot.outcome === "GOAL";

                return (
                  <g
                    key={`shot-${shot.shot_id}`}
                    className="cursor-pointer group"
                    onClick={() => setSelectedShot(shot)}
                  >
                    {isGoal ? (
                      <>
                        <circle cx={cx} cy={cy} r={r + 5} fill="rgba(16, 185, 129, 0.35)" />
                        <circle cx={cx} cy={cy} r={r} fill="#10b981" stroke="#ffffff" strokeWidth="2.5" />
                        <text
                          x={cx}
                          y={cy + 3.5}
                          fill="#ffffff"
                          fontSize="9"
                          fontWeight="bold"
                          textAnchor="middle"
                        >
                          ⚽
                        </text>
                      </>
                    ) : (
                      <rect
                        x={cx - r}
                        y={cy - r}
                        width={r * 2}
                        height={r * 2}
                        fill="#f59e0b"
                        stroke="#ffffff"
                        strokeWidth="1.5"
                        transform={`rotate(45 ${cx} ${cy})`}
                      />
                    )}
                  </g>
                );
              })}
            </g>
          )}

          {/* ==================================================== */}
          {/* LAYER 4: DEFENSIVE ACTIONS (When Mode == DEFENSIVE ACTIONS) */}
          {/* ==================================================== */}
          {activeMode === "DEFENSIVE ACTIONS" && (
            <g>
              {(defensiveActions || [
                { id: "d1", x: 28, y: 35, type: "TACKLE_WON", player_name: "Ryan Edwards", minute: 14 },
                { id: "d2", x: 32, y: 65, type: "TACKLE_WON", player_name: "Bikash Yumnam", minute: 28 },
                { id: "d3", x: 45, y: 40, type: "INTERCEPTION", player_name: "Jiteshwor Singh", minute: 34 },
                { id: "d4", x: 18, y: 50, type: "CLEARANCE", player_name: "Ryan Edwards", minute: 61 },
                { id: "d5", x: 22, y: 48, type: "BLOCK", player_name: "Bikash Yumnam", minute: 78 },
              ]).map((action) => {
                const cx = toSvgX(action.x);
                const cy = toSvgY(action.y);

                return (
                  <g key={`def-${action.id}`}>
                    <circle cx={cx} cy={cy} r="10" fill="#3b82f6" stroke="#ffffff" strokeWidth="1.5" />
                    <text
                      x={cx}
                      y={cy + 3.5}
                      fill="#ffffff"
                      fontSize="9"
                      fontWeight="bold"
                      textAnchor="middle"
                      className="font-mono"
                    >
                      D
                    </text>
                  </g>
                );
              })}
            </g>
          )}

          {/* ==================================================== */}
          {/* LAYER 5: FORMATION & PLAYER MARKERS (Default)        */}
          {/* ==================================================== */}
          {activeMode === "FORMATION" && (
            <g>
              {displayPlayers.map((player) => {
                const cx = toSvgX(player.x);
                const cy = toSvgY(player.y);
                const isSelected = selectedPlayer?.id === player.id;

                return (
                  <g
                    key={player.id}
                    className="cursor-pointer transition-transform duration-200"
                    onClick={() => {
                      setSelectedPlayer(player);
                      onPlayerClick?.(player);
                    }}
                  >
                    {/* Glow halo on selection */}
                    {isSelected && (
                      <circle cx={cx} cy={cy} r="28" fill="rgba(59, 130, 246, 0.4)" stroke="#60a5fa" strokeWidth="2" />
                    )}
                    {/* Player Marker Circle */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r="18"
                      fill={isSelected ? "#2563eb" : "#003399"}
                      stroke="#ffffff"
                      strokeWidth="2.5"
                    />
                    {/* Shirt Number */}
                    <text
                      x={cx}
                      y={cy + 4.5}
                      fill="#ffffff"
                      fontSize="12"
                      fontWeight="bold"
                      textAnchor="middle"
                      className="font-mono"
                    >
                      {player.jersey_number || player.position.slice(0, 2)}
                    </text>
                    {/* Player Name Tag */}
                    <rect
                      x={cx - 36}
                      y={cy + 22}
                      width="72"
                      height="16"
                      rx="4"
                      fill="rgba(15, 23, 42, 0.85)"
                      stroke="rgba(51, 65, 85, 0.6)"
                      strokeWidth="1"
                    />
                    <text
                      x={cx}
                      y={cy + 34}
                      fill="#f1f5f9"
                      fontSize="10"
                      fontWeight="600"
                      textAnchor="middle"
                    >
                      {player.name.split(" ").slice(-1)[0]}
                    </text>
                  </g>
                );
              })}
            </g>
          )}
        </svg>

        {/* Selected Player Flyout Card */}
        {selectedPlayer && activeMode === "FORMATION" && (
          <div className="absolute bottom-4 left-4 bg-slate-900/95 border border-slate-700/80 rounded-xl p-3.5 shadow-2xl backdrop-blur-md max-w-xs animate-in fade-in slide-in-from-bottom-2">
            <div className="flex items-center justify-between space-x-3">
              <div>
                <span className="text-[10px] text-blue-400 font-mono font-bold uppercase tracking-wider">
                  #{selectedPlayer.jersey_number} • {selectedPlayer.position}
                </span>
                <h4 className="text-sm font-bold text-slate-100">{selectedPlayer.name}</h4>
              </div>
              <button
                onClick={() => setSelectedPlayer(null)}
                className="text-slate-400 hover:text-slate-200 text-xs px-1.5 py-0.5 rounded bg-slate-800"
              >
                ✕
              </button>
            </div>
            <div className="mt-2 pt-2 border-t border-slate-800 grid grid-cols-2 gap-2 text-[11px] font-mono">
              <div>
                <span className="text-slate-500">Role:</span>{" "}
                <span className="text-slate-300 font-semibold">{selectedPlayer.role || "Starter"}</span>
              </div>
              <div>
                <span className="text-slate-500">Club:</span>{" "}
                <span className="text-blue-400 font-semibold">Chennaiyin FC</span>
              </div>
            </div>
          </div>
        )}

        {/* Selected Shot Flyout */}
        {selectedShot && activeMode === "SHOT MAP" && (
          <div className="absolute bottom-4 right-4 bg-slate-900/95 border border-slate-700/80 rounded-xl p-3.5 shadow-2xl backdrop-blur-md text-xs font-mono max-w-xs">
            <div className="flex items-center justify-between">
              <span className="text-emerald-400 font-bold">⚽ Shot #{selectedShot.shot_id}</span>
              <button
                onClick={() => setSelectedShot(null)}
                className="text-slate-400 hover:text-slate-200 px-1.5 py-0.5 rounded bg-slate-800"
              >
                ✕
              </button>
            </div>
            <div className="mt-1.5 space-y-1 text-slate-300">
              <div>Player: <span className="font-bold text-white">{selectedShot.player_name}</span></div>
              <div>Outcome: <span className="text-emerald-400 font-bold">{selectedShot.outcome}</span> ({selectedShot.minute}&apos;)</div>
              <div>Expected Goals (xG): <span className="text-blue-400 font-bold">{selectedShot.expected_goals ?? "—"}</span></div>
              <div>Distance: <span className="text-slate-200">{selectedShot.distance_meters}m</span> | Angle: <span className="text-slate-200">{selectedShot.angle_degrees}°</span></div>
            </div>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div className="px-5 py-2.5 bg-slate-900/80 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] text-slate-400 font-mono">
        <div className="flex items-center space-x-4">
          {activeMode === "FORMATION" && (
            <>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-700 border border-white" />
                <span>Chennaiyin FC Starters</span>
              </span>
              <span className="text-slate-500">Click any player marker for tactical breakdown</span>
            </>
          )}
          {activeMode === "SHOT MAP" && (
            <>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                <span>Goal</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rotate-45 bg-amber-500" />
                <span>Saved / Missed</span>
              </span>
              <span className="text-slate-500">Bubble size = Expected Goals (xG)</span>
            </>
          )}
          {activeMode === "PASSING NETWORK" && (
            <>
              <span className="flex items-center space-x-1.5">
                <span className="w-3 h-0.5 bg-blue-400" />
                <span>Weighted Pass Connections</span>
              </span>
              <span className="text-slate-500">Node radius = Touch Volume</span>
            </>
          )}
          {activeMode === "DEFENSIVE ACTIONS" && (
            <>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                <span>Defensive Event Location</span>
              </span>
            </>
          )}
          {activeMode === "HEATMAP" && (
            <>
              <span className="text-rose-400">High Territorial Intensity Zones</span>
            </>
          )}
        </div>

        <div className="text-[10px] text-slate-500">
          Standard Pitch (105m × 68m) • Coordinate Normalized
        </div>
      </div>
    </div>
  );
}
