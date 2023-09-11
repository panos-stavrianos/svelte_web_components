import {defineConfig} from "vite";
import {svelte} from "@sveltejs/vite-plugin-svelte";


export default defineConfig({
    mode: 'production',
    plugins: [svelte({
        include: [`./**/*.svelte`],
        compilerOptions: {
            customElement: true,
        },
    }),],
    build: {
        write: false,
        rollupOptions: {
            input: "./components.js", // Set the entry point to main.js
            output: {
                entryFileNames: `[name].js`,
            }
        },
    }
});


