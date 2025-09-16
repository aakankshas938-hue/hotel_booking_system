from django.contrib import admin
from .models import RoomType, Room, Booking, Review

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_night', 'capacity']
    list_filter = ['capacity']
    search_fields = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'is_available']
    list_filter = ['room_type', 'is_available']
    search_fields = ['room_number']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'room', 'check_in_date', 'check_out_date', 'status', 'total_price']
    list_filter = ['status', 'check_in_date', 'check_out_date']
    search_fields = ['customer__username', 'room__room_number']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['booking__id']
    readonly_fields = ['created_at']