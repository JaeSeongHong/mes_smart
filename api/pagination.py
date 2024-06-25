from rest_framework.pagination import PageNumberPagination


class PostPageNumberPagination5(PageNumberPagination):
    page_size = 5


class PostPageNumberPagination10(PageNumberPagination):
    page_size = 10


class PostPageNumberPagination15(PageNumberPagination):
    page_size = 15
