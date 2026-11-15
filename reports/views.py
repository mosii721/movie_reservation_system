from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.db.models import Q,Count
from django.conf import settings
from movies.models import Genre,Movie
from reservations.models import Reservation,ReservationSeat
from showtimes.models import Cinema,Auditorium,Seat,Showtime
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser




# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperUser])
def report(request):
    User = get_user_model()

    total_movies = Movie.objects.all().count()
    active_movies = Movie.objects.filter(is_active=True).count()
    total_cinemas = Cinema.objects.all().count()
    active_cinemas = Cinema.objects.filter(is_active=True).count()
    total_auditoriums = Auditorium.objects.all().count()
    active_auditoriums = Auditorium.objects.filter(is_active=True).count()
    total_seats = Seat.objects.all().count()
    total_showtimes = Showtime.objects.all().count()
    total_customers = User.objects.filter(is_staff=False).count()

    total_reservations = Reservation.objects.all().count()
    confirmed_reservations = Reservation.objects.filter(status='CONFIRMED').count()
    pending_reservations = Reservation.objects.filter(status='PENDING').count()
    cancelled_reservations = Reservation.objects.filter(status='CANCELLED').count()
    total_reserved_seats = ReservationSeat.objects.filter(Q(status='ACTIVE') | Q(status='PENDING')).count()
    cancelled_reserved_seats = ReservationSeat.objects.filter(status='CANCELLED').count()

    reservations = Reservation.objects.all()
    total_amount = Decimal(0.00)
    confirmed_total_amount = Decimal(0.00)
    cancelled_total_amount = Decimal(0.00)

    for reservation in reservations:
        if reservation.total_amount is not None:
            total_amount += reservation.total_amount

            if reservation.status == 'CONFIRMED':
                confirmed_total_amount += reservation.total_amount
            elif reservation.status == 'CANCELLED':
                cancelled_total_amount += reservation.total_amount
    avg_total_amount = Decimal('0.00')

    if total_reservations > 0:
        avg_total_amount = total_amount / total_reservations 

    movie_reservations = Movie.objects.annotate(reservation_count = Count('showtime__reservations'))
    high_reserved_movie = movie_reservations.order_by('-reservation_count').first()
    low_reserved_movie = movie_reservations.order_by('reservation_count').first()
    highest_reserved_movie = 'N/A'
    highest_reserved_movie_count = 0
    lowest_reserved_movie = 'N/A'
    lowest_reserved_movie_count = 0

    if total_movies != 0:
        highest_reserved_movie = high_reserved_movie.title
        highest_reserved_movie_count = high_reserved_movie.reservation_count

        lowest_reserved_movie = low_reserved_movie.title
        lowest_reserved_movie_count = low_reserved_movie.reservation_count

    movies = Movie.objects.all()
    movie_report = []

    for movie in movies:
        total_reservation_per_movie = Reservation.objects.filter(showtime__movie=movie).count()
        movie_report.append({
            'movie': movie.title,
            'reservations': total_reservation_per_movie
        })

    completed_showtimes = Showtime.objects.filter(status='COMPLETED').count()
    cancelled_showtimes = Showtime.objects.filter(status='CANCELLED').count()
    scheduled_showtimes = Showtime.objects.filter(status='SCHEDULED').count()
    showtime_reservations = Showtime.objects.annotate(reservation_counts = Count('reservations'))
    high_reserved_showtime = showtime_reservations.order_by('-reservation_counts').first()
    low_reserved_showtime = showtime_reservations.order_by('reservation_counts').first()

    highest_reserved_showtime = 'N/A'
    highest_reserved_showtime_count = 0
    lowest_reserved_showtime = 'N/A'
    lowest_reserved_showtime_count = 0

    if total_showtimes != 0:
        highest_reserved_showtime= high_reserved_showtime.name
        highest_reserved_showtime_count = high_reserved_showtime.reservation_counts

        lowest_reserved_showtime= low_reserved_showtime.name
        lowest_reserved_showtime_count = low_reserved_showtime.reservation_counts

    
    showtimes = Showtime.objects.all()
    showtime_report = []

    for showtime in showtimes:
        total_seats_per_showtime = Seat.objects.filter(auditorium=showtime.auditorium).count()
        active_reservation_seats_count = ReservationSeat.objects.filter(status='ACTIVE',showtime=showtime).count()
        occupancy_rate_per_showtime = 0

        if total_seats_per_showtime > 0:
            occupancy_rate_per_showtime = (
                active_reservation_seats_count / total_seats_per_showtime
            ) * 100

        showtime_report.append({
            'movie': showtime.movie.title,
            'start_time': showtime.start_time,
            'total_seats': total_seats_per_showtime,
            'booked_seats': active_reservation_seats_count,
            'occupancy_rate': occupancy_rate_per_showtime
        })

    reservations_per_cinema = Cinema.objects.annotate(reservations_cinema= Count('auditoriums__showtime__reservations'))
    most_popular_cinema = reservations_per_cinema.order_by('-reservations_cinema').first()

    cinema_report = []

    for cinema in Cinema.objects.all():
        cinema_showtimes = Showtime.objects.filter(auditorium__cinema=cinema)

        total_capacity = 0

        for showtime in cinema_showtimes:
            total_capacity += Seat.objects.filter(
                auditorium=showtime.auditorium
            ).count()

        booked_seats = ReservationSeat.objects.filter(
            showtime__auditorium__cinema=cinema,
            status__in=['ACTIVE', 'PENDING']
        ).count()

        occupancy_rate = 0

        if total_capacity > 0:
            occupancy_rate = (booked_seats / total_capacity) * 100

        cinema_report.append({
            'cinema': cinema.name,
            'booked_seats': booked_seats,
            'total_capacity': total_capacity,
            'occupancy_rate': occupancy_rate
        })

    one_month_ago = timezone.now() - timedelta(days=30)
    total_registered_customers = User.objects.filter(is_staff=False).count()
    new_customers = User.objects.filter(is_staff=False,created_at__gte = one_month_ago).count()
    customer_reservations = User.objects.annotate(reservations_user = Count('reservations')).filter(is_staff=False)
    customer_with_highest_reservation = customer_reservations.order_by('-reservations_user').first()

    avg_no_of_reservation_per_customer = 0

    if total_customers > 0:
        avg_no_of_reservation_per_customer = total_reservations / total_customers

    cancelled_reservations = Reservation.objects.filter(status='CANCELLED').count()
    cancelled_seats = ReservationSeat.objects.filter(status='CANCELLED').count()
    showtime_cancellations = Showtime.objects.annotate(cancellation_counts = Count('reservations', filter=Q(reservations__status='CANCELLED')))
    high_cancelled_showtime = showtime_cancellations.order_by('-cancellation_counts').first()
    highest_cancelled_showtime = high_cancelled_showtime.name if high_cancelled_showtime else 'N/A'
    highest_cancelled_showtime_count = ( high_cancelled_showtime.cancellation_counts if high_cancelled_showtime else 0)
    cancellation_rate = 0

    if total_reservations > 0:
        cancellation_rate = (cancelled_reservations/total_reservations) * 100
    

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    
    # PDF layout
    
    p.setTitle("Movie Reservation System Report")

    page_width, page_height = p._pagesize
    y = page_height - 50

    # REPORT HEADING
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(page_width / 2, y, "MOVIE RESERVATION SYSTEM")
    y -= 30

    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(page_width / 2, y, "SYSTEM PERFORMANCE REPORT")
    y -= 30

    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Generated: {timezone.localtime().strftime('%d %B %Y, %H:%M')}")
    y -= 20

    generated_by = request.user.username if request.user.is_authenticated else "System"
    p.drawString(50, y, f"Generated by: {generated_by}")
    y -= 35

    # 1. GENERAL OVERVIEW
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "1. GENERAL SYSTEM OVERVIEW")
    p.line(50, y - 5, 550, y - 5)
    y -= 25

    p.setFont("Helvetica", 10)

    overview = [
        f"Total movies: {total_movies}",
        f"Active movies: {active_movies}",
        f"Total cinemas: {total_cinemas}",
        f"Active cinemas: {active_cinemas}",
        f"Total auditoriums: {total_auditoriums}",
        f"Active auditoriums: {active_auditoriums}",
        f"Total physical seats: {total_seats}",
        f"Total showtimes: {total_showtimes}",
        f"Registered customers: {total_registered_customers}",
    ]

    for item in overview:
        if y < 60:
            p.showPage()
            y = page_height - 50
            p.setFont("Helvetica", 10)

        p.drawString(50, y, item)
        y -= 20

    y -= 15

    # 2. RESERVATION SUMMARY
    if y < 100:
        p.showPage()
        y = page_height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "2. RESERVATION SUMMARY")
    p.line(50, y - 5, 550, y - 5)
    y -= 25

    p.setFont("Helvetica", 10)

    reservation_summary = [
        f"Total reservations: {total_reservations}",
        f"Confirmed reservations: {confirmed_reservations}",
        f"Pending reservations: {pending_reservations}",
        f"Cancelled reservations: {cancelled_reservations}",
        f"Active/Pending reserved seats: {total_reserved_seats}",
        f"Cancelled reserved seats: {cancelled_reserved_seats}",
    ]

    for item in reservation_summary:
        if y < 60:
            p.showPage()
            y = page_height - 50
            p.setFont("Helvetica", 10)

        p.drawString(50, y, item)
        y -= 20

    y -= 15

    # 3. FINANCIAL SUMMARY
    if y < 120:
        p.showPage()
        y = page_height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "3. FINANCIAL SUMMARY")
    p.line(50, y - 5, 550, y - 5)
    y -= 25

    p.setFont("Helvetica", 10)

    financial_summary = [
        f"Total booking value: KSh {total_amount:,.2f}",
        f"Average booking value: KSh {avg_total_amount:,.2f}",
        f"Confirmed booking value: KSh {confirmed_total_amount:,.2f}",
        f"Cancelled booking value: KSh {cancelled_total_amount:,.2f}",
    ]

    for item in financial_summary:
        if y < 60:
            p.showPage()
            y = page_height - 50
            p.setFont("Helvetica", 10)

        p.drawString(50, y, item)
        y -= 20

    y -= 15

    # 4. MOVIE PERFORMANCE
    if y < 160:
        p.showPage()
        y = page_height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "4. MOVIE PERFORMANCE")
    p.line(50, y - 5, 550, y - 5)
    y -= 25

    p.setFont("Helvetica", 10)

    movie_summary = [
        f"Most booked movie: {highest_reserved_movie} ({highest_reserved_movie_count} reservations)",
        f"Least booked movie: {lowest_reserved_movie} ({lowest_reserved_movie_count} reservations)",
        "Reservations per movie:"
    ]

    for item in movie_summary:
        p.drawString(50, y, item)
        y -= 20

    for movie in movie_report:
        if y < 60:
            p.showPage()
            y = page_height - 50
            p.setFont("Helvetica", 10)

        p.drawString(65, y, f"{movie['movie']}: {movie['reservations']} reservations")
        y -= 20

    y -= 15

    # 5. SHOWTIME PERFORMANCE
    if y < 180:
        p.showPage()
        y = page_height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "5. SHOWTIME PERFORMANCE")
    p.line(50, y - 5, 550, y - 5)
    y -= 25

    p.setFont("Helvetica", 10)

    showtime_summary = [
        f"Completed showtimes: {completed_showtimes}",
        f"Scheduled showtimes: {scheduled_showtimes}",
        f"Cancelled showtimes: {cancelled_showtimes}",
        f"Most booked showtime: {highest_reserved_showtime} ({highest_reserved_showtime_count} reservations)",
        f"Least booked showtime: {lowest_reserved_showtime} ({lowest_reserved_showtime_count} reservations)",
        "Individual showtime occupancy:"
    ]

    for item in showtime_summary:
        if y < 60:
            p.showPage()
            y = page_height - 50
            p.setFont("Helvetica", 10)

        p.drawString(50, y, item)
        y -= 20

    for showtime in showtime_report:
        if y < 80:
            p.showPage()
            y = page_height - 50
            p.setFont("Helvetica", 10)

        p.drawString(65, y, f"{showtime['movie']} - {showtime['start_time']}")
        y -= 20
        p.drawString(65, y, f"Seats: {showtime['booked_seats']}/{showtime['total_seats']} | Occupancy: {showtime['occupancy_rate']:.2f}%")
        y -= 25

    y -= 15

    # 6. CINEMA PERFORMANCE
    if y < 120:
        p.showPage()
        y = page_height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "6. CINEMA PERFORMANCE")
    p.line(50, y - 5, 550, y - 5)
    y -= 25

    p.setFont("Helvetica", 10)

    if most_popular_cinema:
        p.drawString(50, y, f"Most popular cinema: {most_popular_cinema.name}")
    else:
        p.drawString(50, y, "Most popular cinema: N/A")

    y -= 25

    for cinema in cinema_report:
        if y < 100:
            p.showPage()
            y = page_height - 50
            p.setFont("Helvetica", 10)

        p.drawString(50, y, f"Cinema: {cinema['cinema']}")
        y -= 20
        p.drawString(65, y, f"Booked seats: {cinema['booked_seats']}")
        y -= 20
        p.drawString(65, y, f"Total capacity: {cinema['total_capacity']}")
        y -= 20
        p.drawString(65, y, f"Occupancy: {cinema['occupancy_rate']:.2f}%")
        y -= 25

    y -= 15

    # 7. CUSTOMER STATISTICS
    if y < 120:
        p.showPage()
        y = page_height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "7. CUSTOMER STATISTICS")
    p.line(50, y - 5, 550, y - 5)
    y -= 25

    p.setFont("Helvetica", 10)

    p.drawString(50, y, f"Registered customers: {total_registered_customers}")
    y -= 20
    p.drawString(50, y, f"New customers in the last 30 days: {new_customers}")
    y -= 20
    p.drawString(50, y, f"Average reservations per customer: {avg_no_of_reservation_per_customer:.2f}")
    y -= 20

    if customer_with_highest_reservation:
        p.drawString(50, y, f"Most active customer: {customer_with_highest_reservation.username}")
        y -= 20
        p.drawString(50, y, f"Reservations: {customer_with_highest_reservation.reservations_user}")
    else:
        p.drawString(50, y, "Most active customer: N/A")

    y -= 35

    # 8. CANCELLATION SUMMARY
    if y < 150:
        p.showPage()
        y = page_height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "8. CANCELLATION SUMMARY")
    p.line(50, y - 5, 550, y - 5)
    y -= 25

    p.setFont("Helvetica", 10)

    p.drawString(50, y, f"Cancelled reservations: {cancelled_reservations}")
    y -= 20
    p.drawString(50, y, f"Cancelled seats: {cancelled_seats}")
    y -= 20
    p.drawString(50, y, f"Cancellation rate: {cancellation_rate:.2f}%")
    y -= 20
    p.drawString(50, y, f"Showtime with most cancellations: {highest_cancelled_showtime}")
    y -= 20
    p.drawString(50, y, f"Cancellation count: {highest_cancelled_showtime_count}")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="movie_reservation_report.pdf")
