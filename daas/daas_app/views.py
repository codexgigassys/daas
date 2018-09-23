from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from .decompilers.utils import RelationRepository


# --------------- #
# --- UPLOADS --- #
# --------------- #
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            RelationRepository().submit_sample(request.FILES['file'])
            return HttpResponseRedirect(reverse('index'))
    else:  # GET
        form = UploadFileForm()
    return render(request, 'daas_app/upload.html', {'form': form})
