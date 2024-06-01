import time
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User


@method_decorator(csrf_exempt, name='dispatch')
class SyncUserView(View):

    def post(self, request, *args, **kwargs):
        try:
            # Get current time in nanoseconds
            timestamp_ns = time.time_ns()
            unique_id = str(uuid.uuid4())
            username = f"user_{timestamp_ns}_{unique_id}"
            email = f"{username}@example.com"
            
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=get_random_string(8)
            )
            
            return JsonResponse({'id': user.id}, status=201) # type: ignore

        except Exception as err:
            return JsonResponse({'error': f'{err}'}, status=400)

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('id')

        if not user_id:
            return JsonResponse({'error': 'user id not found in query param'}, status=400)

        try:
            user = User.objects.get(pk=user_id)
            return JsonResponse({
                'id': user.id, # type: ignore
                'username': user.username,
                'email': user.email
            })
        except User.DoesNotExist as err:
            return JsonResponse({'error': f'User not found {err}'}, status=404)
        except Exception as err:
            return JsonResponse({'error': f'Unable to retrieve user {err}'}, status=404)
