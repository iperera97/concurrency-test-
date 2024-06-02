import time
import uuid
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User

logger = logging.getLogger('django')

@method_decorator(csrf_exempt, name='dispatch')
class SyncUserView(View):

    def post(self, request, *args, **kwargs):
        start_time = time.time()
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
            
            response = JsonResponse({'id': user.id}, status=201)
            logger.info(f"User created with ID: {user.id}")
        except Exception as err:
            response = JsonResponse({'error': f'{err}'}, status=400)
            logger.error(f"Error creating user: {err}")

        execution_time = time.time() - start_time
        logger.info(f"POST /sync-user execution time: {execution_time:.4f} seconds")
        return response

    def get(self, request, *args, **kwargs):
        start_time = time.time()
        user_id = request.GET.get('id')

        if not user_id:
            logger.warning("User ID not found in query param")
            return JsonResponse({'error': 'user id not found in query param'}, status=400)

        try:
            user = User.objects.get(pk=user_id)
            response = JsonResponse({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
            logger.info(f"User retrieved with ID: {user.id}")
        except User.DoesNotExist as err:
            response = JsonResponse({'error': f'User not found {err}'}, status=404)
            logger.error(f"User not found: {err}")
        except Exception as err:
            response = JsonResponse({'error': f'Unable to retrieve user {err}'}, status=404)
            logger.error(f"Unable to retrieve user: {err}")

        execution_time = time.time() - start_time
        logger.debug(f"GET /sync-user execution time: {execution_time:.4f} seconds")
        return response
