from django.urls import path
from .views import TextFixerView
urlpatterns = [ path("fix/", TextFixerView.as_view(), name="textfixer-fix") ]
