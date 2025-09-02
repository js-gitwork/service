from django.shortcuts import render, redirect, get_object_or_404
from .models import Asset
from .forms import AssetForm

def asset_list(request):
    assets = Asset.objects.all()
    return render(request, 'assets/assets_list.html', {'assets': assets})  # ← Ret til 'assets_list.html'

def edit_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        form = AssetForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
    else:
        form = AssetForm(instance=asset)
    return render(request, 'assets/edit_asset.html', {'form': form, 'asset': asset})

def asset_list(request):
    assets = Asset.objects.all()
    focus_id = request.GET.get('focus', None)
    return render(request, 'assets/assets_list.html', {'assets': assets, 'focus_id': focus_id})

