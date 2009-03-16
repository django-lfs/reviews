# django imports
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

# reviews imports
from reviews.models import Review
from reviews.settings import SCORE_CHOICES
from reviews import utils as reviews_utils

class ReviewAddForm(ModelForm):
    """Form to add a review.
    """
    class Meta:
        model = Review
        fields = ("user_name", "user_email", "comment", "score")
    
    def clean(self):
        """
        """
        # For an anonymous user the name is required. Please note that the 
        # request has to be passed explicitely to the form object (see add_form)
        msg = "This field is required"
        if self.request.user.is_anonymous():
            if self.cleaned_data.get("user_name", "") == "":
                self._errors["user_name"] = ErrorList([msg])

        return self.cleaned_data 
        
def add_form(request, content_type_id, content_id, template_name="reviews/review_form.html"):
    """Displays the form to add a review.
    """
    ctype = ContentType.objects.get_for_id(content_type_id)
    object = ctype.get_object_for_this_type(pk=content_id)
    
    if reviews_utils.has_rated(request, object):
        return HttpResponseRedirect(reverse("reviews_already_rated"))
        
    scores = []
    for i, score in enumerate(SCORE_CHOICES):
        scores.append({
            "title": score[0],
            "value" : score[0],
            "z_index" : 10-i,
            "width" : (i+1) * 25,
        })
    
    if request.method == "POST":
        form = ReviewAddForm(data=request.POST)
        form.request = request
        if form.is_valid():
            return preview(request)
    else:
        form = ReviewAddForm()
        
        
    return render_to_response(template_name, RequestContext(request, {
        "content_type_id" : content_type_id,
        "content_id" : content_id,
        "object" : object,
        "form" : form,
        "scores" : scores,
    }))

def reedit(request, template_name="reviews/review_form.html"):
    """Displays a form to edit a review. This is used if a reviewer re-edits 
    a review after she has previewed it.
    """
    # get object    
    content_type_id = request.POST.get("content_type_id")
    content_id = request.POST.get("content_id")

    ctype = ContentType.objects.get_for_id(content_type_id)
    object = ctype.get_object_for_this_type(pk=content_id)
    
    if reviews_utils.has_rated(request, object):
        return HttpResponseRedirect(reverse("reviews_already_rated"))

    scores = []
    for i, score in enumerate(SCORE_CHOICES):
        scores.append({
            "title": score[0],
            "value" : score[0],
            "current" : str(score[0]) == request.POST.get("score"),
            "z_index" : 10-i,
            "width" : (i+1) * 25,
        })
    
    form = ReviewAddForm(data=request.POST)
    return render_to_response(template_name, RequestContext(request, {
        "content_type_id" : content_type_id,
        "content_id" : content_id,
        "form" : form,
        "scores" : scores,
        "object" : object,
    }))
    
def reedit_or_save(request):
    """Edits or saves a review dependend on which button has been pressed.
    """
    if request.POST.get("edit"):
        return reedit(request)
    else:
        form = ReviewAddForm(data=request.POST)
        form.request = request
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.content_type_id = request.POST.get("content_type_id")
            new_review.content_id = request.POST.get("content_id")
            new_review.session_id = request.session.session_key
            new_review.ip_address = request.META.get("REMOTE_ADDR")
            if request.user.is_authenticated():
                new_review.user = request.user
            new_review.save()
        return HttpResponseRedirect(reverse("reviews_thank_you"))
    
def preview(request, template_name="reviews/review_preview.html"):
    """Displays a preview of the review.
    """
    content_type_id = request.POST.get("content_type_id")
    content_id = request.POST.get("content_id")
    
    ctype = ContentType.objects.get_for_id(content_type_id)
    object = ctype.get_object_for_this_type(pk=content_id)
    
    if request.user.is_authenticated():
        name = request.user.get_full_name()
        email = request.user.email
    else:
        name = request.POST.get("user_name")
        email = request.POST.get("user_email")
                
    return render_to_response(template_name, RequestContext(request, {
        "score" : float(request.POST.get("score", 0)),
        "object" : object,
        "name" : name,
        "email" : email,
    }))
    
def thank_you(request, template_name="reviews/thank_you.html"):
    """Displays a thank you page.
    """
    return render_to_response(template_name, RequestContext(request))
    
def already_rated(request, template_name="reviews/already_rated.html"):
    """
    """
    return render_to_response(template_name, RequestContext(request))