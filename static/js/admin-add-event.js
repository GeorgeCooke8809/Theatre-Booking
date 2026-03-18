let seats = [];

async function addSeat(seatID){
    seats.push(seatID)
    console.log(`${seatID} Added`)
    console.log(`${seats}`)

    oldSeatButton = document.getElementById(seatID)

    var newSeatButton = document.createElement("button")
    newSeatButton.className = "seat-button unavailable-seat"
    newSeatButton.id = seatID
    newSeatButton.setAttribute("onclick",`removeSeat('${seatID}')`);
    newSeatButton.textContent = seatID

    oldSeatButton.replaceWith(newSeatButton)
}

async function removeSeat(seatID){
    var index = seats.indexOf(seatID)
    if (index > -1){
        seats.splice(index)
    }

    console.log(`${seatID} removed from index ${index}`)
    console.log(`${seats}`)

    oldSeatButton = document.getElementById(seatID)

    var newSeatButton = document.createElement("button")
    newSeatButton.className = "seat-button available-seat"
    newSeatButton.id = seatID
    newSeatButton.setAttribute("onclick",`addSeat('${seatID}')`);
    newSeatButton.textContent = seatID

    oldSeatButton.replaceWith(newSeatButton)
}

async function addEvent(){
    event.preventDefault();
}