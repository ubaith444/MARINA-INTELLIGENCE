/**
 * MARINA INTELLIGENCE — Frontend Constants & Tactical Presets
 */

import { PitchPlayerMarker } from "./types";

export const PITCH_METRICS = {
  LENGTH: 105.0,
  WIDTH: 68.0,
  GOAL_WIDTH: 7.32,
  PENALTY_SPOT_DIST: 11.0,
  PENALTY_BOX_LENGTH: 16.5,
  PENALTY_BOX_WIDTH: 40.32,
  SIX_YARD_LENGTH: 5.5,
  SIX_YARD_WIDTH: 18.32,
  CENTER_CIRCLE_RADIUS: 9.15,
};

export const CHENNAIYIN_FC_DEFAULTS = {
  ID: "cfc-2026-27",
  NAME: "Chennaiyin FC",
  SHORT_NAME: "CFC",
  SLUG: "chennaiyin-fc",
  PRIMARY_COLOR: "#003399", // Marina Blue
  SECONDARY_COLOR: "#FFFFFF",
  ACCENT_COLOR: "#059669",  // Deep Football Green
  VENUE_NAME: "Jawaharlal Nehru Stadium (Marina Arena)",
};

export interface FormationPreset {
  name: string;
  code: string;
  players: Array<{
    position: string;
    label: string;
    norm_x: number; // 0 (own goal) to 100 (opp goal)
    norm_y: number; // 0 (left sideline) to 100 (right sideline)
  }>;
}

export const FORMATION_PRESETS: Record<string, FormationPreset> = {
  "4-2-3-1": {
    name: "4-2-3-1 (Preferred CFC)",
    code: "4-2-3-1",
    players: [
      { position: "GK", label: "GK", norm_x: 8, norm_y: 50 },
      { position: "LB", label: "LB", norm_x: 25, norm_y: 15 },
      { position: "CB", label: "LCB", norm_x: 22, norm_y: 38 },
      { position: "CB", label: "RCB", norm_x: 22, norm_y: 62 },
      { position: "RB", label: "RB", norm_x: 25, norm_y: 85 },
      { position: "DM", label: "LDM", norm_x: 42, norm_y: 35 },
      { position: "DM", label: "RDM", norm_x: 42, norm_y: 65 },
      { position: "LW", label: "LW", norm_x: 68, norm_y: 18 },
      { position: "AM", label: "CAM", norm_x: 65, norm_y: 50 },
      { position: "RW", label: "RW", norm_x: 68, norm_y: 82 },
      { position: "CF", label: "ST", norm_x: 88, norm_y: 50 },
    ],
  },
  "4-3-3": {
    name: "4-3-3 Attacking",
    code: "4-3-3",
    players: [
      { position: "GK", label: "GK", norm_x: 8, norm_y: 50 },
      { position: "LB", label: "LB", norm_x: 25, norm_y: 15 },
      { position: "CB", label: "LCB", norm_x: 22, norm_y: 38 },
      { position: "CB", label: "RCB", norm_x: 22, norm_y: 62 },
      { position: "RB", label: "RB", norm_x: 25, norm_y: 85 },
      { position: "DM", label: "CDM", norm_x: 40, norm_y: 50 },
      { position: "CM", label: "LCM", norm_x: 55, norm_y: 32 },
      { position: "CM", label: "RCM", norm_x: 55, norm_y: 68 },
      { position: "LW", label: "LW", norm_x: 78, norm_y: 18 },
      { position: "CF", label: "ST", norm_x: 88, norm_y: 50 },
      { position: "RW", label: "RW", norm_x: 78, norm_y: 82 },
    ],
  },
  "3-5-2": {
    name: "3-5-2 Wing-Backs",
    code: "3-5-2",
    players: [
      { position: "GK", label: "GK", norm_x: 8, norm_y: 50 },
      { position: "CB", label: "LCB", norm_x: 22, norm_y: 28 },
      { position: "CB", label: "CB", norm_x: 20, norm_y: 50 },
      { position: "CB", label: "RCB", norm_x: 22, norm_y: 72 },
      { position: "LWB", label: "LWB", norm_x: 48, norm_y: 12 },
      { position: "CM", label: "LCM", norm_x: 45, norm_y: 35 },
      { position: "DM", label: "DM", norm_x: 40, norm_y: 50 },
      { position: "CM", label: "RCM", norm_x: 45, norm_y: 65 },
      { position: "RWB", label: "RWB", norm_x: 48, norm_y: 88 },
      { position: "CF", label: "LS", norm_x: 85, norm_y: 38 },
      { position: "CF", label: "RS", norm_x: 85, norm_y: 62 },
    ],
  },
  "4-4-2": {
    name: "4-4-2 Flat",
    code: "4-4-2",
    players: [
      { position: "GK", label: "GK", norm_x: 8, norm_y: 50 },
      { position: "LB", label: "LB", norm_x: 25, norm_y: 15 },
      { position: "CB", label: "LCB", norm_x: 22, norm_y: 38 },
      { position: "CB", label: "RCB", norm_x: 22, norm_y: 62 },
      { position: "RB", label: "RB", norm_x: 25, norm_y: 85 },
      { position: "LM", label: "LM", norm_x: 52, norm_y: 15 },
      { position: "CM", label: "LCM", norm_x: 50, norm_y: 38 },
      { position: "CM", label: "RCM", norm_x: 50, norm_y: 62 },
      { position: "RM", label: "RM", norm_x: 52, norm_y: 85 },
      { position: "CF", label: "LS", norm_x: 85, norm_y: 38 },
      { position: "CF", label: "RS", norm_x: 85, norm_y: 62 },
    ],
  },
};

export const CHENNAIYIN_FC_SQUAD_FALLBACK: PitchPlayerMarker[] = [
  { id: "p-1", name: "Samik Mitra", jersey_number: 1, position: "GOALKEEPER", x: 8, y: 50, role: "STARTER" },
  { id: "p-2", name: "Ankit Mukherjee", jersey_number: 22, position: "RIGHT_BACK", x: 26, y: 85, role: "STARTER" },
  { id: "p-3", name: "Ryan Edwards", jersey_number: 6, position: "CENTRE_BACK", x: 22, y: 62, role: "STARTER", is_captain: true },
  { id: "p-4", name: "Bikash Yumnam", jersey_number: 3, position: "CENTRE_BACK", x: 22, y: 38, role: "STARTER" },
  { id: "p-5", name: "Laldinliana Renthlei", jersey_number: 26, position: "LEFT_BACK", x: 26, y: 15, role: "STARTER" },
  { id: "p-6", name: "Jiteshwor Singh", jersey_number: 8, position: "DEFENSIVE_MIDFIELDER", x: 42, y: 40, role: "STARTER" },
  { id: "p-7", name: "Connor Shields", jersey_number: 10, position: "CENTRAL_MIDFIELDER", x: 44, y: 62, role: "STARTER" },
  { id: "p-8", name: "Lukas Brambilla", jersey_number: 14, position: "ATTACKING_MIDFIELDER", x: 65, y: 50, role: "STARTER" },
  { id: "p-9", name: "Farukh Choudhary", jersey_number: 11, position: "LEFT_WINGER", x: 72, y: 18, role: "STARTER" },
  { id: "p-10", name: "Vincy Barretto", jersey_number: 7, position: "RIGHT_WINGER", x: 72, y: 82, role: "STARTER" },
  { id: "p-11", name: "Wilmar Jordan Gil", jersey_number: 9, position: "CENTRE_FORWARD", x: 88, y: 50, role: "STARTER" },
];
