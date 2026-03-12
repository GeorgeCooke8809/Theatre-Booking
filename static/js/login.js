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

    correctness = response.json()
    console.log(correctness)

    if (correctness.correct){}
    else{
        console.log("Login is incorrect, showing flash message")
        const container = document.getElementById("flash-container");

        const msg = document.createElement("div");
        msg.className = "flash-message";
        msg.textContent = "That username or password is incorrect.";

        container.appendChild(msg);

        setTimeout(() => {
            msg.remove();
        }, 3000);
    }
}