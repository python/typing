# Static Typing for Python

## Documentation and Support

The documentation for Python's static typing can be found at
[typing.readthedocs.io](https://typing.readthedocs.io/). You can get
help in our [support forum](https://github.com/python/typing/discussions).

Improvements to the type system should be discussed on
[Python's Discourse](https://discuss.python.org/c/typing/32), and are
tracked in the [issues](https://github.com/python/typing/issues) in this
repository.

For conversations that are more suitable to a chat platform, you can use one of the following:

- [gitter](https://gitter.im/python/typing)
- [discord](https://discord.com/channels/267624335836053506/891788761371906108) `#type-hinting` channel

## Repository Content

This GitHub repository is used for several things:

- The documentation at [typing.readthedocs.io](https://typing.readthedocs.io/)
  is maintained in the [docs directory](./docs).

- A [discussion forum](https://github.com/python/typing/discussions) for typing-related user
  help is hosted here.

Historically, this repository also hosted:

- The `typing_extensions` package, which now lives in the
  [typing_extensions](https://github.com/python/typing_extensions) repo.
  It used to be in the `typing_extensions` directory.

- A backport of the
  [`typing` module](https://docs.python.org/3/library/typing.html) for older
  Python versions. It was removed after all Python versions that lack `typing`
  in the standard library reached end of life. The last released version,
  supporting Python 2.7 and 3.4,
  is [available at PyPI](https://pypi.org/project/typing/).
