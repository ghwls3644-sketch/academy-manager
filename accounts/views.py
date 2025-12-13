from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import LoginForm, ProfileForm


class CustomLoginView(LoginView):
    """커스텀 로그인 뷰"""
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:index')
    
    def form_valid(self, form):
        messages.success(self.request, f'{form.get_user().username}님, 환영합니다!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """커스텀 로그아웃 뷰"""
    next_page = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, '로그아웃되었습니다.')
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_view(request):
    """프로필 조회 및 수정"""
    try:
        employee = request.user.employee
    except:
        employee = None
    
    if request.method == 'POST' and employee:
        form = ProfileForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 수정되었습니다.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=employee) if employee else None
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'employee': employee,
    })
