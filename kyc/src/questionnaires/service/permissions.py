# from django.contrib.auth.models import Permission, User
# from django.contrib.contenttypes.models import ContentType
# from yourapp.models import Questionnaire
#
# content_type = ContentType.objects.get_for_model(Questionnaire)
# permission = Permission.objects.get(
#     codename='can_publish_questionnaire',
#     content_type=content_type,
# )
#
# user = User.objects.get(email='admin@example.com')
# user.user_permissions.add(permission)
