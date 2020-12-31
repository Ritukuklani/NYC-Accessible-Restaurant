from sqlite3 import Error

from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect

# from django.contrib import messages
from django.views.generic import CreateView
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings

# from .token_generator import generate_token
from django.core.mail import EmailMessage

from django.db.models import Q

from .forms import (
    UserSignUpForm,
    RestaurantSignUpForm,
    UserUpdateForm,
    UserProfileUpdateForm,
    UserPreferencesForm,
    RestaurantProfileUpdateForm,
    ReviewPostForm,
    UserCertUpdateForm,
    UserCertVerifyForm,
    RestaurantCertUpdateForm,
    RestaurantCertVerifyForm,
    CommentForm,
    ContactForm,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from .models import (
    User,
    Restaurant,
    Review,
    ApprovalPendingUsers,
    ApprovalPendingRestaurants,
    User_Profile,
    User_Preferences,
    Restaurant_Profile,
    FAQ,
    Favorites,
    # Images,
)
from .utils import (
    get_restaurant_list,
    get_filter_restaurant,
    get_restaurant,
    get_page_range,
    get_star_list,
    get_search_restaurant,
    get_public_user_detail,
    get_user_reviews,
    get_user_preferences,
    get_user_favorite,
    get_user_profile_favorite,
)

from django.forms import modelformset_factory

# Create your views here.
# def index_view(request):
#     recommended_restaurants = Restaurant.objects.all()[:3]
#     context = {"recommended_restaurants": recommended_restaurants}
#     return render(request, "home.html", context)


def index_view_personalized(request):
    try:
        if request.user.is_user:
            user = request.user
            recommended_restaurants = get_user_preferences(user)[:3]
        else:
            temp = (
                Restaurant.objects.all()
                .filter(
                    Q(review_count__gt=20)
                    & Q(rating__gte=4.0)
                    & Q(compliant__exact=True)
                )
                .order_by("-rating")
            )
            recommended_restaurants = temp[:3]
    except (
        TypeError,
        ValueError,
        AttributeError,
    ):
        temp = (
            Restaurant.objects.all()
            .filter(
                Q(review_count__gt=20) & Q(rating__gte=4.0) & Q(compliant__exact=True)
            )
            .order_by("-rating")
        )
        recommended_restaurants = temp[:3]
    context = {"recommended_restaurants": recommended_restaurants}
    return render(request, "home.html", context)


# def about_view(request):
#     return render(request, "accounts/about.html")


@login_required
def logout_view(request):
    return render(request, "accounts/logout.html")


def signup_view(request):
    if request.method == "GET":
        return render(request, "accounts/signup.html")


def emailsent_view(request):
    if request.method == "GET":
        return render(request, "accounts/emailSent.html")


def activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        # print(user.username)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "accounts/activate_confirmation.html")
    return render(request, "accounts/register.html")


class UserSignUpView(CreateView):
    model = User
    form_class = UserSignUpForm
    template_name = "accounts/userSignup.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "user"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # check if user's email has already exist in the database
        user_email = form.cleaned_data.get("email")
        if User.objects.filter(email=user_email).exists():
            return render(
                self.request,
                self.template_name,
                {
                    "error_message": "Email has already been registered.",
                    "form": form,
                },
            )
        user = form.save()
        user.is_active = False
        user.save()
        # Email verification
        current_site = get_current_site(self.request)
        email_subject = "Activate Your NYC Accessible Restaurant Advisor Account!"
        message = render_to_string(
            "accounts/activate_account.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": PasswordResetTokenGenerator().make_token(user),
            },
        )
        to_email = form.cleaned_data.get("email")
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()
        return redirect("accessible_restaurant:emailsent")


class RestaurantSignUpView(CreateView):
    model = User
    form_class = RestaurantSignUpForm
    template_name = "accounts/restaurantSignup.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "restaurant"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        # check if restaurant's email has already exist in the database
        restaurant_email = form.cleaned_data.get("email")
        if User.objects.filter(email=restaurant_email).exists():
            return render(
                self.request,
                self.template_name,
                {
                    "error_message": "Email has already been registered.",
                    "form": form,
                },
            )
        restaurant = form.save()
        restaurant.is_active = False
        restaurant.save()
        # Email verification
        current_site = get_current_site(self.request)
        email_subject = "Activate Your NYC Accessible Restaurant Advisor Account!"
        message = render_to_string(
            "accounts/activate_account.html",
            {
                "user": restaurant,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(restaurant.pk)),
                "token": PasswordResetTokenGenerator().make_token(restaurant),
            },
        )
        to_email = form.cleaned_data.get("email")
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()
        return redirect("accessible_restaurant:emailsent")


@login_required
@user_passes_test(lambda u: u.is_user, login_url="/", redirect_field_name=None)
def user_profile_view(request):
    if request.method == "POST":
        if "submit-certificate" in request.POST:
            auth_form = UserCertUpdateForm(request.POST, request.FILES)
            if auth_form.is_valid():
                tmp_auth = auth_form.save(commit=False)
                tmp_auth.user = request.user
                tmp_auth.auth_status = "pending"
                prev_auth_len = ApprovalPendingUsers.objects.filter(
                    user=request.user
                ).count()
                if prev_auth_len > 0:
                    prev_auth = ApprovalPendingUsers.objects.get(user=request.user)
                    prev_auth.auth_documents.delete()
                    prev_auth.delete()
                auth_form.save()
                p_instance = User_Profile.objects.get(user=request.user)
                p_instance.auth_status = "pending"
                p_instance.save()
                messages.success(
                    request, f'{"Your certificate has been sent to administrator!"}'
                )
                return redirect("accessible_restaurant:user_profile")
            else:
                u_form = UserUpdateForm(instance=request.user)
                p_form = UserProfileUpdateForm(instance=request.user.uprofile)
                preferences_form = UserPreferencesForm(
                    instance=request.user.upreferences
                )

        elif "submit-info" in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = UserProfileUpdateForm(
                request.POST, request.FILES, instance=request.user.uprofile
            )
            preferences_form = UserPreferencesForm(instance=request.user.upreferences)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, f'{"Your profile has been updated!"}')
                return redirect("accessible_restaurant:user_profile")
            else:
                queue = ApprovalPendingUsers.objects.filter(user=request.user).count()
                if queue > 0:
                    q = ApprovalPendingUsers.objects.get(user=request.user)
                    auth_form = UserCertUpdateForm(instance=q.user.auth)
                else:
                    auth_form = UserCertUpdateForm()

        elif "submit-preferences" in request.POST:
            preferences_form = UserPreferencesForm(
                request.POST, request.FILES, instance=request.user.upreferences
            )
            u_form = UserUpdateForm(instance=request.user)
            p_form = UserProfileUpdateForm(instance=request.user.uprofile)
            if preferences_form.is_valid():
                preferences_form.save()
                messages.success(request, f'{"Your profile has been updated!"}')
                return redirect("accessible_restaurant:user_profile")
            else:
                queue = ApprovalPendingUsers.objects.filter(user=request.user).count()
                if queue > 0:
                    q = ApprovalPendingUsers.objects.get(user=request.user)
                    auth_form = UserCertUpdateForm(instance=q.user.auth)
                else:
                    auth_form = UserCertUpdateForm()

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = UserProfileUpdateForm(instance=request.user.uprofile)
        preferences_form = UserPreferencesForm(instance=request.user.upreferences)
        queue = ApprovalPendingUsers.objects.filter(user=request.user).count()
        if queue > 0:
            q = ApprovalPendingUsers.objects.get(user=request.user)
            auth_form = UserCertUpdateForm(instance=q.user.auth)
        else:
            auth_form = UserCertUpdateForm()

    response_favorite = get_user_profile_favorite(request.user)
    star_list = get_star_list()

    for restaurant in response_favorite:
        full, half, null = star_list[float(restaurant["rating"])]
        restaurant["full"] = full
        restaurant["half"] = half
        restaurant["null"] = null

    action = request.GET.get("action")
    if action == "Edit Profile":
        profile_action = "edit"
    else:
        profile_action = "view"

    context = {
        "user_form": u_form,
        "profile_form": p_form,
        "auth_form": auth_form,
        "preferences_form": preferences_form,
        "profile_action": profile_action,
        "user_favorite": response_favorite,
    }
    return render(request, "profile/user_profile.html", context)


@login_required
@user_passes_test(lambda u: u.is_superuser, login_url="/", redirect_field_name=None)
def authentication_view(request):
    if request.method == "POST":
        if "submit-user" in request.POST:
            user_auth_form = UserCertVerifyForm(request.POST)
            if user_auth_form.is_valid():
                user_id = request.POST.get("user_id")
                auth_status = user_auth_form.cleaned_data["auth_status"]
                if auth_status != "pending" and auth_status != "N/A":
                    p_instance = User_Profile.objects.get(user=user_id)
                    if auth_status == "approve":
                        p_instance.auth_status = "certified"
                    else:
                        p_instance.auth_status = "uncertified"
                    p_instance.save()
                    curr_user = ApprovalPendingUsers.objects.get(user=user_id)
                    # delete document from the database
                    curr_user.auth_documents.delete()
                    curr_user.delete()
                    if auth_status == "approve":
                        messages.success(request, f'{"Approved!"}')
                    else:
                        messages.success(request, f'{"Disapproved!"}')
                return redirect("accessible_restaurant:authenticate")

        elif "submit-restaurant" in request.POST:
            restaurant_auth_form = RestaurantCertVerifyForm(request.POST)
            if restaurant_auth_form.is_valid():
                owner_id = request.POST.get("owner_id")
                rest_id = request.POST.get("restaurant_id")
                auth_status = restaurant_auth_form.cleaned_data["auth_status"]
                if auth_status != "pending" and auth_status != "N/A":
                    if auth_status == "approve":
                        Restaurant.objects.filter(business_id=rest_id).update(
                            user=owner_id
                        )
                    rest = Restaurant.objects.get(business_id=rest_id)
                    curr_user = ApprovalPendingRestaurants.objects.get(
                        user=owner_id, restaurant=rest
                    )
                    # delete document from the database
                    curr_user.auth_documents.delete()
                    curr_user.delete()
                    if auth_status == "approve":
                        messages.success(request, f'{"Approved!"}')
                    else:
                        messages.success(request, f'{"Disapproved!"}')
                return redirect("accessible_restaurant:authenticate")

    user_certificate_list = ApprovalPendingUsers.objects.order_by("time_created")
    restaurant_certificate_list = ApprovalPendingRestaurants.objects.order_by(
        "time_created"
    )
    user_form_list = []
    for c in user_certificate_list:
        curr = UserCertVerifyForm(instance=c.user.auth)
        user_form_list.append(curr)
    restaurant_form_list = []
    for c in restaurant_certificate_list:
        curr = RestaurantCertVerifyForm(instance=c)
        restaurant_form_list.append(curr)
    context = {
        "user_certificate_list": user_form_list,
        "restaurant_certificate_list": restaurant_form_list,
    }
    return render(request, "admin/manage.html", context)


@login_required
@user_passes_test(lambda u: u.is_restaurant, login_url="/", redirect_field_name=None)
def restaurant_profile_view(request):
    if request.method == "POST":
        if "submit-certificate" in request.POST:
            auth_form = RestaurantCertUpdateForm(request.POST, request.FILES)
            if auth_form.is_valid():
                tmp_auth = auth_form.save(commit=False)
                tmp_auth.user = request.user
                tmp_auth.auth_status = "pending"
                prev_auth_len = ApprovalPendingRestaurants.objects.filter(
                    user=request.user, restaurant=tmp_auth.restaurant
                ).count()
                if prev_auth_len > 0:
                    prev_auth = ApprovalPendingRestaurants.objects.get(
                        user=request.user, restaurant=tmp_auth.restaurant
                    )
                    prev_auth.auth_documents.delete()
                    prev_auth.delete()
                auth_form.save()
                # update the auth_status in restaurant profile
                tmp_rprofile = Restaurant_Profile.objects.get(user=request.user)
                tmp_rprofile.auth_status = True
                tmp_rprofile.save()
                messages.success(
                    request, f'{"Your certificate has been sent to administrator!"}'
                )
                return redirect("accessible_restaurant:restaurant_profile")
            else:
                u_form = UserUpdateForm(instance=request.user)
                p_form = RestaurantProfileUpdateForm(instance=request.user.rprofile)

        elif "submit-info" in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = RestaurantProfileUpdateForm(
                request.POST, request.FILES, instance=request.user.rprofile
            )

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, f'{"Your profile has been updated!"}')
                return redirect("accessible_restaurant:restaurant_profile")
            else:
                auth_form = RestaurantCertUpdateForm()

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = RestaurantProfileUpdateForm(instance=request.user.rprofile)
        auth_form = RestaurantCertUpdateForm()

    action = request.GET.get("action")
    if action == "Edit Profile":
        profile_action = "edit"
    else:
        profile_action = "view"

    restaurant_list = Restaurant.objects.filter(user=request.user)

    auth_request = ApprovalPendingRestaurants.objects.filter(user=request.user)
    auth_request_list = []
    for req in auth_request:
        auth_request_list.append(req.restaurant)

    context = {
        "user_form": u_form,
        "profile_form": p_form,
        "auth_form": auth_form,
        "profile_action": profile_action,
        "restaurant_list": restaurant_list,
        "auth_request_list": auth_request_list,
    }
    return render(request, "profile/restaurant_profile.html", context)


def restaurant_list_view(request, page):
    sort_property = request.GET.get("sort_property", "default")
    # if sort_property == "nearest":
    #     messages.warning(
    #         request,
    #         f'{"Your current IP address will be used for this feature. "}',
    #     )
    page = int(page)
    if sort_property == "nearest":
        client_ip = get_client_ip(request)
    else:
        client_ip = ""
    restaurants = Restaurant.objects.all()

    keyword = request.GET.get("query", "")
    price1 = request.GET.get("price1", "")
    price2 = request.GET.get("price2", "")
    price3 = request.GET.get("price3", "")
    price4 = request.GET.get("price4", "")
    chinese = request.GET.get("Chinese", "")
    korean = request.GET.get("Korean", "")
    salad = request.GET.get("Salad", "")
    pizza = request.GET.get("Pizza", "")
    sandwiches = request.GET.get("Sandwiches", "")
    brunch = request.GET.get("Brunch", "")
    coffee = request.GET.get("Coffee", "")
    allRestaurants = request.GET.get("allRestaurants", "")
    notCompliant = request.GET.get("notCompliant", "")

    filters_applied = False
    if (
        price1
        or price2
        or price3
        or price4
        or chinese
        or korean
        or salad
        or pizza
        or sandwiches
        or brunch
        or coffee
        or allRestaurants
        or notCompliant
    ):
        filters_applied = True

    filters = {
        "prices": [price1, price2, price3, price4],
        "categories": [chinese, korean, salad, pizza, sandwiches, brunch, coffee],
        "compliant": [allRestaurants, notCompliant],
    }

    if keyword:
        restaurants = get_search_restaurant(keyword)
    restaurants = get_filter_restaurant(filters, restaurants)
    restaurant_results = get_restaurant_list(
        page, 10, sort_property, client_ip, restaurants
    )
    restaurant_list = restaurant_results["restaurants_list"]

    star_list = get_star_list()
    for restaurant in restaurant_list:
        full, half, null = star_list[restaurant["rating"]]
        restaurant["full"] = full
        restaurant["half"] = half
        restaurant["null"] = null

    # Page count
    total_restaurant = restaurant_results["total_restaurant"]
    total_page = total_restaurant // 10
    if total_restaurant % 10 == 0:
        total_page -= 1

    # Previous and next page numbers
    page_range = get_page_range(int(total_page), page + 1)
    page_exceed_error = (
        "page number exceeds maximum page number, please choose valid page"
    )

    postfix = request.GET.urlencode()
    context = {
        "restaurants": restaurant_list,
        "star_list": star_list,
        "page_num": page,
        "total_page": total_page,
        "page_range": page_range,
        "page_exceed_error": page_exceed_error,
        "sort_property": sort_property,
        "keyword": keyword,
        "postfix": postfix,
        "price1": price1,
        "price2": price2,
        "price3": price3,
        "price4": price4,
        "Chinese": chinese,
        "Korean": korean,
        "Salad": salad,
        "Pizza": pizza,
        "Sandwiches": sandwiches,
        "Brunch": brunch,
        "Coffee": coffee,
        "allRestaurants": allRestaurants,
        "notCompliant": notCompliant,
        "filter_applied": filters_applied,
    }
    return render(request, "restaurants/listing.html", context)


def restaurant_detail_view(request, business_id):
    try:
        restaurant = Restaurant.objects.get(business_id=business_id)
    except (KeyError, Restaurant.DoesNotExist):
        return render(
            request,
            "restaurants/error.html",
            {
                "business_id": business_id,
                "error_message": "Restaurant not found!",
            },
        )
    else:
        if request.method == "POST" and "save_favorite_form" in request.POST:
            user = request.user
            restaurant = Restaurant.objects.get(business_id=business_id)
            Favorites.objects.create(
                user=user,
                restaurant=restaurant,
            )

        if request.method == "POST" and "delete_favorite_form" in request.POST:
            # restaurant = Restaurant.objects.get(business_id=business_id)
            Favorites.objects.filter(user=request.user, restaurant=restaurant).delete()

        response = get_restaurant(restaurant.business_id)
        star_list = get_star_list()
        full, half, null = star_list[restaurant.rating]

        restaurant_data = response["restaurant_data"]
        restaurant_reviews = response["restaurant_reviews"]
        local_restaurant_reviews = response["local_restaurant_reviews"]
        local_restaurant_data = response["local_restaurant_data"]

        # Accessible Rating
        (
            level_entry_rating_full,
            level_entry_rating_half,
            level_entry_rating_null,
        ) = star_list[local_restaurant_data.get("level_entry_rating")]
        wide_door_rating_full, wide_door_rating_half, wide_door_rating_null = star_list[
            local_restaurant_data.get("wide_door_rating")
        ]
        (
            accessible_table_rating_full,
            accessible_table_rating_half,
            accessible_table_rating_null,
        ) = star_list[local_restaurant_data.get("accessible_table_rating")]
        (
            accessible_restroom_rating_full,
            accessible_restroom_rating_half,
            accessible_restroom_rating_null,
        ) = star_list[local_restaurant_data.get("accessible_restroom_rating")]
        (
            accessible_path_rating_full,
            accessible_path_rating_half,
            accessible_path_rating_null,
        ) = star_list[local_restaurant_data.get("accessible_path_rating")]

        # initial
        lr_full = 0
        lr_half = 0
        lr_null = 0
        username = ""
        photo = ""

        # Rating stars
        if local_restaurant_reviews != null:
            for review in local_restaurant_reviews:
                lr_full, lr_half, lr_null = star_list[float(review["rating"])]
                review["lfull"] = lr_full
                review["lhalf"] = lr_half
                review["lnull"] = lr_null
                username = review["username"]
                photo = review["photo"]

        for review in restaurant_reviews["reviews"]:
            r_full, r_half, r_null = star_list[float(review["rating"])]
            review["full"] = r_full
            review["half"] = r_half
            review["null"] = r_null

        # Get open hours and is_open status
        hours = []
        is_open_now = False
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if "hours" in restaurant_data:
            if restaurant_data["hours"]:
                is_open_now = restaurant_data["hours"][0]["is_open_now"]
                for day in restaurant_data["hours"][0]["open"]:
                    index = int(day["day"])
                    day["weekday"] = weekdays[index]
                    start = day["start"]
                    end = day["end"]
                    day["start"] = start[:2] + ":" + start[2:]
                    day["end"] = end[:2] + ":" + end[2:]
                    hours.append(day)
        else:
            hours = None

        comment_form = CommentForm()

        # if user likes the favorite
        if request.user.is_authenticated:
            isFavorite = (
                len(Favorites.objects.filter(user=request.user, restaurant=restaurant))
                > 0
            )
        else:
            isFavorite = False

        context = {
            # "review": Review.objects.all(),
            "restaurant": restaurant,
            "restaurant_data": restaurant_data,
            "restaurant_review": restaurant_reviews,
            "local_restaurant_review": local_restaurant_reviews,
            "local_restaurant_data": local_restaurant_data,
            "full": full,
            "half": half,
            "null": null,
            "lfull": lr_full,
            "lhalf": lr_half,
            "lnull": lr_null,
            "hours": hours,
            "is_open_now": is_open_now,
            "username": username,
            "photo": photo,
            "level_entry_rating_full": level_entry_rating_full,
            "level_entry_rating_half": level_entry_rating_half,
            "level_entry_rating_null": level_entry_rating_null,
            "wide_door_rating_full": wide_door_rating_full,
            "wide_door_rating_half": wide_door_rating_half,
            "wide_door_rating_null": wide_door_rating_null,
            "accessible_table_rating_full": accessible_table_rating_full,
            "accessible_table_rating_half": accessible_table_rating_half,
            "accessible_table_rating_null": accessible_table_rating_null,
            "accessible_restroom_rating_full": accessible_restroom_rating_full,
            "accessible_restroom_rating_half": accessible_restroom_rating_half,
            "accessible_restroom_rating_null": accessible_restroom_rating_null,
            "accessible_path_rating_full": accessible_path_rating_full,
            "accessible_path_rating_half": accessible_path_rating_half,
            "accessible_path_rating_null": accessible_path_rating_null,
            "comment_form": comment_form,
            "is_favorite": isFavorite,
        }
        return render(request, "restaurants/details.html", context)


@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url="/", redirect_field_name=None)
def write_review_view(request, business_id):
    # ImageFormSet = modelformset_factory(Images,
    # form=ImageForm, extra=3)
    if request.user.is_user:
        if request.method == "POST":
            review_form = ReviewPostForm(request.POST, request.FILES)
            # formset = ImageFormSet(request.POST, request.FILES,
            #    queryset=Images.objects.none())
            restaurant_instance = Restaurant.objects.get(business_id=business_id)
            # formset = ImageFormset(request.POST or None, request.FILES or None)
            if review_form.is_valid():
                temp = review_form.save(commit=False)
                temp.user = request.user
                temp.restaurant = restaurant_instance
                review_form.save()
                # for form in formset.cleaned_data:
                #     image = form.get('image')
                #     photo = Images(post=temp, image=image)
                #     photo.save()
                # messages.success(request,
                #                 "Posted!")
                # else:
                #     print(review_form.errors, formset.errors)
                return redirect("accessible_restaurant:detail", business_id)
        else:

            review_form = ReviewPostForm(request.POST)
            # formset = ImageFormSet(queryset=Images.objects.none())
            restaurant_instance = Restaurant.objects.get(business_id=business_id)
        context = {
            "user": request.user,
            "restaurant": restaurant_instance,
            "review_form": review_form,
            # "formset":formset,
        }
        return render(request, "review/writeReview.html", context)
    else:
        messages.warning(
            request,
            f'{"Sorry, as a restaurant user, you can not write reviews. "}',
        )
        return redirect("accessible_restaurant:detail", business_id)


@login_required
@user_passes_test(lambda u: not u.is_superuser, login_url="/", redirect_field_name=None)
def add_comment_view(request, business_id, review_id):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        review = Review.objects.get(id=review_id)
        user = request.user

        # print(review.restaurant.user)
        if user.is_restaurant:
            if (
                review.restaurant.user is None
                or request.user.id != review.restaurant.user.id
            ):
                messages.warning(
                    request,
                    f'{"Sorry, as a restaurant user, you can only make comments under your own restaurants and this one is not yours. "}',
                )
                return redirect("accessible_restaurant:detail", business_id)

        if comment_form.is_valid():
            temp_form = comment_form.save(commit=False)
            temp_form.user = user
            temp_form.review = review
            temp_form.save()
            messages.success(request, f'{"Your comment is successfully made!"}')
            return redirect("accessible_restaurant:detail", business_id)

    else:
        comment_form = CommentForm()

    context = {
        "comment_form": comment_form,
    }
    # TODO: add a page for writing comments or embed the comment form under each review
    return render(request, "review/write_review.html", context)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def user_detail_view(request, user):
    response_info = get_public_user_detail(user)
    response_review = get_user_reviews(user)
    response_favorite = get_user_favorite(user)
    star_list = get_star_list()
    for review in response_review:
        r_full, r_half, r_null = star_list[float(review["rating"])]
        review["full"] = r_full
        review["half"] = r_half
        review["null"] = r_null

    for restaurant in response_favorite:
        full, half, null = star_list[float(restaurant["rating"])]
        restaurant["full"] = full
        restaurant["half"] = half
        restaurant["null"] = null

    context = {
        "username": response_info.get("username"),
        "email": response_info.get("email"),
        "first_name": response_info.get("first_name"),
        "last_name": response_info.get("last_name"),
        "address": response_info.get("address"),
        "phone": response_info.get("phone"),
        "zip_code": response_info.get("zip_code"),
        "state": response_info.get("state"),
        "city": response_info.get("city"),
        "photo": response_info.get("photo"),
        "user_review": response_review,
        "user_favorite": response_favorite,
    }
    return render(request, "publicface/public_profile.html", context)


def faq_view(request):
    if request.method == "GET":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.data.get("Subject")
            from_email = form.data.get("Email")
            message = form.data.get("Message")
            whole_message = render_to_string(
                "accounts/request_received.html",
                {
                    "subject": subject,
                    "message": message,
                },
            )
            try:
                send_mail(
                    "Thank you for your feedback",
                    whole_message,
                    "nyc.accessible.rest@gmail.com",
                    [from_email],
                )
                messages.success(
                    request, f'{"Your request has been sent successfully"}'
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return redirect("accessible_restaurant:faq")

    faq_content = FAQ.objects.all()
    context = {
        "faq_content": faq_content,
        "form": form,
    }
    return render(request, "faq/faq_contact.html", context)
