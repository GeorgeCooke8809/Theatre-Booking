async function checkPassword(email, password){
    event.preventDefault()
    var email = document.querySelector("#username").value;
    console.log(email);
    var password = document.querySelector("#password").value;
    console.log(password);

    response = await fetch("/api/check-login-details", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({"email": email, "password": password})
            });

    console.log(response.json())
}