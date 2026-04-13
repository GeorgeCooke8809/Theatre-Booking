let seats = [];

async function addSeat(seatID){
    seats.push(seatID);
    console.log(`${seatID} Added`);
    console.log(`${seats}`);

    oldSeatButton = document.getElementById(seatID);

    var newSeatButton = document.createElement("button");
    newSeatButton.className = "seat-button selected-seat";
    newSeatButton.id = seatID;
    newSeatButton.setAttribute("onclick",`removeSeat('${seatID}')`);
    newSeatButton.textContent = seatID;

    oldSeatButton.replaceWith(newSeatButton);
}

async function removeSeat(seatID){
    var index = seats.indexOf(seatID);
    if (index > -1){
        seats.splice(index);
    };

    console.log(`${seatID} removed from index ${index}`);
    console.log(`${seats}`);

    oldSeatButton = document.getElementById(seatID);

    var newSeatButton = document.createElement("button");
    newSeatButton.className = "seat-button available-seat";
    newSeatButton.id = seatID;
    newSeatButton.setAttribute("onclick",`addSeat('${seatID}')`);
    newSeatButton.textContent = seatID;

    oldSeatButton.replaceWith(newSeatButton);
}

async function bookShowing(userID, showingID){
    event.preventDefault();

    console.log("Trying to book seats")

    var childSeats = document.querySelector("#childSeats").value;
    var adultSeats = document.querySelector("#adultSeats").value;
    var elderlySeats = document.querySelector("#elderlySeats").value;

    response = await fetch("/api/book-showing", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "userID": userID,
                    "showingID": showingID,
                    "childSeats": childSeats,
                    "adultSeats": adultSeats,
                    "elderlySeats": elderlySeats,
                    "bookedSeats": seats
                })
            });

    response_json = await response.json()
    console.log(response_json)

    if (response_json.code == 200){
        console.log("Information correct, redirecting.")
        window.location.replace(`./thank-you?bid=${response_json.bookingID}&&uid=${userID}`)
    }
    else{
        console.log("Information incorrect, flashing error.")
        
        flashMessage(response_json.message)
    }
}

function markUnavailableSeats(unavailableSeatsArray){
    console.log(unavailableSeatsArray);

    for (let i = 0; i < unavailableSeatsArray.length; i++) {
        let seat = unavailableSeatsArray[i];
        let seat_button = document.getElementById(seat[0]);

        seat_button.setAttribute("onclick","");

        if (seat[1] == "BOOKED") {
            seat_button.classList = "seat-button booked-seat";
        } else if (seat[1] == "UNAVAILABLE") {
            seat_button.classList = "seat-button unavailable-seat";
        }
    }
}

async function updateSubtotal(userID, showingID){
    console.log("Updating price")

    var price_display = document.querySelector("#price-display")

    var childSeats = document.querySelector("#childSeats").value;
    var adultSeats = document.querySelector("#adultSeats").value;
    var elderlySeats = document.querySelector("#elderlySeats").value;

    response = await fetch("/api/get-price", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "userID": userID,
                    "showingID": showingID,
                    "childSeats": childSeats,
                    "adultSeats": adultSeats,
                    "elderlySeats": elderlySeats,
                })
            });

    response_json = await response.json()
    console.log(response_json)

    if (response_json.code == 200){
        console.log("Got price")
    }
    else{
        console.log("Error, flashing error.")
        
        flashMessage(response_json.message)
    }

    price_display.textContent = response_json.price
}