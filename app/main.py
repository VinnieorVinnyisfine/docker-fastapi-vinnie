import os
import psycopg

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")


class Booking(BaseModel):
    guest_id: int
    room_id: int
    datefrom: str
    dateto: str
    addinfo: str = ""


class StarsReview(BaseModel):
    stars: int


@app.get("/rooms")
def get_rooms():
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, room_number, type, price
        FROM hotel_rooms
        ORDER BY room_number
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    rooms = []

    for row in rows:
        rooms.append({
            "id": row[0],
            "room_number": row[1],
            "type": row[2],
            "price": float(row[3])
        })

    return rooms


@app.get("/guests")
def get_guests():
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            hotel_guests.id,
            hotel_guests.name,
            hotel_guests.email,

            (
                SELECT COUNT(*)
                FROM hotel_bookings
                WHERE hotel_bookings.guest_id = hotel_guests.id
            ) AS previous_visits

        FROM hotel_guests
        ORDER BY hotel_guests.id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    guests = []

    for row in rows:
        guests.append({
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "previous_visits": row[3]
        })

    return guests


@app.get("/bookings")
def get_bookings():
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            hotel_bookings.id,

            hotel_guests.name,

            hotel_rooms.room_number,
            hotel_rooms.price,

            hotel_bookings.datefrom,
            hotel_bookings.dateto,

            hotel_bookings.addinfo,

            (hotel_bookings.dateto - hotel_bookings.datefrom) AS number_of_nights,

            (hotel_bookings.dateto - hotel_bookings.datefrom)
            * hotel_rooms.price AS total_price,

            hotel_bookings.stars

        FROM hotel_bookings

        INNER JOIN hotel_rooms
            ON hotel_bookings.room_id = hotel_rooms.id

        INNER JOIN hotel_guests
            ON hotel_bookings.guest_id = hotel_guests.id

        ORDER BY hotel_bookings.id
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    bookings = []

    for row in rows:
        bookings.append({
            "id": row[0],
            "guest_name": row[1],
            "room_number": row[2],
            "price_per_night": float(row[3]),
            "datefrom": str(row[4]),
            "dateto": str(row[5]),
            "addinfo": row[6],
            "number_of_nights": row[7],
            "total_price": float(row[8]),
            "stars": row[9]
        })

    return bookings


@app.post("/bookings")
def create_booking(booking: Booking):
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO hotel_bookings
        (guest_id, room_id, datefrom, dateto, addinfo)

        VALUES (%s, %s, %s, %s, %s)
    """, (
        booking.guest_id,
        booking.room_id,
        booking.datefrom,
        booking.dateto,
        booking.addinfo
    ))

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Booking saved"}


@app.put("/bookings/{booking_id}")
def update_stars(booking_id: int, review: StarsReview):
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        UPDATE hotel_bookings
        SET stars = %s
        WHERE id = %s
    """, (
        review.stars,
        booking_id
    ))

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Stars updated"}


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Hotel Front-end</title>
    </head>

    <body>

        <h1>Hotel Booking</h1>

        <label>Choose guest:</label>
        <select id="guest"></select>

        <br><br>

        <label>Choose room:</label>
        <select id="room"></select>

        <br><br>

        <label>Date from:</label>
        <input type="date" id="datefrom">

        <br><br>

        <label>Date to:</label>
        <input type="date" id="dateto">

        <br><br>

        <label>Additional info:</label>
        <input type="text" id="info">

        <br><br>

        <button onclick="saveBooking()">
            Save booking
        </button>

        <h2>All bookings</h2>

        <ul id="bookingList"></ul>

        <script>

            async function loadGuests() {

                let response = await fetch("/guests");

                let guests = await response.json();

                let select = document.getElementById("guest");

                select.innerHTML = "";

                for (let i = 0; i < guests.length; i++) {

                    let option = document.createElement("option");

                    option.value = guests[i].id;

                    option.textContent =
                        guests[i].name +
                        " (" +
                        guests[i].previous_visits +
                        " visits)";

                    select.appendChild(option);
                }
            }


            async function loadRooms() {

                let response = await fetch("/rooms");

                let rooms = await response.json();

                let select = document.getElementById("room");

                select.innerHTML = "";

                for (let i = 0; i < rooms.length; i++) {

                    let option = document.createElement("option");

                    option.value = rooms[i].id;

                    option.textContent =
                        "Room " +
                        rooms[i].room_number +
                        " - " +
                        rooms[i].type;

                    select.appendChild(option);
                }
            }


            async function loadBookings() {

                let response = await fetch("/bookings");

                let bookings = await response.json();

                let list = document.getElementById("bookingList");

                list.innerHTML = "";

                for (let i = 0; i < bookings.length; i++) {

                    let li = document.createElement("li");

                    let starsText = "No review";

                    if (bookings[i].stars !== null) {
                        starsText = bookings[i].stars + " stars";
                    }

                    li.innerHTML =

                        bookings[i].guest_name +

                        " | Room " +

                        bookings[i].room_number +

                        " | " +

                        bookings[i].datefrom +

                        " to " +

                        bookings[i].dateto +

                        " | Nights: " +

                        bookings[i].number_of_nights +

                        " | Total: $" +

                        bookings[i].total_price +

                        " | Review: " +

                        starsText +

                        " | " +

                        bookings[i].addinfo +

                        " | Select stars: " +

                        "<select id='stars-" + bookings[i].id + "'>" +
                            "<option value='1'>1 star</option>" +
                            "<option value='2'>2 stars</option>" +
                            "<option value='3'>3 stars</option>" +
                            "<option value='4'>4 stars</option>" +
                            "<option value='5'>5 stars</option>" +
                        "</select>" +

                        " <button onclick='updateStars(" + bookings[i].id + ")'>Save review</button>";

                    list.appendChild(li);
                }
            }


            async function saveBooking() {

                let guest_id =
                    parseInt(document.getElementById("guest").value);

                let room_id =
                    parseInt(document.getElementById("room").value);

                let datefrom =
                    document.getElementById("datefrom").value;

                let dateto =
                    document.getElementById("dateto").value;

                let addinfo =
                    document.getElementById("info").value;

                let response = await fetch("/bookings", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        guest_id: guest_id,
                        room_id: room_id,
                        datefrom: datefrom,
                        dateto: dateto,
                        addinfo: addinfo
                    })
                });

                let result = await response.json();

                alert(result.message);

                loadGuests();
                loadBookings();
            }


            async function updateStars(bookingId) {

                let stars =
                    parseInt(document.getElementById("stars-" + bookingId).value);

                let response = await fetch("/bookings/" + bookingId, {

                    method: "PUT",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        stars: stars
                    })
                });

                let result = await response.json();

                alert(result.message);

                loadBookings();
            }


            loadGuests();
            loadRooms();
            loadBookings();

        </script>

    </body>
    </html>
    """
