from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from .models import SiteUser, Note
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        u_pass = request.POST.get('password')
        
        # Foydalanuvchi allaqachon mavjudligini tekshiramiz
        if SiteUser.objects.filter(username=u_name).exists():
            return render(request, 'notes/register.html', {'error': "Bu foydalanuvchi nomi band!"})
        
        # Yangi foydalanuvchi yaratamiz
        new_user = SiteUser.objects.create(username=u_name, password=u_pass)
        request.session['user_id'] = new_user.id
        request.session['username'] = new_user.username
        return redirect('dashboard')
        
    return render(request, 'notes/register.html')

def login_view(request):
    error = None
    # Faqat dinamik session rejimidan foydalanamiz
    security_mode = request.session.get('security_mode', False)
    status = "SECURE" if security_mode else "VULNERABLE"
    
    if request.method == "POST":
        u_name = request.POST.get('username')
        u_pass = request.POST.get('password')

        if not security_mode:
            # SQL INJECTION ZAIFLIGI (Raw Query)
            query = f"SELECT * FROM notes_siteuser WHERE username = '{u_name}' AND password = '{u_pass}'"
            with connection.cursor() as cursor:
                cursor.execute(query)
                user = cursor.fetchone()
                if user:
                    request.session['user_id'] = user[0]
                    request.session['username'] = user[1]
                    return redirect('dashboard')
        else:
            # SQL INJECTION HIMOYASI (ORM)
            user = SiteUser.objects.filter(username=u_name, password=u_pass).first()
            if user:
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                return redirect('dashboard')
        
        error = "Login yoki parol xato!"

    return render(request, 'notes/login.html', {
        'error': error, 
        'status': status, 
        'security_mode': security_mode
    })

def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id: 
        return redirect('login')
    
    security_mode = request.session.get('security_mode', False)
    
    if not security_mode:
        # BROKEN ACCESS CONTROL ZAIFLIGI: Hamma hamma narsani ko'radi
        notes = Note.objects.all().order_by('-created_at')
    else:
        # BROKEN ACCESS CONTROL HIMOYASI: Faqat o'ziga tegishli eslatmalar
        notes = Note.objects.filter(user_id=user_id).order_by('-created_at')

    return render(request, 'notes/dashboard.html', {
        'notes': notes,
        'username': request.session.get('username'),
        'security_mode': security_mode,
        'notes_count': notes.count() # Dashboarddagi statistika uchun
    })

def security_test_page(request):
    if not request.session.get('user_id'): return redirect('login')
    security_mode = request.session.get('security_mode', False)
    return render(request, 'notes/security_test.html', {'security_mode': security_mode})

def toggle_security(request):
    # Bu funksiya ham GET ham POST bo'lib ishlayveradi
    current_status = request.session.get('security_mode', False)
    request.session['security_mode'] = not current_status
    return redirect('security_test_page')

def delete_note(request, note_id):
    user_id = request.session.get('user_id')
    if not user_id: return redirect('login')

    security_mode = request.session.get('security_mode', False)

    if not security_mode:
        # ZAIFLIK: Istalgan ID dagi eslatmani o'chira oladi
        note = get_object_or_404(Note, id=note_id)
    else:
        # HIMOYA: Faqat o'ziga tegishli bo'lsagina o'chiradi
        note = get_object_or_404(Note, id=note_id, user_id=user_id)
    
    note.delete()
    return redirect('dashboard')

def add_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Note.objects.create(
            title=title, 
            content=content, 
            user_id=request.session.get('user_id')
        )
    return redirect('dashboard')