from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView


from bootcamp.messager.models import Message
from bootcamp.helpers import ajax_required


class MessagesListView(LoginRequiredMixin, ListView):
    """CBV to render the inbox, showing by default the most recent
    conversation as the active one.
    """

    model = Message
    paginate_by = 50
    template_name = "messager/message_list.html"

    def _annotate_grouping(self, messages):
        """Pre-compute grouping flags for each message so the template can
        render grouped bubbles, avatars, and timestamps correctly."""
        msgs = list(messages)
        annotated = []
        for i, msg in enumerate(msgs):
            prev_sender = msgs[i - 1].sender_id if i > 0 else None
            next_sender = msgs[i + 1].sender_id if i < len(msgs) - 1 else None
            same_as_prev = msg.sender_id == prev_sender
            same_as_next = msg.sender_id == next_sender
            msg.is_first_in_group = not same_as_prev
            msg.is_last_in_group = not same_as_next
            msg.show_avatar = msg.is_last_in_group
            annotated.append(msg)
        return annotated

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        contact_list = self.request.user.contact_list.all().order_by("username")
        unread_conversations = []
        for user in contact_list:
            unread_conversations.append(len(self.request.user.received_messages.unread(user)))
        context["users_dict"] = dict(zip(contact_list, unread_conversations))

        last_conversation = Message.objects.get_most_recent_conversation(
            self.request.user
        )
        context["active"] = last_conversation.username
        # Annotated messages with grouping info
        context["grouped_messages"] = self._annotate_grouping(context["object_list"])
        return context

    def get_queryset(self):
        active_user = Message.objects.get_most_recent_conversation(self.request.user)
        Message.objects.mark_conversation_as_read(active_user, self.request.user)
        return Message.objects.get_conversation(active_user, self.request.user)


class ConversationListView(MessagesListView):
    """CBV to render the inbox, showing an specific conversation with a given
    user, who requires to be active too."""

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["active"] = self.kwargs["username"]
        return context

    def get_queryset(self):
        # todo: avoid this query overriding the 'unread-messages' call
        #if(self.kwargs["username"]!="unread-messages"):
        active_user = get_user_model().objects.get(username=self.kwargs["username"])
        Message.objects.mark_conversation_as_read(active_user, self.request.user)
        return Message.objects.get_conversation(active_user, self.request.user)


@login_required
@ajax_required
@require_http_methods(["POST"])
def send_message(request):
    """AJAX Functional view to recieve just the minimum information, process
    and create the new message and return the new data to be attached to the
    conversation stream."""
    sender = request.user
    recipient_username = request.POST.get("to")
    recipient = get_user_model().objects.get(username=recipient_username)
    message = request.POST.get("message", "")
    image = request.FILES.get("image")
    if len(message.strip()) == 0 and not image:
        return HttpResponse()

    if sender != recipient:
        msg = Message.send_message(sender, recipient, message, image=image)
        return render(request, "messager/single_message.html", {
            "message": msg,
            "current_user": request.user,
            "show_avatar": True,
            "is_first_in_group": True,
            "is_last_in_group": True,
        })

    return HttpResponse()


@login_required
@ajax_required
@require_http_methods(["GET"])
def receive_message(request):
    """Simple AJAX functional view to return a rendered single message on the
    receiver side providing realtime connections."""
    message_id = request.GET.get("message_id")
    try:
        message = Message.objects.get(pk=message_id)
    except Message.DoesNotExist as e:
        raise e

    return render(request, "messager/single_message.html", {
        "message": message,
        "current_user": request.user,
        "show_avatar": True,
        "is_first_in_group": True,
        "is_last_in_group": True,
    })


@login_required
def get_unread_messages(request):
    sender_str = request.GET.get('sender')
    sender = None
    if sender_str:
        sender = get_user_model().objects.get(username=sender_str)
    messages = request.user.received_messages.unread(sender)
    return JsonResponse({"unread_messages": str(len(messages))})


@login_required
def mark_read_messages(request):
    sender_str = request.GET.get("sender")
    sender = get_user_model().objects.get(username=sender_str)
    Message.objects.mark_conversation_as_read(sender, request.user)
    return JsonResponse({"mark_messages_state": "success"})


@login_required
@ajax_required
@require_http_methods(["POST"])
def delete_message(request, message_id):
    try:
        message = Message.objects.get(pk=message_id)
        if message.sender == request.user:
            message.delete()
            return JsonResponse({"status": "deleted"})
        return JsonResponse({"status": "unauthorized"}, status=403)
    except Message.DoesNotExist:
        return JsonResponse({"status": "not_found"}, status=404)


@login_required
@ajax_required
@require_http_methods(["POST"])
def react_message(request, message_id):
    try:
        reaction = request.POST.get("reaction")
        message = Message.objects.get(pk=message_id)
        # Anyone in the conversation can react
        if request.user in [message.sender, message.recipient]:
            # Toggle off if the reaction is already set to the same emoji
            if message.reaction == reaction:
                message.reaction = ""
            else:
                message.reaction = reaction
            message.save()
            return JsonResponse({"status": "reacted", "reaction": message.reaction})
        return JsonResponse({"status": "unauthorized"}, status=403)
    except Message.DoesNotExist:
        return JsonResponse({"status": "not_found"}, status=404)


@login_required
@ajax_required
@require_http_methods(["POST"])
def mute_conversation(request, username):
    try:
        target_user = get_user_model().objects.get(username=username)
        if target_user in request.user.muted_users.all():
            request.user.muted_users.remove(target_user)
            muted = False
        else:
            request.user.muted_users.add(target_user)
            muted = True
        return JsonResponse({"status": "success", "muted": muted})
    except get_user_model().DoesNotExist:
        return JsonResponse({"status": "not_found"}, status=404)


@login_required
@ajax_required
@require_http_methods(["POST"])
def delete_conversation(request, username):
    try:
        target_user = get_user_model().objects.get(username=username)
        # Two deletes to avoid TypeError on union() queryset
        Message.objects.filter(sender=request.user, recipient=target_user).delete()
        Message.objects.filter(sender=target_user, recipient=request.user).delete()
        return JsonResponse({"status": "success"})
    except get_user_model().DoesNotExist:
        return JsonResponse({"status": "not_found"}, status=404)
