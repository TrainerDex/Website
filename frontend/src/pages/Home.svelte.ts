import App from './Home.svelte';

const app = new App({
	target: document.getElementsByTagName('main')[0],
	props: JSON.parse(document.getElementById('home-props').textContent)
});

export default app;
