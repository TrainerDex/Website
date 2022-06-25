import { intComma } from "humanize-plus";

export class StatMeta {
  parameter: string;
  name: string;
  description: string | null;
  precision: number;
  prefix: string;
  suffix: string;

  constructor(
    parameter: string,
    name: string,
    description: string | null = null,
    precision: number = 0,
    prefix: string = "",
    suffix: string = ""
  ) {
    this.parameter = parameter;
    this.name = name;
    this.description = description;
    this.precision = precision;
    this.prefix = prefix;
    this.suffix = suffix;
  }

  formatValue(value: number): string {
    return `${this.prefix}${intComma(value, this.precision)}${this.suffix}`;
  }
}

export const TotalXP = new StatMeta(
  "total_xp",
  "Total XP",
  "Total XP",
  0,
  "",
  " XP"
);

export const listOfStats: StatMeta[] = [
  TotalXP,
  new StatMeta(
    "travel_km",
    "Jogger",
    `Walk ${intComma(10000)} km.`,
    1,
    "",
    " km"
  ),
];

export function getStatByParameter(parameter: string): StatMeta | null {
  return listOfStats.find((stat) => stat.parameter === parameter) || null;
}

export function getStatByName(name: string): StatMeta | null {
  return listOfStats.find((stat) => stat.name === name) || null;
}

export function formatValue(value: number, statString: string): string {
  let stat: StatMeta = getStatByParameter(statString);
  return stat.formatValue(value);
}
