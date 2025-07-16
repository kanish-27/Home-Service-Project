from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError

def handler404(request, exception):
    """Custom 404 error handler"""
    context = {
        'error_code': '404',
        'error_title': 'Page Not Found',
        'error_message': 'The page you are looking for does not exist.',
        'back_url': '/',
        'back_text': 'Go to Home'
    }
    return HttpResponseNotFound(render(request, 'errors/error.html', context))

def handler500(request):
    """Custom 500 error handler"""
    context = {
        'error_code': '500',
        'error_title': 'Server Error',
        'error_message': 'Something went wrong on our end. Please try again later.',
        'back_url': '/',
        'back_text': 'Go to Home'
    }
    return HttpResponseServerError(render(request, 'errors/error.html', context))
