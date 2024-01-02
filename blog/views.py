from urllib.parse import quote_plus
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View, ListView, DetailView
from .models import Post, PostImage, Comment, Subscriber, Image
from django.core.mail import send_mail, get_connection
from .forms import EmailPostForm, CommentForm, ContactForm, SubscriberForm
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.urls import reverse
from . import forms

# Create your views here.
def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 20)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post_list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag}) 

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 20
    template_name = 'blog/post_list.html'

def PostLike(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(requuest.user)

    return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))



def post_detail(request, year, month, day, post):
    template_name: 'post_detail.html'
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    photos = PostImage.objects.filter(post=post)
    share_string = quote_plus(post.body)
    share_string = quote_plus('')
    
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
           
            # normal comment
            # create comment object but do not save to database
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            
            
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:6]

    return render(request, 'blog/post_detail.html',{'post': post,'photos': photos,'comments': comments,'new_comment': new_comment,'comment_form': comment_form,'similar_posts': similar_posts,'share_string': share_string})

# handling reply, reply view
def reply_page(request):
    if request.method == "POST":

        form = CommentForm(request.POST)

        if form.is_valid():
            post_id = request.POST.get('post_id')  # from hidden input
            parent_id = request.POST.get('parent')  # from hidden input
            post_url = request.POST.get('post_url')  # from hidden input

            reply = form.save(commit=False)
    
            reply.post = Post(id=post_id)
            reply.parent = Comment(id=parent_id)
            reply.save()

            return redirect(post_url+'#'+str(reply.id))

    return redirect("/")



class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        likes_connected = get_object_or_404(Post, id=self.kwargs['pk'])
        liked = False
        if likes_connected.likes.filter(id=self.request.user.id).exists():
            liked = True
        data['number_of_likes'] = likes_connected.number_of_likes()
        data['post_is_liked'] = liked
        return data
    

def post_search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        posts = Post.objects.filter(title__contains=searched)


        return render(request, 'blog/post_search.html',{'searched':searched,
                                                        'posts':posts})

    else:
        return render(request, 'blog/post_search.html',{})

def home(request, tag_slug=None):
    object_list = Post.published.all( )
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 15)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post_list.html', {'page': page,
                                                   'posts': posts,
                                                   'tag': tag})

def about(request):
    return render(request, 'blog/About.html')


def contact(request):
    
    if request.method == 'POST':
        form =  ContactForm(request.POST)
        
        if form.is_valid():
            sender_name = form.cleaned_data['name']
            sender_email = form.cleaned_data['email']
            message = "{0} has sent you a new message:\n\n{1}".format(sender_name, form.cleaned_data ['message'])
            send_mail('New Enquiry', message, sender_email, ['akinpeluoluwadamilare79@gmail.com'])
            html = 'Thanks for contacting us!'
        else:
            html = 'Form is not valid. Check your input.'
    else:
        form = ContactForm() 
        html = 'Fill up the forms'
          
    return render(request, 'blog/Contact.html', {'form': form, 'html': html})


def random_digits():
    return "%0.12d" % random.randint(0, 999999999999)

@csrf_exempt
def self(request):
    pics=Image.objects.all()


    if request.method == 'POST':
        sub = Subscriber(email=request.POST['email'], conf_num=random_digits())
        sub.save()
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=sub.email,
            subject='Newsletter Confirmation',
            html_content='Thank you for signing up for my email newsletter! \
                Please complete the process by \
                <a href="{}/confirm/?email={}&conf_num={}"> clicking here to \
                confirm your registration</a>.'.format(request.build_absolute_uri('/confirm/'),
                                                    sub.email,
                                                    sub.conf_num))
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'added', 'form': SubscriberForm()})
    else:
        return render(request, 'blog/self.html', {
                                                  'form': SubscriberForm(),
                                                  'pics':pics })
    
def confirm(request):
    sub = Subscriber.objects.get(email=request.GET['email'])
    if sub.conf_num == request.GET['conf_num']:
        sub.confirmed = True
        sub.save()
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'confirmed'})
    else:
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'denied'})

def delete(request):
    sub = Subscriber.objects.get(email=request.GET['email'])
    if sub.conf_num == request.GET['conf_num']:
        sub.delete()
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'unsubscribed'})
    else:
        return render(request, 'blog/self.html', {'email': sub.email, 'action': 'denied'})


