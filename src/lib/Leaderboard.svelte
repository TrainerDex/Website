<script lang="ts">
  import DataTable, { Head, Body, Row, Cell } from "@smui/data-table";
  import LinearProgress from "@smui/linear-progress";

  type SnapshotLeaderboardAggregation = {
    average: number;
    min: number;
    max: number;
    sum: number;
  };

  type SnapshotLeaderboardEntry = {
    rank: number;
    username: string;
    faction: number;
    value: number;
    trainer_uuid: string;
    entry_uuid: string;
    entry_datetime: Date;
  };

  type SnapshotLeaderboard = {
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

  let leaderboard: SnapshotLeaderboard | null = null;
  let loaded = false;

  async function loadLeaderboard(
    stat: string = "total_xp"
  ): Promise<SnapshotLeaderboard> {
    if (typeof fetch !== "undefined") {
      return fetch(`https://trainerdex.app/api/v2/leaderboard/?stat=${stat}`)
        .then((response) => response.json())
        .then((json) => json);
    }
  }
</script>

{#await loadLeaderboard()}
  <DataTable table$aria-label="Leaderboard" style="width: 100%;">
    <Head>
      <Row>
        <Cell numeric>Rank</Cell>
        <Cell style="width: 100%;">Name</Cell>
        <Cell>Stat</Cell>
        <Cell>Submitted at</Cell>
      </Row>
    </Head>
    <Body />

    <LinearProgress
      indeterminate
      bind:closed={loaded}
      aria-label="Data is being loaded..."
      slot="progress"
    />
  </DataTable>
{:then leaderboard}
  <DataTable table$aria-label="Leaderboard" style="width: 100%;">
    <Head>
      <Row>
        <Cell numeric>Rank</Cell>
        <Cell style="width: 100%;">Name</Cell>
        <Cell>{leaderboard.stat}</Cell>
        <Cell>Submitted at</Cell>
      </Row>
    </Head>
    <Body>
      {#each leaderboard.entries as entry (entry.trainer_uuid)}
        <Row>
          <Cell numeric>{entry.rank}</Cell>
          <Cell>{entry.username}</Cell>
          <Cell>{entry.value}</Cell>
          <Cell>{entry.entry_datetime}</Cell>
        </Row>
      {/each}
    </Body>
  </DataTable>
{/await}
