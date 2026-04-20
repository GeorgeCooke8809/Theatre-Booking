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

        container = document.querySelector("#users-section");
        container.innerHTML = '';
        
        updateUsersList(response_json.elements)
    }
    else{
        console.log("Information incorrect, flashing error.")
        
        flashMessage(response_json.message)
    }
}

function updateUsersList(users){
    for (let i=0; i < (users.length); i++){
        let user = users[i]

        let card = document.createElement("div")
        card.classList.add("user-card", "inline-split")
        
        let heading = document.createElement("h4")
        heading.textContent = `${ user[1] } ${ user[2] } - ${ user[3] }`
        card.appendChild(heading)

        let form = document.createElement("form")
        form.classList.add("inline", "user-type-form")
        form.id = `update-${user[0]}`
        form.setAttribute("onsubmit", `updateUser('${user[0]}')`)

        let select = document.createElement("select")
        select.className = "visitor-new-type"
        select.name = "user-type"

        let options = [["VISITOR", "Visitor"], ["SPECIAL", "Special"], ["ADMIN", "Admin"]]

        for (j = 0; j < options.length; j++){
            option = options[j]

            option_elem = document.createElement("option")
            option_elem.value = option[0]

            if (user[4] == option[0]){
                option_elem.selected = "selected"
                option_elem.textContent = `${option[1]}*`
            }
            else{
                option_elem.textContent = option[1]
            }

            select.appendChild(option_elem)
        }

        let delete_option = document.createElement("option")
        delete_option.value = "DELETE"
        delete_option.textContent = "DELETE"
        delete_option.className = "delete-user"

        select.appendChild(delete_option)

        form.appendChild(select)

        let form_submit = document.createElement("input")
        form_submit.type = "submit"
        form_submit.value = "Submit"
        form_submit.className = "basic-button"

        form.appendChild(form_submit)

        card.appendChild(form)

        container.appendChild(card)
    }
}