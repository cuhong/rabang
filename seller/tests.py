from django.contrib.auth import get_user_model
from django.test import TestCase

from seller.models import Seller

User = get_user_model()
# Create your tests here.
def create_user():
    try:
        user = User.objects.get(email="test@test.com")
    except User.DoesNotExist:
        user = User.objects.create_user("test@test.com", "테스트셀러", "01000000000", password="xptmxm1!")
    return user

def create_seller(user):
    seller = Seller.objects.create(
        user=user,
        name=f"테스트 셀러{user.email}",
        contact="01000000000",
        email="teset@tesset.com",
        rep_name="홍길동",
        rep_email="gdhong@test.com",
        rep_contact="01000000000",
        sales_name="홍길동",
        sales_email="gdhong@test.com",
        sales_contact="01000000000",
        cs_name="홍길동",
        cs_email="gdhong@test.com",
        cs_contact="01000000000",
        logistic_name="홍길동",
        logistic_email="gdhong@test.com",
        logistic_contact="01000000000",
    )
    return seller

user = create_user()
seller = create_seller(user)