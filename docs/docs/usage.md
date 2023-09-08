# Usage

## Install

``` bash
pip install svelte-web-components
# or 
pip install "svelte_web_components[fastapi]"
```

## Create a component

Create a folder to store your components, for example `assets/components`.

In there create a file `my_component.svelte` for your component:

``` html title="Svelte"
<svelte:options customElement="my_component"/>
<script>
  export let name = 'World';
</script>

<h1>Hello {name}!</h1>
```

## Generate the js bundle

If you are using `fastapi` see [bellow](#fastapi-integration).

> Flask and other frameworks are not supported yet, but it will be easy to add support for them.

Initiate a `Bundle` instance with the path to your components folder and a name:

``` python
from svelte_web_components import Bundle

bundle = Bundle({
    "components": "assets/components",
})

js_bundle = bundle["components"]
```

### Use the component

In your html file, import the js bundle:

``` html  
<my-component name="John"></my-component>

<script>
{{ js_bundle | safe }}
</script>
```

> This is not a good way to import the js bundle,
> because it will be loaded synchronously and will block the page rendering.
> Also your html file would be huge because this will add inline the js bundle.

### FastAPI integration

Generate you components the same way as before.

Initiate a `SvelteFiles` instance with the path to your components folder and a name.
Also pass the `templates` and `app` arguments.

``` python
from svelte_web_components import SvelteFiles 
app = FastAPI()
templates = Jinja2Templates(directory="templates")

svelte = SvelteFiles({
       "components": "assets/components",
}, templates=templates, app=app)
```

In your html file, import the js bundle:

``` html
<my-component name="John"></my-component>
{{ svelte_scripts | safe }}
```

This will take care of loading the js bundle asynchronously and only once.

For more details see the [Bundle](/svelte_web_components/bundle) and [FastAPI integration](/svelte_web_components/fastapi_integration) pages.

