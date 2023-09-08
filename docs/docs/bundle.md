# Bundle

The Bundle class can generate multiple js bundles and install extra npm packages.

> The actual build will happen on the initialization of the Bundle instance.

## Usage

### Simple example

Here we have only one folder with components

``` python
from svelte_web_components import Bundle

bundle = Bundle({
    "components": "assets/components",
})

js_bundle = bundle["components"]
```

the js_bundle variable will contain the js code as string.

### Multiple component folders

In this way you can use `code splitting` to load only the components that you need.

> This is only useful if you have some large npm packages that you don't need in all pages.
>
> Otherwise, it's better to have only one bundle because the generated js code
> will almost be the same.

``` python
from svelte_web_components import Bundle
bundle = Bundle({
    "c_home": "assets/components/home",
    "c_contact": "assets/components/contact",
})

components_home = bundle["c_home"]
components_contact = bundle["c_contact"]
```

### Install extra npm packages

You can install extra npm packages that your components need.

``` python
from svelte_web_components import Bundle

bundle = Bundle({"components": "assets/components", }, extra_packages=["moment"])

js_bundle = bundle["components"]
```

### Npm packages conflicts

For now there is no way to resolve npm packages conflicts, as all the packages are installed in the same folder,
even for different projects. So if you have two projects that use different versions of the same package,
the last one that will be installed will overwrite the other one.

This limitation will be fixed in the future, maybe by installing the packages in a different folder for each project.