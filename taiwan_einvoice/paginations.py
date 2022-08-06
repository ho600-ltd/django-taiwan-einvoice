from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class TaiwanEInvoicePageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


    def get_paginated_response(self, data):
        page = int(self.request.query_params.get(self.page_query_param, "1"))
        page_size = self.page.paginator.per_page
        count = self.page.paginator.count
        init_page_no = count - (page - 1) * page_size
        return Response({
            'init_page_no': init_page_no,
            'count': count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })



class Default30PerPagePagination(TaiwanEInvoicePageNumberPagination):
    page_size = 30
    max_page_size = 30



class TenTo100PerPagePagination(TaiwanEInvoicePageNumberPagination):
    page_size = 10
    max_page_size = 100


class TenTo1000PerPagePagination(TaiwanEInvoicePageNumberPagination):
    page_size = 10
    max_page_size = 1000

