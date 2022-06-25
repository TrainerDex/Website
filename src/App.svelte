<script lang="ts">
  // import logo from "./assets/svelte.png";
  import Leaderboard from "./lib/Leaderboard.svelte";
</script>

<svelte:head>
  <link
    href="https://fonts.googleapis.com/css?family=Raleway"
    rel="stylesheet"
  />
  <link
    rel="stylesheet"
    href="/src/theme/_smui-theme.scss"
    media="(prefers-color-scheme: light)"
  />
  <link
    rel="stylesheet"
    href="/src/theme/dark/_smui-theme.scss"
    media="screen and (prefers-color-scheme: dark)"
  />
</svelte:head>

<main>
  <!-- <img src={logo} alt="Svelte Logo" /> -->
  <h1>TrainerDex</h1>

  <Leaderboard />
</main>

<style lang="scss">
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
