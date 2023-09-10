import {build} from 'vite';

async function buildViteProject() {
    try {

        // Create a Vite build instance
        const buildResult = await build({
            configFile: 'vite.config.js',
            logLevel: 'silent',
        },);

        // You can access the build result and do further processing here if needed
        console.log(buildResult.output[0].code);
    } catch (error) {
        console.error('Error building Vite project:', error);
    }
}

buildViteProject();
