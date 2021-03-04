from django.contrib.auth import get_user_model

from product.models import ProductImage
from seller.models import Seller

User = get_user_model()

user = User.objects.first()

contact = "01024846313"
name = '홍길동'
email = 'cuhong@itechs.io'
seller = Seller.objects.get_or_create(
    name="테스트셀러",
    defaults=dict(
        user=user,
        contact=contact,
        email=email,
        rep_name=name,
        rep_contact=contact,
        rep_email=email,
        sales_name=name,
        sales_contact=contact,
        sales_email=email,
        cs_name=name,
        cs_contact=contact,
        cs_email=email,
        logistic_name=name,
        logistic_contact=contact,
        logistic_email=email
    )
)


image = ProductImage.objects.create(
    seller=seller,
    file="/",
)

