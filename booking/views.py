from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Room, RoomType, Booking, Review
from .forms import BookingForm, ReviewForm
import datetime

# Ensure this home view exists
def home(request):
    room_types = RoomType.objects.all()
    return render(request, 'booking/home.html', {'room_types': room_types})

# ... keep all your other views (room_list, book_room, etc.) ...
def room_list(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    guests = request.GET.get('guests', 1)

    rooms = Room.objects.filter(is_available=True)

    if check_in and check_out:
        try:
            check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()
            
            # Filter rooms that are not booked for the selected dates
            booked_rooms = Booking.objects.filter(
                Q(check_in_date__lt=check_out_date) & Q(check_out_date__gt=check_in_date) &
                Q(status__in=['confirmed', 'pending'])
            ).values_list('room_id', flat=True)
            
            rooms = rooms.exclude(id__in=booked_rooms)
            rooms = rooms.filter(room_type__capacity__gte=int(guests))
            
        except ValueError:
            messages.error(request, "Invalid date format.")

    return render(request, 'booking/room_list.html', {
        'rooms': rooms,
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests
    })

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_available=True)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.room = room
            
            # Calculate total price
            nights = (booking.check_out_date - booking.check_in_date).days
            booking.total_price = nights * room.room_type.price_per_night
            
            # Set initial status
            booking.status = 'pending'
            
            booking.save()
            messages.success(request, f"Your booking has been submitted successfully! Your booking ID is #{booking.id}.")
            return redirect('booking_success', booking_id=booking.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill check-in and check-out dates from query parameters
        initial = {}
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        guests = request.GET.get('guests', 1)
        
        if check_in and check_out:
            try:
                initial['check_in_date'] = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
                initial['check_out_date'] = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()
                initial['guests'] = int(guests)
            except ValueError:
                pass
        
        form = BookingForm(initial=initial)

    return render(request, 'booking/booking_form.html', {'form': form, 'room': room})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    return render(request, 'booking/booking_success.html', {'booking': booking})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    return render(request, 'booking/booking_detail.html', {'booking': booking})

@login_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)

    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, "You can only update pending or confirmed bookings.")
        return redirect('my_bookings')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            updated_booking = form.save(commit=False)
            
            # Recalculate total price if dates changed
            if (updated_booking.check_in_date != booking.check_in_date or 
                updated_booking.check_out_date != booking.check_out_date):
                nights = (updated_booking.check_out_date - updated_booking.check_in_date).days
                updated_booking.total_price = nights * booking.room.room_type.price_per_night
            
            updated_booking.save()
            messages.success(request, "Your booking has been updated successfully!")
            return redirect('my_bookings')
    else:
        form = BookingForm(instance=booking)
        form.fields['room'].queryset = Room.objects.filter(id=booking.room.id)

    return render(request, 'booking/update_booking.html', {'form': form, 'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)

    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, "You can only cancel pending or confirmed bookings.")
        return redirect('my_bookings')

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Your booking has been cancelled successfully!")
        return redirect('my_bookings')

    return render(request, 'booking/cancel_booking.html', {'booking': booking})

@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)

    # Check if the booking is completed and doesn't already have a review
    if booking.status != 'completed' or hasattr(booking, 'review'):
        messages.error(request, "You can only review completed bookings that don't have a review yet.")
        return redirect('my_bookings')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('my_bookings')
    else:
        form = ReviewForm()

    return render(request, 'booking/add_review.html', {'form': form, 'booking': booking})

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'booking/register.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        # Save the user first
        user = form.save()
        # Then log them in
        login(self.request, user)
        messages.success(self.request, f"Welcome {user.username}! Your account has been created successfully.")
        return redirect('home')