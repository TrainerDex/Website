<script lang="ts">
	import Leaderboard from '../components/Leaderboard.svelte';

	import type { TopAppBarComponentDev } from '@smui/top-app-bar';
	import TopAppBar, { Row, Section, Title, AutoAdjust } from '@smui/top-app-bar';

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
		font-family: 'Raleway', Roboto, Oxygen, Ubuntu, 'Open Sans', sans-serif;
	}
</style>
