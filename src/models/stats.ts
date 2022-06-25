export class StatMeta {
    parameter: string;
    name: string;
    description: string | null;

    constructor(parameter: string, name: string, description: string | null = null) {
        this.parameter = parameter;
        this.name = name;
        this.description = description;
    }
}

export const TotalXP = new StatMeta('total_xp', 'Total XP', 'Total XP');

export const listOfStats: StatMeta[] = [TotalXP];

export function getStatByParameter(parameter: string): StatMeta | null {
    return listOfStats.find(stat => stat.parameter === parameter) || null;
}

export function getStatByName(name: string): StatMeta | null {
    return listOfStats.find(stat => stat.name === name) || null;
}