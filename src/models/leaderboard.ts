export type SnapshotLeaderboardAggregation = {
	average: number;
	min: number;
	max: number;
	sum: number;
};

export type SnapshotLeaderboardEntry = {
	rank: number;
	username: string;
	faction: number;
	value: number;
	trainer_uuid: string;
	entry_uuid: string;
	entry_datetime: Date;
};

export type SnapshotLeaderboard = {
	count: number | null;
	next: URL | null;
	previous: URL | null;
	generated_datetime: Date;
	datetime: Date;
	title: string;
	stat: string;
	aggregations: SnapshotLeaderboardAggregation;
	entries: SnapshotLeaderboardEntry[];
};
