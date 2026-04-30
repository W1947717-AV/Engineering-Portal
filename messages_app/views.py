# Author: Gopishan Murukadasan
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Message


def get_user_display_name(user):
    """
    Returns a user's full name if available, otherwise their username.
    Used in templates to display sender/recipient names consistently.
    """
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name if full_name else user.username


@login_required(login_url='/login/')
def new_message(request):
    """
    Handles composing and sending a new message.

    GET: Renders the new message form with a list of all other users.
    POST: Creates a Message object. If action='draft', saves as draft
          and redirects to drafts. Otherwise sends and redirects to sent.
    """
    users = User.objects.exclude(id=request.user.id).order_by('first_name', 'last_name', 'username')

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        action = request.POST.get('action')  # 'send' or 'draft'

        recipient = get_object_or_404(User, id=recipient_id)

        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            body=body,
            is_draft=(action == 'draft')  # True if saving as draft
        )

        if action == 'draft':
            return redirect('/messages/drafts/')

        return redirect('/messages/sent/')

    return render(request, 'messages_app/new_message.html', {
        'users': users,
    })


@login_required(login_url='/login/')
def inbox(request):
    """
    Displays the current user's inbox (received, non-draft messages).

    Supports free-text search across subject, body, and sender name.
    Results can be sorted by newest (default) or oldest first.
    """
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'newest')

    # Only show received messages that are not drafts
    messages = Message.objects.filter(
        recipient=request.user,
        is_draft=False
    ).select_related('sender', 'recipient')

    if query:
        messages = messages.filter(
            Q(subject__icontains=query) |
            Q(body__icontains=query) |
            Q(sender__first_name__icontains=query) |
            Q(sender__last_name__icontains=query) |
            Q(sender__username__icontains=query)
        )

    # Apply sort order
    if sort == 'oldest':
        messages = messages.order_by('created_at')
    else:
        messages = messages.order_by('-created_at')

    return render(request, 'messages_app/inbox.html', {
        'messages': messages,
        'query': query,
        'sort': sort,
    })


@login_required(login_url='/login/')
def sent_messages(request):
    """
    Displays messages sent by the current user (excluding drafts).

    Supports search by subject, body, or recipient name.
    Sorted by newest first by default.
    """
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'newest')

    messages = Message.objects.filter(
        sender=request.user,
        is_draft=False
    ).select_related('sender', 'recipient')

    if query:
        messages = messages.filter(
            Q(subject__icontains=query) |
            Q(body__icontains=query) |
            Q(recipient__first_name__icontains=query) |
            Q(recipient__last_name__icontains=query) |
            Q(recipient__username__icontains=query)
        )

    if sort == 'oldest':
        messages = messages.order_by('created_at')
    else:
        messages = messages.order_by('-created_at')

    return render(request, 'messages_app/sent.html', {
        'messages': messages,
        'query': query,
        'sort': sort,
    })


@login_required(login_url='/login/')
def drafts(request):
    """
    Displays draft messages saved by the current user.

    Drafts are messages where is_draft=True and the sender
    is the current user. Ordered by most recently created first.
    """
    messages = Message.objects.filter(
        sender=request.user,
        is_draft=True
    ).select_related('sender', 'recipient').order_by('-created_at')

    return render(request, 'messages_app/drafts.html', {
        'messages': messages,
    })


@login_required(login_url='/login/')
def view_message(request, id):
    """
    Displays a single message.

    Only the sender or recipient may view a message — anyone else
    is redirected to the inbox. When the recipient views an unread
    message, it is automatically marked as read.
    """
    message = get_object_or_404(Message, id=id)

    # Restrict access to sender and recipient only
    if message.recipient != request.user and message.sender != request.user:
        return redirect('/messages/')

    # Mark as read when recipient opens it
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()

    return render(request, 'messages_app/view_message.html', {
        'message': message,
        'get_user_display_name': get_user_display_name,
    })