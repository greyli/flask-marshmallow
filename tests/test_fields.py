import pytest
from flask import url_for
from flask_marshmallow.fields import _tpl
from werkzeug.routing import BuildError


@pytest.mark.parametrize(
    "template", ["<id>", " <id>", "<id> ", "< id>", "<id  >", "< id >"]
)
def test_tpl(template):
    assert _tpl(template) == "id"
    assert _tpl(template) == "id"
    assert _tpl(template) == "id"


def test_url_field(ma, mockauthor):
    field = ma.URLFor("author", values=dict(id="<id>"))
    result = field.serialize("url", mockauthor)
    assert result == url_for("author", id=mockauthor.id)

    mockauthor.id = 0
    result = field.serialize("url", mockauthor)
    assert result == url_for("author", id=0)


def test_url_field_with_invalid_attribute(ma, mockauthor):
    field = ma.URLFor("author", values=dict(id="<not-an-attr>"))
    expected_msg = "{!r} is not a valid attribute of {!r}".format(
        "not-an-attr", mockauthor
    )
    with pytest.raises(AttributeError, match=expected_msg):
        field.serialize("url", mockauthor)


def test_url_field_handles_nested_attribute(ma, mockbook, mockauthor):
    field = ma.URLFor("author", values=dict(id="<author.id>"))
    result = field.serialize("url", mockbook)
    assert result == url_for("author", id=mockauthor.id)


def test_url_field_handles_none_attribute(ma, mockbook, mockauthor):
    mockbook.author = None

    field = ma.URLFor("author", values=dict(id="<author>"))
    result = field.serialize("url", mockbook)
    assert result is None

    field = ma.URLFor("author", values=dict(id="<author.id>"))
    result = field.serialize("url", mockbook)
    assert result is None


def test_url_field_deserialization(ma):
    field = ma.URLFor("author", values=dict(id="<not-an-attr>"), allow_none=True)
    # noop
    assert field.deserialize("foo") == "foo"
    assert field.deserialize(None) is None


def test_invalid_endpoint_raises_build_error(ma, mockauthor):
    field = ma.URLFor("badendpoint")
    with pytest.raises(BuildError):
        field.serialize("url", mockauthor)


def test_hyperlinks_field(ma, mockauthor):
    field = ma.Hyperlinks(
        {
            "self": ma.URLFor("author", values={"id": "<id>"}),
            "collection": ma.URLFor("authors"),
        }
    )

    result = field.serialize("_links", mockauthor)
    assert result == {
        "self": url_for("author", id=mockauthor.id),
        "collection": url_for("authors"),
    }


def test_hyperlinks_field_recurses(ma, mockauthor):
    field = ma.Hyperlinks(
        {
            "self": {
                "href": ma.URLFor("author", values={"id": "<id>"}),
                "title": "The author",
            },
            "collection": {"href": ma.URLFor("authors"), "title": "Authors list"},
        }
    )
    result = field.serialize("_links", mockauthor)

    assert result == {
        "self": {"href": url_for("author", id=mockauthor.id), "title": "The author"},
        "collection": {"href": url_for("authors"), "title": "Authors list"},
    }


def test_hyperlinks_field_recurses_into_list(ma, mockauthor):
    field = ma.Hyperlinks(
        [
            {"rel": "self", "href": ma.URLFor("author", values={"id": "<id>"})},
            {"rel": "collection", "href": ma.URLFor("authors")},
        ]
    )
    result = field.serialize("_links", mockauthor)

    assert result == [
        {"rel": "self", "href": url_for("author", id=mockauthor.id)},
        {"rel": "collection", "href": url_for("authors")},
    ]


def test_hyperlinks_field_deserialization(ma):
    field = ma.Hyperlinks(
        {"href": ma.URLFor("author", values={"id": "<id>"})}, allow_none=True
    )
    # noop
    assert field.deserialize("/author") == "/author"
    assert field.deserialize(None) is None


def test_absolute_url(ma, mockauthor):
    field = ma.AbsoluteURLFor("authors")
    result = field.serialize("abs_url", mockauthor)
    assert result == url_for("authors", _external=True)


def test_absolute_url_deserialization(ma):
    field = ma.AbsoluteURLFor("authors", allow_none=True)
    assert field.deserialize("foo") == "foo"
    assert field.deserialize(None) is None


def test_aliases(ma):
    from flask_marshmallow.fields import AbsoluteUrlFor, AbsoluteURLFor, UrlFor, URLFor

    assert UrlFor is URLFor
    assert AbsoluteUrlFor is AbsoluteURLFor
