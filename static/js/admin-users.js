async function updateUser(userID){
    event.preventDefault();

    var new_type = document.querySelector(`#update-${userID}`).querySelector(".visitor-new-type").value;

    response = await fetch("/api/update-user-type", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "userID": userID,
                    "newType": new_type
                })
            });

    response_json = await response.json()
    console.log(response_json)

    if (response_json.code == 200){
        console.log("Information correct, redirecting.")
        window.location.replace("./admin-users")
    }
    else{
        console.log("Information incorrect, flashing error.")
        
        flashMessage(response_json.message)
    }
}

async function search(term){
    event.preventDefault();

    term = document.querySelector(`#update-${userID}`).querySelector(".visitor-new-type").value

    response = await fetch("/api/add-showing", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "performanceID": performanceID,
                    "date": date
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

async function deleteShowing(showingID){
    event.preventDefault()

    response = await fetch("/api/delete-showing", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "showingID": showingID
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