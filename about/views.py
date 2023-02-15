from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_text'] = ('''
            Привет, я автор этого сайта и я сделал его на python.
            Тут я размещу информацию о себе, используя свои умения верстать.
        ''')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_text'] = ('''
            Вот какие технологии python и django я изучил,
            чтобы создать этот сайт.
        ''')
        return context
