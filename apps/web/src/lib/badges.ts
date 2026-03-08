import type { BadgeDefinition } from "./types";

export const BADGE_DEFINITIONS: BadgeDefinition[] = [
  {
    id: "first_look",
    name: "Primera Vigilancia",
    icon: "👁️",
    description: "Abriste tu primera licitación",
  },
  {
    id: "streak_7",
    name: "Semana de Vigilancia",
    icon: "🔥",
    description: "7 días consecutivos monitoreando",
  },
  {
    id: "streak_30",
    name: "Vigía Mensual",
    icon: "⚡",
    description: "30 días consecutivos de monitoreo",
  },
  {
    id: "fast_responder",
    name: "Primera Respuesta",
    icon: "⚡",
    description: "Abriste un bid dentro de 1h de su publicación",
  },
  {
    id: "ccss_specialist",
    name: "Especialista CCSS",
    icon: "🏥",
    description: "Revisaste 20+ licitaciones de la CCSS",
  },
  {
    id: "intel_pro",
    name: "Intel Pro",
    icon: "🎯",
    description: "Perfil de monitoreo 100% optimizado",
  },
];

export function getBadge(id: string): BadgeDefinition | undefined {
  return BADGE_DEFINITIONS.find((b) => b.id === id);
}
