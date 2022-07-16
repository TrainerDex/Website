import App from './Pagination.svelte';

const app = new App({
	target: document.getElementsByTagName('main')[0],
	props: JSON.parse(document.getElementById('pagination-props').textContent)
});

export default app;
