import json

from django.http import JsonResponse
from django.shortcuts import render

from recon_note.models import TodoNote
from dashboard.utils import user_has_project_access

@user_has_project_access
def list_note(request, slug):
    context = {}
    context['recon_note_active'] = 'active'
    return render(request, 'note/index.html', context)

def flip_todo_status(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        note = TodoNote.objects.get(id=body['id'])
        note.is_done = not note.is_done
        note.save()

    return JsonResponse({'status': True})

def flip_important_status(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        note = TodoNote.objects.get(id=body['id'])
        note.is_important = not note.is_important
        note.save()

    return JsonResponse({'status': True})

def delete_note(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        TodoNote.objects.filter(id=body['id']).delete()

    return JsonResponse({'status': True})