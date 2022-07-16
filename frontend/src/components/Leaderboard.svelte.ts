import App from './Leaderboard.svelte';

const app = new App({
	target: document.getElementsByTagName('main')[0],
	props: JSON.parse(document.getElementById('leaderboard-props').textContent)
});

export default app;
