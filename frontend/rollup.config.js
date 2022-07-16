import svelte from 'rollup-plugin-svelte';
import commonjs from '@rollup/plugin-commonjs';
import resolve from '@rollup/plugin-node-resolve';
import { terser } from 'rollup-plugin-terser';
import sveltePreprocess from 'svelte-preprocess';
import typescript from '@rollup/plugin-typescript';
import css from 'rollup-plugin-css-only';
import replace from '@rollup/plugin-replace';
import fs from 'fs';

// const production = !process.env.ROLLUP_WATCH;
const production = false;

function componentExportDetails(componentName) {
	return {
		input: `src/components/${componentName}.svelte.ts`,
		output: {
			sourcemap: true,
			format: 'iife',
			name: componentName,
			file: `public/build/${componentName}.js`
		},
		plugins: [
			replace({
				__API_BASE_URL__: process.env.API_BASE_URL
			}),
			svelte({
				preprocess: sveltePreprocess(),
				compilerOptions: {
					// enable run-time checks when not in production
					dev: !production
				}
			}),
			// we'll extract any component CSS out into
			// a separate file - better for performance
			css({ output: `${componentName}.css` }),

			// If you have external dependencies installed from
			// npm, you'll most likely need these plugins. In
			// some cases you'll need additional configuration -
			// consult the documentation for details:
			// https://github.com/rollup/plugins/tree/master/packages/commonjs
			resolve({
				browser: true,
				dedupe: ['svelte']
			}),
			commonjs(),
			typescript({
				sourceMap: !production,
				inlineSources: !production
			}),

			// If we're building for production (npm run build
			// instead of npm run dev), minify
			production && terser()
		],
		watch: {
			clearScreen: false
		}
	};
}

let exportable = [];

// Add your component names here!

// Get all components from the src/components directory
const components = fs.readdirSync('./src/components'); // returns an array of all files in the directory
for (let i = 0; i < components.length; i++) {
	if (components[i].endsWith('.svelte.ts')) {
		exportable.push(componentExportDetails(components[i].replace('.svelte.ts', '')));
	}
}

export default exportable;
