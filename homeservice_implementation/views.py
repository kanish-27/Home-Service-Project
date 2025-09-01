from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from services.models import Service, ServiceCategory, Booking
from users.models import User

def home(request):
    """Home page view - redirects based on user type if logged in"""
    if request.user.is_authenticated:
        if request.user.user_type == 'admin' or request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.user_type == 'provider':
            return redirect('servicer_dashboard')
        else:
            return redirect('user_dashboard')

    # For anonymous users, show the regular home page
    return render(request, 'home.html')

@login_required
def user_dashboard(request):
    """Dashboard for regular users to browse and book services"""

    # Get sample featured services (top 6 services)
    featured_services = [
        {
            'id': 1,
            'name': 'Electrical Installation',
            'description': 'Professional installation of electrical systems in your home or office. Includes wiring, outlets, switches, and circuit breakers.',
            'price': 2500,
            'duration': 3,
            'average_rating': 4.5,
            'review_count': 12,
            'category': {'name': 'Electrical'},
            'provider': {'user': {'get_full_name': 'Rajesh Kumar'}},
            'image': None
        },
        {
            'id': 4,
            'name': 'Pipe Repair',
            'description': 'Professional repair of leaking or damaged pipes. Includes copper, PVC, and PEX pipe repairs.',
            'price': 1200,
            'duration': 2,
            'average_rating': 4.6,
            'review_count': 10,
            'category': {'name': 'Plumbing'},
            'provider': {'user': {'get_full_name': 'Suresh Patel'}},
            'image': None
        },
        {
            'id': 7,
            'name': 'Deep Cleaning',
            'description': 'Comprehensive deep cleaning service for your entire home. Includes all rooms and surfaces.',
            'price': 3500,
            'duration': 4,
            'average_rating': 4.8,
            'review_count': 22,
            'category': {'name': 'Cleaning'},
            'provider': {'user': {'get_full_name': 'Sunita Joshi'}},
            'image': None
        },
        {
            'id': 10,
            'name': 'Furniture Repair',
            'description': 'Professional furniture repair and restoration services.',
            'price': 1800,
            'duration': 3,
            'average_rating': 4.7,
            'review_count': 11,
            'category': {'name': 'Carpentry'},
            'provider': {'user': {'get_full_name': 'Manoj Kumar'}},
            'image': None
        },
        {
            'id': 14,
            'name': 'AC Repair',
            'description': 'Professional air conditioning repair and maintenance services.',
            'price': 2500,
            'duration': 2,
            'average_rating': 4.8,
            'review_count': 19,
            'category': {'name': 'Appliance Repair'},
            'provider': {'user': {'get_full_name': 'Rohit Sharma'}},
            'image': None
        },
        {
            'id': 20,
            'name': 'CCTV Installation',
            'description': 'Professional CCTV camera installation and setup.',
            'price': 5500,
            'duration': 4,
            'average_rating': 4.7,
            'review_count': 12,
            'category': {'name': 'Security'},
            'provider': {'user': {'get_full_name': 'Ajay Kumar'}},
            'image': None
        }
    ]

    # Get sample categories
    categories = [
        {'name': 'Electrical', 'slug': 'electrical'},
        {'name': 'Plumbing', 'slug': 'plumbing'},
        {'name': 'Cleaning', 'slug': 'cleaning'},
        {'name': 'Carpentry', 'slug': 'carpentry'},
        {'name': 'Painting', 'slug': 'painting'},
        {'name': 'Appliance Repair', 'slug': 'appliance-repair'},
    ]

    context = {
        'featured_services': featured_services,
        'categories': categories,
        'user_bookings': [],
        'is_user_dashboard': True,
        'dashboard_message': 'Welcome to your dashboard! Browse our featured services below.'
    }

    # Try to get real user bookings from database if available
    try:
        from services.models import Booking
        if request.user.is_authenticated:
            # Get all user bookings for recent bookings display
            try:
                all_bookings = list(Booking.objects.filter(customer=request.user).order_by('-booking_date')[:3])
            except:
                try:
                    all_bookings = list(Booking.objects.filter(customer=request.user).order_by('-id')[:3])
                except:
                    all_bookings = list(Booking.objects.filter(customer=request.user)[:3])

            # Get confirmed bookings count for the dashboard counter
            try:
                confirmed_bookings_count = Booking.objects.filter(
                    customer=request.user,
                    status='confirmed'
                ).count()
            except:
                confirmed_bookings_count = 0

            context['user_bookings'] = all_bookings
            context['confirmed_bookings_count'] = confirmed_bookings_count

            if all_bookings:
                print(f"Found {len(all_bookings)} total bookings for user {request.user.email}")
            print(f"Found {confirmed_bookings_count} confirmed bookings for user {request.user.email}")
    except Exception as e:
        # Continue with empty bookings if database error
        print(f"Bookings data error (non-critical): {e}")
        context['confirmed_bookings_count'] = 0
        import traceback
        traceback.print_exc()

    return render(request, 'dashboards/user_dashboard.html', context)

@login_required
def admin_dashboard(request):
    """Dashboard for admins to manage services and view bookings"""
    if not (request.user.user_type == 'admin' or request.user.is_superuser):
        return redirect('user_dashboard')

    try:
        # Get statistics
        total_services = Service.objects.count()
        total_bookings = Booking.objects.count()

        # Calculate total revenue from confirmed/completed AND paid bookings only
        # Using manual approach due to Djongo boolean field query issues
        try:
            revenue_data = Booking.objects.filter(
                status__in=['confirmed', 'completed'],
                is_paid=True
            ).aggregate(total=Sum('total_amount'))
            total_revenue = revenue_data['total'] if revenue_data['total'] is not None else 0
        except Exception as e:
            # Fallback: Manual calculation for MongoDB/Djongo compatibility
            print(f"DEBUG: Using manual revenue calculation due to query error: {e}")
            confirmed_bookings = Booking.objects.filter(status__in=['confirmed', 'completed'])
            total_revenue = 0
            for booking in confirmed_bookings:
                try:
                    if hasattr(booking, 'is_paid') and booking.is_paid:
                        total_revenue += float(booking.total_amount or 0)
                except Exception:
                    continue

        # If no total_amount, calculate from service prices for confirmed+paid bookings
        if total_revenue == 0:
            try:
                paid_confirmed_bookings = Booking.objects.filter(
                    status__in=['confirmed', 'completed'],
                    is_paid=True
                ).select_related('service')
                total_revenue = sum(booking.service.price for booking in paid_confirmed_bookings)
            except Exception:
                # Manual fallback for service price calculation
                confirmed_bookings = Booking.objects.filter(status__in=['confirmed', 'completed']).select_related('service')
                for booking in confirmed_bookings:
                    try:
                        if hasattr(booking, 'is_paid') and booking.is_paid:
                            total_revenue += float(booking.service.price or 0)
                    except Exception:
                        continue

        pending_bookings = Booking.objects.filter(status='pending').count()

        # Recent bookings
        recent_bookings = Booking.objects.select_related(
            'service', 'customer', 'provider'
        ).order_by('-created_at')[:5]

        # Popular services
        popular_services = Service.objects.annotate(
            booking_count=Count('booking')
        ).order_by('-booking_count')[:5]

    except Exception as e:
        # Handle database errors gracefully
        total_services = 0
        total_bookings = 0
        total_revenue = 0
        pending_bookings = 0
        recent_bookings = []
        popular_services = []

    context = {
        'total_services': total_services,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
        'popular_services': popular_services,
        'is_admin_dashboard': True,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

def about(request):
    """About page view"""
    context = {
        'page_title': 'About Us',
        'company_name': 'HomeService',
        'founded_year': '2024',
        'team_size': '50+',
        'services_count': '100+',
        'customers_served': '1000+',
    }
    return render(request, 'about.html', context)

def contact(request):
    """Contact page view"""
    context = {
        'page_title': 'Contact Us',
        'company_name': 'HomeService',
        'contact_email': 'kanishkrishna.jp2024@cse.ac.in',
        'contact_phone': '7708750455',
        'office_address': 'HomeService Office, Tech City, India',
        'business_hours': 'Monday - Saturday: 9:00 AM - 6:00 PM',
    }
    return render(request, 'contact.html', context)
