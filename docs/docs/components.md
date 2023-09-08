# Components

> You can probably do most of the things that you can do with `svelte web components`.
> 
> Check out the [svelte web components documentation](https://svelte.dev/docs/custom-elements-api).

Create one or more folders to store your components, for example `assets/components`.

You can nest components in sub-folders with no problem.


## Example component

``` html title="Svelte"
<svelte:options customElement="my-counter" />

<script>
    let count = 0;
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

``` html title="Svelte"
<svelte:options customElement="my-counter" />

<script>
    import moment from 'moment'
    let count = 0;
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
