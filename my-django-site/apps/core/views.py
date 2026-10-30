from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

class HomeView(TemplateView):
    template_name = "core/home.html"
class TextResponseView(View):
    def get(self, request):
        return HttpResponse("這是一段由 HttpResponse 回傳的文字。")

class JsonResponseView(View):
    def get(self, request):
        return JsonResponse(
            {
                "message": "這是一份由 JsonResponse 回傳的資料。",
                "course": "Python 全端開發",
            },
            status=200,
        )


from django.shortcuts import redirect

class GoHomeView(View):
    def get(self, request):
        return redirect("core:home")

class GreetingView(View):
    def get(self, request):
        name = request.GET.get("name", "訪客")
        context = {"name": name}
        return render(request, "core/greeting.html", context)
