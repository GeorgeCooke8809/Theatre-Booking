let seats = [];

async function addSeat(seatID){
    seats.push(seatID);
    console.log(`${seatID} Added`);
    console.log(`${seats}`);

    oldSeatButton = document.getElementById(seatID);

    var newSeatButton = document.createElement("button");
    newSeatButton.className = "seat-button unavailable-seat";
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
    console.log(response)

    if (response_json.code == 200){
        console.log("Information correct, redirecting.")
        window.location.replace("./admin-dashboard")
    }
    else{
        console.log("Information incorrect, flashing error.")
        
        flashMessage(response_json.message)
    }
}