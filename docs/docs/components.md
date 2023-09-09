# Components

> You can probably do most of the things that you can do with `svelte web components`.
>
> Check out the [svelte web components documentation](https://svelte.dev/docs/custom-elements-api).



Create one or more folders to store your components, for example `assets/components`.

You can nest components in sub-folders with no problem.

## svelte-retag

`<svelte:options/>` is not supported because this library
uses [svelte-retag](https://github.com/patricknelson/svelte-retag) .

The reason is to overcome [svelte limitations](https://github.com/patricknelson/svelte-retag) with custom elements.
In specific, the fact that when shadow DOM is disabled, the `<slot/>` is not working. Check out this [discussion](https://github.com/sveltejs/svelte/issues/8686).

If the svelte team decides to fix this issue, we can drop svelte-retag and use the base svelte library.

Svelte-retag wants to support `<svelte:options/>` in the future, so we will be able to use it when it's ready.

 

**Shadow DOM** is disabled by default, currently there is no way to enable it, but it will be added in the future.

## Example component

Let's create a simple component that increments a counter when you click on a button.

Make sure that your file name is CamelCase and comprised of at least two words.
This important because the component name will be the file name converted to kebab-case.

For example `MyComponent.svelte` will be `<my-component></my-component>`.

``` html title="MyCounter.svelte"
<script>
    export let count = 0;
    $: count = Number(count) || 0; // convert to number

    const increment = () => {
        count += 1;
    };
</script>

<button on:click={increment}>
    count is {count}
</button>
```

## Use npm packages

You can use npm packages in your components, but don't forget to add them to the `extra_packages` argument of
the `Bundle` or `SvelteFiles` class.

``` html title="MyCounter.svelte"
<script>
    import moment from 'moment'
    let count = 0;
    $: count = Number(count) || 0; // convert to number
    
    let time = moment().format("MMMM Do YYYY, h:mm:ss a");
    const increment = () => {
        count += 1;
        time = moment().format("MMMM Do YYYY, h:mm:ss a");
    };
</script>

<button on:click={increment}>
    count is {count}
</button>
<h1>The time is {time}</h1>
```
