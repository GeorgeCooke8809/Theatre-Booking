async function deletePerformance(performanceID){
    event.preventDefault()

    response = await fetch("/api/delete-performance", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "performanceID": performanceID
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

async function addShowing(date, performanceID){
    event.preventDefault()

    console.log(date)

    response = await fetch("/api/add-showing", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                    "performanceID": performanceID,
                    "date": date
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