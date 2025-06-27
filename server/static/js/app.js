$(document).foundation();

function convertToDateISO8601(strDate) {
    const parts = strDate.split("/");
    // because the view shows and the datetime picker is set dd/mm/yyyy
    // JavaScript counts months from 0 to 11;
    // hours=2 makes sure that the system instantiates the exact date
    // chosen from the datetime picker regardless of BST
    let isoDate = new Date(parts[2], parts[1]-1, parts[0],2,0,0);
    isoDate = isoDate.toISOString();
    console.log(isoDate);
    return isoDate.split('T')[0];
}


function convertToISODateTime() {
    const d = new Date(); // for now
    const hour = d.getHours() < 10 ? "0" + d.getHours().toString() : d.getHours();
    const minute = d.getMinutes() < 10 ? "0" + d.getMinutes().toString() : d.getMinutes();
    const second = d.getSeconds() < 10 ? "0" + d.getSeconds().toString() : d.getSeconds();
    return " " + hour + ":" + minute + ":"+ second;
}

function getTimestamp(strDate) {
    const date = new Date(strDate);
    return date.getTime()/1000;
}

