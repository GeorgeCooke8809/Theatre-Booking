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

async function addEvent(){
    event.preventDefault();

    console.log("Trying to add event")

    var title = document.querySelector("#name").value;
    var description = document.querySelector("#description").value;
    var childPrice = document.querySelector("#childPrice").value;
    var adultPrice = document.querySelector("#adultPrice").value;
    var elderlyPrice = document.querySelector("#elderlyPrice").value;

    response = await fetch("/api/add-event", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "title": title,
                    "description": description,
                    "childPrice": childPrice,
                    "adultPrice": adultPrice,
                    "elderlyPrice": elderlyPrice,
                    "unavailableSeats": seats
                })
            });

    response_json = await response.json()
    console.log(response_json)

    if (response_json.code == 200){
        console.log("Information correct, redirecting.")
        window.location.replace("./admin-dashboard")
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