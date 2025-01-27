from django.shortcuts import redirect

class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.session.get_expiry_age() > 0:
                # Session expired; redirect to login
                return redirect('/')
        return self.get_response(request)

