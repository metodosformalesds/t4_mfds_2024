from django.urls import path
from . import views, views_stripe


urlpatterns = [
    path('', views.servicios_sin_login, name='servicios_sin_login'),
    path('publicar_servicio/', views.publicar_servicio, name='publicar_servicio'),
    path('publicacion_servicio/<int:id>/', views.publicacion_servicio, name='publicacion_servicio'), 
    path('publicacion_servicio/<int:id>/delete', views.eliminar_publicacion, name='eliminar_publicacion'), 
    path('editar_servicio/<int:servicio_id>/', views.editar_servicio, name='editar_servicio'),
    path('create_account/', views_stripe.create_account, name='create_account'),
    path('create_account_link/', views_stripe.create_account_link, name='create_account_link'),
    path('onboarding_complete/', views_stripe.stripe_onboarding_complete, name='stripe_onboarding_complete'),
    path('create_checkout_session/<int:solicitud_id>/', views_stripe.create_checkout_session, name='create_checkout_session'),
    path('payment_success/', views_stripe.payment_success, name='payment_success'),
    path('payment_cancel/', views_stripe.payment_cancel, name='payment_cancel'),
    path('stripe_dashboard/', views_stripe.stripe_dashboard_link, name='stripe_dashboard_link'),
    path('servicio/<int:solicitud_id>/agregar_reseña/', views.agregar_reseña, name='agregar_reseña'),
    ]
