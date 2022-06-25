<script lang="ts">
  import DataTable, { Head, Body, Row, Cell } from "@smui/data-table";
  import LinearProgress from "@smui/linear-progress";
  import Card, {
    Content,
    PrimaryAction,
    Actions,
    ActionButtons,
    ActionIcons,
  } from "@smui/card";
  import Button, { Label } from "@smui/button";
  import Select, { Option } from "@smui/select";
  import IconButton, { Icon } from "@smui/icon-button";
  import {
    getStatByParameter,
    StatMeta,
    TotalXP,
    formatValue,
    listOfStats,
  } from "../models/stats";
  import moment from "moment";
  import type { SnapshotLeaderboard } from "src/models/leaderboard";

  let statString = TotalXP.parameter;
  $: stat = getStatByParameter(statString);

  $: loadLeaderboard = async (): Promise<SnapshotLeaderboard> => {
    if (typeof fetch !== "undefined") {
      return fetch(
        `https://trainerdex.app/api/v2/leaderboard/?stat=${stat.parameter}`
      )
        .then((response) => response.json())
        .then((json) => json);
    }
  };
</script>

<div class="card-display">
  <div class="card-container">
    <Card>
      <Content>
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
      </Content>
      <Actions>
        <div class="columns margins" style="justify-content: flex-start;">
          <Select bind:value={statString} label="Stat">
            {#each listOfStats as stat}
              <Option value={stat.parameter}>{stat.name}</Option>
            {/each}
          </Select>
        </div>
        <IconButton
          toggle
          aria-label="Add to favorites"
          title="Add to favorites"
        >
          <Icon class="material-icons" on>favorite</Icon>
          <Icon class="material-icons">favorite_border</Icon>
        </IconButton>
        <IconButton class="material-icons" title="Share">share</IconButton>
        <IconButton class="material-icons" title="More options"
          >more_vert</IconButton
        >
      </Actions>
    </Card>
  </div>
</div>
