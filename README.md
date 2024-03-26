
# Embedit

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/) [![Python Versions](https://img.shields.io/badge/Python-3.11%20|%203.12-blue.svg)](https://python.org)

Embedit is a project that strives to provide a website that allows every social media platform to be embedded in apps like
discord (and any others that support the opengraph and twitter cards data).

> [!WARNING]
> While this server takes steps to avoid detection from
> social media sites, like caching, it cannot be guaranteed
> that you won't be detected/banned from a social media.
> This program makes no guarantees that you will not be banned.




## Deployment

To install and deploy, Python 3.11+ and python-poetry are required.

After you have those, move ``config-template.toml`` to ``config.toml`` and fill it out with your information.

Then, you can run the following commands:

```bash
  poetry install
```

After running this, you can start the server with:

```bash
  poetry run poe run
  # Or
  poetry run poe dev # for the dev server (reloading)
```


## Contributing

Contributions are always welcome!

If you would like another provider for more social medias, you can either open an issue or contribute it yourself.

You can run ``poetry run poe dev`` to start the development server. Additionally, you should also run ``poetry run pre-commit install`` and have pre-commit on your path so tests are ran before you commit. If you would prefer not installing pre-commit, ``poetry run poe all`` does the same thing.

<details>
<summary>More information on providers</summary>
<br />
If you would like to contribute another provider for
other social medias, take a look [at the code](embedit/providers/provider.py) for the base provider. Also in that directory are other implmented providers for usage as a base.

A couple of notes:

    1. Providers should only match their given URLs.
    2. Providers should avoid making any extrenous web requests and try to call out to the website only.
    3. Providers should raise a ``fastapi.HttpException`` if an error occurs within them.

</details>


## License

[MIT](https://choosealicense.com/licenses/mit/)

