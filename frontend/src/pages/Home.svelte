<script lang="ts">
	import LayoutGrid, { Cell } from '@smui/layout-grid';
	import Paper, { Title, Content } from '@smui/paper';

	import Leaderboard from '../components/LeaderboardComponent.svelte';

	export let stat: string | undefined = undefined;
</script>

<LayoutGrid>
	<Cell span={4}>
		<Paper>
			<Title>Leaderboard</Title>
			<Content style="margin: 0px -16px -24px -16px"
				><Leaderboard {stat} rowsPerPage={10} /></Content
			>
		</Paper>
	</Cell>
	<Cell span={4}>
		<Paper>
			<Title>Welcome</Title>
			<Content>Welcome to TrainerDex, the Pokemon Go Trainer leaderboard.</Content>
		</Paper>
	</Cell>
	<Cell span={4}>
		<Paper style="padding: 0px">
			<iframe
				src="https://discord.com/widget?id=364313717720219651&theme=light"
				height="500"
				allowtransparency={true}
				sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"
				title="Discord Widget"
			/>
		</Paper>
	</Cell>
</LayoutGrid>
