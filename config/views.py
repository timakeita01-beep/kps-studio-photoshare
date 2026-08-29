from django.shortcuts import redirect, render


def home(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect('accounts:admin_dashboard')
        return redirect('events:dashboard')
    return render(request, 'home.html')
