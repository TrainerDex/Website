<script lang="ts">
  // import logo from "./assets/svelte.png";
  import Leaderboard from "./lib/Leaderboard.svelte";

  import type { TopAppBarComponentDev } from "@smui/top-app-bar";
  import TopAppBar, {
    Row,
    Section,
    Title,
    AutoAdjust,
  } from "@smui/top-app-bar";
  import IconButton from "@smui/icon-button";

  let topAppBar: TopAppBarComponentDev;
</script>

<TopAppBar bind:this={topAppBar} variant="fixed">
  <Row>
    <Section>
      <!-- <IconButton class="material-icons">menu</IconButton> -->
      <Title>TrainerDex</Title>
    </Section>
    <!-- <Section align="end" toolbar>
      <IconButton class="material-icons" aria-label="Download"
        >file_download</IconButton
      >
      <IconButton class="material-icons" aria-label="Print this page"
        >print</IconButton
      >
      <IconButton class="material-icons" aria-label="Bookmark this page"
        >bookmark</IconButton
      >
    </Section> -->
  </Row>
</TopAppBar>
<AutoAdjust {topAppBar}>
  <Leaderboard />
</AutoAdjust>

<style>
  /* Hide everything above this component. */
  :global(app),
  :global(body),
  :global(html) {
    margin: 0;
    padding: 0;
    display: block !important;
    height: auto !important;
    width: auto !important;
    position: static !important;
  }

  :root {
    font-family: "Raleway", "Roboto", "Segoe UI", Roboto, Oxygen, Ubuntu,
      Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  }

  main {
    text-align: center;
    padding: 1em;
    margin: 0 auto;
  }

  img {
    height: 16rem;
    width: 16rem;
  }

  h1 {
    font-size: 4rem;
    font-weight: 100;
    line-height: 1.1;
    margin: 2rem auto;
    max-width: 14rem;
  }

  p {
    max-width: 14rem;
    margin: 1rem auto;
    line-height: 1.35;
  }

  @media (min-width: 480px) {
    h1 {
      max-width: none;
    }

    p {
      max-width: none;
    }
  }
</style>
