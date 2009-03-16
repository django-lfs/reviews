# django imports
from django import template
from django.contrib.contenttypes.models import ContentType

# review imports
from reviews.models import Review
from reviews import utils as reviews_utils

register = template.Library()

@register.inclusion_tag('reviews/reviews_for_instance.html', takes_context=True)
def reviews_for_instance(context, instance):
    """
    """
    ctype = ContentType.objects.get_for_model(instance)
    has_rated = reviews_utils.has_rated(context.get("request"), instance)
    reviews = reviews_utils.get_reviews_for_instance(instance)

    return {
        "reviews" : reviews,
        "has_rated" : has_rated,
        "content_id" : instance.id,
        "content_type_id" : ctype.id,
    }

@register.inclusion_tag('reviews/average_for_instance.html', takes_context=True)
def average_for_instance(context, instance):
    """
    """
    average = reviews_utils.get_average_for_instance(instance)
    return {
        "average" : average,
    }