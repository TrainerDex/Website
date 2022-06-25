<script lang="ts">
  import DataTable, { Head, Body, Row, Cell } from "@smui/data-table";
  import Select, { Option } from "@smui/select";
  import IconButton from "@smui/icon-button";
  import { Label } from "@smui/common";
  import LinearProgress from "@smui/linear-progress";
  import {
    getStatByParameter,
    TotalXP,
    formatValue,
    listOfStats,
  } from "../models/stats";
  import moment from "moment";
  import type { SnapshotLeaderboard } from "src/models/leaderboard";
  import Pagination from "./Pagination.svelte";

  let statString = TotalXP.parameter;
  $: stat = getStatByParameter(statString);

  let leaderboard: SnapshotLeaderboard;

  $: loaded = leaderboard?.count ?? false;

  let rowsPerPage = 25;
  $: rowOffset = stat ? 0 : 0; // This resets rowOffset to 0 when stat is changed.

  $: maximumRowOffset = loaded ? Math.ceil(leaderboard.count - rowsPerPage) : 0;

  $: hasNextPage = rowOffset < maximumRowOffset;
  $: hasPreviousPage = rowOffset > 0;

  $: loadPage = async (): Promise<void> => {
    if (typeof fetch !== "undefined") {
      leaderboard = await fetch(
        `https://trainerdex.app/api/v2/leaderboard/?stat=${stat.parameter}&limit=${rowsPerPage}&offset=${rowOffset}`
      )
        .then((response) => response.json())
        .then((json) => json);
    }
  };
</script>

{#await loadPage()}
  <LinearProgress
    indeterminate
    aria-label="Data is being loaded..."
    slot="progress"
  />
{:then}
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
    <Pagination slot="paginate">
      <svelte:fragment slot="stat">
        <Label>Selected Stat</Label>
        <Select variant="outlined" bind:value={statString} noLabel>
          {#each listOfStats as stat}
            <Option value={stat.parameter}>{stat.name}</Option>
          {/each}
        </Select>
      </svelte:fragment>

      <svelte:fragment slot="rowsPerPage">
        <Label>Rows Per Page</Label>
        <Select variant="outlined" bind:value={rowsPerPage} noLabel>
          <Option value={10}>10</Option>
          <Option value={25}>25</Option>
          <Option value={100}>100</Option>
        </Select>
      </svelte:fragment>
      <svelte:fragment slot="total">
        {rowOffset + 1}-{rowOffset + rowsPerPage} of {leaderboard.count}
      </svelte:fragment>

      <IconButton
        class="material-icons"
        action="first-page"
        title="First page"
        on:click={() => (rowOffset = 0)}
        disabled={!hasPreviousPage}>first_page</IconButton
      >
      <IconButton
        class="material-icons"
        action="prev-page"
        title="Prev page"
        on:click={() => (rowOffset = Math.max(rowOffset - rowsPerPage, 0))}
        disabled={!hasPreviousPage}>chevron_left</IconButton
      >
      <IconButton
        class="material-icons"
        action="next-page"
        title="Next page"
        on:click={() =>
          (rowOffset = Math.min(rowOffset + rowsPerPage, maximumRowOffset))}
        disabled={!hasNextPage}>chevron_right</IconButton
      >
      <IconButton
        class="material-icons"
        action="last-page"
        title="Last page"
        on:click={() => (rowOffset = maximumRowOffset)}
        disabled={!hasNextPage}>last_page</IconButton
      >
    </Pagination>
  </DataTable>
{/await}
