async function createAccount(){
    event.preventDefault()
    var fname = document.querySelector("#fName").value;
    var lname = document.querySelector("#lName").value;
    var phone = document.querySelector("#phone-number").value;
    var email = document.querySelector("#email").value;
    var password = document.querySelector("#password").value;
    var repeatPassword = document.querySelector("#repeat-password").value;

    response = await fetch("/api/create-account", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "fName": fname,
                "lName": lname,
                "email": email,
                "phone": phone,
                "password": password,
                "repeatPassword": repeatPassword
            })
            });

    response_json = await response.json()
    console.log(response)

    if (response_json.code == 200){
        console.log("Information correct, redirecting.")
        window.location.replace("./account-created")
    }
    else{
        console.log("Information incorrect, flashing error.")
        
        flashMessage(response_json.message)
    }
}