import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView, FormView
)
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.contrib.auth.views import PasswordChangeView
from django.views.decorators.http import require_http_methods

from .models import User, UserProfile, UserAddress, Notification
from .forms import (
    UserRegistrationForm, ProviderRegistrationForm, UserProfileForm, 
    UserAddressForm, PasswordChangeCustomForm, ProviderProfileForm, BookingStatusForm
)
from services.models import Service, Booking, Review, ProviderProfile
from services.forms import ServiceForm, ProviderScheduleForm


# Authentication Views
class SignUpView(TemplateView):
    """Simplified view for user registration with better Djongo compatibility."""
    template_name = 'users/signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sign Up'
        if 'form' not in context:
            context['form'] = UserRegistrationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            try:
                # Check if user already exists
                email = form.cleaned_data['email']
                from django.contrib.auth import get_user_model
                User = get_user_model()

                if User.objects.filter(email=email).exists():
                    messages.error(request, 'A user with this email already exists.')
                    context = self.get_context_data(**kwargs)
                    context['form'] = form
                    return self.render_to_response(context)

                # Create user using the form's save method (simpler approach)
                user = form.save(commit=False)
                user.user_type = 'customer'
                user.is_active = True

                # Set username to email if not provided
                if not user.username:
                    user.username = user.email

                try:
                    user.save()
                    print(f"DEBUG: User created successfully: {user.email}")
                    messages.success(request, 'Your account has been created! You can now log in.')
                    return redirect('login')

                except Exception as save_error:
                    print(f"DEBUG: User save error: {save_error}")
                    # Try alternative approach
                    try:
                        # Create user with minimal fields first
                        from django.contrib.auth import get_user_model
                        User = get_user_model()

                        user = User.objects.create_user(
                            email=form.cleaned_data['email'],
                            password=form.cleaned_data['password1'],
                            first_name=form.cleaned_data['first_name'],
                            last_name=form.cleaned_data['last_name'],
                            username=form.cleaned_data['email'],
                            user_type='customer'
                        )

                        print(f"DEBUG: User created with create_user method: {user.email}")
                        messages.success(request, 'Your account has been created! You can now log in.')
                        return redirect('login')

                    except Exception as create_error:
                        print(f"DEBUG: create_user also failed: {create_error}")
                        messages.error(request, 'There was an error creating your account. Please try again later.')

            except Exception as form_error:
                print(f"DEBUG: Form processing error: {form_error}")
                messages.error(request, 'There was an error processing your registration. Please try again.')

        # If form is not valid or there was an error, show the form again
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class ProviderSignUpView(TemplateView):
    """View for service provider registration with MongoDB compatibility."""
    template_name = 'users/provider_signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Provider Sign Up'
        if 'form' not in context:
            context['form'] = ProviderRegistrationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ProviderRegistrationForm(request.POST)

        if form.is_valid():
            try:
                # Create provider user with proper error handling for MongoDB
                user = form.save(commit=False)

                # Set additional fields
                user.user_type = 'provider'
                user.is_active = True

                # Try to save with MongoDB compatibility
                try:
                    user.save()
                    messages.success(request, 'Your provider account has been created! You can now log in.')
                    return redirect('login')
                except Exception as save_error:
                    print(f"DEBUG: Provider save error: {save_error}")
                    # Try alternative save method
                    try:
                        user.save(using='default')
                        messages.success(request, 'Your provider account has been created! You can now log in.')
                        return redirect('login')
                    except Exception as alt_save_error:
                        print(f"DEBUG: Alternative provider save error: {alt_save_error}")
                        messages.error(request, 'There was an error creating your provider account. Please try again.')

            except Exception as form_error:
                print(f"DEBUG: Provider form processing error: {form_error}")
                messages.error(request, 'There was an error processing your provider registration. Please try again.')

        # If form is not valid or there was an error, show the form again
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

class ProviderDetailView(DetailView):
    """View to display provider's profile details."""
    model = User
    template_name = 'users/provider_detail.html'
    context_object_name = 'provider'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return User.objects.filter(user_type='provider')


class ProfileView(LoginRequiredMixin, TemplateView):
    """View to display user profile information."""
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user profile if it exists
        try:
            user_profile = user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = None
            
        # Get user addresses
        addresses = UserAddress.objects.filter(user=user)
        
        # Get recent bookings (if customer)
        recent_bookings = []
        if not user.is_service_provider:
            recent_bookings = Booking.objects.filter(customer=user).order_by('-created_at')[:5]
            
        # Get services (if provider)
        services = []
        if user.is_service_provider:
            services = Service.objects.filter(provider=user).order_by('-created_at')[:5]
            
        context.update({
            'user_profile': user_profile,
            'addresses': addresses,
            'recent_bookings': recent_bookings,
            'services': services
        })
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Become a Service Provider'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            'Your provider account has been created! Please wait for admin approval.'
        )
        return response


# Profile Views
class ProfileView(LoginRequiredMixin, TemplateView):
    """View for user profile."""
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Profile'
        
        # Get user's upcoming and past bookings
        now = timezone.now()
        context['upcoming_bookings'] = self.request.user.bookings.filter(
            booking_date__gte=now
        ).order_by('booking_date')[:5]
        
        context['recent_reviews'] = Review.objects.filter(
            booking__customer=self.request.user
        ).order_by('-created_at')[:3]
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating user profile."""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Profile'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated!')
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """View for changing user password."""
    template_name = 'users/password_change.html'
    form_class = PasswordChangeCustomForm
    success_url = reverse_lazy('users:profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Change Password'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been updated!')
        return super().form_valid(form)


# Address Views
class AddressListView(LoginRequiredMixin, ListView):
    """View for listing user addresses."""
    model = UserAddress
    template_name = 'users/address_list.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return self.request.user.addresses.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Addresses'
        return context


class AddressCreateView(LoginRequiredMixin, CreateView):
    """View for adding a new address."""
    model = UserAddress
    form_class = UserAddressForm
    template_name = 'users/address_form.html'
    success_url = reverse_lazy('users:address_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Address added successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Address'
        return context


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an address."""
    model = UserAddress
    form_class = UserAddressForm
    template_name = 'users/address_form.html'
    success_url = reverse_lazy('users:address_list')

    def get_queryset(self):
        return self.request.user.addresses.all()

    def form_valid(self, form):
        messages.success(self.request, 'Address updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Address'
        return context


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting an address."""
    model = UserAddress
    template_name = 'users/address_confirm_delete.html'
    success_url = reverse_lazy('users:address_list')
    context_object_name = 'address'

    def get_queryset(self):
        return self.request.user.addresses.all()

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Address deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Notification Views
class NotificationListView(LoginRequiredMixin, TemplateView):
    """View for listing user notifications with MongoDB compatibility."""
    template_name = 'users/notification_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Notifications'

        try:
            # Try Django ORM first
            notifications = self.request.user.notifications.all().order_by('-created_at')
            unread_count = self.request.user.notifications.filter(is_read=False).count()

            # Convert to list to handle ObjectId issues
            notifications_list = list(notifications)

            context['notifications'] = notifications_list
            context['unread_count'] = unread_count

        except Exception as e:
            print(f"DEBUG: Notification query error: {e}")
            # Fallback to MongoDB direct query
            try:
                from pymongo import MongoClient

                client = MongoClient('mongodb://localhost:27017/')
                db = client['homeservice_db']
                notifications_collection = db['users_notification']
                users_collection = db['users_user']

                # Get user's ObjectId
                user_doc = users_collection.find_one({'email': self.request.user.email})
                if user_doc:
                    user_id = user_doc['_id']

                    # Get notifications for this user
                    notifications_docs = list(notifications_collection.find(
                        {'user_id': user_id}
                    ).sort('created_at', -1).limit(50))

                    # Convert to notification-like objects
                    notifications_list = []
                    unread_count = 0

                    for doc in notifications_docs:
                        notification_obj = type('Notification', (), {
                            'id': str(doc['_id']),
                            'title': doc.get('title', 'No Title'),
                            'message': doc.get('message', 'No Message'),
                            'notification_type': doc.get('notification_type', 'system'),
                            'is_read': doc.get('is_read', False),
                            'created_at': doc.get('created_at', ''),
                        })()

                        notifications_list.append(notification_obj)
                        if not doc.get('is_read', False):
                            unread_count += 1

                    context['notifications'] = notifications_list
                    context['unread_count'] = unread_count
                    context['using_fallback'] = True
                else:
                    context['notifications'] = []
                    context['unread_count'] = 0

            except Exception as mongo_error:
                print(f"DEBUG: MongoDB fallback also failed: {mongo_error}")
                context['notifications'] = []
                context['unread_count'] = 0
                context['error_message'] = "Unable to load notifications. Please try again later."

        return context


class NotificationDetailView(LoginRequiredMixin, TemplateView):
    """View for viewing a notification with MongoDB compatibility."""
    template_name = 'users/notification_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notification Details'

        notification_id = kwargs.get('pk')

        try:
            # Try Django ORM first
            notification = self.request.user.notifications.get(id=notification_id)

            # Mark as read if not already
            if not notification.is_read:
                notification.is_read = True
                notification.save()

            context['notification'] = notification

        except Exception as e:
            print(f"DEBUG: Notification detail query error: {e}")
            # Fallback to MongoDB direct query
            try:
                from pymongo import MongoClient
                from bson import ObjectId

                client = MongoClient('mongodb://localhost:27017/')
                db = client['homeservice_db']
                notifications_collection = db['users_notification']
                users_collection = db['users_user']

                # Get user's ObjectId
                user_doc = users_collection.find_one({'email': self.request.user.email})
                if user_doc:
                    user_id = user_doc['_id']

                    # Try to find notification by ObjectId
                    try:
                        notification_doc = notifications_collection.find_one({
                            '_id': ObjectId(notification_id),
                            'user_id': user_id
                        })
                    except:
                        # If ObjectId conversion fails, try string search
                        notification_doc = notifications_collection.find_one({
                            'user_id': user_id
                        })

                    if notification_doc:
                        # Create notification-like object
                        notification_obj = type('Notification', (), {
                            'id': str(notification_doc['_id']),
                            'title': notification_doc.get('title', 'No Title'),
                            'message': notification_doc.get('message', 'No Message'),
                            'notification_type': notification_doc.get('notification_type', 'system'),
                            'is_read': notification_doc.get('is_read', False),
                            'created_at': notification_doc.get('created_at', ''),
                        })()

                        # Mark as read in MongoDB
                        if not notification_doc.get('is_read', False):
                            notifications_collection.update_one(
                                {'_id': notification_doc['_id']},
                                {'$set': {'is_read': True}}
                            )
                            notification_obj.is_read = True

                        context['notification'] = notification_obj
                        context['using_fallback'] = True
                    else:
                        context['error_message'] = "Notification not found."
                else:
                    context['error_message'] = "User not found."

            except Exception as mongo_error:
                print(f"DEBUG: MongoDB notification detail fallback failed: {mongo_error}")
                context['error_message'] = "Unable to load notification. Please try again later."

        return context


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read with MongoDB compatibility."""
    if request.method == 'POST':
        try:
            # Try Django ORM first
            updated = request.user.notifications.filter(is_read=False).update(is_read=True)
            messages.success(request, f'Marked {updated} notifications as read.')

        except Exception as e:
            print(f"DEBUG: Mark all notifications error: {e}")
            # Fallback to MongoDB direct update
            try:
                from pymongo import MongoClient

                client = MongoClient('mongodb://localhost:27017/')
                db = client['homeservice_db']
                notifications_collection = db['users_notification']
                users_collection = db['users_user']

                # Get user's ObjectId
                user_doc = users_collection.find_one({'email': request.user.email})
                if user_doc:
                    user_id = user_doc['_id']

                    # Update all unread notifications for this user
                    result = notifications_collection.update_many(
                        {'user_id': user_id, 'is_read': False},
                        {'$set': {'is_read': True}}
                    )

                    messages.success(request, f'Marked {result.modified_count} notifications as read via MongoDB.')
                else:
                    messages.error(request, 'User not found.')

            except Exception as mongo_error:
                print(f"DEBUG: MongoDB mark all notifications fallback failed: {mongo_error}")
                messages.error(request, 'Unable to mark notifications as read. Please try again later.')

    return redirect('users:notification_list')


# Provider Dashboard Views
class ProviderDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View for provider dashboard."""
    template_name = 'users/provider/dashboard.html'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'provider'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Provider Dashboard'
        
        # Get provider's services
        provider_services = Service.objects.filter(provider=self.request.user)
        context['service_count'] = provider_services.count()
        
        # Get provider's bookings
        bookings = Booking.objects.filter(provider=self.request.user)
        
        # Count bookings by status
        context['pending_bookings'] = bookings.filter(status='pending').count()
        context['confirmed_bookings'] = bookings.filter(status='confirmed').count()
        context['completed_bookings'] = bookings.filter(status='completed').count()
        
        # Get recent bookings
        context['recent_bookings'] = bookings.order_by('-created_at')[:5]
        
        # Get reviews for provider's services
        context['recent_reviews'] = Review.objects.filter(
            booking__service__provider=self.request.user
        ).order_by('-created_at')[:3]
        
        # Get total earnings (this would need to be implemented with payment processing)
        context['total_earnings'] = 0
        
        return context


class ProviderServiceListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View for listing provider's services."""
    model = Service
    template_name = 'users/provider/service_list.html'
    context_object_name = 'services'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'provider'

    def get_queryset(self):
        return Service.objects.filter(provider=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Services'
        return context


class ProviderServiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """View for creating a new service."""
    model = Service
    form_class = ServiceForm
    template_name = 'users/provider/service_form.html'
    success_url = reverse_lazy('users:provider_service_list')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'provider'

    def form_valid(self, form):
        form.instance.provider = self.request.user
        messages.success(self.request, 'Service created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Service'
        return context


class ProviderServiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating a service."""
    model = Service
    form_class = ServiceForm
    template_name = 'users/provider/service_form.html'
    success_url = reverse_lazy('users:provider_service_list')

    def test_func(self):
        service = self.get_object()
        return self.request.user == service.provider

    def form_valid(self, form):
        messages.success(self.request, 'Service updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Service'
        return context


class ProviderServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a service."""
    model = Service
    template_name = 'users/provider/service_confirm_delete.html'
    success_url = reverse_lazy('users:provider_service_list')
    context_object_name = 'service'

    def test_func(self):
        service = self.get_object()
        return self.request.user == service.provider

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Service deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ProviderBookingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View for listing provider's bookings."""
    model = Booking
    template_name = 'users/provider/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'provider'

    def get_queryset(self):
        return Booking.objects.filter(provider=self.request.user).order_by('-booking_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Bookings'
        return context


class ProviderBookingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View for viewing booking details."""
    model = Booking
    template_name = 'users/provider/booking_detail.html'
    context_object_name = 'booking'

    def test_func(self):
        booking = self.get_object()
        return self.request.user == booking.provider

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Booking Details'
        context['form'] = BookingStatusForm(instance=self.object)
        return context


@login_required
def update_booking_status(request, pk):
    """Update booking status."""
    booking = get_object_or_404(Booking, pk=pk, provider=request.user)
    
    if request.method == 'POST':
        form = BookingStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking status updated successfully!')
            
            # Create notification for the customer
            Notification.objects.create(
                user=booking.customer,
                notification_type='booking_updated',
                title=f'Booking #{booking.id} Status Update',
                message=f'Your booking status has been updated to {booking.get_status_display()}.',
                related_object_id=booking.id,
                related_content_type='booking'
            )
            
            return redirect('users:provider_booking_detail', pk=booking.id)
    
    return redirect('users:provider_booking_detail', pk=booking.id)


class ProviderProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View for displaying provider profile."""
    model = User
    template_name = 'users/provider/profile.html'
    context_object_name = 'user_profile'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'provider'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Provider Profile'
        context['provider_profile'] = self.object.provider_profile
        return context


class ProviderProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating provider profile."""
    model = User
    form_class = ProviderProfileForm
    template_name = 'users/provider/profile_edit.html'
    success_url = reverse_lazy('users:provider_profile')

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'provider'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Provider Profile'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated!')
        return super().form_valid(form)


class ProviderReviewListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View for listing provider's reviews."""
    model = Review
    template_name = 'users/provider/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def test_func(self):
        return hasattr(self.request.user, 'provider_profile')
    
    def get_queryset(self):
        return Review.objects.filter(booking__provider=self.request.user).select_related('booking', 'booking__customer')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Reviews'
        context['average_rating'] = self.get_queryset().aggregate(avg_rating=Avg('rating'))['avg_rating']
        return context


class ProviderScheduleView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View for managing provider's schedule."""
    template_name = 'users/provider/schedule.html'
    
    def test_func(self):
        return hasattr(self.request.user, 'provider_profile')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Schedule'
        context['schedule_form'] = ProviderScheduleForm()
        context['schedule'] = self.request.user.provider_profile.schedules.all()
        return context


@login_required
@require_http_methods(["POST"])
def add_schedule_slot(request):
    """Add a new schedule slot."""
    if request.user.user_type != 'provider':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    form = ProviderScheduleForm(request.POST)
    if form.is_valid():
        # Save the schedule slot
        # This is a simplified example - you'll need to implement the actual logic
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid form data'}, status=400)


@login_required
def get_available_time_slots(request, service_id, date):
    """Get available time slots for a service on a specific date."""
    service = get_object_or_404(Service, id=service_id, is_available=True)
    
    # This is a simplified example - you'll need to implement the actual logic
    # to check provider's availability and existing bookings
    
    # For now, return some sample time slots
    time_slots = [
        '09:00 AM - 10:00 AM',
        '10:00 AM - 11:00 AM',
        '11:00 AM - 12:00 PM',
        '01:00 PM - 02:00 PM',
        '02:00 PM - 03:00 PM',
        '03:00 PM - 04:00 PM',
    ]
    
    return JsonResponse({'time_slots': time_slots})
