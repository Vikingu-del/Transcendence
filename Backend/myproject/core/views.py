from django.http import JsonResponse

def secret_view(request):
    return JsonResponse({"message": "This is a secret view!"})
