import os
import psycopg

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")


class Booking(BaseModel):
    room_id: int
    datefrom: str
    dateto: str
    addinfo: str = ""


@app.get("/rooms")
def get_rooms():
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("SELECT id, room_number, type, price FROM hotel_rooms ORDER BY room_number")
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


@app.get("/bookings")
def get_bookings():
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT hotel_bookings.id, hotel_bookings.room_id, hotel_rooms.room_number,
               hotel_bookings.datefrom, hotel_bookings.dateto, hotel_bookings.addinfo
        FROM hotel_bookings
        JOIN hotel_rooms ON hotel_bookings.room_id = hotel_rooms.id
        ORDER BY hotel_bookings.id
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    bookings = []
    for row in rows:
        bookings.append({
            "id": row[0],
            "room_id": row[1],
            "room_number": row[2],
            "datefrom": str(row[3]),
            "dateto": str(row[4]),
            "addinfo": row[5]
        })

    return bookings


@app.post("/bookings")
def create_booking(booking: Booking):
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO hotel_bookings (guest_id, room_id, datefrom, dateto, addinfo)
        VALUES (%s, %s, %s, %s, %s)
    """, (1, booking.room_id, booking.datefrom, booking.dateto, booking.addinfo))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Booking saved"}


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Hotel Front-end</title>
    </head>
    <body>
        <h1>Hotel Booking</h1>

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

        <button onclick="saveBooking()">Save booking</button>

        <h2>All bookings</h2>
        <ul id="bookingList"></ul>

        <script>
            async function loadRooms() {
                let response = await fetch("/rooms");
                let rooms = await response.json();

                let select = document.getElementById("room");
                select.innerHTML = "";

                for (let i = 0; i < rooms.length; i++) {
                    let option = document.createElement("option");
                    option.value = rooms[i].id;
                    option.textContent = "Room " + rooms[i].room_number + " - " + rooms[i].type;
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
                    li.textContent =
                        "Room " + bookings[i].room_number +
                        " | " + bookings[i].datefrom +
                        " to " + bookings[i].dateto +
                        " | " + bookings[i].addinfo;
                    list.appendChild(li);
                }
            }

            async function saveBooking() {
                let room_id = parseInt(document.getElementById("room").value);
                let datefrom = document.getElementById("datefrom").value;
                let dateto = document.getElementById("dateto").value;
                let addinfo = document.getElementById("info").value;

                let response = await fetch("/bookings", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        room_id: room_id,
                        datefrom: datefrom,
                        dateto: dateto,
                        addinfo: addinfo
                    })
                });

                let result = await response.json();
                alert(result.message);

                loadBookings();
            }

            loadRooms();
            loadBookings();
        </script>
    </body>
    </html>
    """
