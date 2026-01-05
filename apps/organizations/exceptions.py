import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that logs all exceptions and returns proper error responses.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    # If DRF couldn't handle the exception, log it and return a 500 response
    if response is None:
        # Log the exception with full traceback
        logger.error(
            f"Unhandled exception in {context['view'].__class__.__name__}: {str(exc)}",
            exc_info=True,
            extra={
                'request': context.get('request'),
                'view': context.get('view'),
            }
        )
        
        # Return a generic 500 error response
        return Response(
            {
                'error': 'Internal server error',
                'detail': 'An unexpected error occurred. Please try again later.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Log the exception even if DRF handled it
    logger.warning(
        f"Exception in {context['view'].__class__.__name__}: {str(exc)}",
        exc_info=True,
        extra={
            'request': context.get('request'),
            'view': context.get('view'),
        }
    )
    
    return response


def log_view_errors(view_name):
    """
    Decorator to log view errors for function-based views.
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                return func(request, *args, **kwargs)
            except Http404:
                # Don't log 404 errors as they're normal
                raise
            except Exception as e:
                logger.error(
                    f"Error in {view_name}: {str(e)}",
                    exc_info=True,
                    extra={'request': request}
                )
                return Response(
                    {'error': 'Internal server error'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return wrapper
    return decorator
