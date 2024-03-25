from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, viewsets
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class NotificationViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user.userprofile)
        return queryset
