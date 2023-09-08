# FastAPI integration

Using the `SvelteFiles` class you can integrate your components with FastAPI very easily and with good performance.

## Extra features

* Generate input `<script>` elements for your components and make them available in your html template.
* Automatic mount of the components.
* Proper cache handling.

## Usage

Initiate a `SvelteFiles` instance with the path to your components folder and a name.
Also pass the `templates` and `app` arguments.

> This also support multiple component folders

``` python
from svelte_web_components import SvelteFiles 
app = FastAPI()
templates = Jinja2Templates(directory="templates")

svelte = SvelteFiles({
    "c_home": "assets/components/home",
    "c_contact": "assets/components/contact",
}, templates=templates, app=app)
```

In your html file, import all js bundles:

``` html
<my-component name="John"></my-component>
{{ svelte_scripts | safe }}
```

You can also import only the js bundles that you need:

``` html
<my-component name="John"></my-component>
{{ svelte_script["c_home"] | safe }}
```

## Alternative usage

### No automatic mount

If you don't want to automatically mount the components, you can use the `SvelteFiles` class like this:

``` python
from svelte_web_components import SvelteFiles
app = FastAPI()
templates = Jinja2Templates(directory="templates")

svelte = SvelteFiles({
    "/components/c1": "templates/components/c1",
    "/components/c2": "templates/components/c2"
}, )

app.mount("/components/c1", svelte)
app.mount("/components/c2", svelte)
```

### No automatic input script generation and insertion

``` html
<my-component name="John"></my-component>
<script src="/components/c1/" type="module"></script>
<script src="/components/c2/" type="module"></script>
```

> A small detail, notice that the `src` attribute ends with `/`, if we remove it,
> the fastapi will return redirect to the same url with `/` at the end.
> So we add it to prevent an extra round trip to the server.