from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views import generic

from .models import Post, Vote


class IndexView(generic.ListView):
    context_object_name = 'posts'
    model = Post
    paginate_by = 50
    template_name = 'blog/index.html'
    available_orderings = {
        'created': 'Creation time',
        'rating': 'Rating',
    }

    def get_ordering(self):
        ordering = self.request.GET.get('ordering')
        if ordering is None or ordering.strip('-') not in self.available_orderings:
            ordering = '-created'
        return ordering

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('author')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['ordering_with_direction'] = self.get_ordering()
        context['ordering'] = context['ordering_with_direction'].strip('-')
        context['available_orderings'] = self.available_orderings
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
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'code': 404, 'msg': 'Post {} does not exist'.format(post_id)}, status=404)

    try:
        vote = Vote.objects.get(post=post, author=request.user)
    except Vote.DoesNotExist:
        vote_direction = None
    else:
        vote_direction = vote.up
        post = vote.post  # The same post but with updated ratings after vote removal
        vote.delete()

    if vote_direction is not bool(direction):

        vote = Vote()
        vote.post = post
        vote.author = request.user
        vote.up = bool(direction)
        vote.save()
        data = {
            'vote': vote.up,
        }
    else:
        data = {
            'vote': None,
        }

    data['upvotes'] = post.upvotes
    data['downvotes'] = post.downvotes

    return JsonResponse(data)
