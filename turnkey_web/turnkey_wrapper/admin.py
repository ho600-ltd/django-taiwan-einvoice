import logging
logger = logging.getLogger(__name__)

from django.contrib import admin

# from .models import (
#     FROM_CONFIG,
#     SCHEDULE_CONFIG,
#     SIGN_CONFIG,
#     TASK_CONFIG,
#     TO_CONFIG,
#     TURNKEY_MESSAGE_LOG,
#     TURNKEY_MESSAGE_LOG_DETAIL,
#     TURNKEY_SEQUENCE,
#     TURNKEY_SYSEVENT_LOG,
#     TURNKEY_TRANSPORT_CONFIG,
#     TURNKEY_USER_PROFILE,
# )


# class ReadOnlyAdmin(admin.ModelAdmin):
#     readonly_fields = []

#     def get_readonly_fields(self, request, obj=None):
#         return list(self.readonly_fields) + \
#                [field.name for field in obj._meta.fields] + \
#                [field.name for field in obj._meta.many_to_many]


#     def has_add_permission(self, request):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     def has_delete_permission(self, request, obj=None):
#         return False


# class FROM_CONFIGAdmin(ReadOnlyAdmin):
#     pass

# class SCHEDULE_CONFIGAdmin(ReadOnlyAdmin):
#     pass

# class SIGN_CONFIGAdmin(ReadOnlyAdmin):
#     pass

# class TASK_CONFIGAdmin(ReadOnlyAdmin):
#     pass

# class TO_CONFIGAdmin(ReadOnlyAdmin):
#     pass

# class TURNKEY_MESSAGE_LOGAdmin(ReadOnlyAdmin):
#     pass

# class TURNKEY_MESSAGE_LOG_DETAILAdmin(ReadOnlyAdmin):
#     pass

# class TURNKEY_SEQUENCEAdmin(ReadOnlyAdmin):
#     pass

# class TURNKEY_SYSEVENT_LOGAdmin(ReadOnlyAdmin):
#     pass

# class TURNKEY_TRANSPORT_CONFIGAdmin(ReadOnlyAdmin):
#     pass

# class TURNKEY_USER_PROFILEAdmin(ReadOnlyAdmin):
#     pass



# admin.site.register(FROM_CONFIG, FROM_CONFIGAdmin)
# admin.site.register(SCHEDULE_CONFIG, SCHEDULE_CONFIGAdmin)
# admin.site.register(SIGN_CONFIG, SIGN_CONFIGAdmin)
# admin.site.register(TASK_CONFIG, TASK_CONFIGAdmin)
# admin.site.register(TO_CONFIG, TO_CONFIGAdmin)
# admin.site.register(TURNKEY_MESSAGE_LOG, TURNKEY_MESSAGE_LOGAdmin)
# admin.site.register(TURNKEY_MESSAGE_LOG_DETAIL, TURNKEY_MESSAGE_LOG_DETAILAdmin)
# admin.site.register(TURNKEY_SEQUENCE, TURNKEY_SEQUENCEAdmin)
# admin.site.register(TURNKEY_SYSEVENT_LOG, TURNKEY_SYSEVENT_LOGAdmin)
# admin.site.register(TURNKEY_TRANSPORT_CONFIG, TURNKEY_TRANSPORT_CONFIGAdmin)
# admin.site.register(TURNKEY_USER_PROFILE, TURNKEY_USER_PROFILEAdmin)
