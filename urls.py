from django.conf.urls.defaults import *

urlpatterns = patterns('views',
    # Example:
    # (r'^kochliste/', include('kochliste.foo.urls')),
    (r'^$', 'index'),
    (r'^(\d{4})/(\d{2})/$', 'index'),
    (r'^plan/$', 'plan'),
    (r'^plan/(\d{4})/(\d{2})/$', 'plan'),
    (r'^kinder/(all/?)?$', 'list_children'),
    (r'^kinder(?:/all)?/create/$', 'create_child'),
    (r'^kinder(?:/all)?/edit/$', 'edit_child'),
    (r'^kinder(?:/all)?/setvisible/$', 'set_visible_child'),
    (r'^kinder(?:/all)?/delete/$', 'delete_child'),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
