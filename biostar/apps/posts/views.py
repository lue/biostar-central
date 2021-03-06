# Create your views here.
from django.shortcuts import render_to_response
from django.views.generic import TemplateView, DetailView, ListView, FormView, UpdateView
from .models import Post, RelatedPosts, Tag
from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, Submit, ButtonHolder
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from . import auth
from braces.views import LoginRequiredMixin
from datetime import datetime
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from biostar.const import OrderedDict
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from mptt.templatetags.mptt_tags import cache_tree_children
from biostar.server.ajax import json_response
from django_select2 import AutoModelSelect2Field, AutoHeavySelect2Widget, AutoModelSelect2TagField
import logging

logger = logging.getLogger(__name__)


def valid_title(text):
    "Validates form input for tags"
    text = text.strip()
    if not text:
        raise ValidationError(_('Please enter a title'))

    if len(text) < 10:
        raise ValidationError(_('The title is too short'))

    words = text.split(" ")
    if len(words) < 3:
        raise ValidationError(_('More than two words please.'))


def valid_tag(text):
    "Validates form input for tags"
    text = text.strip()
    if not text:
        raise ValidationError(_('Please enter at least one tag'))
    if len(text) > 50:
        raise ValidationError(_('Tag line is too long (50 characters max)'))
    words = text.split(",")
    if len(words) > 5:
        raise ValidationError(_('You have too many tags (5 allowed)'))


class LongForm(forms.Form):
    FIELDS = "title content post_type".split()

    POST_CHOICES = [(Post.QUESTION, _("Question")),
                    (Post.JOB, _("Job Ad")),
                    (Post.TUTORIAL, _("Tutorial")), (Post.TOOL, _("Tool")),
                    (Post.FORUM, _("Forum")), (Post.NEWS, _("News")),
                    (Post.BLOG, _("Blog")), (Post.PAGE, _("Page"))]

    title = forms.CharField(
        label=_("Post Title"),
        max_length=200, min_length=10, validators=[valid_title],
        help_text=_("Descriptive titles promote better answers."))

    post_type = forms.ChoiceField(
        label=_("Post Type"),
        choices=POST_CHOICES, help_text=_("Select a post type: Question, Forum, Job, Blog"))

    content = forms.CharField(widget=forms.Textarea,
                              min_length=80, max_length=15000,
                              label=_("Enter your post below"))

    def __init__(self, *args, **kwargs):
        super(LongForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "post-form"
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                'Post Form',
                Field('title'),
                Field('post_type'),
                Field('content'),
            ),
        )


class RelatedPostChoices(AutoModelSelect2Field):
    queryset = Post.objects.filter(type=0)
    search_fields = ['title__icontains', ]


class RelatedForm(forms.ModelForm):
    model = RelatedPosts

    similar_post = RelatedPostChoices(
        label=u'Post',
        widget=AutoHeavySelect2Widget(
            select2_options={
                'width': '30em',
                'placeholder': _('Post'),
                'minimumInputLength': 1,
            }
        )
    )
    fields = ('similar_post', 'type')

    def __init__(self, *args, **kwargs):
        super(RelatedForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class RelatedFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(RelatedFormSetHelper, self).__init__(*args, **kwargs)
        self.form_tag = False


class ShortForm(forms.Form):
    FIELDS = ["content"]

    content = forms.CharField(widget=forms.Textarea, min_length=20)

    def __init__(self, *args, **kwargs):
        super(ShortForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                'Post',
                'content',
            ),
        )


def parse_tags(category, tag_val):
    pass


@login_required
@csrf_exempt
def external_post_handler(request):
    "This is used to pre-populate a new form submission"
    import hmac

    user = request.user
    home = reverse("home")
    name = request.REQUEST.get("name")

    if not name:
        messages.error(request, _("Incorrect request. The name parameter is missing"))
        return HttpResponseRedirect(home)

    try:
        secret = dict(settings.EXTERNAL_AUTH).get(name)
    except Exception, exc:
        logger.error(exc)
        messages.error(request, _("Incorrect EXTERNAL_AUTH settings, internal exception"))
        return HttpResponseRedirect(home)

    if not secret:
        messages.error(request, _("Incorrect EXTERNAL_AUTH, no KEY found for this name"))
        return HttpResponseRedirect(home)

    content = request.REQUEST.get("content")
    submit = request.REQUEST.get("action")
    digest1 = request.REQUEST.get("digest")
    digest2 = hmac.new(secret, content).hexdigest()

    if digest1 != digest2:
        messages.error(request, _("digests does not match"))
        return HttpResponseRedirect(home)

    # auto submit the post
    if submit:
        post = Post(author=user, type=Post.QUESTION)
        for field in settings.EXTERNAL_SESSION_FIELDS:
            setattr(post, field, request.REQUEST.get(field, ''))
        post.save()
        post.add_tags(post.tag_val)
        return HttpResponseRedirect(reverse("post-details", kwargs=dict(pk=post.id)))

    # pre populate the form
    sess = request.session
    sess[settings.EXTERNAL_SESSION_KEY] = dict()
    for field in settings.EXTERNAL_SESSION_FIELDS:
        sess[settings.EXTERNAL_SESSION_KEY][field] = request.REQUEST.get(field, '')

    return HttpResponseRedirect(reverse("new-post"))


class NewPost(LoginRequiredMixin, FormView):
    form_class = LongForm
    template_name = "post_edit.html"

    def get(self, request, *args, **kwargs):
        initial = dict()

        # Attempt to prefill from GET parameters
        for key in "title tag_val content".split():
            value = request.GET.get(key)
            if value:
                initial[key] = value

        # Attempt to prefill from external session
        sess = request.session
        if settings.EXTERNAL_SESSION_KEY in sess:
            for field in settings.EXTERNAL_SESSION_FIELDS:
                initial[field] = sess[settings.EXTERNAL_SESSION_KEY].get(field)
            del sess[settings.EXTERNAL_SESSION_KEY]

        form = self.form_class(initial=initial)

        # Related formset
        RelatedFormSet = inlineformset_factory(Post, RelatedPosts, RelatedForm, fk_name="post")
        formset = RelatedFormSet()
        helper = RelatedFormSetHelper()
        return render(request, self.template_name, {'form': form, 'formset': formset, 'helper': helper})

    def post(self, request, *args, **kwargs):
        # Validating the form.
        form = self.form_class(request.POST)

        # Related formset
        RelatedFormSet = inlineformset_factory(Post, RelatedPosts, RelatedForm, fk_name="post")
        formset = RelatedFormSet(request.POST)
        helper = RelatedFormSetHelper()

        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'formset': formset, 'helper': helper})

        # Valid forms start here.
        data = form.cleaned_data.get

        title = data('title')
        content = data('content')
        post_type = int(data('post_type'))

        post = Post(
            title=title, content=content,
            author=request.user, type=post_type,
        )
        post.save()

        # Update formset with post instance
        formset = RelatedFormSet(request.POST, instance=post)

        # Save related formset for questions
        if post.type == 0 and formset:
            if formset.is_valid():
                formset.save()
            else:
                return render(request, self.template_name, {'form': form, 'formset': formset, 'helper': helper})

        # Triggers a new post save.
        tag_ids = request.POST.getlist('tags', [])
        post.add_tags_by_id(tag_ids)

        messages.success(request, _("%s created") % post.get_type_display())
        return HttpResponseRedirect(post.get_absolute_url())


class NewAnswer(LoginRequiredMixin, FormView):
    """
    Creates a new post.
    """
    form_class = ShortForm
    template_name = "post_edit.html"
    type_map = dict(answer=Post.ANSWER, comment=Post.COMMENT)
    post_type = None

    def get(self, request, *args, **kwargs):
        initial = {}

        # The parent id.
        pid = int(self.kwargs['pid'])
        # form_class = ShortForm if pid else LongForm
        form = self.form_class(initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        pid = int(self.kwargs['pid'])

        # Find the parent.
        try:
            parent = Post.objects.get(pk=pid)
        except ObjectDoesNotExist, exc:
            messages.error(request, _("The post does not exist. Perhaps it was deleted"))
            return HttpResponseRedirect("/")

        # Validating the form.
        form = self.form_class(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        # Valid forms start here.
        data = form.cleaned_data.get

        # Figure out the right type for this new post
        post_type = self.type_map.get(self.post_type)
        # Create a new post.
        post = Post(
            title=parent.title, content=data('content'), author=request.user, type=post_type,
            parent=parent,
        )

        messages.success(request, _("%s created") % post.get_type_display())
        post.save()

        return HttpResponseRedirect(post.get_absolute_url())


class EditPost(LoginRequiredMixin, FormView):
    """
    Edits an existing post.
    """

    # The template_name attribute must be specified in the calling apps.
    template_name = "post_edit.html"
    form_class = LongForm

    def get(self, request, *args, **kwargs):
        initial = {}

        pk = int(self.kwargs['pk'])
        post = Post.objects.get(pk=pk)
        post = auth.post_permissions(request=request, post=post)

        RelatedFormSet = inlineformset_factory(Post, RelatedPosts, RelatedForm, fk_name="post")
        formset = RelatedFormSet(instance=post)
        helper = RelatedFormSetHelper()

        # Check and exit if not a valid edit.
        if not post.is_editable:
            messages.error(request, _("This user may not modify the post"))
            return HttpResponseRedirect(reverse("home"))

        initial = dict(title=post.title, content=post.content, post_type=post.type, tag_val=post.tag_val)

        # Disable rich editing for preformatted posts
        pre = 'class="preformatted"' in post.content
        form_class = LongForm if post.is_toplevel else ShortForm
        form = form_class(initial=initial)
        return render(request, self.template_name, {'form': form, 'pre': pre, 'formset': formset, 'helper': helper, 'post': post})

    def post(self, request, *args, **kwargs):

        pk = int(self.kwargs['pk'])
        post = Post.objects.get(pk=pk)
        post = auth.post_permissions(request=request, post=post)

        # For historical reasons we had posts with iframes
        # these cannot be edited because the content would be lost in the front end
        # allow iframes from youtube and geogebra
        if "<iframe" in post.content and not ('tube.geogebra.org' in post.content or 'youtube.com' in post.content):
            messages.error(request, _("This post is not editable because of an iframe! Contact if you must edit it"))
            return HttpResponseRedirect(post.get_absolute_url())

        # Check and exit if not a valid edit.
        if not post.is_editable:
            messages.error(request, _("This user may not modify the post"))
            return HttpResponseRedirect(post.get_absolute_url())

        # Posts with a parent are not toplevel
        form_class = LongForm if post.is_toplevel else ShortForm

        form = form_class(request.POST)

        # Related formset
        RelatedFormSet = inlineformset_factory(Post, RelatedPosts, RelatedForm, fk_name="post")
        formset = RelatedFormSet(request.POST, instance=post)
        helper = RelatedFormSetHelper()

        if not form.is_valid():
            # Invalid form submission.
            return render(request, self.template_name, {'form': form, 'formset': formset, 'helper': helper})

        # Valid forms start here.
        data = form.cleaned_data

        # Set the form attributes.
        for field in form_class.FIELDS:
            setattr(post, field, data[field])

        # TODO: fix this oversight!
        post.type = int(data.get('post_type', post.type))

        # This is needed to validate some fields.
        post.save()

        # Save related formset for questions
        if post.type == 0 and formset:
            if formset.is_valid():
                formset.save()
            else:
                return render(request, self.template_name, {'form': form, 'formset': formset, 'helper': helper})
        else:
            # Remove related post if switch post type
            for related_post in RelatedPosts.objects.filter(post=post):
                related_post.delete()

        if post.is_toplevel:
            tag_ids = request.POST.getlist('tags', [])
            post.add_tags_by_id(tag_ids)


        # Update the last editing user.
        post.lastedit_user = request.user
        post.lastedit_date = datetime.utcnow().replace(tzinfo=utc)
        post.save()
        messages.success(request, _("Post updated"))

        return HttpResponseRedirect(post.get_absolute_url())

    def get_success_url(self):
        return reverse("user_details", kwargs=dict(pk=self.kwargs['pk']))



def tag_list(request, pk=None):
    """
    Ajax view which return list of tags in fancytree json format
    :param pk: -  add 'selected' attr to this post tags if passed
    """
    post_tags = []
    if pk:
        post = Post.objects.get(pk=pk)
        post_tags = [tag for tag in post.tag_set.all()]

    def recursive_node_to_dict(node):

        def is_active(a):
            """
            Return true if any child of node is selected .
            """
            for x in a:
                if 'selected' in x:
                    return True
                if 'children' in x:
                    return is_active(x['children'])
            return False


        result = {
            'key': node.pk,
            'title': node.name,
        }
        if node in post_tags:
            result['selected'] = True


        children = [recursive_node_to_dict(c) for c in node.get_children()]
        if children:
            result['children'] = children
            # TODO: remove double recursion
            if is_active(result['children']):
                result['expanded'] = True

        # Add tags link to json object
        if request.GET.get('href', False):
            result['href'] = node.get_absolute_url()

        return result

    root_nodes = cache_tree_children(Tag.objects.all())
    dicts = []
    for n in root_nodes:
        dicts.append(recursive_node_to_dict(n))
    return json_response(dicts)
