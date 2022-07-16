import App from './LargeLeaderboard.svelte';

const app = new App({
	target: document.getElementsByTagName('main')[0],
	props: JSON.parse(document.getElementById('largeleaderboard-props').textContent)
});

export default app;
