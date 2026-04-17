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

    response_json = await response.json();
    console.log(response_json);

    if (response_json.code == 200){
        console.log("Information correct, redirecting.");
        window.location.replace("./admin-users");
    }
    else{
        console.log("Information incorrect, flashing error.");
        
        flashMessage(response_json.message);
    }
}

async function search(term){
    event.preventDefault();

    term = document.querySelector('#search-field').value;

    response = await fetch("/api/search-users", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "term": term
                })
            });

    response_json = await response.json()
    console.log(response_json)

    if (response_json.code == 200){
        console.log("Information correct, inserting elements.")

        container = document.querySelector("#users-section");
        container.innerHTML = '';
        
        for (let i=0; i < (response_json.elements.length); i++){
            let user = response_json.elements[i]
            console.log(user)

            let card = document.createElement("div")
            card.classList.add("user-card", "inline-split")
            console.log(card)
            
            let heading = document.createElement("h4")
            heading.textContent = `${ user[1] } ${ user[2] } - ${ user[3] }`
            card.appendChild(heading)

            let form = document.createElement("form")
            form.classList.add("inline", "user-type-form")
            form.id = `update-${user[0]}` /* TODO: Contiunue generating form */

            container.appendChild(card)
        }
    }
    else{
        console.log("Information incorrect, flashing error.")
        
        flashMessage(response_json.message)
    }
}