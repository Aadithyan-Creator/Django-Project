from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Account


def account_list(request):
    accounts = Account.objects.filter(is_deleted=False)
    return render(request, 'accounts/index.html', {'accounts': accounts})



def account_create(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        mobile_number = request.POST.get('mobile_number')

        account = Account.objects.create(
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            email=email,
            mobile_number=mobile_number
        )
        return redirect('account_list')
    return render(request, 'accounts/account_form.html')



def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk, is_deleted=False)
    if request.method == "POST":
        account.first_name = request.POST.get('first_name')
        account.last_name = request.POST.get('last_name')
        account.gender = request.POST.get('gender')
        account.email = request.POST.get('email')
        account.mobile_number = request.POST.get('mobile_number')
        account.save()
        return redirect('account_list')
    return render(request, 'accounts/account_form.html', {'account': account})



def account_deactivate(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.deactivate()
    return redirect('account_list')



def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.delete_account()
    return redirect('account_list')



def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk, is_deleted=False)
    return render(request, 'accounts/account_detail.html', {'account': account})
