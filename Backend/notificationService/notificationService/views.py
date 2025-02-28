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

class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """Get count of unread notifications for the current user"""
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count})

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk=None):
        try:
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
                count = Notification.objects.filter(recipient=request.user).update(is_read=True)
                return Response({"status": f"all marked as read, count: {count}"})
                
        except Exception as e:
            # Handle any unexpected errors
            import traceback
            print(f"Error in NotificationMarkReadView: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": f"Server error: {str(e)}"}, 
                status=500
            )