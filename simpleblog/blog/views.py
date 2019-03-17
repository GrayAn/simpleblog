from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views import generic

from .models import Post, Vote


class IndexView(generic.ListView):
    context_object_name = 'posts'
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    ordering = '-created'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('vote_set')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        if self.request.user.is_authenticated:
            votes = Vote.objects.filter(author=self.request.user)
            context['votes'] = {vote.post_id: vote.up for vote in votes}
        else:
            context['votes'] = {}
        return context


class AuthorView(IndexView):
    template_name = 'blog/author.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.kwargs['author_id'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        try:
            author = User.objects.get(pk=self.kwargs['author_id'])
        except User.DoesNotExist:
            pass
        else:
            context['author'] = author
        return context


class CreateView(generic.CreateView):
    fields = ('title', 'text')
    model = Post
    template_name = 'blog/create.html'

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponse(status=401)
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdateView(generic.UpdateView):
    fields = ('title', 'text')
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def form_valid(self, form):
        if self.request.user != form.instance.author:
            return HttpResponseForbidden()
        return super().form_valid(form)


class DetailView(generic.DetailView):
    context_object_name = 'post'
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            votes = Vote.objects.filter(author=self.request.user, post_id=self.kwargs['post_id'])
            context['votes'] = {vote.post_id: vote.up for vote in votes}
        else:
            context['votes'] = {}
        return context


def cast_vote(request, post_id, direction):
    try:
        vote = Vote.objects.get(post_id=post_id, author=request.user)
    except Vote.DoesNotExist:
        vote = Vote()
        vote.post_id = post_id
        vote.author = request.user

    if vote.up is bool(direction):
        data = {
            'vote': None,
            'change': -1 if vote.up else 1,
        }
        vote.delete()
    else:
        data = {
            'vote': bool(direction),
            'change': 1 if direction else -1,
        }
        if vote.up is not None:
            data['change'] *= 2
        vote.up = bool(direction)
        vote.save()

    return JsonResponse(data)
