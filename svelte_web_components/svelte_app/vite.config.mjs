import {defineConfig} from "vite";
import {svelte, vitePreprocess} from "@sveltejs/vite-plugin-svelte";


export default defineConfig({
    mode: 'production',
    plugins: [
        svelte({
            configFile: false,
            preprocess: vitePreprocess(),
            include: [`../../**/*.svelte`],
            compilerOptions: {
                customElement: true,
            },
        }),
    ],
    build: {
        write: true,
        rollupOptions: {
            input: "./components.js", // Set the entry point to main.js
            output: {
                entryFileNames: `[name].js`,
            }
        },
    },
});


