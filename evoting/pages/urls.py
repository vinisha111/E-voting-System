
# pages/urls.py
from django.urls import path
from .views import view_bulletin_board, voter_registration, voter_login, voter_logout, voter_dashboard, admin_login, admin_logout, admin_dashboard, tallying_authority_registration, tallying_authority_login, tallying_authority_logout, tallying_authority_dashboard, view_voters, view_candidates, view_tallying_authorities

urlpatterns = [
    path('', view_bulletin_board, name='bulletin_board'),

    path('voter/login/', voter_login, name='login'),
    path('voter/register/', voter_registration, name='register'),
    path('voter/home/', voter_dashboard, name='home'),
    path('voter/logout/', voter_logout, name='logout'),

    path('administrator/login/', admin_login, name='admin'),
    path('administrator/logout/', admin_logout, name='admin_logout'),
    path('administrator/home/', admin_dashboard, name='admin_dashboard'),
    path('administrator/voters/', view_voters, name='view_voters'),
    path('administrator/candidates/', view_candidates, name='view_candidates'),
    path('administrator/tallyingauthorities/', view_tallying_authorities, name='view_tallying_authorities'),

    path('tallyingauthority/login/', tallying_authority_login, name='tallying_authority_login'),
    path('tallyingauthority/logout/', tallying_authority_logout, name='tallying_authority_logout'),
    path('tallyingauthority/register/', tallying_authority_registration, name='tallying_authority_registration'),
    path('tallyingauthority/home/', tallying_authority_dashboard, name='tallying_authority_dashboard'),
]
