import {
  AlignLeft,
  Atom,
  BadgePercent,
  BarChart3,
  Binary,
  BookMarked,
  BookOpen,
  Bot,
  Briefcase,
  Bug,
  CalendarClock,
  CalendarRange,
  ChartSpline,
  Clapperboard,
  ClipboardList,
  Code2,
  Compass,
  Component,
  Database,
  ExternalLink,
  FileCode2,
  FileSearch,
  FileText,
  FlaskConical,
  GraduationCap,
  Image as ImageIcon,
  ImagePlus,
  Library,
  Lightbulb,
  ListChecks,
  Megaphone,
  MessageSquareText,
  MessagesSquare,
  PencilRuler,
  Route,
  Search,
  Sigma,
  Sparkles,
  TableProperties,
  Type,
  Zap,
} from 'lucide-react'

/**
 * Maps the `icon` name from the backend catalog to a lucide component.
 * Every domain and agent in the catalog declares one of these; anything
 * unrecognised falls back to a generic bot glyph rather than crashing.
 */
const ICON_MAP = {
  AlignLeft,
  Atom,
  BadgePercent,
  BarChart3,
  Binary,
  BookMarked,
  BookOpen,
  Briefcase,
  Bug,
  CalendarClock,
  CalendarRange,
  ChartSpline,
  Clapperboard,
  ClipboardList,
  Code2,
  Compass,
  Component,
  Database,
  ExternalLink,
  FileCode2,
  FileSearch,
  FileText,
  FlaskConical,
  GraduationCap,
  Image: ImageIcon,
  ImagePlus,
  Library,
  Lightbulb,
  ListChecks,
  Megaphone,
  MessageSquareText,
  MessagesSquare,
  PencilRuler,
  Route,
  Search,
  Sigma,
  Sparkles,
  TableProperties,
  Type,
  Zap,
}

export function agentIcon(name) {
  return ICON_MAP[name] ?? Bot
}

/**
 * Accent tokens per domain. Every agent inherits its domain's accent, so the
 * whole UI stays colour-coded by domain. Kept as full class strings (not
 * interpolated) so Tailwind's content scanner keeps them in the build.
 */
export const ACCENTS = {
  emerald: {
    text: 'text-emerald-600 dark:text-emerald-400',
    bg: 'bg-emerald-50 dark:bg-emerald-500/10',
    ring: 'ring-emerald-500/30',
    border: 'border-emerald-200 dark:border-emerald-500/30',
    solid: 'bg-emerald-600',
    hoverBorder: 'hover:border-emerald-400 dark:hover:border-emerald-500/60',
  },
  sky: {
    text: 'text-sky-600 dark:text-sky-400',
    bg: 'bg-sky-50 dark:bg-sky-500/10',
    ring: 'ring-sky-500/30',
    border: 'border-sky-200 dark:border-sky-500/30',
    solid: 'bg-sky-600',
    hoverBorder: 'hover:border-sky-400 dark:hover:border-sky-500/60',
  },
  amber: {
    text: 'text-amber-600 dark:text-amber-400',
    bg: 'bg-amber-50 dark:bg-amber-500/10',
    ring: 'ring-amber-500/30',
    border: 'border-amber-200 dark:border-amber-500/30',
    solid: 'bg-amber-600',
    hoverBorder: 'hover:border-amber-400 dark:hover:border-amber-500/60',
  },
  fuchsia: {
    text: 'text-fuchsia-600 dark:text-fuchsia-400',
    bg: 'bg-fuchsia-50 dark:bg-fuchsia-500/10',
    ring: 'ring-fuchsia-500/30',
    border: 'border-fuchsia-200 dark:border-fuchsia-500/30',
    solid: 'bg-fuchsia-600',
    hoverBorder: 'hover:border-fuchsia-400 dark:hover:border-fuchsia-500/60',
  },
  cyan: {
    text: 'text-cyan-600 dark:text-cyan-400',
    bg: 'bg-cyan-50 dark:bg-cyan-500/10',
    ring: 'ring-cyan-500/30',
    border: 'border-cyan-200 dark:border-cyan-500/30',
    solid: 'bg-cyan-600',
    hoverBorder: 'hover:border-cyan-400 dark:hover:border-cyan-500/60',
  },
  violet: {
    text: 'text-violet-600 dark:text-violet-400',
    bg: 'bg-violet-50 dark:bg-violet-500/10',
    ring: 'ring-violet-500/30',
    border: 'border-violet-200 dark:border-violet-500/30',
    solid: 'bg-violet-600',
    hoverBorder: 'hover:border-violet-400 dark:hover:border-violet-500/60',
  },
  rose: {
    text: 'text-rose-600 dark:text-rose-400',
    bg: 'bg-rose-50 dark:bg-rose-500/10',
    ring: 'ring-rose-500/30',
    border: 'border-rose-200 dark:border-rose-500/30',
    solid: 'bg-rose-600',
    hoverBorder: 'hover:border-rose-400 dark:hover:border-rose-500/60',
  },
}

export function accent(name) {
  return ACCENTS[name] ?? ACCENTS.sky
}

export const ROUTING_SOURCE_LABELS = {
  explicit: 'You selected this agent',
  llm_router: 'Router agent (LLM)',
  keyword_router: 'Router agent (heuristic)',
  conversation_default: 'Continued this conversation’s agent',
  fallback: 'No clear signal — default agent',
}

/** What each agent hands back, used for badges and empty states. */
export const OUTPUT_KIND_LABELS = {
  text: 'Text answer',
  image: 'Generates an image',
  chart: 'Renders a chart',
}

export const OUTPUT_KIND_ICONS = {
  text: AlignLeft,
  image: ImageIcon,
  chart: BarChart3,
}

/** `marketing.post-image` -> `marketing`. */
export function domainOf(agentKey) {
  return String(agentKey || '').split('.')[0]
}

export function isVisualKind(kind) {
  return kind === 'image' || kind === 'chart'
}
