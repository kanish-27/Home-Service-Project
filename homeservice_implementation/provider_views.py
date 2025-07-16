@login_required
def provider_dashboard(request):
    """Dashboard for service providers"""
    if request.user.user_type != 'provider':
        return redirect('user_dashboard')

    # Get provider's services
    provider_services = Service.objects.filter(
        provider=request.user
    ).select_related('category')

    # Get provider's bookings
    provider_bookings = Booking.objects.filter(
        provider=request.user
    ).select_related('service', 'customer').order_by('-created_at')[:5]

    # Get statistics
    total_bookings = Booking.objects.filter(provider=request.user).count()
    total_earnings = Booking.objects.filter(
        provider=request.user,
        is_paid=True
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'provider_services': provider_services,
        'provider_bookings': provider_bookings,
        'total_bookings': total_bookings,
        'total_earnings': total_earnings,
        'is_provider_dashboard': True,
    }
    return render(request, 'dashboards/provider_dashboard.html', context)

@login_required
def servicer_dashboard(request):
    """Dashboard for servicers to manage service completion using invoice ID"""
    if request.user.user_type != 'provider':
        return redirect('user_dashboard')

    try:
        # Get confirmed bookings assigned to this provider that need service completion
        confirmed_bookings = []

        # Try MongoDB first for better compatibility
        try:
            import pymongo
            from django.conf import settings
            from bson import ObjectId

            client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]

            # Get all admin-approved bookings (ready for service completion by any servicer)
            booking_docs = db['services_booking'].find({
                'status': 'confirmed'  # All admin approved bookings
            }).sort('booking_date', -1)

            for booking_doc in booking_docs:
                # Get invoice for this booking
                invoice_doc = db['services_invoice'].find_one({
                    'booking_id': booking_doc['_id']
                })

                if not invoice_doc:
                    # Create invoice if doesn't exist
                    from datetime import datetime
                    invoice_doc = {
                        'booking_id': booking_doc['_id'],
                        'invoice_number': f"INV-{str(booking_doc['_id'])[:8].upper()}",
                        'generated_at': datetime.now(),
                        'subtotal': float(booking_doc.get('total_amount', 0)),
                        'tax_amount': float(booking_doc.get('total_amount', 0)) * 0.18,
                        'total_amount': float(booking_doc.get('total_amount', 0)) * 1.18
                    }
                    db['services_invoice'].insert_one(invoice_doc)

                # Get customer info
                customer = User.objects.get(id=booking_doc['customer_id'])

                confirmed_bookings.append({
                    'booking_id': str(booking_doc['_id']),
                    'invoice_number': invoice_doc['invoice_number'],
                    'customer_name': customer.get_full_name(),
                    'customer_email': customer.email,
                    'customer_phone': booking_doc.get('phone_number', ''),
                    'service_name': booking_doc.get('notes', 'Service'),
                    'booking_date': booking_doc.get('booking_date'),
                    'address': booking_doc.get('address', ''),
                    'total_amount': booking_doc.get('total_amount', 0),
                    'status': booking_doc.get('status', 'confirmed'),
                    'special_instructions': booking_doc.get('special_instructions', ''),
                })

        except Exception as mongo_error:
            print(f"MongoDB query failed, using Django ORM: {mongo_error}")

            # Fallback to Django ORM - Get all admin-approved bookings
            bookings = Booking.objects.filter(
                status='confirmed'  # All admin approved bookings
            ).select_related('customer').order_by('-booking_date')

            for booking in bookings:
                # Get or create invoice
                from services.models import Invoice
                invoice, created = Invoice.objects.get_or_create(
                    booking=booking,
                    defaults={
                        'subtotal': booking.total_amount,
                        'tax_amount': booking.total_amount * 0.18,
                        'total_amount': booking.total_amount * 1.18,
                    }
                )

                confirmed_bookings.append({
                    'booking_id': str(booking.id),
                    'invoice_number': invoice.invoice_number,
                    'customer_name': booking.customer.get_full_name(),
                    'customer_email': booking.customer.email,
                    'customer_phone': booking.phone_number,
                    'service_name': getattr(booking.service, 'name', 'Service'),
                    'booking_date': booking.booking_date,
                    'address': booking.address,
                    'total_amount': booking.total_amount,
                    'status': booking.status,
                    'special_instructions': getattr(booking, 'special_instructions', ''),
                })

        # Get statistics
        total_assigned = len(confirmed_bookings)

        # Count completed services (try MongoDB first, then Django ORM)
        try:
            import pymongo
            client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]
            completed_count = db['services_booking'].count_documents({'status': 'completed'})
        except:
            completed_count = Booking.objects.filter(status='completed').count()

        context = {
            'confirmed_bookings': confirmed_bookings,
            'total_assigned': total_assigned,
            'completed_count': completed_count,
            'is_servicer_dashboard': True,
            'provider_name': request.user.get_full_name(),
        }

    except Exception as e:
        print(f"Error in servicer dashboard: {e}")
        context = {
            'confirmed_bookings': [],
            'total_assigned': 0,
            'completed_count': 0,
            'is_servicer_dashboard': True,
            'provider_name': request.user.get_full_name(),
            'error_message': 'Unable to load bookings at this time.'
        }

    return render(request, 'dashboards/servicer_dashboard.html', context)

@login_required
def update_service_status(request):
    """Update service status using invoice ID"""
    if request.method != 'POST':
        return redirect('servicer_dashboard')

    if request.user.user_type != 'provider':
        return redirect('user_dashboard')

    invoice_id = request.POST.get('invoice_id')
    new_status = request.POST.get('status')

    if not invoice_id or new_status not in ['completed', 'rejected']:
        messages.error(request, 'Invalid request parameters.')
        return redirect('servicer_dashboard')

    try:
        # Try MongoDB first
        try:
            import pymongo
            from django.conf import settings
            from bson import ObjectId
            from datetime import datetime

            client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]

            # Find invoice by invoice number
            invoice_doc = db['services_invoice'].find_one({
                'invoice_number': invoice_id
            })

            if not invoice_doc:
                messages.error(request, f'Invoice {invoice_id} not found.')
                return redirect('servicer_dashboard')

            # Get booking (any servicer can update any confirmed booking)
            booking_doc = db['services_booking'].find_one({
                '_id': invoice_doc['booking_id'],
                'status': 'confirmed'  # Only allow updates to confirmed bookings
            })

            if not booking_doc:
                messages.error(request, 'Booking not found or not in confirmed status.')
                return redirect('servicer_dashboard')

            # Update booking status
            update_result = db['services_booking'].update_one(
                {'_id': invoice_doc['booking_id']},
                {
                    '$set': {
                        'status': new_status,
                        'updated_at': datetime.now(),
                        'service_completed_at': datetime.now() if new_status == 'completed' else None,
                        'service_completed_by': request.user.id if new_status == 'completed' else None
                    }
                }
            )

            if update_result.modified_count > 0:
                if new_status == 'completed':
                    messages.success(request, f'Service for invoice {invoice_id} marked as completed successfully!')
                else:
                    messages.success(request, f'Service for invoice {invoice_id} marked as rejected.')
            else:
                messages.error(request, 'Failed to update service status.')

        except Exception as mongo_error:
            print(f"MongoDB update failed, trying Django ORM: {mongo_error}")

            # Fallback to Django ORM
            from services.models import Invoice, Booking

            try:
                invoice = Invoice.objects.get(invoice_number=invoice_id)
                booking = invoice.booking

                if booking.status != 'confirmed':
                    messages.error(request, 'Only confirmed bookings can be updated.')
                    return redirect('servicer_dashboard')

                booking.status = new_status
                booking.save()

                if new_status == 'completed':
                    messages.success(request, f'Service for invoice {invoice_id} marked as completed successfully!')
                else:
                    messages.success(request, f'Service for invoice {invoice_id} marked as rejected.')

            except Invoice.DoesNotExist:
                messages.error(request, f'Invoice {invoice_id} not found.')
            except Exception as orm_error:
                messages.error(request, f'Error updating service status: {orm_error}')

    except Exception as e:
        messages.error(request, f'Error updating service status: {e}')

    return redirect('servicer_dashboard')
