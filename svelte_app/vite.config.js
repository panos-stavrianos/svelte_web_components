import {defineConfig} from "vite";
import {svelte} from "@sveltejs/vite-plugin-svelte";


export default defineConfig({
    mode: 'production', plugins: [svelte({
        include: [`./components/**/*.svelte`], compilerOptions: {
            customElement: true,
        },
    }),], build: {
        write: false, rollupOptions: {
            input: "./components.js", // Set the entry point to main.js
            output: {
                entryFileNames: `[name].js`,
            }
        },

    }, resolve: {
        alias: {
            'moment': '/home/panos/WebstormProjects/svelte_test/node_modules/moment', // Add more aliases for other packages as needed
        },
    }
});


