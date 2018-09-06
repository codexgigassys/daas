from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm


# --------------- #
# --- UPLOADS --- #
# --------------- #
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # process(request.FILES['file'])
            return HttpResponseRedirect(reverse('index'))
    else:  # GET
        form = UploadFileForm()
    return render(request, 'daas/upload.html', {'form': form})
