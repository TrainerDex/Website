<script lang="ts">
	import Paper, { Title, Content } from '@smui/paper';

	import Leaderboard from './Leaderboard.svelte';

	export let stat: string;
</script>

<Paper>
	<Title>Leaderboard</Title>
	<Content><Leaderboard {stat} /></Content>
</Paper>
