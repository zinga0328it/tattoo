from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Tattoo

def gallery_list(request):
    """Lista di tutti i tatuaggi"""
    tattoos = Tattoo.objects.all().order_by('-uploaded_at')
    context = {
        'tattoos': tattoos,
        'total_count': tattoos.count()
    }
    return render(request, 'gallery/list.html', context)

def tattoo_detail(request, pk):
    """Dettaglio singolo tatuaggio con SEO e link Telegram"""
    tattoo = get_object_or_404(Tattoo, pk=pk)
    
    # Tatuaggi correlati (stesso utente)
    related_tattoos = Tattoo.objects.filter(username=tattoo.username).exclude(pk=pk)[:3]
    
    context = {
        'tattoo': tattoo,
        'related_tattoos': related_tattoos,
        'seo_title': tattoo.seo_title,
        'seo_description': tattoo.seo_description,
        'keywords': tattoo.keywords
    }
    return render(request, 'gallery/detail.html', context)

def api_tattoo_detail(request, pk):
    """API JSON per singolo tatuaggio"""
    tattoo = get_object_or_404(Tattoo, pk=pk)
    
    data = {
        'id': tattoo.id,
        'username': tattoo.username,
        'description': tattoo.description,
        'filename': tattoo.filename,
        'uploaded_at': tattoo.uploaded_at.isoformat(),
        'image_url': tattoo.image_url,
        'telegram_url': tattoo.telegram_url,
        'seo_title': tattoo.seo_title,
        'seo_description': tattoo.seo_description,
        'keywords': tattoo.keywords
    }
    
    return JsonResponse(data)

def api_artist_tattoos(request, username):
    """API JSON per tatuaggi di uno specifico artista"""
    tattoos = Tattoo.objects.filter(username=username).order_by('-uploaded_at')
    data = []
    
    for tattoo in tattoos:
        if tattoo.file_exists:
            data.append({
                'id': tattoo.id,
                'username': tattoo.username,
                'description': tattoo.description,
                'filename': tattoo.filename,
                'uploaded_at': tattoo.uploaded_at.isoformat(),
                'image_url': tattoo.image_url,
                'telegram_url': tattoo.telegram_url
            })
    
    return JsonResponse(data, safe=False)

def api_tattoos(request):
    """API JSON per compatibilità"""
    tattoos = Tattoo.objects.all().order_by('-uploaded_at')
    data = []
    
    for tattoo in tattoos:
        if tattoo.file_exists:
            data.append({
                'id': tattoo.id,
                'username': tattoo.username,
                'description': tattoo.description,
                'filename': tattoo.filename,
                'uploaded_at': tattoo.uploaded_at.isoformat(),
                'image_url': tattoo.image_url,
                'detail_url': tattoo.get_absolute_url(),
                'telegram_url': tattoo.telegram_url,
                'seo_title': tattoo.seo_title,
                'seo_description': tattoo.seo_description,
                'keywords': tattoo.keywords
            })
    
    return JsonResponse(data, safe=False)
