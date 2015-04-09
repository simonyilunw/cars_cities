from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from views import Home, Stats, Samples, AggregateStats, Hotspots, Results, \
    Heatmap, Coverage, CountryHeatmap, CustomZip, Voting

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(pattern_name='home')),
    url(r'^home$', Home.as_view(), name='home'),
    url(r'^aggregate$', AggregateStats.as_view(), name='aggregate'),
    url(r'^stats$', Stats.as_view(), name='stats'),
    url(r'^coverage$', Coverage.as_view(), name='coverage'),
    url(r'^results$', Results.as_view(), name='results'),
    url(r'^results/zipcode/correlations$', TemplateView.as_view(template_name='correlations.html'), name='correlations'),
    url(r'^samples/(?P<cityid>[\d]+)$', Samples.as_view(), name='samples'),
    url(r'^hotspots/(?P<cityid>[\d]+)$', Hotspots.as_view(), name='hotspots'),
    url(r'^heatmap/(?P<cityid>[\d]+)$', Heatmap.as_view(), name='heatmap'),
    url(r'^customzip/$', CustomZip.as_view(), name='customzip'),
    url(r'^countryheatmap$', CountryHeatmap.as_view(), name='countryheatmap'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^car_cities/', include(staticfiles_urlpatterns())),
    url(r'^voting/(?P<cityid>[\d]+)$', Voting.as_view(), name='voting')
)

urlpatterns += staticfiles_urlpatterns()
