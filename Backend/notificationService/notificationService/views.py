from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk=None):
        if pk:
            # Mark a specific notification as read
            try:
                notification = Notification.objects.get(pk=pk, recipient=request.user)
                notification.is_read = True
                notification.save()
                return Response({"status": "marked as read"})
            except Notification.DoesNotExist:
                return Response({"error": "Notification not found"}, status=404)
        else:
            # Mark all notifications as read
            Notification.objects.filter(recipient=request.user).update(is_read=True)
            return Response({"status": "all marked as read"})