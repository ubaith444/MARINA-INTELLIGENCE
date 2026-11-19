"use client";

import React, { useState, useEffect } from "react";
import { clsx } from "clsx";
import {
  PitchMode,
  PitchPlayerMarker,
  PitchView,
  PassingNetworkNode,
  PassingNetworkEdge,
  ShotEvent,
  DefensiveActionMarker,
  HeatmapZone,
} from "@/lib/types";
import { FORMATION_PRESETS, PITCH_METRICS } from "@/lib/constants";
import { Shield, Crosshair, Users, Activity, Eye, AlertTriangle, Info } from "lucide-react";

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
  heatmapAvailable?: boolean;
  heatmapMessage?: string;
  selectedPlayerId?: string | null;
  showTabs?: boolean;
  onPlayerClick?: (player: PitchPlayerMarker) => void;
  onNodeClick?: (playerId: string) => void;
  onModeChange?: (mode: PitchMode) => void;
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
  heatmapZones = [],
  heatmapAvailable = false,
  heatmapMessage,
  selectedPlayerId,
  showTabs = true,
  onPlayerClick,
  onNodeClick,
  onModeChange,
  className,
}: FootballPitchProps) {
  const [activeMode, setActiveMode] = useState<PitchMode>(mode);
  const [view, setView] = useState<PitchView>(initialView);
  const [activeFormation, setActiveFormation] = useState<string>(formation);
  const [selectedPlayerMarker, setSelectedPlayerMarker] = useState<PitchPlayerMarker | null>(null);
  const [selectedShot, setSelectedShot] = useState<ShotEvent | null>(null);
  const [selectedAction, setSelectedAction] = useState<DefensiveActionMarker | null>(null);

  useEffect(() => {
    if (mode && mode !== activeMode) {
      setActiveMode(mode);
    }
  }, [mode]);

  const handleModeSwitch = (newMode: PitchMode) => {
    setActiveMode(newMode);
    onModeChange?.(newMode);
  };

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

  const getFormattedPlayerName = (name: string) => {
    if (!name) return "";
    return name.split(" ").slice(-1)[0];
  };

  const getPosCode = (pos: string) => {
    if (!pos) return "";
    const p = pos.toUpperCase();
    if (p.includes("GOALKEEPER") || p === "GK") return "GK";
    if (p === "RIGHT_BACK" || p === "RB") return "RB";
    if (p === "LEFT_BACK" || p === "LB") return "LB";
    if (p === "CENTRE_BACK" || p === "CB") return "CB";
    if (p === "LCB" || p === "RCB") return p;
    if (p.includes("DEFENDER") || p === "DEF") return "DEF";
    if (p.includes("DEFENSIVE") || p === "DM" || p === "LDM" || p === "RDM") return "DM";
    if (p.includes("ATTACKING") || p === "CAM" || p === "AM") return "CAM";
    if (p.includes("CENTRAL") || p === "CM") return "CM";
    if (p.includes("LEFT_WING") || p === "LW") return "LW";
    if (p.includes("RIGHT_WING") || p === "RW") return "RW";
    if (p.includes("FORWARD") || p.includes("STRIKER") || p === "ST" || p === "CF") return "ST";
    return pos.slice(0, 3).toUpperCase();
  };

  return (
    <div className={clsx("flex flex-col bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl overflow-hidden shadow-sm", className)}>
      {/* Pitch Header Controls */}
      <div className="px-5 py-3.5 bg-[#FFFFFF] border-b border-[#E2EAE3] flex flex-wrap items-center justify-between gap-3">
        {/* Mode Selector Tabs */}
        {showTabs ? (
          <div className="flex items-center space-x-1 bg-[#F4F8F4] p-1 rounded-lg border border-[#E2EAE3] text-xs">
            {(
              [
                "PASSING NETWORK",
                "SHOT MAP",
                "DEFENSIVE ACTIONS",
                "HEATMAP",
                "FORMATION",
              ] as PitchMode[]
            ).map((m) => (
              <button
                key={m}
                onClick={() => handleModeSwitch(m)}
                className={clsx(
                  "px-3 py-1.5 rounded-md font-bold tracking-wider text-[11px] transition-all",
                  activeMode === m
                    ? "bg-[#246B45] text-white shadow-xs"
                    : "text-[#718078] hover:text-[#26332B] hover:bg-[#FFFFFF]"
                )}
              >
                {m}
              </button>
            ))}
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-[#174B32]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#246B45]" />
            <span>{activeMode}</span>
          </div>
        )}

        {/* View and Formation Selectors */}
        <div className="flex items-center space-x-2.5">
          {activeMode === "FORMATION" && (
            <div className="flex items-center space-x-1.5 bg-[#F4F8F4] border border-[#E2EAE3] rounded-lg px-2.5 py-1 text-xs">
              <span className="text-[10px] text-[#718078] uppercase font-mono font-bold">Preset:</span>
              <select
                value={activeFormation}
                onChange={(e) => setActiveFormation(e.target.value)}
                className="bg-transparent text-[#26332B] text-xs font-bold focus:outline-none cursor-pointer"
              >
                {Object.keys(FORMATION_PRESETS).map((f) => (
                  <option key={f} value={f} className="bg-[#FFFFFF] text-[#26332B]">
                    {f}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Full / Half View Toggle */}
          <div className="flex items-center space-x-1 bg-[#F4F8F4] border border-[#E2EAE3] p-0.5 rounded-lg text-xs font-mono">
            <button
              onClick={() => setView("FULL")}
              className={clsx(
                "px-2.5 py-1 rounded text-[11px] font-bold transition-colors",
                view === "FULL" ? "bg-[#FFFFFF] text-[#246B45] shadow-xs" : "text-[#718078] hover:text-[#26332B]"
              )}
            >
              Full Pitch
            </button>
            <button
              onClick={() => setView("HALF")}
              className={clsx(
                "px-2.5 py-1 rounded text-[11px] font-bold transition-colors",
                view === "HALF" ? "bg-[#FFFFFF] text-[#246B45] shadow-xs" : "text-[#718078] hover:text-[#26332B]"
              )}
            >
              Attacking Half
            </button>
          </div>
        </div>
      </div>

      {/* SVG Canvas Area: Professional Football Pitch */}
      <div className="relative w-full aspect-[105/68] max-h-[580px] bg-[#276F3D] overflow-hidden select-none">
        <svg
          viewBox={viewBox}
          className="w-full h-full"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Turf Grass Alternating Mowed Stripes */}
            <pattern id="turf-stripes-light" width="105" height="680" patternUnits="userSpaceOnUse">
              <rect x="0" y="0" width="52.5" height="680" fill="#2E7D46" />
              <rect x="52.5" y="0" width="52.5" height="680" fill="#276F3D" />
            </pattern>
          </defs>

          {/* Background Grass Pattern */}
          <rect x="0" y="0" width={SVG_LENGTH} height={SVG_WIDTH} fill="url(#turf-stripes-light)" />

          {/* ==================================================== */}
          {/* Pitch Markings (Crisp Solid White Football Lines)    */}
          {/* ==================================================== */}
          <g stroke="rgba(255, 255, 255, 0.90)" strokeWidth="2.5" fill="none">
            {/* Outer Boundary */}
            <rect x="2" y="2" width={SVG_LENGTH - 4} height={SVG_WIDTH - 4} />

            {/* Halfway Line */}
            <line x1="525" y1="0" x2="525" y2={SVG_WIDTH} />

            {/* Center Circle */}
            <circle cx="525" cy="340" r="91.5" />
            <circle cx="525" cy="340" r="4.5" fill="#ffffff" />

            {/* Left Penalty Area */}
            <rect x="0" y="138.4" width="165" height="403.2" />
            <rect x="0" y="248.4" width="55" height="183.2" />
            <circle cx="110" cy="340" r="4.5" fill="#ffffff" />
            <path d="M 165 275 A 91.5 91.5 0 0 1 165 405" />

            {/* Right Penalty Area (Opponent Box) */}
            <rect x="885" y="138.4" width="165" height="403.2" />
            <rect x="995" y="248.4" width="55" height="183.2" />
            <circle cx="940" cy="340" r="4.5" fill="#ffffff" />
            <path d="M 885 275 A 91.5 91.5 0 0 0 885 405" />

            {/* Corner Arcs */}
            <path d="M 0 15 A 15 15 0 0 0 15 0" />
            <path d="M 0 665 A 15 15 0 0 1 15 680" />
            <path d="M 1035 0 A 15 15 0 0 0 1050 15" />
            <path d="M 1035 680 A 15 15 0 0 1 1050 665" />

            {/* Goals */}
            <rect x="-18" y="303.4" width="18" height="73.2" stroke="#ffffff" fill="rgba(255, 255, 255, 0.15)" />
            <rect x="1050" y="303.4" width="18" height="73.2" stroke="#ffffff" fill="rgba(255, 255, 255, 0.15)" />
          </g>

          {/* ==================================================== */}
          {/* LAYER 1: HEATMAP (Zero Fabrication Verified)         */}
          {/* ==================================================== */}
          {activeMode === "HEATMAP" && heatmapAvailable && heatmapZones.length > 0 && (
            <g>
              {heatmapZones.map((z, idx) => {
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
          {/* LAYER 2: PASSING NETWORK                             */}
          {/* ==================================================== */}
          {activeMode === "PASSING NETWORK" && (
            <g>
              {/* Pass Connection Edges */}
              {(passEdges || []).map((edge, idx) => {
                const nodesList = passNodes || [];
                const fromNode = nodesList.find((n) => n.player_id === edge.passer_id);
                const toNode = nodesList.find((n) => n.player_id === edge.recipient_id);
                if (!fromNode || !toNode) return null;

                const isConnectedToSelected =
                  Boolean(selectedPlayerId) &&
                  (edge.passer_id === selectedPlayerId || edge.recipient_id === selectedPlayerId);

                const x1 = toSvgX(fromNode.avg_x);
                const y1 = toSvgY(fromNode.avg_y);
                const x2 = toSvgX(toNode.avg_x);
                const y2 = toSvgY(toNode.avg_y);

                const strokeWidth = Math.min(8, Math.max(2, edge.pass_count * 0.45));
                const strokeColor = isConnectedToSelected
                  ? "#D9A441"
                  : "rgba(255, 255, 255, 0.70)";

                return (
                  <g key={`edge-${idx}`}>
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke={strokeColor}
                      strokeWidth={strokeWidth}
                      strokeLinecap="round"
                    />
                    {isConnectedToSelected && (
                      <g>
                        <rect
                          x={(x1 + x2) / 2 - 28}
                          y={(y1 + y2) / 2 - 16}
                          width="56"
                          height="16"
                          rx="4"
                          fill="#174B32"
                          stroke="#D9A441"
                          strokeWidth="1"
                        />
                        <text
                          x={(x1 + x2) / 2}
                          y={(y1 + y2) / 2 - 4}
                          fill="#D9A441"
                          fontSize="10"
                          fontWeight="bold"
                          textAnchor="middle"
                          className="font-mono"
                        >
                          {edge.pass_count} passes
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}

              {/* Player Average Position Nodes */}
              {(passNodes || []).map((node) => {
                const cx = toSvgX(node.avg_x);
                const cy = toSvgY(node.avg_y);
                const isSelected = selectedPlayerId === node.player_id;
                const radius = Math.min(26, Math.max(14, node.touches * 0.3));

                return (
                  <g
                    key={`pnode-${node.player_id}`}
                    className="cursor-pointer"
                    onClick={() => onNodeClick?.(node.player_id)}
                  >
                    {/* Glowing halo for selected player */}
                    {isSelected && (
                      <circle cx={cx} cy={cy} r={radius + 8} fill="rgba(217, 164, 65, 0.45)" stroke="#D9A441" strokeWidth="2.5" />
                    )}
                    <circle cx={cx} cy={cy} r={radius + 3} fill="rgba(23, 75, 50, 0.3)" />
                    <circle
                      cx={cx}
                      cy={cy}
                      r={radius}
                      fill={isSelected ? "#D9A441" : "#174B32"}
                      stroke="#ffffff"
                      strokeWidth={isSelected ? "3" : "2"}
                    />
                    <text
                      x={cx}
                      y={cy + 4}
                      fill="#ffffff"
                      fontSize="11"
                      fontWeight="bold"
                      textAnchor="middle"
                      className="font-mono"
                    >
                      {node.jersey_number || node.position || node.player_name.slice(0, 2)}
                    </text>
                    <g>
                      <rect
                        x={cx - 36}
                        y={cy + radius + 4}
                        width="72"
                        height="15"
                        rx="3"
                        fill="rgba(23, 75, 50, 0.90)"
                        stroke="#ffffff"
                        strokeWidth="0.75"
                      />
                      <text
                        x={cx}
                        y={cy + radius + 15}
                        fill="#ffffff"
                        fontSize="9.5"
                        fontWeight="bold"
                        textAnchor="middle"
                      >
                        {node.player_name.split(" ").slice(-1)[0]}
                      </text>
                    </g>
                  </g>
                );
              })}
            </g>
          )}

          {/* ==================================================== */}
          {/* LAYER 3: SHOT MAP                                    */}
          {/* ==================================================== */}
          {activeMode === "SHOT MAP" && (
            <g>
              {(shots || [])
                .filter((shot) => typeof shot.x === "number" && typeof shot.y === "number")
                .map((shot) => {
                const cx = toSvgX(shot.x);
                const cy = toSvgY(shot.y);
                const r = 9 + (shot.expected_goals || 0.1) * 16;
                const outcome = shot.outcome?.toUpperCase();

                if (outcome === "GOAL") {
                  return (
                    <g
                      key={`shot-${shot.shot_id}`}
                      className="cursor-pointer group"
                      onClick={() => setSelectedShot(shot)}
                    >
                      <circle cx={cx} cy={cy} r={r + 5} fill="rgba(36, 107, 69, 0.4)" />
                      <circle cx={cx} cy={cy} r={r} fill="#246B45" stroke="#ffffff" strokeWidth="2.5" />
                      <text
                        x={cx}
                        y={cy + 3.5}
                        fill="#ffffff"
                        fontSize="10"
                        fontWeight="bold"
                        textAnchor="middle"
                      >
                        ⚽
                      </text>
                    </g>
                  );
                } else if (outcome === "SAVED") {
                  return (
                    <g
                      key={`shot-${shot.shot_id}`}
                      className="cursor-pointer group"
                      onClick={() => setSelectedShot(shot)}
                    >
                      <rect
                        x={cx - r}
                        y={cy - r}
                        width={r * 2}
                        height={r * 2}
                        fill="#003399"
                        stroke="#ffffff"
                        strokeWidth="2"
                        transform={`rotate(45 ${cx} ${cy})`}
                      />
                      <text
                        x={cx}
                        y={cy + 3.5}
                        fill="#ffffff"
                        fontSize="9"
                        fontWeight="bold"
                        textAnchor="middle"
                      >
                        S
                      </text>
                    </g>
                  );
                } else if (outcome === "BLOCKED") {
                  return (
                    <g
                      key={`shot-${shot.shot_id}`}
                      className="cursor-pointer group"
                      onClick={() => setSelectedShot(shot)}
                    >
                      <rect
                        x={cx - r}
                        y={cy - r}
                        width={r * 2}
                        height={r * 2}
                        fill="#D9A441"
                        stroke="#ffffff"
                        strokeWidth="2"
                      />
                      <text
                        x={cx}
                        y={cy + 3.5}
                        fill="#ffffff"
                        fontSize="9"
                        fontWeight="bold"
                        textAnchor="middle"
                      >
                        B
                      </text>
                    </g>
                  );
                } else {
                  // MISSED / OFF_TARGET
                  return (
                    <g
                      key={`shot-${shot.shot_id}`}
                      className="cursor-pointer group"
                      onClick={() => setSelectedShot(shot)}
                    >
                      <circle cx={cx} cy={cy} r={r} fill="#C65B56" stroke="#ffffff" strokeWidth="2" />
                      <text
                        x={cx}
                        y={cy + 3.5}
                        fill="#ffffff"
                        fontSize="10"
                        fontWeight="bold"
                        textAnchor="middle"
                      >
                        ✕
                      </text>
                    </g>
                  );
                }
              })}
            </g>
          )}

          {/* ==================================================== */}
          {/* LAYER 4: DEFENSIVE ACTIONS (Distinct Markers/Colours)*/}
          {/* ==================================================== */}
          {activeMode === "DEFENSIVE ACTIONS" && (
            <g>
              {(defensiveActions || [])
                .filter((action) => action && typeof action.x === "number" && typeof action.y === "number")
                .map((action, idx) => {
                  const cx = toSvgX(action.x);
                  const cy = toSvgY(action.y);
                  const rawType = (action.action_type || (action as any).type || "").toUpperCase();

                  let fillColor = "#246B45";
                  let label = "D";

                  if (rawType.includes("TACKLE_WON") || rawType === "TACKLE") {
                    fillColor = "#246B45";
                    label = "T";
                  } else if (rawType.includes("TACKLE_LOST")) {
                    fillColor = "#C65B56";
                    label = "T";
                  } else if (rawType.includes("INTERCEPTION") || rawType === "I") {
                    fillColor = "#003399";
                    label = "I";
                  } else if (rawType.includes("CLEARANCE") || rawType === "C") {
                    fillColor = "#D9A441";
                    label = "C";
                  } else if (rawType.includes("BLOCK") || rawType === "B") {
                    fillColor = "#5E3A8C";
                    label = "B";
                  } else if (rawType.includes("RECOVERY") || rawType === "R") {
                    fillColor = "#174B32";
                    label = "R";
                  }

                  return (
                    <g
                      key={`def-${action.id || idx}`}
                      className="cursor-pointer group"
                      onClick={() => setSelectedAction(action)}
                    >
                      <circle cx={cx} cy={cy} r="12" fill={fillColor} stroke="#ffffff" strokeWidth="2" />
                      <text
                        x={cx}
                        y={cy + 4}
                        fill="#ffffff"
                        fontSize="9"
                        fontWeight="bold"
                        textAnchor="middle"
                        className="font-mono"
                      >
                        {label}
                      </text>
                    </g>
                  );
                })}
            </g>
          )}

          {/* ==================================================== */}
          {/* LAYER 5: FORMATION & SQUAD LINEUP                    */}
          {/* ==================================================== */}
          {activeMode === "FORMATION" && (
            <g>
              {displayPlayers.map((player) => {
                const cx = toSvgX(player.x);
                const cy = toSvgY(player.y);
                const isSelected = selectedPlayerMarker?.id === player.id;
                const formattedName = getFormattedPlayerName(player.name);
                const posCode = getPosCode(player.position);

                return (
                  <g
                    key={player.id}
                    className="cursor-pointer transition-transform duration-200"
                    onClick={() => {
                      setSelectedPlayerMarker(player);
                      onPlayerClick?.(player);
                    }}
                  >
                    {/* Selected halo */}
                    {isSelected && (
                      <circle cx={cx} cy={cy} r="26" fill="rgba(217, 164, 65, 0.4)" stroke="#D9A441" strokeWidth="2.5" />
                    )}

                    {/* 3. Position Supporting Badge (Top Pill) */}
                    {posCode && (
                      <g>
                        <rect
                          x={cx - 18}
                          y={cy - 34}
                          width="36"
                          height="14"
                          rx="3"
                          fill="#E6F0E7"
                          stroke="#C3DEC7"
                          strokeWidth="0.8"
                        />
                        <text
                          x={cx}
                          y={cy - 24}
                          fill="#174B32"
                          fontSize="9"
                          fontWeight="800"
                          textAnchor="middle"
                          className="font-mono"
                        >
                          {posCode}
                        </text>
                      </g>
                    )}

                    {/* 2. Secondary: Shirt Number Circle */}
                    <circle
                      cx={cx}
                      cy={cy}
                      r="18"
                      fill={isSelected ? "#D9A441" : "#174B32"}
                      stroke="#ffffff"
                      strokeWidth="2.5"
                    />
                    <text
                      x={cx}
                      y={cy + 4.5}
                      fill={isSelected ? "#174B32" : "#D9A441"}
                      fontSize="12"
                      fontWeight="800"
                      textAnchor="middle"
                      className="font-mono"
                    >
                      {player.jersey_number ? `#${player.jersey_number}` : posCode.slice(0, 2)}
                    </text>

                    {/* 1. Primary & Prominent: Player Name Label */}
                    <rect
                      x={cx - 52}
                      y={cy + 22}
                      width="104"
                      height="20"
                      rx="4"
                      fill="#174B32"
                      stroke="#C3DEC7"
                      strokeWidth="1.2"
                    />
                    <text
                      x={cx}
                      y={cy + 36}
                      fill="#ffffff"
                      fontSize="11"
                      fontWeight="700"
                      textAnchor="middle"
                    >
                      {formattedName}
                    </text>
                  </g>
                );
              })}
            </g>
          )}
        </svg>

        {/* ==================================================== */}
        {/* HEATMAP ZERO-FABRICATION EMPTY STATE OVERLAY         */}
        {/* ==================================================== */}
        {activeMode === "HEATMAP" && (!heatmapAvailable || heatmapZones.length === 0) && (
          <div className="absolute inset-0 flex items-center justify-center p-6 bg-white/85 backdrop-blur-xs">
            <div className="max-w-md bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-6 text-center shadow-lg space-y-3">
              <div className="w-12 h-12 mx-auto rounded-full bg-[#FEF3C7] border border-[#FDE68A] flex items-center justify-center text-[#92400E]">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-[#26332B]">
                Broadcast Optical Tracking Telemetry Unavailable
              </h3>
              <p className="text-xs text-[#718078] leading-relaxed font-sans">
                {heatmapMessage ||
                  "Optical tracking and high-frequency GPS coordinate telemetry was not provisioned for this fixture by the official league broadcast feed. In strict accordance with MARINA zero-fabrication standards, synthetic heat-map coordinates are not generated."}
              </p>
              <div className="pt-2 flex items-center justify-center gap-2 text-[10px] font-mono">
                <span className="px-2.5 py-1 rounded bg-[#F4F8F4] border border-[#E2EAE3] text-[#26332B]">
                  ISL 2026–27 Broadcast Feed
                </span>
                <span className="px-2.5 py-1 rounded bg-[#E6F0E7] border border-[#C3DEC7] text-[#174B32] font-bold">
                  Zero Synthetic Telemetry
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================== */}
        {/* SHOT MAP ZERO-FABRICATION EMPTY STATE OVERLAY        */}
        {/* ==================================================== */}
        {activeMode === "SHOT MAP" && (!shots || shots.filter((s) => typeof s.x === "number" && typeof s.y === "number").length === 0) && (
          <div className="absolute inset-0 flex items-center justify-center p-6 bg-white/85 backdrop-blur-xs">
            <div className="max-w-md bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-6 text-center shadow-lg space-y-3">
              <div className="w-12 h-12 mx-auto rounded-full bg-[#E6F0E7] border border-[#C3DEC7] flex items-center justify-center text-[#174B32]">
                <Crosshair className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-[#26332B]">
                Spatial Shot Coordinates Unavailable
              </h3>
              <p className="text-xs text-[#718078] leading-relaxed font-sans">
                Official coordinate telemetry for these shot events was not provisioned in the league broadcast feed. In strict compliance with MARINA zero-fabrication standards, synthetic locations are not rendered. All verified shot events, conversion metrics, and xG values are detailed below.
              </p>
              <div className="pt-2 flex items-center justify-center gap-2 text-[10px] font-mono">
                <span className="px-2.5 py-1 rounded bg-[#F4F8F4] border border-[#E2EAE3] text-[#26332B]">
                  ISL Official Feed
                </span>
                <span className="px-2.5 py-1 rounded bg-[#E6F0E7] border border-[#C3DEC7] text-[#174B32] font-bold">
                  Verified Event Totals
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Selected Player Formation Flyout */}
        {selectedPlayerMarker && activeMode === "FORMATION" && (
          <div className="absolute bottom-4 left-4 bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-3.5 shadow-xl max-w-xs animate-in fade-in slide-in-from-bottom-2">
            <div className="flex items-center justify-between space-x-3">
              <div>
                <span className="text-[10px] text-[#246B45] font-mono font-bold uppercase tracking-wider">
                  #{selectedPlayerMarker.jersey_number} • {selectedPlayerMarker.position}
                </span>
                <h4 className="text-sm font-bold text-[#26332B]">{selectedPlayerMarker.name}</h4>
              </div>
              <button
                onClick={() => setSelectedPlayerMarker(null)}
                className="text-[#718078] hover:text-[#26332B] text-xs px-1.5 py-0.5 rounded bg-[#F4F8F4] border border-[#E2EAE3]"
              >
                ✕
              </button>
            </div>
            <div className="mt-2 pt-2 border-t border-[#E2EAE3] grid grid-cols-2 gap-2 text-[11px] font-mono">
              <div>
                <span className="text-[#718078]">Role:</span>{" "}
                <span className="text-[#26332B] font-bold">{selectedPlayerMarker.role || "Starter"}</span>
              </div>
              <div>
                <span className="text-[#718078]">Club:</span>{" "}
                <span className="text-[#246B45] font-bold">Chennaiyin FC</span>
              </div>
            </div>
          </div>
        )}

        {/* Selected Shot Flyout */}
        {selectedShot && activeMode === "SHOT MAP" && (
          <div className="absolute bottom-4 right-4 bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-3.5 shadow-xl text-xs font-mono max-w-xs">
            <div className="flex items-center justify-between">
              <span className="text-[#246B45] font-bold">⚽ Shot #{selectedShot.shot_id}</span>
              <button
                onClick={() => setSelectedShot(null)}
                className="text-[#718078] hover:text-[#26332B] px-1.5 py-0.5 rounded bg-[#F4F8F4] border border-[#E2EAE3]"
              >
                ✕
              </button>
            </div>
            <div className="mt-1.5 space-y-1 text-[#26332B]">
              <div>Player: <span className="font-bold">{selectedShot.player_name}</span></div>
              <div>Outcome: <span className="text-[#246B45] font-bold">{selectedShot.outcome}</span> ({selectedShot.minute}&apos;)</div>
              <div>Expected Goals (xG): <span className="text-[#174B32] font-bold">{selectedShot.expected_goals !== null && selectedShot.expected_goals !== undefined ? selectedShot.expected_goals : "N/A"}</span></div>
              <div>Distance: <span className="text-[#718078]">{selectedShot.distance_meters}m</span> | Angle: <span className="text-[#718078]">{selectedShot.angle_degrees}°</span></div>
            </div>
          </div>
        )}

        {/* Selected Defensive Action Flyout */}
        {selectedAction && activeMode === "DEFENSIVE ACTIONS" && (
          <div className="absolute bottom-4 left-4 bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-3.5 shadow-xl text-xs font-mono max-w-xs">
            <div className="flex items-center justify-between">
              <span className="text-[#246B45] font-bold">🛡️ {selectedAction.action_type}</span>
              <button
                onClick={() => setSelectedAction(null)}
                className="text-[#718078] hover:text-[#26332B] px-1.5 py-0.5 rounded bg-[#F4F8F4] border border-[#E2EAE3]"
              >
                ✕
              </button>
            </div>
            <div className="mt-1.5 space-y-1 text-[#26332B]">
              <div>Player: <span className="font-bold">{selectedAction.player_name}</span></div>
              <div>Minute: <span className="text-[#718078] font-bold">{selectedAction.minute}&apos;</span></div>
              <div>Outcome: <span className="text-[#246B45] font-bold">{selectedAction.outcome}</span></div>
            </div>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div className="px-5 py-2.5 bg-[#F4F8F4] border-t border-[#E2EAE3] flex flex-wrap items-center justify-between text-[11px] text-[#718078] font-mono">
        <div className="flex items-center space-x-4">
          {activeMode === "FORMATION" && (
            <>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#174B32] border border-white" />
                <span className="text-[#26332B] font-semibold">Chennaiyin FC Starters</span>
              </span>
              <span>Click any player marker for tactical breakdown</span>
            </>
          )}
          {activeMode === "SHOT MAP" && (
            <>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#246B45]" />
                <span className="text-[#26332B] font-semibold">Goal</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rotate-45 bg-[#003399]" />
                <span className="text-[#26332B] font-semibold">Saved / Missed</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 bg-[#D9A441]" />
                <span className="text-[#26332B] font-semibold">Blocked</span>
              </span>
              <span>Bubble radius = Expected Goals (xG)</span>
            </>
          )}
          {activeMode === "PASSING NETWORK" && (
            <>
              <span className="flex items-center space-x-1.5">
                <span className="w-3 h-0.5 bg-white" />
                <span className="text-[#26332B] font-semibold">Pass Connections</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-3 h-0.5 bg-[#D9A441]" />
                <span className="text-[#26332B] font-semibold">Selected Combinations</span>
              </span>
              <span>Node radius = Touch Volume</span>
            </>
          )}
          {activeMode === "DEFENSIVE ACTIONS" && (
            <>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#246B45]" />
                <span className="text-[#26332B] font-semibold">Tackles</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#003399]" />
                <span className="text-[#26332B] font-semibold">Interceptions</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#D9A441]" />
                <span className="text-[#26332B] font-semibold">Clearances</span>
              </span>
            </>
          )}
          {activeMode === "HEATMAP" && (
            <span className="text-[#26332B] font-semibold">
              Broadcast Tracking Telemetry: Standard Audit Mode
            </span>
          )}
        </div>

        <div className="text-[10px] text-[#718078]">
          Standard Pitch (105m × 68m) • Coordinate Normalized
        </div>
      </div>
    </div>
  );
}
