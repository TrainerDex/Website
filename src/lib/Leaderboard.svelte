<script lang="ts">
  import DataTable, { Head, Body, Row, Cell } from "@smui/data-table";
  import LinearProgress from "@smui/linear-progress";
  import {
    getStatByParameter,
    StatMeta,
    TotalXP,
    formatValue,
  } from "../models/stats";
  import moment from "moment";
  import type { SnapshotLeaderboard } from "src/models/leaderboard";

  async function loadLeaderboard(
    stat: StatMeta | string = TotalXP
  ): Promise<SnapshotLeaderboard> {
    if (typeof stat === "string") {
      stat = getStatByParameter(stat);
    }
    if (typeof fetch !== "undefined") {
      return fetch(
        `https://trainerdex.app/api/v2/leaderboard/?stat=${stat.parameter}`
      )
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
        <Cell>{getStatByParameter(leaderboard.stat).name}</Cell>
        <Cell>Submitted at</Cell>
      </Row>
    </Head>
    <Body>
      {#each leaderboard.entries as entry (entry.trainer_uuid)}
        <Row>
          <Cell numeric>{entry.rank}</Cell>
          <Cell>{entry.username}</Cell>
          <Cell>{formatValue(entry.value, leaderboard.stat)}</Cell>
          <Cell>{moment(entry.entry_datetime).format("ll")}</Cell>
        </Row>
      {/each}
    </Body>
  </DataTable>
{/await}
