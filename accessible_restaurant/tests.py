from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.test import SimpleTestCase
import accessible_restaurant
import django
from accessible_restaurant.views import (
    index_view,
    user_profile_view,
    emailsent_view,
    activate_account,
    restaurant_profile_view,
    restaurant_detail_view,
    signup_view,
    UserSignUpView,
    RestaurantSignUpView,
    restaurant_list_view,
)
from django.contrib.auth import views as auth_views
from accessible_restaurant.forms import (
    UserSignUpForm,
    RestaurantSignUpForm,
    UserProfileUpdateForm,
    UserUpdateForm,
    RestaurantProfileUpdateForm,
    ReviewPostForm,
)

from django.test import TestCase, Client
from django.urls import reverse
from accessible_restaurant.models import (
    User,
    User_Profile,
    Restaurant_Profile,
    Restaurant,
    Review,
)
import json


# Create your tests here.
class TestForms(TestCase):
    def test_userSignUpForm_is_valid(self):
        form = UserSignUpForm(
            data={
                "username": "test1",
                "email": "test@test.com",
                "first_name": "test",
                "last_name": "user",
                "password1": "Password123#",
                "password2": "Password123#",
            }
        )
        self.assertTrue(form.is_valid())

    def test_userSignUpForm_no_data(self):
        form = UserSignUpForm(
            data={
                "username": "test1",
                "email": "test@test.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

    def test_userSignUpForm_no_data_4(self):
        form = UserSignUpForm(
            data={
                "username": "test1",
                "email": "test@test.com",
                "first_name": "test",
                "last_name": "user",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

    def test_RestaurantSignUpForm_is_valid(self):
        form = RestaurantSignUpForm(
            data={
                "username": "test1",
                "email": "test@test.com",
                "password1": "Password123#",
                "password2": "Password123#",
            }
        )
        self.assertTrue(form.is_valid())

    def test_RestaurantSignUpForm_no_data(self):
        form = RestaurantSignUpForm(
            data={
                "username": "test1",
                "email": "test@test.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

    def test_RestaurantSignUpForm_no_data_4(self):
        form = RestaurantSignUpForm(
            data={
                "username": "test1",
                "email": "test@test.com",
                "first_name": "test",
                "last_name": "user",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

    def test_UserProfileUpdateForm_is_valid(self):
        form = UserProfileUpdateForm(
            data={
                "photo": "photo",
                "phone": "1234567889",
                "address": "123 New York",
                "city": "New York",
                "Zip Code": "11220",
                "state": "NY",
                "auth_status": "uncertified",
            }
        )
        self.assertTrue(form.is_valid())

    def test_RestaurantProfileUpdateForm_is_valid(self):
        form = RestaurantProfileUpdateForm(
            data={
                "restaurant_name": "Pizza",
                "photo": "Photo",
                "phone": "1234567889",
                "address": "345 NY",
                "city": "Manhattan",
                "zip_code": "11220",
                "state": "NY",
                "is_open": "True",
            }
        )
        self.assertTrue(form.is_valid())

    def test_UserUpdateForm_is_valid(self):
        form = UserUpdateForm(
            data={"username": "testuser", "first_name": "test", "last_name": "user"}
        )
        self.assertTrue(form.is_valid())

    def test_WriteReviewForm_is_valid(self):
        form = ReviewPostForm(
            data={
                "rating": 5,
                "level_entry_rating": 5,
                "wide_door_rating": 5,
                "accessible_table_rating": 5,
                "accessible_restroom_rating": 5,
                "accessible_path_rating": 5,
                "review_context": "test review",
            }
        )
        self.assertTrue(form.is_valid())


class TestUrls(SimpleTestCase):
    def test_index_url_is_resolved(self):
        url = reverse("accessible_restaurant:index")
        # print(resolve(url))
        self.assertEquals(resolve(url).func, accessible_restaurant.views.index_view)

    def test_email_sent_url_is_resolved(self):
        url = reverse("accessible_restaurant:emailsent")
        # print(resolve(url))
        self.assertEquals(resolve(url).func, accessible_restaurant.views.emailsent_view)

    def test_user_profile_url_is_resolved(self):
        url = reverse("accessible_restaurant:user_profile")
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func, accessible_restaurant.views.user_profile_view
        )

    def test_restaurant_profile_sent_url_is_resolved(self):
        url = reverse("accessible_restaurant:restaurant_profile")
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func, accessible_restaurant.views.restaurant_profile_view
        )

    def test_login_url_is_resolved(self):
        url = reverse("accessible_restaurant:login")
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func.view_class, django.contrib.auth.views.LoginView
        )

    def test_logout_url_is_resolved(self):
        url = reverse("accessible_restaurant:logout")
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func.view_class, django.contrib.auth.views.LogoutView
        )

    def test_signup_url_is_resolved(self):
        url = reverse("accessible_restaurant:signup")
        # print(resolve(url))
        self.assertEquals(resolve(url).func, accessible_restaurant.views.signup_view)

    def test_user_signup_url_is_resolved(self):
        url = reverse("accessible_restaurant:user_signup")
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func.view_class, accessible_restaurant.views.UserSignUpView
        )

    def test_restaurant_signup_url_is_resolved(self):
        url = reverse("accessible_restaurant:restaurant_signup")
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func.view_class,
            accessible_restaurant.views.RestaurantSignUpView,
        )

    def test_browse_url_is_resolved(self):
        url = reverse("accessible_restaurant:browse", args=["page", "sort-property"])
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func, accessible_restaurant.views.restaurant_list_view
        )

    def test_detail_sent_url_is_resolved(self):
        url = reverse("accessible_restaurant:detail", args=["detail"])
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func, accessible_restaurant.views.restaurant_detail_view
        )

    def test_activate_url_is_resolved(self):
        url = reverse("accessible_restaurant:activate", args=["uidb64", "token"])
        # print(resolve(url))
        self.assertEquals(
            resolve(url).func, accessible_restaurant.views.activate_account
        )

    def test_write_review_url_is_resolved(self):
        url = reverse(
            "accessible_restaurant:write_review", args=["FaPtColHYcTnZAxtoM33cA"]
        )
        self.assertEquals(
            resolve(url).func, accessible_restaurant.views.write_review_view
        )


class UserSignUpTest(TestCase):
    def setUp(self):
        self.usersignup_url = reverse("accessible_restaurant:user_signup")
        self.user = {
            "username": "test",
            "email": "testemail@gmail.com",
            "first_name": "first",
            "last_name": "last",
            "password1": "123456test",
            "password2": "123456test",
        }
        return super().setUp()

    def test_can_view_page_correctly(self):
        response = self.client.get(self.usersignup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/userRegister.html")

    def test_can_register_user(self):
        response = self.client.post(self.usersignup_url, self.user, format="text/html")
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, "accounts/activate_account.html")


class RestaurantSignUpTest(TestCase):
    def setUp(self):
        self.restaurantsignup_url = reverse("accessible_restaurant:restaurant_signup")
        self.restaurant = {
            "username": "test",
            "email": "testemail@gmail.com",
            "password1": "123456test",
            "password2": "123456test",
        }
        return super().setUp()

    def test_can_view_page_correctly(self):
        response = self.client.get(self.restaurantsignup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/restaurantRegister.html")

    def test_can_register_user(self):
        response = self.client.post(
            self.restaurantsignup_url, self.restaurant, format="text/html", follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/emailSent.html")


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse("accessible_restaurant:index")
        self.logout_url = reverse("accessible_restaurant:logout")
        self.signup_url = reverse("accessible_restaurant:signup")
        self.emailsent_url = reverse("accessible_restaurant:emailsent")
        self.activate_url = reverse(
            "accessible_restaurant:activate", args=["uid", "token"]
        )

        self.userprofile_url = reverse("accessible_restaurant:user_profile")
        self.resprofile_url = reverse("accessible_restaurant:restaurant_profile")
        self.browse_url = reverse(
            "accessible_restaurant:browse", args=[10, "lowestPrice"]
        )
        self.detail_url = reverse(
            "accessible_restaurant:detail", args=["FaPtColHYcTnZAxtoM33cA"]
        )
        self.review_url = reverse(
            "accessible_restaurant:write_review", args=["FaPtColHYcTnZAxtoM33cA"]
        )
        self.public_url = reverse("accessible_restaurant:public_facing", args=["8"])

    def test_index_view_GET(self):
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_logout_view_GET(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)

    def test_signup_view_GET(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_email_sent_view_GET(self):
        response = self.client.get(self.emailsent_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/emailSent.html")

    # def test_activate_view_GET(self):
    #     # User.objects.create(
    #     #     username="username",
    #     #     first_name="first",
    #     #     last_name="last"
    #     # )
    #     response = self.client.get(self.activate_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "accountss/activate_account.html")

    def test_browse_view_GET(self):
        response = self.client.get(self.browse_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "restaurants/browse.html")

    def test_detail_view_GET(self):
        Restaurant.objects.create(
            business_id="FaPtColHYcTnZAxtoM33cA",
            name="name",
            img_url="https://i.pinimg.com/originals/4e/24/f5/4e24f523182e09376bfe8424d556610a.png",
            rating="4.5",
            address="50 W 34th street",
            city="New York",
            zip_code="10001",
            phone="3472692389",
            compliant="1",
        )
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "restaurants/detail.html")

    def test_user_profile_view_POST(self):
        self.user = User.objects.create_user(
            "huanjin", "zhanghuanjin97@gmail.com", "test123456"
        )
        # self.client.login(username="huanjin", password="test123456")
        self.user.uprofile = User_Profile.objects.create(
            photo="default.jpg",
            phone="3474223609",
            address="35 River Drive South",
            city="Jersey City",
            zip_code="07310",
            state="NJ",
        )
        response = self.client.post(
            self.userprofile_url,
            {
                "photo": "default.jpg",
                "phone": "3474223609",
                "address": "35 River Drive South",
                "city": "Jersey City",
                "zip_code": "07310",
                "state": "NJ",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.user.uprofile.phone, "3474223609")
        # self.assertTemplateUsed(response, "profile/user_profile.html")

    def test_res_profile_view_POST(self):
        self.user = User.objects.create_user(
            "huanjin", "zhanghuanjin97@gmail.com", "test123456"
        )
        # self.client.login(username="huanjin", password="test123456")
        self.user.rprofile = Restaurant_Profile.objects.create(
            restaurant_name="name",
            photo="default.jpg",
            phone="3474223609",
            address="35 River Drive South",
            city="Jersey City",
            zip_code="07310",
            state="NJ",
            is_open=True,
        )

        response = self.client.post(self.resprofile_url)  # self.user.rprofile)
        self.assertEqual(response.status_code, 302)

    def test_write_review_view_GET(self):
        self.user = User.objects.create_user(
            "huanjin", "zhanghuanjin97@gmail.com", "test123456"
        )
        self.client.login(username="huanjin", password="test123456")

        Restaurant.objects.create(
            business_id="FaPtColHYcTnZAxtoM33cA",
            name="Chu Tea",
            img_url="https://s3-media4.fl.yelpcdn.com/bphoto/05Q6eHDSpXmytCf4JHR7AQ/o.jpg",
            rating="4.0",
            latitude="40.668253",
            longitude="-73.986898",
            address="471 5th Ave",
            city="Brooklyn",
            zip_code="11215",
            phone="+17187881113",
            compliant=True,
            price="$",
            category1="Bubble Tea",
            category2="Poke",
            category3="Juice Bars & Smoothies",
        )
        response = self.client.get(self.review_url)
        self.assertEqual(response.status_code, 302)
        # self.assertTemplateUsed(response, "review/write_review.html")

    # def test_public_facing_view(self):
    #     self.user = User.objects.create_user(
    #         "huanjin", "zhanghuanjin97@gmail.com", "test123456"
    #     )
    #     response = self.client.get(self.public_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "publicface/public_user_detail.html")

    # def test_review_form_valid_view_GET(self):
    #     self.user = User.objects.create_user(
    #         "huanjin", "zhanghuanjin97@gmail.com", "test123456"
    #     )
    #     self.client.login(username="huanjin", password="test123456")
    #     form_data = {
    #         "rating": 5,
    #         "level_entry_rating": 5,
    #         "wide_door_rating": 5,
    #         "accessible_table_rating": 5,
    #         "accessible_restroom_rating": 5,
    #         "accessible_path_rating": 5,
    #         "review_context": "test review",
    #     }
    #
    #     Restaurant.objects.create(
    #         business_id="FaPtColHYcTnZAxtoM33cA",
    #         name="Chu Tea",
    #         img_url="https://s3-media4.fl.yelpcdn.com/bphoto/05Q6eHDSpXmytCf4JHR7AQ/o.jpg",
    #         rating="4.0",
    #         latitude="40.668253",
    #         longitude="-73.986898",
    #         address="471 5th Ave",
    #         city="Brooklyn",
    #         zip_code="11215",
    #         phone="+17187881113",
    #         compliant=True,
    #         price="$",
    #         category1="Bubble Tea",
    #         category2="Poke",
    #         category3="Juice Bars & Smoothies",
    #     )
    #     response = self.client.post(self.detail_url, form_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "restaurants/detail.html")


class SortTest(TestCase):
    def setUp(self):
        self.sortbydefault_url = reverse(
            "accessible_restaurant:browse", args=["0", "default"]
        )
        self.sortbylowestprice_url = reverse(
            "accessible_restaurant:browse", args=["0", "lowestprice"]
        )
        self.sortbyhighestprice_url = reverse(
            "accessible_restaurant:browse", args=["0", "highestprice"]
        )
        self.sortbynearest_url = reverse(
            "accessible_restaurant:browse", args=["0", "nearest"]
        )
        return super().setUp()

    def test_can_view_page_correctly(self):
        sortbydefault_response = self.client.get(self.sortbydefault_url)
        sortbylowestprice_response = self.client.get(self.sortbylowestprice_url)
        sortbyhighestprice_response = self.client.get(self.sortbyhighestprice_url)
        sortbynearest_response = self.client.get(self.sortbynearest_url)
        self.assertEqual(sortbydefault_response.status_code, 200)
        self.assertEqual(sortbylowestprice_response.status_code, 200)
        self.assertEqual(sortbyhighestprice_response.status_code, 200)
        self.assertEqual(sortbynearest_response.status_code, 200)
        self.assertTemplateUsed(sortbydefault_response, "restaurants/browse.html")
        self.assertTemplateUsed(sortbylowestprice_response, "restaurants/browse.html")
        self.assertTemplateUsed(sortbyhighestprice_response, "restaurants/browse.html")
        self.assertTemplateUsed(sortbynearest_response, "restaurants/browse.html")


class SearchTest(TestCase):
    def setUp(self) -> None:
        Restaurant.objects.create(
            business_id="FaPtColHYcTnZAxtoM33cA",
            name="Chu Tea",
            img_url="https://s3-media4.fl.yelpcdn.com/bphoto/05Q6eHDSpXmytCf4JHR7AQ/o.jpg",
            rating="4.0",
            latitude="40.668253",
            longitude="-73.986898",
            address="471 5th Ave",
            city="Brooklyn",
            zip_code="11215",
            phone="+17187881113",
            compliant=True,
            price="$",
            category1="Bubble Tea",
            category2="Poke",
            category3="Juice Bars & Smoothies",
        )

        Restaurant.objects.create(
            business_id="De_10VF2CrC2moWaPA81mg",
            name="Just Salad",
            img_url="https://s3-media1.fl.yelpcdn.com/bphoto/xX9UzyMKSao3qfsufH9SnA/o.jpg",
            rating="3.5",
            latitude="40.669429",
            longitude="-73.979494",
            address="252 7th Ave",
            city="Brooklyn",
            zip_code="11215",
            phone="+18666733757",
            compliant=True,
            price="$$",
            category1="Salad",
            category2="Wraps",
            category3="Vegetarian",
        )

        self.search_url = reverse("accessible_restaurant:browse", args=["0", "default"])
        self.filter_url = reverse("accessible_restaurant:browse", args=["0", "default"])

    def test_can_view_page_correctly(self):
        response_search_zipcode = self.client.get(self.search_url, {"query": "11215"})
        response_search_restaurant_name = self.client.get(
            self.search_url, {"query": "Chu Tea"}
        )
        response_search_category = self.client.get(
            self.search_url, {"query": "Bubble Tea"}
        )
        response_search_address = self.client.get(self.search_url, {"query": "5th Ave"})
        response_search_multicondition = self.client.get(
            self.search_url, {"query": "11215, Juice Bars"}
        )

        response_filter_price = self.client.get(self.filter_url, {"price1": "$"})
        response_filter_category = self.client.get(self.filter_url, {"Salad": "Salad"})

        self.assertEqual(response_search_zipcode.status_code, 200)
        self.assertEqual(response_search_restaurant_name.status_code, 200)
        self.assertEqual(response_search_category.status_code, 200)
        self.assertEqual(response_search_address.status_code, 200)
        self.assertEqual(response_search_multicondition.status_code, 200)

        self.assertEqual(response_filter_price.status_code, 200)
        self.assertEqual(response_filter_category.status_code, 200)

        self.assertTemplateUsed(response_search_zipcode, "restaurants/browse.html")
        self.assertTemplateUsed(
            response_search_restaurant_name, "restaurants/browse.html"
        )
        self.assertTemplateUsed(response_search_category, "restaurants/browse.html")
        self.assertTemplateUsed(response_search_address, "restaurants/browse.html")
        self.assertTemplateUsed(
            response_search_multicondition, "restaurants/browse.html"
        )

        self.assertTemplateUsed(response_filter_price, "restaurants/browse.html")
        self.assertTemplateUsed(response_filter_category, "restaurants/browse.html")


class TestModels(TestCase):
    def test_save_restaurant_profile_image_correctly(self):
        self.user = User.objects.create_user(
            "huanjin", "zhanghuanjin97@gmail.com", "test123456"
        )
        # self.client.login(username="huanjin", password="test123456")
        self.user.rprofile = Restaurant_Profile.objects.create(
            restaurant_name="name",
            photo="default.jpg",
            phone="3474223609",
            address="35 River Drive South",
            city="Jersey City",
            zip_code="07310",
            state="NJ",
            is_open=True,
        )

        self.assertEquals(self.user.rprofile.photo.height, 300)
        self.assertEquals(self.user.rprofile.photo.width, 300)
        self.assertEqual(str(self.user.rprofile), "huanjin Restaurant Profile")
        # self.assertEquals(self.user.rprofile.photo.path , "\media\default.jpg")

    def test_save_user_profile_image_correctly(self):
        self.user = User.objects.create_user(
            "huanjin", "zhanghuanjin97@gmail.com", "test123456"
        )
        # self.client.login(username="huanjin", password="test123456")
        self.user.uprofile = User_Profile.objects.create(
            photo="default.jpg",
            phone="3474223609",
            address="35 River Drive South",
            city="Jersey City",
            zip_code="07310",
            state="NJ",
        )
        self.assertEquals(self.user.uprofile.photo.height, 300)
        self.assertEquals(self.user.uprofile.photo.width, 300)

        self.assertEqual(str(self.user.uprofile), "huanjin User Profile")

    def test_review_model_correctly(self):
        self.user = User.objects.create_user(
            "huanjin", "zhanghuanjin97@gmail.com", "test123456"
        )
        self.client.login(username="huanjin", password="test123456")

        self.Restaurant = Restaurant.objects.create(
            business_id="FaPtColHYcTnZAxtoM33cA",
            name="Chu Tea",
            img_url="https://s3-media4.fl.yelpcdn.com/bphoto/05Q6eHDSpXmytCf4JHR7AQ/o.jpg",
            rating="4.0",
            latitude="40.668253",
            longitude="-73.986898",
            address="471 5th Ave",
            city="Brooklyn",
            zip_code="11215",
            phone="+17187881113",
            compliant=True,
            price="$",
            category1="Bubble Tea",
            category2="Poke",
            category3="Juice Bars & Smoothies",
        )
        self.Review = Review.objects.create(
            user=self.user,
            restaurant=self.Restaurant,
            review_date="2020-05-01",
            rating=5,
            level_entry_rating=5,
            wide_door_rating=5,
            accessible_table_rating=5,
            accessible_restroom_rating=5,
            accessible_path_rating=5,
            review_context="test review",
        )
        self.assertEqual(str(self.Review), "huanjin review on Chu Tea")

    def test_save_restaurant_name_correctly(self):
        self.Restaurant = Restaurant.objects.create(
            business_id="De_10VF2CrC2moWaPA81mg",
            name="Just Salad",
            img_url="https://s3-media1.fl.yelpcdn.com/bphoto/xX9UzyMKSao3qfsufH9SnA/o.jpg",
            rating="3.5",
            latitude="40.669429",
            longitude="-73.979494",
            address="252 7th Ave",
            city="Brooklyn",
            zip_code="11215",
            phone="+18666733757",
            compliant=True,
            price="$$",
            category1="Salad",
            category2="Wraps",
            category3="Vegetarian",
        )

        self.assertEqual(str(self.Restaurant), "Just Salad")


class TestManageCertificate(TestCase):
    def setUp(self):
        self.management_url = reverse("accessible_restaurant:authenticate")
        return super().setUp()

    def test_can_view_management_page_correctly(self):
        self.user = User.objects.create_superuser(
            "admin", "shonna.x.tang@gmail.com", "accessible"
        )
        self.client.login(username="admin", password="accessible")
        management_response = self.client.get(self.management_url)
        self.assertEqual(management_response.status_code, 200)
        self.assertTemplateUsed(management_response, "admin/manage.html")
