from django import template

register = template.Library()


@register.simple_tag
def check_like(post, user):
    return post.is_liked_by_user(user)


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})
