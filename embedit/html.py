import html
from typing import Any
from urllib.parse import quote

__all__ = ("generate_tag", "generate_attribute", "generate_meta_tag", "generate_html")


def generate_tag(name: str, value: str = "", *, children: str | None = None) -> str:
    """Generates an html tag.

    Args:
        name (str): The name of the tag.
        value (str): The value provided inside of the tag, like attributes.
        children (str | None): The children of the element. This implicitly converts it from a < /> type tag to a <> </> tag.

    Returns:
        str: The tag.
    """  # noqa: E501
    if value:
        value = " " + value
    if children is not None:
        return f"<{name}{value}> {children} </{name}>"
    return f"<{name}{value}/>"


def generate_attribute(attribute: str, value: Any) -> str:
    """Generates a property value like ``foo="bar"``, with a space at the end.

    Args:
        attribute (str): The attribute's name.
        value (Any): The value of the property, this will implicitly call str() on it.

    Returns:
        str: The attribute value in the form of ``foo="bar" ``.
    """
    return f'{attribute}="{value}" '


def generate_meta_tag(
    *, prop: str | None = None, value: Any, extras: dict[str, Any] | None = None, safe: bool = True
) -> str:
    """Generates a meta tag with the property set and content set.

    Args:
        prop (str | None): The ``property`` tag value, if applicable.
        value (Any): The value of the tag. This has str() implicitly called on it.
        extras (dict[str, Any] | None): The extras to encode inside of the url.
        safe (bool): Whether or not to call ``urllib.parse.quote`` on the value.

    Returns:
        str: The meta tag, in the form of ``<meta foo=bar />``.
    """
    if extras is None:
        extras = {}
    if not safe:
        value = quote(str(value))
    attrs = ""

    if prop is not None:
        attrs += generate_attribute("property", prop)

    if value:
        attrs += generate_attribute("content", value)

    if extras:
        for key, val in extras.items():
            attrs += generate_attribute(key, val)

    return generate_tag("meta", attrs)


def generate_html(head_children: list[str], body_children: list[str] | None) -> str:
    head_children.append(generate_meta_tag(value="text/html; charset=UTF-8", extras={"http-equiv": "Content-Type"}))
    if not body_children:
        body_children = [header_to_text(head_children)]
    else:
        body_children.append(header_to_text(head_children))

    html = generate_tag("!DOCTYPE", "html")
    meta = generate_tag("head", children="\n".join(head_children))
    body = generate_tag("body", children="\n".join(body_children or []))
    return html + generate_tag("html", generate_attribute("lang", "en"), children=meta + body)


def header_to_text(headers: list[str]) -> str:
    """Turns the given head into html text tags for usage in the body.

    Args:
        headers (list[str]): The list of headers.

    Returns:
        str: _description_
    """
    return "\n".join(f"<pre><code>{html.escape(header)}</code></pre>" for header in headers)
