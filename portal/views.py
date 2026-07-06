import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from rapidfuzz import process, fuzz
from .models import Item, Message, StudentProfile
from .forms import CampusRegistrationForm

def landing_view(request):
    """Renders the professional homepage. Redirects logged-in users to the dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def register_view(request):
    if request.method == 'POST':
        form = CampusRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CampusRegistrationForm()
    return render(request, 'register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    # Handle Profile Update from Modal
    if request.method == 'POST' and request.POST.get('action') == 'update_profile':
        try:
            year_of_study = int(request.POST.get('year_of_study', 1))
        except ValueError:
            year_of_study = 1
            
        # FIX: Use update_or_create to supply all required fields simultaneously
        # This prevents PostgreSQL from throwing a "NOT NULL" IntegrityError
        StudentProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'full_name': request.POST.get('full_name', ''),
                'contact_number': request.POST.get('contact_number', ''),
                'hostel': request.POST.get('hostel', ''),
                'branch': request.POST.get('branch', ''),
                'degree': request.POST.get('degree', ''),
                'year_of_study': year_of_study
            }
        )
        return redirect('dashboard')

    # Separate the items based on timestamps
    lost_items = Item.objects.filter(status='Open', item_type='Lost').order_by('-created_at')
    found_items = Item.objects.filter(status='Open', item_type='Found').order_by('-created_at')
    
    # Gracefully fetch profile (prevents crash if superuser logs in without a profile)
    profile = getattr(request.user, 'profile', None)
    
    return render(request, 'dashboard.html', {
        'lost_items': lost_items, 
        'found_items': found_items, 
        'profile': profile
    })

@login_required
def report_item_view(request, item_type):
    # item_type will be passed from the URL as either 'lost' or 'found'
    log_type = item_type.capitalize() 
    
    if request.method == 'POST':
        Item.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            category=request.POST.get('category'),
            location=request.POST.get('location'),
            item_type=log_type,
            image=request.FILES.get('image'),
            owner=request.user
        )
        return redirect('dashboard')
    
    return render(request, 'report.html', {'log_type': log_type})

@login_required
def search_matches_api(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({'matches': []})

    items = Item.objects.filter(status='Open')
    choices = {item.id: f"{item.title} {item.description}" for item in items}
    
    # FIX: WRatio is much more robust for partial string matching combined with token sorting
    results = process.extract(query, choices, scorer=fuzz.WRatio, limit=5)
    
    matches_data = []
    # RapidFuzz extract with dict returns: (match_string, score, key)
    for match in results:
        score = match[1]
        item_id = match[2]
        
        if score >= 50:  # Forgiving threshold for partial typos
            item = Item.objects.get(id=item_id)
            matches_data.append({
                'id': item.id,
                'title': item.title,
                'type': item.item_type,
                'score': round(score, 1),
                'image_url': item.image.url if item.image else None
            })
            
    return JsonResponse({'matches': matches_data})

@login_required
def get_inquiries_api(request, item_id):
    """Fetches a list of users who have messaged the owner about this item."""
    item = get_object_or_404(Item, id=item_id)
    if request.user != item.owner:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    messages = Message.objects.filter(item=item).exclude(sender=item.owner)
    inquirers = {}
    for m in messages:
        if m.sender.id not in inquirers:
            inquirers[m.sender.id] = {
                'id': m.sender.id,
                'username': m.sender.username,
                'last_message': m.content,
                'time': m.timestamp.strftime('%b %d %H:%M')
            }
        else:
            inquirers[m.sender.id]['last_message'] = m.content
            inquirers[m.sender.id]['time'] = m.timestamp.strftime('%b %d %H:%M')
            
    return JsonResponse({'inquirers': list(inquirers.values())})

@login_required
def get_messages_api(request, item_id, other_user_id=None):
    """Fetches a private 1-on-1 message thread between the owner and a specific user."""
    item = get_object_or_404(Item, id=item_id)
    
    # Determine the target user ID to filter messages for the 1-on-1 tunnel
    if request.user == item.owner:
        if not other_user_id:
            return JsonResponse({'messages': []}) # Owner must specify who they are talking to
        target_user_id = other_user_id
    else:
        target_user_id = request.user.id
        
    messages = Message.objects.filter(item=item).filter(
        Q(sender_id=target_user_id, receiver=item.owner) |
        Q(sender=item.owner, receiver_id=target_user_id)
    ).order_by('timestamp')
    
    msg_list = [{'sender': m.sender.username, 'content': m.content, 'time': m.timestamp.strftime('%H:%M')} for m in messages]
    return JsonResponse({'messages': msg_list})

@login_required
def send_message_api(request, item_id, other_user_id=None):
    """Sends a message within the secure 1-on-1 tunnel."""
    if request.method == 'POST':
        item = get_object_or_404(Item, id=item_id)
        data = json.loads(request.body)
        content = data.get('content')
        
        # Route the message to the correct receiver
        if request.user == item.owner:
            receiver_id = other_user_id
        else:
            receiver_id = item.owner.id
            
        Message.objects.create(sender=request.user, receiver_id=receiver_id, item=item, content=content)
        return JsonResponse({'status': 'success'})
        
    return JsonResponse({'error': 'Invalid method'}, status=400)