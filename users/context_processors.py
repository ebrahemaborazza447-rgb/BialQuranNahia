from users.models import ContactMessage

def unread_messages_count(request):
    if request.user.is_authenticated:
        count = ContactMessage.objects.filter(
            user=request.user,
            is_read=False
        ).count()
    else:
        count = 0
    return {'unread_messages_count': count}
