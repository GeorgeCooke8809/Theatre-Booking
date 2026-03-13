async function flashMessage(message){
    console.log(`Flashing message ${message}`)
    const container = document.getElementById("flash-container");

    const msg = document.createElement("div");
    msg.className = "flash-message";
    msg.textContent = message;

    container.appendChild(msg);

    setTimeout(() => {
        msg.remove();
    }, 3000);
}