# Introduction

This is an experiment!

It's a way to see if it's possible to use Svelte web components from Python without a build step.

## Why?

I am currently very happy with `fastapi`, `jinja2` and `htmx` for building web applications.

But I was needing a way to build small but rich web components.

I had try `svelte` in the past, and I was very impressed by the reactivity and the simplicity of the components.
The problem was that I don't to add a build step to my projects.

> What if there was a way to just write `.svelte` files and import them in html like `.js` files?

## How?

### What happens on installation?

When you run `pip install svelte-web-components` it will do the following:

* Download `node` in `~/.svelte-web-components/node`
* Copy a base project in `~/.svelte-web-components/svete_app`
* Install `svelte` and `vite` in `~/.svelte-web-components/svete_app` creating `node_modules`

### What happens at runtime?

When you run initiate Bundle or SvelteFiles instances, it will:

* Copy the all the `.svelte` files from the folder you specify in <br/> `~/.svelte-web-components/svete_app/components`
* Run `vite build` in `~/.svelte-web-components/svete_app` to build the components
* Save in memory the generated bundles for fast access in the future

