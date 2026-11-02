// ==============================
// This is a mongo shell script that generates shows from movie id in show collection
// ==============================

// ==============================
// CONFIG
// ==============================

const movieId = "68b02b634cb16581f7773601";

// Add your 3-4 theatre location IDs here
const locationIds = [
    "68b0635b4cb16581f77735b3",
    "68b0635b4cb16581f77735b2",
    "68b0635b4cb16581f77735b4",
    "68b0635b4cb16581f77735b0",
    "68b0635b4cb16581f77735b5",
    "68b0635b4cb16581f77735b1"
];

// Date for all shows
const year = 2027;
const month = 2;
const day = 21;

// Number of shows generated PER LOCATION
const minShowsPerLocation = 4;
const maxShowsPerLocation = 7;


// ==============================
// HELPERS
// ==============================

function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomItem(array) {
    return array[Math.floor(Math.random() * array.length)];
}

function shuffle(array) {
    return array.sort(() => Math.random() - 0.5);
}


// Convert IST date/time to Unix epoch seconds
function getEpoch(hour, minute) {
    const dateString =
        `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")} ` +
        `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}:00`;

    // IST = UTC + 5:30
    const utcDate = new Date(
        dateString.replace(" ", "T") + "+05:30"
    );

    return Math.floor(utcDate.getTime() / 1000);
}


// ==============================
// SHOW TIME OPTIONS
// ==============================

const possibleTimes = [
    [10, 0],
    [11, 30],
    [13, 0],
    [14, 30],
    [16, 0],
    [17, 30],
    [19, 0],
    [20, 30],
    [22, 0],
    [23, 0]
];


// ==============================
// FETCH MOVIE
// ==============================

const movie = db.movie.findOne({
    _id: ObjectId(movieId)
});

if (!movie) {
    throw new Error(`Movie not found: ${movieId}`);
}

print(`Movie: ${movie.title}`);
print(`Locations: ${locationIds.length}`);
print("--------------------------------");


// ==============================
// GENERATE SEATS
// ==============================

function generateSeats() {

    // Random number of rows
    const rowCount = randomInt(8, 10);

    // Random seats per row
    const seatsPerRow = randomInt(6, 8);

    const rows = [];

    for (let r = 0; r < rowCount; r++) {

        const rowLetter = String.fromCharCode(65 + r);

        const seats = [];

        for (let s = 0; s < seatsPerRow; s++) {

            // Front rows VIP, rest Regular
            const type = r < 2 ? "VIP" : "Regular";

            const random = Math.random();

            let status = "available";
            let booking_id = undefined;

            if (random < 0.03) {
                status = "booked";
            }
            else if (random < 0.05) {
                status = "reserved";

                booking_id =
                    Math.random().toString(36).substring(2, 14);
            }

            const seat = {
                type: type,
                status: status
            };

            if (booking_id) {
                seat.booking_id = booking_id;
            }

            seats.push(seat);
        }

        rows.push({
            row: rowLetter,
            seats: seats
        });
    }

    return {
        rows: rows,
        capacity: rowCount * seatsPerRow
    };
}


// ==============================
// GENERATE AISLES
// ==============================

function generateAisles(rowCount, seatsPerRow) {

    const verticalOptions = [];

    if (seatsPerRow >= 6) {
        verticalOptions.push(2);
        verticalOptions.push(3);
        verticalOptions.push(5);
    }

    const verticalCount = randomInt(1, 2);

    const vertical = shuffle(verticalOptions)
        .slice(0, verticalCount);

    const horizontalOptions = [];

    if (rowCount >= 8) {
        horizontalOptions.push("B");
        horizontalOptions.push("D");
        horizontalOptions.push("F");
        horizontalOptions.push("H");
    }

    const horizontalCount = randomInt(1, 2);

    const horizontal = shuffle(horizontalOptions)
        .slice(0, horizontalCount);

    return {
        vertical_after_seat_indexes: vertical,
        horizontal_after_rows: horizontal
    };
}


// ==============================
// GENERATE SHOWS
// ==============================

const shows = [];

for (const locationId of locationIds) {

    // Random number of shows for this theatre
    const numberOfShows =
        randomInt(minShowsPerLocation, maxShowsPerLocation);

    // Pick unique timings
    const selectedTimes =
        shuffle([...possibleTimes])
            .slice(0, numberOfShows);

    print(`Location: ${locationId}`);
    print(`Shows: ${numberOfShows}`);

    for (let i = 0; i < selectedTimes.length; i++) {

        const [hour, minute] = selectedTimes[i];

        const seatData = generateSeats();

        const rowCount = seatData.rows.length;
        const seatsPerRow = seatData.rows[0].seats.length;

        const showTypes = [
            "2D",
            "2D",
            "2D",
            "IMAX 2D",
            "IMAX 3D",
            "3D"
        ];

        const showType = randomItem(showTypes);

        const price =
            showType === "IMAX 3D"
                ? randomItem([180, 200, 220, 250])
                : showType === "IMAX 2D"
                    ? randomItem([150, 170, 180, 200])
                    : showType === "3D"
                        ? randomItem([130, 150, 170])
                        : randomItem([100, 120, 140]);

        const screenNumber = randomInt(1, 6);

        const show = {
            movie_id: movieId,

            show_type: showType,

            location_id: locationId,

            screen_number: screenNumber,

            show_timing_epoch: NumberLong(
                getEpoch(hour, minute)
            ),

            movie_title: movie.title,

            exits: shuffle([
                "bottom-left",
                "bottom-right",
                "middle-left",
                "middle-right",
                "top-left",
                "top-right"
            ]).slice(0, randomInt(3, 4)),

            status: "scheduled",

            seating_capacity: seatData.capacity,

            seat_rows: seatData.rows,

            price_label: NumberInt(price),

            aisles: generateAisles(
                rowCount,
                seatsPerRow
            )
        };

        shows.push(show);

        print(
            `  ${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")} ` +
            `| ${showType} | Screen ${screenNumber} | ₹${price}`
        );
    }

    print("--------------------------------");
}


// ==============================
// INSERT
// ==============================

if (shows.length > 0) {

    const result = db.show.insertMany(shows);

    print(`Inserted ${result.insertedIds.length} shows.`);
}